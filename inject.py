#!/usr/bin/env python3
"""
inject.py – Bereitet das modifizierte Debian-Installer-Image vor:
  1. Injiziert preseed.cfg in die initrd (macOS-kompatibler CPIO-Append)
  2. Patcht grub.cfg: timeout=0, Automated install als Standard, locale/keymap
  3. Patcht isolinux.cfg: timeout=0, Automated install als Standard (BIOS)
"""

import gzip
import shutil
import os
import re
import struct
import sys

# -----------------------------------------------------------------------
# Hilfsfunktionen für CPIO (newc-Format) – macOS-kompatibel, kein -A Flag
# -----------------------------------------------------------------------

def cpio_header(name, filesize):
    """Erzeugt einen CPIO newc-Header für eine Datei."""
    name_bytes = name.encode() + b'\x00'
    name_len = len(name_bytes)
    # CPIO newc Header (110 Bytes fix)
    header = (
        b'070701'                          # Magic
        + b'00000000'                      # ino
        + b'000081A4'                      # mode (reguläre Datei, 0644)
        + b'00000000'                      # uid
        + b'00000000'                      # gid
        + b'00000001'                      # nlink
        + b'00000000'                      # mtime
        + f'{filesize:08X}'.encode()       # filesize
        + b'00000000'                      # devmajor
        + b'00000000'                      # devminor
        + b'00000000'                      # rdevmajor
        + b'00000000'                      # rdevminor
        + f'{name_len:08X}'.encode()       # namesize
        + b'00000000'                      # check
    )
    # Header + Name auf 4-Byte-Grenze auffüllen
    header_and_name = header + name_bytes
    pad = (4 - len(header_and_name) % 4) % 4
    header_and_name += b'\x00' * pad
    return header_and_name

def cpio_trailer():
    """Erzeugt den CPIO-Abschluss-Eintrag (TRAILER!!!)."""
    return cpio_header('TRAILER!!!', 0)

def append_file_to_cpio(cpio_data, filepath):
    """Hängt eine Datei an vorhandene CPIO-Daten an (ersetzt TRAILER)."""
    # Bestehenden TRAILER am Ende entfernen
    trailer = cpio_header('TRAILER!!!', 0)
    if cpio_data.endswith(trailer):
        cpio_data = cpio_data[:-len(trailer)]
    # Padding auf 512-Byte-Grenze (cpio-Konvention)
    pad = (512 - len(cpio_data) % 512) % 512
    cpio_data += b'\x00' * pad

    # Dateiinhalt einlesen
    with open(filepath, 'rb') as f:
        file_data = f.read()
    filesize = len(file_data)

    # Header + Dateiinhalt + Padding + neuer TRAILER
    entry = cpio_header(os.path.basename(filepath), filesize)
    entry += file_data
    pad = (4 - filesize % 4) % 4
    entry += b'\x00' * pad

    return cpio_data + entry + cpio_trailer()


# -----------------------------------------------------------------------
# 1. preseed.cfg in initrd injizieren
# -----------------------------------------------------------------------
print("[1/3] Injiziere preseed.cfg in initrd...")

if not os.path.exists('initrd.gz'):
    print("FEHLER: 'initrd.gz' nicht gefunden!")
    sys.exit(1)
if not os.path.exists('preseed.cfg'):
    print("FEHLER: 'preseed.cfg' nicht gefunden!")
    sys.exit(1)

# initrd.gz entpacken
with gzip.open('initrd.gz', 'rb') as f:
    cpio_data = f.read()

# preseed.cfg anhängen
cpio_data = append_file_to_cpio(cpio_data, 'preseed.cfg')

# Als initrd_master.gz wieder einpacken
with gzip.open('initrd_master.gz', 'wb', compresslevel=9) as f:
    f.write(cpio_data)

print("    -> initrd_master.gz erstellt.")


# -----------------------------------------------------------------------
# 2. grub.cfg patchen (UEFI)
# -----------------------------------------------------------------------
print("[2/3] Patche grub.cfg...")

GRUB_CFG = 'grub.cfg'
if not os.path.exists(GRUB_CFG):
    print(f"    WARNUNG: '{GRUB_CFG}' nicht gefunden – übersprungen.")
else:
    with open(GRUB_CFG, 'r', encoding='utf-8') as f:
        grub = f.read()

    # Timeout auf 0 setzen
    grub = re.sub(r'set timeout=\S+', 'set timeout=0', grub)

    # default auf den "Automated install"-Eintrag setzen
    # Im Debian 13 netinst ISO ist "Automated install" menuentry Nummer 4 (0-basiert)
    grub = re.sub(r'set default=\S+', 'set default=4', grub)

    # locale und keymap an die Kernel-Zeile des "Automated install"-Eintrags anhängen
    # Die Zeile beginnt mit "linux" und enthält "auto=true"
    grub = re.sub(
        r'([ \t]+linux[ \t]+/install\.amd/vmlinuz.*auto=true.*?)(\n)',
        r'\1 locale=de_AT.UTF-8 keymap=at\2',
        grub
    )

    with open(GRUB_CFG, 'w', encoding='utf-8') as f:
        f.write(grub)
    print("    -> grub.cfg gepatcht.")


# -----------------------------------------------------------------------
# 3. isolinux.cfg patchen (BIOS)
# -----------------------------------------------------------------------
print("[3/3] Patche isolinux.cfg...")

ISOLINUX_CFG = 'isolinux.cfg'
if not os.path.exists(ISOLINUX_CFG):
    print(f"    WARNUNG: '{ISOLINUX_CFG}' nicht gefunden – übersprungen.")
else:
    with open(ISOLINUX_CFG, 'r', encoding='utf-8') as f:
        isolinux = f.read()

    isolinux = re.sub(r'^timeout\s+\S+', 'timeout 0', isolinux, flags=re.MULTILINE)
    isolinux = re.sub(r'^default\s+\S+', 'default auto', isolinux, flags=re.MULTILINE)

    with open(ISOLINUX_CFG, 'w', encoding='utf-8') as f:
        f.write(isolinux)
    print("    -> isolinux.cfg gepatcht.")


print("Fertig!")
