"""
Stundenplan-Automatisierung für die Schule
Dieses Programm läuft im Hintergrund und öffnet automatisch alle benötigten
Anwendungen und Webseiten zu Beginn jeder Unterrichtsstunde.
"""

import json
import time
import subprocess
import webbrowser
from datetime import datetime
import os


def load_timetable(filename="stundenplan.json"):
    """
    Lädt den Stundenplan aus der JSON-Datei
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Stundenplan geladen: {filename}")
        print(f"  Erstellt am: {data.get('erstellt_am', 'Unbekannt')}")
        return data['stundenplan']
    except FileNotFoundError:
        print(f"❌ Fehler: {filename} nicht gefunden!")
        print("   Bitte führe zuerst export.py aus, um einen Stundenplan zu erstellen.")
        return None
    except json.JSONDecodeError:
        print(f"❌ Fehler: {filename} enthält ungültiges JSON!")
        return None


def get_current_lesson(timetable):
    """
    Ermittelt die aktuelle Unterrichtsstunde basierend auf Wochentag und Uhrzeit
    """
    now = datetime.now()
    current_day = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"][now.weekday()]
    current_time = now.strftime("%H:%M")
    
    # Prüfe, ob heute Unterricht stattfindet
    if current_day not in timetable:
        return None, None
    
    lessons_today = timetable[current_day]
    
    for lesson in lessons_today:
        if lesson['start'] == current_time:
            return current_day, lesson
    
    return current_day, None


def open_websites(urls):
    """
    Öffnet eine Liste von Webseiten im Standardbrowser
    """
    for url in urls:
        try:
            webbrowser.open(url)
            print(f"  ✓ Webseite geöffnet: {url}")
            time.sleep(0.5)  # Kurze Pause zwischen den Tabs
        except Exception as e:
            print(f"  ❌ Fehler beim Öffnen von {url}: {e}")


def open_applications(apps):
    """
    Öffnet eine Liste von Anwendungen
    """
    # Mapping für bekannte Anwendungen (Windows)
    app_commands = {
        "onenote": "onenote",
        "word": "winword",
        "excel": "excel",
        "powerpoint": "powerpnt",
        "outlook": "outlook",
        "teams": "teams",
        "chrome": "chrome",
        "firefox": "firefox",
        "edge": "msedge",
        "code": "code",
        "notepad": "notepad",
        "calculator": "calc"
    }
    
    for app in apps:
        app_lower = app.lower()
        command = app_commands.get(app_lower, app)
        
        try:
            subprocess.Popen(command, shell=True)
            print(f"  ✓ Anwendung gestartet: {app}")
            time.sleep(0.3)  # Kurze Pause zwischen den Programmen
        except Exception as e:
            print(f"  ❌ Fehler beim Starten von {app}: {e}")


def start_lesson_resources(lesson):
    """
    Startet alle Ressourcen für eine Unterrichtsstunde
    """
    print(f"\n{'=' * 60}")
    print(f"📚 {lesson['fach']} beginnt jetzt!")
    print(f"⏰ {lesson['start']} - {lesson['ende']}")
    print('=' * 60)
    
    resources = lesson['ressourcen']
    
    # Webseiten öffnen
    if resources['webseiten']:
        print("\n🌐 Öffne Webseiten...")
        open_websites(resources['webseiten'])
    
    # Anwendungen starten
    if resources['anwendungen']:
        print("\n💻 Starte Anwendungen...")
        open_applications(resources['anwendungen'])
    
    print(f"\n✓ Alle Ressourcen für {lesson['fach']} wurden geöffnet!\n")


def display_today_schedule(timetable):
    """
    Zeigt den Stundenplan für heute an
    """
    now = datetime.now()
    current_day = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"][now.weekday()]
    
    print(f"\n{'=' * 60}")
    print(f"📅 Stundenplan für {current_day}, {now.strftime('%d.%m.%Y')}")
    print('=' * 60)
    
    if current_day not in timetable or not timetable[current_day]:
        print("(keine Unterrichtsstunden heute)")
        return
    
    for lesson in timetable[current_day]:
        print(f"\n{lesson['start']} - {lesson['ende']}: {lesson['fach']}")
        if lesson['ressourcen']['webseiten']:
            print(f"  Webseiten: {len(lesson['ressourcen']['webseiten'])}")
        if lesson['ressourcen']['anwendungen']:
            print(f"  Anwendungen: {len(lesson['ressourcen']['anwendungen'])}")


def monitor_mode(timetable):
    """
    Überwachungsmodus: Läuft im Hintergrund und startet Ressourcen automatisch
    """
    print("\n" + "=" * 60)
    print("🔄 AUTOMATISCHER MODUS GESTARTET")
    print("=" * 60)
    print("Das Programm überwacht jetzt kontinuierlich die Uhrzeit...")
    print("Drücke Ctrl+C zum Beenden.\n")
    
    last_checked_minute = None
    opened_lessons = set()  # Speichert bereits geöffnete Lektionen (Tag_StartZeit)
    
    try:
        while True:
            now = datetime.now()
            current_minute = now.strftime("%H:%M")
            
            # Prüfe nur einmal pro Minute
            if current_minute != last_checked_minute:
                last_checked_minute = current_minute
                
                day, lesson = get_current_lesson(timetable)
                
                if lesson:
                    lesson_key = f"{day}_{lesson['start']}"
                    
                    # Öffne Ressourcen nur, wenn noch nicht geöffnet
                    if lesson_key not in opened_lessons:
                        start_lesson_resources(lesson)
                        opened_lessons.add(lesson_key)
                        
                        # Bereinige alte Einträge (älter als heute)
                        if len(opened_lessons) > 20:
                            opened_lessons.clear()
            
            time.sleep(30)  # Prüfe alle 30 Sekunden
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("⏹️  Automatischer Modus wurde beendet.")
        print("=" * 60)


def manual_mode(timetable):
    """
    Manueller Modus: Zeigt den Stundenplan und ermöglicht manuelles Öffnen
    """
    display_today_schedule(timetable)
    
    print("\n" + "=" * 60)
    print("MANUELLER MODUS")
    print("=" * 60)
    print("Du kannst jetzt manuell die Ressourcen für ein Fach öffnen.")
    
    now = datetime.now()
    current_day = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"][now.weekday()]
    
    if current_day not in timetable or not timetable[current_day]:
        print("\nKeine Unterrichtsstunden heute.")
        return
    
    lessons = timetable[current_day]
    
    print("\nVerfügbare Fächer heute:")
    for i, lesson in enumerate(lessons, 1):
        print(f"{i}. {lesson['fach']} ({lesson['start']} - {lesson['ende']})")
    
    choice = input("\nWelches Fach möchtest du öffnen? (Nummer oder Enter zum Beenden): ").strip()
    
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(lessons):
            start_lesson_resources(lessons[idx])
        else:
            print("Ungültige Auswahl.")


def main():
    """
    Hauptprogramm
    """
    print("\n" + "=" * 60)
    print("STUNDENPLAN-AUTOMATISIERUNG")
    print("=" * 60)
    
    # Stundenplan laden
    timetable = load_timetable()
    
    if not timetable:
        return
    
    print("\nWähle einen Modus:")
    print("1 - Automatischer Modus (läuft im Hintergrund)")
    print("2 - Manueller Modus (Ressourcen manuell öffnen)")
    print("3 - Heutigen Stundenplan anzeigen")
    
    choice = input("\nDeine Wahl (1, 2 oder 3): ").strip()
    
    if choice == "1":
        monitor_mode(timetable)
    elif choice == "2":
        manual_mode(timetable)
    elif choice == "3":
        display_today_schedule(timetable)
    else:
        print("Ungültige Auswahl.")


if __name__ == "__main__":
    main()
