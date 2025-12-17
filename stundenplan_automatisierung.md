# Protokoll_Stundenplan_Automatisierung.md

**Projekt:** Stundenplan-Automatisierung (Python)

**Name:** Pietros  
**Klasse:** —  
**Datum:** —

---

## Einleitung
Im Rahmen dieses Projekts wurde ein Python-Tool entwickelt, das Schul- oder Arbeitsstundenpläne automatisiert verarbeitet. Der Stundenplan wird aus einer PDF-Datei aus dem Intranet eingelesen, in ein maschinenlesbares JSON-Format überführt und anschliessend genutzt, um zum jeweiligen Unterrichtsbeginn automatisch die zugehörigen Web-Ressourcen zu öffnen.

Das Projekt wurde als Einzelarbeit umgesetzt und lokal mit Python 3 getestet. Ziel war eine möglichst robuste Automatisierung mit klarer Benutzerführung und nachvollziehbarer Dokumentation.

---

## Zielsetzung
- Automatisches Einlesen eines Stundenplans aus einer PDF-Datei
- Zuordnung von Fächern zu Web-Ressourcen (z. B. Moodle, Teams, Webseiten)
- Zeitgesteuertes Öffnen der Ressourcen zum Stundenbeginn
- Manueller Zugriff auf Lektionen bei Bedarf
- Klare Trennung von Import-, Daten- und Ausführungslogik
- Nachvollziehbare und prüfbare Dokumentation

---

## Anforderungen
- Python 3.x muss installiert sein
- Stundenplan muss als **textbasiertes PDF** vorliegen
- Zeiten müssen im Format `HH:MM - HH:MM` vorhanden sein **oder** manuell gepflegt werden
- Internetzugang zum Öffnen der Web-Ressourcen
- Abgabe als Python-Projekt mit Begleitdokumentation (Markdown)

---

## Vorgehen
Das Problem wurde in klar definierte Teilschritte zerlegt:

1. **Beschaffung des Stundenplans** aus dem Intranet als PDF
2. **Parsing des PDFs** (Tage, Fächer, Zeiten)
3. **Interaktive Ergänzung** von URLs pro Fach
4. **Speicherung** aller Daten in `stundenplan.json`
5. **Automatisierte oder manuelle Nutzung** über `main.py`

### Entwicklungsprozess
- Erste Version: Nur manuelle Öffnung von Lektionen
- Erkenntnis: Wiederkehrender Tagesablauf → Auto-Modus ergänzt
- Erkenntnis: Unterschiedliche PDF-Layouts → flexible Zeiterkennung eingebaut
- Erkenntnis: Parsing kann fehlschlagen → manuelle JSON-Pflege dokumentiert

---

## Beschaffung des Stundenplans (Intranet)

1. Anmeldung im Intranet oder auf der Schulplattform (z. B. Moodle, Teams)
2. Navigation zu einem Bereich wie:
   - „Stundenplan"
   - „Dokumente / Downloads"
   - „Klasse / Organisation"
3. Download des Stundenplans **als PDF-Datei**
4. Kontrolle:
   - aktueller Zeitraum
   - Mo–Fr vorhanden
   - Zeitangaben sichtbar

**Nicht geeignet:** Screenshots, gescannte PDFs, Word-Dateien

---

## Umsetzung

### Projektstruktur
- `main.py` – Steuerung (Auto-Modus, Manuell, Anzeige)
- `export.py` – Import des PDFs und Erzeugung der JSON-Datei
- `pdf_parser.py` – Extraktion von Tagen, Fächern und Zeiten
- `stundenplan.json` – Zentrale Datendatei
- `stundenplaene/` – Ablage der PDF-Dateien

### Import des Stundenplans

```bash
python export.py
```

- PDF wird aus `stundenplaene/` gelesen
- Fächer und Zeiten werden automatisch erkannt
- Benutzer gibt URLs pro Fach ein
- Ergebnis wird in `stundenplan.json` gespeichert

### Nutzung der Automatisierung

```bash
python main.py
```

Modi:
- **Auto-Modus:** Öffnet Ressourcen automatisch zum Stundenbeginn
- **Manuell:** Benutzer wählt Lektion
- **Heute anzeigen:** Übersicht ohne Aktion

---

## Manuelle Pflege der Zeiten (Fallback)

Dieser Schritt ist nur notwendig, wenn:
- das PDF keine Zeiten enthält
- das Layout nicht korrekt geparst werden kann

Beispiel-Eintrag in `stundenplan.json`:

```json
{
  "day": "Mo",
  "subject": "MATH",
  "start": "08:00",
  "end": "09:00",
  "urls": ["https://moodle.schule.ch/math"]
}
```

**Regeln:**
- 24-Stunden-Format
- `start` < `end`
- Ohne korrekte Zeiten kein Auto-Modus

---

## Testprotokoll

**Testumgebung:**
- Lokales System
- Python 3.x
- Standard-Webbrowser

| TestNr | Szenario | Erwartung (SOLL) | Ergebnis (IST) | Status |
|------:|---------|------------------|---------------|--------|
| 1 | Gültiges PDF | JSON wird erstellt | JSON erstellt | OK |
| 2 | Auto-Modus | Webseiten öffnen sich | Öffnung korrekt | OK |
| 3 | Fehlende Zeiten | Hinweis auf manuelle Pflege | Hinweis angezeigt | OK |
| 4 | Manuelle Auswahl | Ressourcen öffnen | Öffnung korrekt | OK |

---

## Erkenntnisse
- Textbasierte PDFs sind entscheidend für zuverlässiges Parsing
- Klare Trennung von Import und Nutzung erhöht Wartbarkeit
- JSON als Zwischenschicht vereinfacht Debugging
- Dokumentation der Fallbacks ist zwingend notwendig

---

## Fazit
Das Projekt erfüllt die definierten Anforderungen vollständig. Die Automatisierung spart Zeit im Alltag, ist flexibel erweiterbar und durch die klare Struktur gut wartbar. Fehlerfälle sind dokumentiert und können manuell korrigiert werden.

---

## Hilfestellungen / Deklaration von KI
Die Entwicklung des Projekts erfolgte mit Unterstützung von KI (ChatGPT) zur Ideengenerierung, Fehlersuche und Textüberarbeitung. Die Implementierung, Strukturierung und finale Bewertung wurden eigenständig durchgeführt.

