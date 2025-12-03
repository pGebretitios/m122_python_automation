"""
Stundenplan-Exporter für Schulautomatisierung
Dieses Programm ermöglicht die Eingabe eines Stundenplans und speichert ihn als JSON.
"""

import json
import os
from datetime import datetime, time
from pdf_parser import parse_timetable_pdf

def get_timetable_input():
    """
    Interaktive Eingabe des Stundenplans für die Woche
    """
    print("=" * 60)
    print("STUNDENPLAN-EXPORTER")
    print("=" * 60)
    print("\nBitte gib deinen Stundenplan ein.")
    print("Für jeden Wochentag kannst du mehrere Fächer mit Zeitangaben eintragen.\n")
    
    weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
    timetable = {}
    
    for day in weekdays:
        print(f"\n{'=' * 60}")
        print(f"{day.upper()}")
        print('=' * 60)
        
        timetable[day] = []
        
        while True:
            print(f"\nFach hinzufügen für {day} (oder Enter für nächsten Tag):")
            subject = input("  Fachname (z.B. 'Mathematik', 'Deutsch'): ").strip()
            
            if not subject:
                break
            
            # Zeitangaben
            start_time = input("  Startzeit (HH:MM, z.B. 08:00): ").strip()
            end_time = input("  Endzeit (HH:MM, z.B. 09:45): ").strip()
            
            # Validierung der Zeitangaben
            try:
                datetime.strptime(start_time, "%H:%M")
                datetime.strptime(end_time, "%H:%M")
            except ValueError:
                print("  ⚠️  Ungültiges Zeitformat! Bitte HH:MM verwenden (z.B. 08:00)")
                continue
            
            # Ressourcen für dieses Fach
            print(f"\n  Ressourcen für '{subject}':")
            resources = get_resources_for_subject(subject)
            
            lesson = {
                "fach": subject,
                "start": start_time,
                "ende": end_time,
                "ressourcen": resources
            }
            
            timetable[day].append(lesson)
            print(f"\n  ✓ {subject} ({start_time} - {end_time}) wurde hinzugefügt!")
    
    return timetable


def get_resources_for_subject(subject):
    """
    Abfrage der Ressourcen (Webseiten und Apps) für ein bestimmtes Fach
    """
    resources = {
        "webseiten": [],
        "anwendungen": []
    }
    
    print(f"  Webseiten für {subject}:")
    while True:
        url = input("    URL (oder Enter wenn fertig): ").strip()
        if not url:
            break
        resources["webseiten"].append(url)
        print(f"    [OK] {url} hinzugefügt")
    
    print(f"\n  Anwendungen für {subject}:")
    print("    (z.B. 'onenote', 'word', 'excel', 'code')")
    while True:
        app = input("    Anwendung (oder Enter wenn fertig): ").strip()
        if not app:
            break
        resources["anwendungen"].append(app)
        print(f"    [OK] {app} hinzugefügt")
    
    return resources


def save_timetable_json(timetable, filename="stundenplan.json"):
    """
    Speichert den Stundenplan als JSON-Datei
    """
    # Metadaten hinzufügen
    export_data = {
        "erstellt_am": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0",
        "stundenplan": timetable
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"[OK] Stundenplan wurde erfolgreich gespeichert: {filename}")
    print('=' * 60)


def load_example_timetable():
    """
    Erstellt einen Beispiel-Stundenplan für Testzwecke
    """
    example = {
        "Montag": [
            {
                "fach": "Mathematik",
                "start": "08:00",
                "ende": "09:45",
                "ressourcen": {
                    "webseiten": ["https://www.geogebra.org"],
                    "anwendungen": ["onenote", "calculator"]
                }
            },
            {
                "fach": "Deutsch",
                "start": "10:15",
                "ende": "12:00",
                "ressourcen": {
                    "webseiten": ["https://www.duden.de"],
                    "anwendungen": ["word", "onenote"]
                }
            }
        ],
        "Dienstag": [
            {
                "fach": "Informatik",
                "start": "08:00",
                "ende": "09:45",
                "ressourcen": {
                    "webseiten": ["https://github.com", "https://stackoverflow.com"],
                    "anwendungen": ["code", "chrome"]
                }
            }
        ],
        "Mittwoch": [],
        "Donnerstag": [
            {
                "fach": "Englisch",
                "start": "08:00",
                "ende": "09:45",
                "ressourcen": {
                    "webseiten": ["https://dict.leo.org"],
                    "anwendungen": ["onenote"]
                }
            }
        ],
        "Freitag": []
    }
    return example


def display_timetable_summary(timetable):
    """
    Zeigt eine Zusammenfassung des Stundenplans an
    """
    print("\n" + "=" * 60)
    print("STUNDENPLAN-ÜBERSICHT")
    print("=" * 60)
    
    for day, lessons in timetable.items():
        print(f"\n{day}:")
        if not lessons:
            print("  (keine Unterrichtsstunden)")
        else:
            for lesson in lessons:
                print(f"  {lesson['start']} - {lesson['ende']}: {lesson['fach']}")
                if lesson['ressourcen']['webseiten']:
                    print(f"    Webseiten: {', '.join(lesson['ressourcen']['webseiten'])}")
                if lesson['ressourcen']['anwendungen']:
                    print(f"    Apps: {', '.join(lesson['ressourcen']['anwendungen'])}")


def import_from_pdf():
    """
    Importiert Stundenplan aus einem PDF
    """
    print("\n" + "=" * 60)
    print("PDF-IMPORT")
    print("=" * 60)
    
    # Suche nach PDFs im stundenplaene-Ordner
    pdf_dir = "stundenplaene"
    
    if not os.path.exists(pdf_dir):
        print(f"[FEHLER] Ordner '{pdf_dir}' nicht gefunden!")
        return None
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"[FEHLER] Keine PDF-Dateien in '{pdf_dir}' gefunden!")
        return None
    
    print(f"\nGefundene PDF-Dateien:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf_file}")
    
    if len(pdf_files) == 1:
        choice = "1"
        print(f"\n=> Verwende automatisch: {pdf_files[0]}")
    else:
        choice = input(f"\nWelches PDF möchtest du importieren? (1-{len(pdf_files)}): ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(pdf_files):
            pdf_path = os.path.join(pdf_dir, pdf_files[idx])
            print(f"\nImportiere {pdf_files[idx]}...")
            
            timetable = parse_timetable_pdf(pdf_path)
            
            if timetable:
                total = sum(len(lessons) for lessons in timetable.values())
                print(f"\n[OK] {total} Lektionen erfolgreich importiert!")
                return timetable
            else:
                print("\n[FEHLER] PDF konnte nicht geparst werden.")
                return None
        else:
            print("[FEHLER] Ungültige Auswahl.")
            return None
    except ValueError:
        print("[FEHLER] Ungültige Eingabe.")
        return None


def add_resources_to_timetable(timetable):
    """
    Fügt zu jedem Fach im Stundenplan die Ressourcen hinzu
    """
    # Sammle alle einzigartigen Fächer
    unique_subjects = {}
    
    for day, lessons in timetable.items():
        for lesson in lessons:
            subject = lesson['fach']
            if subject not in unique_subjects:
                unique_subjects[subject] = {
                    "webseiten": [],
                    "anwendungen": []
                }
    
    if not unique_subjects:
        return timetable
    
    print(f"\nEs wurden {len(unique_subjects)} verschiedene Fächer gefunden.")
    print("Bitte gib für jedes Fach die Ressourcen an:\n")
    
    # Für jedes Fach Ressourcen abfragen
    for subject in unique_subjects.keys():
        print(f"\n--- {subject} ---")
        resources = get_resources_for_subject(subject)
        unique_subjects[subject] = resources
    
    # Ressourcen zu allen Lektionen hinzufügen
    for day, lessons in timetable.items():
        for lesson in lessons:
            subject = lesson['fach']
            if subject in unique_subjects:
                lesson['ressourcen'] = unique_subjects[subject].copy()
    
    return timetable


def main():
    """
    Hauptprogramm
    """
    print("\nWillkommen beim Stundenplan-Exporter!\n")
    
    # Automatischer PDF-Import
    timetable = import_from_pdf()
    
    if not timetable:
        print("\n[INFO] Kein PDF gefunden oder Import fehlgeschlagen.")
        print("\nWähle eine Option:")
        print("1 - Stundenplan manuell eingeben")
        print("2 - Beispiel-Stundenplan verwenden")
        
        choice = input("\nDeine Wahl (1 oder 2): ").strip()
        
        if choice == "2":
            print("\n[OK] Verwende Beispiel-Stundenplan...")
            timetable = load_example_timetable()
        else:
            timetable = get_timetable_input()
    
    # Ressourcen für jedes Fach abfragen
    print("\n" + "=" * 60)
    print("RESSOURCEN ZU FÄCHERN HINZUFÜGEN")
    print("=" * 60)
    print("Jetzt kannst du für jedes Fach Webseiten und Anwendungen festlegen.\n")
    
    timetable = add_resources_to_timetable(timetable)
    
    # Zusammenfassung anzeigen
    display_timetable_summary(timetable)
    
    # JSON speichern
    filename = input("\nDateiname für Export (Enter für 'stundenplan.json'): ").strip()
    if not filename:
        filename = "stundenplan.json"
    if not filename.endswith('.json'):
        filename += '.json'
    
    save_timetable_json(timetable, filename)
    
    print("\nDer Stundenplan kann jetzt von main.py geladen werden!")


if __name__ == "__main__":
    main()
