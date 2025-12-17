# 📚 Stundenplan-Automatisierung für die Schule

Ein Python-Programm zur Automatisierung des Schulalltags. Es öffnet automatisch alle benötigten Webseiten zu Beginn jeder Unterrichtsstunde.

## 🎯 Funktionen

- **PDF-Import**: Importiere deinen Stundenplan direkt aus einem PDF
- **Automatischer Modus**: Läuft im Hintergrund und öffnet Webseiten automatisch zur richtigen Zeit
- **Manueller Modus**: Manuelles Öffnen von Webseiten für einzelne Fächer
- **JSON-basiert**: Stundenplan wird als JSON gespeichert und kann einfach bearbeitet werden

## 📋 Voraussetzungen

- Python 3.8 oder höher
- Windows 11
- Webbrowser (Chrome, Firefox, Edge, etc.)

## 📦 Installation

### 1. Repository klonen oder herunterladen

```powershell
git clone https://github.com/pGebretitios/m122_python_automation.git
cd m122_python_automation
```

### 2. Virtuelle Umgebung erstellen (empfohlen)

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Abhängigkeiten installieren

```powershell
pip install pdfplumber
```

## 🚀 Gebrauch

### Schritt-für-Schritt Anleitung

#### 1. PowerShell öffnen

Drücke `Windows-Taste + X` und wähle "Windows PowerShell" oder "Terminal".

#### 2. Zum Projektordner navigieren

```powershell
cd C:\workdir\m122_python_automation
```

(Passe den Pfad an, wo du das Projekt gespeichert hast)

#### 3. Virtuelle Umgebung aktivieren

```powershell
.venv\Scripts\activate
```

**Wichtig:** Du siehst jetzt `(.venv)` vor deinem Prompt. Das bedeutet, die virtuelle Umgebung ist aktiv!

Beispiel:
```
PS C:\workdir\m122_python_automation> .venv\Scripts\activate
(.venv) PS C:\workdir\m122_python_automation>
```

#### 4. Stundenplan aus PDF importieren

Lege dein Stundenplan-PDF in den Ordner `stundenplaene/` und führe aus:

```powershell
python export.py
```

Das Programm zeigt alle verfügbaren PDFs an. Wähle dein PDF aus und es wird automatisch geparst. 
Nach dem Import kannst du für jedes Fach Webseiten hinzufügen.

Die Daten werden in `stundenplan.json` gespeichert.

#### 5. Automatisierung starten

Starte das Hauptprogramm:

```powershell
python main.py
```

Wähle einen Modus:
- **Modus 1** (Automatisch): Läuft im Hintergrund und öffnet Webseiten automatisch zur richtigen Zeit
- **Modus 2** (Manuell): Öffne Webseiten für einzelne Fächer manuell
- **Modus 3** (Anzeige): Zeige nur den heutigen Stundenplan

#### 6. Virtuelle Umgebung deaktivieren

Wenn du fertig bist:

```powershell
deactivate
```

Das `(.venv)` verschwindet wieder von deinem Prompt.

## 📁 JSON-Struktur

Die `stundenplan.json` hat folgende Struktur:

```json
{
  "erstellt_am": "2025-12-17 14:30:00",
  "stundenplan": {
    "Montag": [
      {
        "fach": "Mathematik",
        "start": "08:00",
        "ende": "09:45",
        "ressourcen": {
          "webseiten": [
            "https://www.geogebra.org"
          ]
        }
      }
    ],
    "Dienstag": [ ... ],
    ...
  }
}
```

## 💡 Tipps

- Der **automatische Modus** prüft alle 30 Sekunden die Uhrzeit
- Webseiten werden nur **einmal pro Unterrichtsstunde** geöffnet
- Bearbeite `stundenplan.json` direkt mit einem Texteditor wenn du Änderungen vornehmen willst
- Beende den automatischen Modus mit `Ctrl+C`

## 📝 Beispiel-Workflow

1. Stundenplan-PDF in `stundenplaene/` Ordner legen
2. Virtuelle Umgebung aktivieren: `.venv\Scripts\activate`
3. `python export.py` ausführen und PDF importieren
4. Webseiten für jedes Fach hinzufügen
5. `python main.py` starten und Modus 1 (Automatisch) wählen
6. Alle Webseiten werden automatisch zur richtigen Zeit geöffnet
7. Konzentriere dich auf den Unterricht! 🎓
--- 

