"""Stundenplan-Automatisierung: Öffnet Webseiten/Apps zur richtigen Zeit"""
import json
import time
import subprocess
import webbrowser
from datetime import datetime


def load_timetable(filename="stundenplan.json"):
    """Lädt Stundenplan aus JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)['stundenplan']
    except:
        print(f"[FEHLER] {filename} nicht gefunden!")
        return None


def open_resources(lesson):
    """Öffnet Webseiten und Apps für eine Lektion"""
    print(f"\n{'='*50}\n{lesson['fach']} ({lesson['start']}-{lesson['ende']})\n{'='*50}")
    
    # Webseiten
    for url in lesson['ressourcen']['webseiten']:
        webbrowser.open(url)
        print(f"[OK] {url}")
        time.sleep(0.5)
    
    # Apps
    apps = {"onenote": "onenote", "word": "winword", "excel": "excel", "powerpoint": "powerpnt",
            "outlook": "outlook", "teams": "teams", "chrome": "chrome", "firefox": "firefox",
            "edge": "msedge", "code": "code", "notepad": "notepad", "calculator": "calc"}
    
    for app in lesson['ressourcen']['anwendungen']:
        subprocess.Popen(apps.get(app.lower(), app), shell=True)
        print(f"[OK] {app}")
        time.sleep(0.3)


def auto_mode(timetable):
    """Automatischer Modus: Überwacht Zeit und öffnet Ressourcen"""
    print("\n=== AUTOMATISCHER MODUS ===")
    print("Überwache Uhrzeit... (Ctrl+C zum Beenden)\n")
    
    opened = set()
    last_min = None
    
    try:
        while True:
            now = datetime.now()
            day = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"][now.weekday()]
            current_min = now.strftime("%H:%M")
            
            if current_min != last_min and day in timetable:
                last_min = current_min
                
                for lesson in timetable[day]:
                    if lesson['start'] == current_min:
                        key = f"{day}_{current_min}"
                        if key not in opened:
                            open_resources(lesson)
                            opened.add(key)
            
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n\n[OK] Beendet.")


def manual_mode(timetable):
    """Manueller Modus: Zeigt Stundenplan und ermöglicht manuelles Öffnen"""
    day = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"][datetime.now().weekday()]
    
    if day not in timetable or not timetable[day]:
        print("\nKeine Lektionen heute.")
        return
    
    print(f"\n=== {day} ===\n")
    for i, lesson in enumerate(timetable[day], 1):
        print(f"{i}. {lesson['start']}-{lesson['ende']}: {lesson['fach']}")
    
    choice = input("\nWelche Lektion öffnen? ").strip()
    if choice.isdigit() and 0 < int(choice) <= len(timetable[day]):
        open_resources(timetable[day][int(choice)-1])


def main():
    print("\n=== STUNDENPLAN-AUTOMATISIERUNG ===\n")
    
    timetable = load_timetable()
    if not timetable:
        return
    
    print("1 - Automatisch\n2 - Manuell\n3 - Heute anzeigen")
    choice = input("\nWahl: ").strip()
    
    if choice == "1":
        auto_mode(timetable)
    elif choice == "2":
        manual_mode(timetable)
    elif choice == "3":
        day = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"][datetime.now().weekday()]
        print(f"\n=== {day} ===")
        for lesson in timetable.get(day, []):
            print(f"{lesson['start']}-{lesson['ende']}: {lesson['fach']}")


if __name__ == "__main__":
    main()
