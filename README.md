# Vollautomatische Debian 13 Installation via USB-Stick (macOS-Workflow)

Diese Anleitung beschreibt den Workflow, um auf einem macOS-Gerät ein modifiziertes Debian-ISO zu erstellen und damit einen Dell-Laptop vollautomatisch via Preseed aufzusetzen. Das `build`-Skript übernimmt dabei alle Schritte automatisch: ISO-Download, Extraktion, Preseed-Injektion und ISO-Bau.

Da die `preseed.cfg` direkt in die `initrd` des Installers gepatcht wird, findet der Installer sie beim Booten automatisch — es ist kein manuelles Eingreifen in die Boot-Parameter notwendig.

---

## 🛠️ Teil 1: Vorbereitung auf dem Mac

### 1. Repository klonen

```bash
git clone https://github.com/rpetrits/debian_auto_install.git
cd debian_auto_install
```

Das Repository enthält bereits alle notwendigen Dateien:

* `build` – Hauptskript, das den gesamten Prozess automatisch durchführt
* `preseed.cfg` – Konfigurationsdatei für die automatische Installation
* `inject.py` – Python-Skript zur Injektion der `preseed.cfg` in die `initrd`

### 2. Benötigte Werkzeuge installieren

Öffne das Terminal auf dem Mac und installiere die benötigten Tools via Homebrew:

```bash
brew install xorriso python3
```

---

## 🚀 Teil 2: Preseed-ISO erstellen

### 1. Build-Skript ausführbar machen und starten

```bash
chmod +x build
./build
```

Das Skript führt automatisch folgende Schritte durch:

1. **Download** – Lädt das offizielle Debian netinst ISO herunter (sofern noch nicht vorhanden)
2. **Extraktion** – Extrahiert die originale `initrd.gz` aus dem ISO
3. **Injektion** – Fügt die `preseed.cfg` via `inject.py` in die `initrd` ein
4. **ISO-Bau** – Erstellt das fertige, bootfähige `debian-preseed.iso`

Nach erfolgreichem Durchlauf liegt die Datei `debian-preseed.iso` im aktuellen Verzeichnis bereit.

### 2. Auf USB-Stick flashen

1. Öffne den **Raspberry Pi Imager** auf deinem Mac.
2. Klicke auf **OS wählen** → ganz unten auf **„Eigenes verwenden"** (Custom) und wähle die neu erstellte `debian-preseed.iso` aus.
3. Klicke auf **SD-Karte wählen** und wähle deinen USB-Stick aus.
4. Klicke auf **Schreiben** und bestätige mit deinem Mac-Passwort.
5. Nach Abschluss des Schreibvorgangs den Stick einfach abziehen (Fehlermeldungen von macOS bezüglich „nicht lesbar" einfach ignorieren).

---

## 💻 Teil 3: Start am Dell-Laptop

1. Schließe das **LAN-Kabel** an den Dell-Laptop an (wird für den Paket-Download benötigt).
2. Stecke den USB-Stick ein, starte den Laptop und drücke mehrfach **F12**, um ins Boot-Menü zu gelangen.
3. Wähle deinen USB-Stick aus.
4. Navigiere im blauen Debian-Menü auf **Advanced options** → **Automated install**.

Die Installation läuft ab diesem Punkt vollautomatisch durch. Es sind keine weiteren Eingaben notwendig.

---

## 💾 Ergebnis & Login

Nach dem automatischen Neustart lauten die Zugangsdaten:

* **Benutzername:** `default`
* **Passwort:** `start123`
* **Root-Rechte:** über `sudo <befehl>`
