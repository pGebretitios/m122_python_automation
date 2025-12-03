# 📚 Stundenplan-Automatisierung für die Schule

Ein Python-Programm zur Automatisierung des Schulalltags. Es öffnet automatisch alle benötigten Anwendungen und Webseiten zu Beginn jeder Unterrichtsstunde.

## 🎯 Funktionen

- **Stundenplan-Export**: Interaktive Eingabe deines Stundenplans mit Fächern, Zeiten und Ressourcen
- **Automatischer Modus**: Läuft im Hintergrund und startet Ressourcen automatisch zur richtigen Zeit
- **Manueller Modus**: Manuelles Öffnen von Ressourcen für einzelne Fächer
- **JSON-basiert**: Stundenplan wird als JSON gespeichert und kann einfach bearbeitet werden

## 📋 Voraussetzungen

- Python 3.7 oder höher
- Windows-Betriebssystem (für automatisches Öffnen von Anwendungen)

## 🚀 Verwendung

### 1. Stundenplan erstellen

Führe zuerst `export.py` aus, um deinen Stundenplan zu erstellen:

```powershell
python export.py
```

Das Programm fragt dich interaktiv nach:
- **Fächern** für jeden Wochentag
- **Zeiten** (Start und Ende jeder Unterrichtsstunde)
- **Webseiten** (URLs, die geöffnet werden sollen)
- **Anwendungen** (Programme wie OneNote, Word, etc.)

Die Daten werden in `stundenplan.json` gespeichert.

#### Beispiel-Eingabe:
```
Fachname: Mathematik
Startzeit: 08:00
Endzeit: 09:45
URL: https://www.geogebra.org
Anwendung: onenote
Anwendung: calculator
```

### 2. Automatisierung starten

Starte das Hauptprogramm:

```powershell
python main.py
```

Wähle einen Modus:
- **Modus 1** (Automatisch): Läuft im Hintergrund und öffnet Ressourcen automatisch
- **Modus 2** (Manuell): Öffne Ressourcen für einzelne Fächer manuell
- **Modus 3** (Anzeige): Zeige nur den heutigen Stundenplan

## 📁 JSON-Struktur

Die `stundenplan.json` hat folgende Struktur:

```json
{
  "erstellt_am": "2025-12-03 14:30:00",
  "version": "1.0",
  "stundenplan": {
    "Montag": [
      {
        "fach": "Mathematik",
        "start": "08:00",
        "ende": "09:45",
        "ressourcen": {
          "webseiten": [
            "https://www.geogebra.org"
          ],
          "anwendungen": [
            "onenote",
            "calculator"
          ]
        }
      }
    ],
    "Dienstag": [ ... ],
    ...
  }
}
```

## 🔧 Unterstützte Anwendungen

Das Programm unterstützt folgende Anwendungen automatisch:
- `onenote` - Microsoft OneNote
- `word` - Microsoft Word
- `excel` - Microsoft Excel
- `powerpoint` - Microsoft PowerPoint
- `outlook` - Microsoft Outlook
- `teams` - Microsoft Teams
- `chrome` - Google Chrome
- `firefox` - Mozilla Firefox
- `edge` - Microsoft Edge
- `code` - Visual Studio Code
- `notepad` - Notepad
- `calculator` - Windows Taschenrechner

Weitere Anwendungen können durch ihren Befehlsnamen hinzugefügt werden.

## 💡 Tipps

- Nutze den **Beispiel-Stundenplan** in `export.py` (Option 2) zum Testen
- Der **automatische Modus** prüft alle 30 Sekunden die Uhrzeit
- Ressourcen werden nur **einmal pro Unterrichtsstunde** geöffnet
- Beende den automatischen Modus mit `Ctrl+C`

## 📝 Beispiel-Workflow

1. Stundenplan einmalig erstellen: `python export.py`
2. Programm beim Systemstart automatisch ausführen
3. Alle Ressourcen werden zur richtigen Zeit automatisch geöffnet
4. Konzentriere dich auf den Unterricht! 🎓

## 🛠️ Weiterentwicklung

Mögliche Erweiterungen:
- Unterstützung für Doppelstunden und Pausen
- Integration mit Kalender-Apps
- Benachrichtigungen vor Unterrichtsbeginn
- Autostart bei Windows-Anmeldung
- Mehrere Stundenpläne (A/B-Wochen)

---

Viel Erfolg mit der Automatisierung! 🚀
