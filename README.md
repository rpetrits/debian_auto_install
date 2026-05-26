---

# Vollautomatische Debian 13 Installation via USB-Stick (macOS-Workflow)

Diese Anleitung beschreibt den fehlerfreien Workflow, um auf einem macOS-Gerät ein modifiziertes Debian-ISO zu erstellen und damit einen Dell-Laptop vollautomatisch via Preseed aufzusetzen. Dieser Weg umgeht alle macOS-Mount-Probleme und korrigiert die Benutzernamen-Blockade des Installers.

---

## 🛠️ Teil 1: Vorbereitung auf dem Mac

### 1. Ordnerstruktur und Dateien bereitlegen

Stelle sicher, dass sich auf deinem Schreibtisch der Ordner `usb_preseed` befindet und folgende Dateien darin liegen:

* `debian-13.5.0-amd64-netinst.iso` (Das offizielle Debian netinst Image)
* `initrd.gz` (Die originale Boot-Datei aus dem Debian-Archiv)
* `preseed.cfg` (Deine Konfigurationsdatei)
* `inject.py` (Dein gespeichertes Python-Skript zur nativen Dateiinjektion)

### 2. Benötigte Werkzeuge installieren

Öffne das Terminal auf dem Mac und installiere das ISO-Tool `xorriso` via Homebrew:

```bash
brew install xorriso

```

### 3. Die neue Boot-Datei (initrd_master.gz) generieren

Wechsle im Terminal in deinen Arbeitsordner und führe dein Python-Skript aus, um die `preseed.cfg` fehlerfrei und nativ in den RAM-Kern des Installers zu schreiben:

```bash
cd ~/Desktop/usb_preseed
python3 inject.py

```

*Nach erfolgreichem Durchlauf liegt die Datei `initrd_master.gz` im Ordner bereit.*

### 4. Das modifizierte ISO-Image bauen

Lösche eventuelle alte ISO-Fragmente und erstelle das finale, bootfähige Image mit `xorriso`:

```bash
xorriso \
  -indev debian-13.5.0-amd64-netinst.iso \
  -outdev debian-preseed.iso \
  -overwrite on \
  -boot_image any replay \
  -map initrd_master.gz /install.amd/initrd.gz

```

### 5. Auf USB-Stick flashen

1. Öffne den **Raspberry Pi Imager** auf deinem Mac.
2. Klicke auf **OS wählen** -> ganz unten auf **"Eigenes verwenden"** (Custom) und wähle die neu erstellte `debian-preseed.iso` aus.
3. Klicke auf **SD-Karte wählen** und wähle deinen USB-Stick aus.
4. Klicke auf **Schreiben** und bestätige mit deinem Mac-Passwort.
5. Nach Abschluss des Schreibvorgangs den Stick einfach abziehen (Fehlermeldungen von macOS bezüglich "nicht lesbar" einfach ignorieren).

---

## 🚀 Teil 2: Start am Dell-Laptop

1. Schließe das **LAN-Kabel** an den Dell-Laptop an.
2. Stecke den USB-Stick ein, starte den Laptop und drücke mehrfach **F12**, um ins Boot-Menü zu gelangen.
3. Wähle deinen USB-Stick aus.
4. Navigiere im blauen Debian-Menü auf **Advanced options** -> **Automated install**.
5. Drücke die Taste **`e`**, um in den Bearbeitungsmodus der Boot-Befehle zu gelangen.
6. Navigiere in **Zeile 2** (beginnt mit `linux /install.amd/vmlinuz...`) ganz ans Ende hinter das Wort `quiet`.
7. Füge ein Leerzeichen ein und hänge exakt folgenden Text an:
```text
file=/preseed.cfg

```


*Die gesamte Zeile 2 muss danach so aussehen:*
```text
linux /install.amd/vmlinuz auto=true priority=critical vga=788 --- quiet file=/preseed.cfg

```


8. Drücke **Strg + X** (oder **F10**), um den Bootvorgang mit diesen Parametern zu starten.

---

## 💾 Ergebnis & Login

Der Installer lädt die Konfiguration nun direkt aus dem RAM-Archiv, umgeht die USB-Mount-Ebene sowie die Namensblockade und setzt das System vollautomatisch auf. Nach dem automatischen Neustart lauten deine Zugangsdaten:

* **Benutzername:** `default`
* **Passwort:** `start123`
* **Root-Rechte:** Erhältst du im System wie gewohnt über den Befehl: `sudo <befehl>`
