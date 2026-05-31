#!/usr/bin/env python3

import gzip
import shutil
import os
import subprocess
import sys

# Prüfen ob preseed.cfg vorhanden ist
if not os.path.exists('preseed.cfg'):
    print("FEHLER: 'preseed.cfg' nicht gefunden!")
    sys.exit(1)

if not os.path.exists('initrd.gz'):
    print("FEHLER: 'initrd.gz' nicht gefunden!")
    sys.exit(1)

try:
    # 1. initrd.gz entpacken
    with gzip.open('initrd.gz', 'rb') as f_in:
        with open('initrd.cpio', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    # 2. preseed.cfg als neuen CPIO-Eintrag anhängen
    with open('initrd.cpio', 'ab') as f_out:
        subprocess.run(
            ['cpio', '-o', '-H', 'newc'],
            input=b'preseed.cfg\n',
            stdout=f_out,
            check=True
        )

    # 3. Wieder einpacken
    with open('initrd.cpio', 'rb') as f_in:
        with gzip.open('initrd_master.gz', 'wb', compresslevel=9) as f_out:
            shutil.copyfileobj(f_in, f_out)

    print("Erfolgreich! 'initrd_master.gz' wurde erstellt.")

except Exception as e:
    print(f"FEHLER: {e}")
    sys.exit(1)

finally:
    # Aufräumen – auch im Fehlerfall
    if os.path.exists('initrd.cpio'):
        os.remove('initrd.cpio')
