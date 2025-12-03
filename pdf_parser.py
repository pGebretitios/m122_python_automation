"""
PDF-Parser für Stundenpläne
Extrahiert automatisch Fächer und Zeiten aus PDF-Stundenplänen
"""

import pdfplumber
import re
from datetime import datetime


def parse_timetable_pdf(pdf_path):
    """
    Analysiert ein Stundenplan-PDF und extrahiert die Unterrichtsstunden
    
    Args:
        pdf_path: Pfad zum PDF-Stundenplan
        
    Returns:
        Dictionary mit Stundenplan nach Wochentagen
    """
    timetable = {
        "Montag": [],
        "Dienstag": [],
        "Mittwoch": [],
        "Donnerstag": [],
        "Freitag": []
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            tables = page.extract_tables()
            
            if not tables:
                print("[FEHLER] Keine Tabellen im PDF gefunden!")
                return None
            
            table = tables[0]
            
            # Erste Zeile enthält die Wochentage
            header_row = table[0]
            print(f"Header: {header_row}")
            
            # Finde die Spaltenindizes für jeden Wochentag
            day_columns = {}
            weekday_mapping = {
                "Mo": "Montag",
                "Di": "Dienstag", 
                "Mi": "Mittwoch",
                "Do": "Donnerstag",
                "Fr": "Freitag"
            }
            
            for idx, cell in enumerate(header_row):
                if cell:
                    for short, full in weekday_mapping.items():
                        if short in cell:
                            day_columns[idx] = full
                            print(f"  Spalte {idx}: {full}")
                            break
            
            # Verarbeite die Tabelle zeilenweise
            # Sammle Fachname und die darauffolgende Zeitangabe
            for row_idx in range(1, len(table)):
                row = table[row_idx]
                
                # Durchsuche jede Wochentag-Spalte
                for col_idx, full_day in day_columns.items():
                    if col_idx < len(row):
                        cell = row[col_idx]
                        
                        if cell and str(cell).strip():
                            cell_text = str(cell).strip()
                            
                            # Prüfe ob es ein Fachname ist (enthält " - " Muster)
                            # Erweitert um mehrteilige Namen wie "Englisch A2 e"
                            if re.search(r'^([A-ZÄÖÜa-zäöü&\d\s]+?)\s*[\(\!]*\s*[-–]', cell_text):
                                # Extrahiere Fachname (inkl. Leerzeichen, z.B. "Englisch A2 e")
                                subject_match = re.match(r'^([A-ZÄÖÜa-zäöü&\d\s]+?)\s*[\(\!]*\s*[-–]', cell_text)
                                subject = subject_match.group(1).strip()
                                
                                start_time = None
                                end_time = None
                                
                                # Fall 1: Zeit ist in DERSELBEN Zelle (mehrzeilig)
                                time_in_cell = re.search(r'(\d{2}):(\d{2})\s*[-–]\s*(\d{2}):(\d{2})', cell_text)
                                if time_in_cell:
                                    start_time = f"{time_in_cell.group(1)}:{time_in_cell.group(2)}"
                                    end_time = f"{time_in_cell.group(3)}:{time_in_cell.group(4)}"
                                
                                # Fall 2: Zeit ist in NÄCHSTER Zeile
                                if not start_time and row_idx + 1 < len(table):
                                    next_row = table[row_idx + 1]
                                    if col_idx < len(next_row) and next_row[col_idx]:
                                        time_cell = str(next_row[col_idx]).strip()
                                        time_match = re.match(r'^(\d{2}):(\d{2})\s*[-–]\s*(\d{2}):(\d{2})$', time_cell)
                                        if time_match:
                                            start_time = f"{time_match.group(1)}:{time_match.group(2)}"
                                            end_time = f"{time_match.group(3)}:{time_match.group(4)}"
                                
                                # Fall 3: Verwende Zeitslot aus Spalte 1 (Fallback)
                                if not start_time:
                                    time_cell = row[1] if len(row) > 1 else None
                                    if time_cell and ":" in str(time_cell):
                                        time_match = re.search(r'(\d{2}):(\d{2})', str(time_cell))
                                        if time_match:
                                            start_time = time_match.group(1) + ":" + time_match.group(2)
                                            end_time = calculate_end_time(start_time, 90)
                                
                                # Erstelle Lektion wenn Zeit gefunden wurde
                                if start_time and end_time:
                                    lesson = {
                                        "fach": subject,
                                        "start": start_time,
                                        "ende": end_time,
                                        "ressourcen": {
                                            "webseiten": [],
                                            "anwendungen": []
                                        }
                                    }
                                    
                                    if not is_duplicate_lesson(timetable[full_day], lesson):
                                        timetable[full_day].append(lesson)
                                        print(f"  [OK] {full_day}: {subject} ({start_time} - {end_time})")
            
            return timetable
            
    except Exception as e:
        print(f"[FEHLER] Fehler beim Parsen des PDFs: {e}")
        return None


def parse_lesson_cell_multi(cell_text, default_start_time=None):
    """
    Extrahiert MEHRERE Fachinformationen aus einer Tabellenzelle
    (kann mehrere Fächer/Module enthalten)
    
    Args:
        cell_text: Text der Zelle
        default_start_time: Standard-Startzeit falls nicht in Zelle enthalten
        
    Returns:
        Liste von Dictionaries mit Fach, Start- und Endzeit
    """
    if not cell_text or str(cell_text).strip() == '':
        return []
    
    text = str(cell_text).strip()
    lessons = []
    
    # Teile Text in Zeilen (falls mehrere Fächer untereinander)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Suche alle Zeitangaben im Format HH:MM-HH:MM
    time_pattern = r'(\d{2}):(\d{2})\s*[-–]\s*(\d{2}):(\d{2})'
    all_times = re.findall(time_pattern, text)
    
    # Extrahiere alle Fachnamen (Buchstaben am Zeilenanfang oder nach " - ")
    # Muster: "M - ", "W&R - ", "122 - ", etc.
    subject_pattern = r'^([A-ZÄÖÜa-zäöü&\d]+)\s*[-–]'
    
    current_subject = None
    current_times = []
    
    for line in lines:
        # Überspringe reine Zeitangaben
        if re.match(r'^\d{2}:\d{2}\s*[-–]\s*\d{2}:\d{2}$', line):
            # Zeitangabe für aktuelles Fach
            time_match = re.search(time_pattern, line)
            if time_match and current_subject:
                start_time = f"{time_match.group(1)}:{time_match.group(2)}"
                end_time = f"{time_match.group(3)}:{time_match.group(4)}"
                current_times.append((start_time, end_time))
            continue
        
        # Suche nach Fachname
        subject_match = re.match(subject_pattern, line)
        
        if subject_match:
            # Neues Fach gefunden - speichere vorheriges wenn vorhanden
            if current_subject and current_times:
                for start_time, end_time in current_times:
                    lessons.append({
                        "fach": current_subject,
                        "start": start_time,
                        "ende": end_time,
                        "ressourcen": {
                            "webseiten": [],
                            "anwendungen": []
                        }
                    })
            
            # Neues Fach
            current_subject = subject_match.group(1).strip()
            current_times = []
            
            # Prüfe ob Zeit in derselben Zeile
            time_match = re.search(time_pattern, line)
            if time_match:
                start_time = f"{time_match.group(1)}:{time_match.group(2)}"
                end_time = f"{time_match.group(3)}:{time_match.group(4)}"
                current_times.append((start_time, end_time))
    
    # Letztes Fach hinzufügen
    if current_subject:
        if current_times:
            for start_time, end_time in current_times:
                lessons.append({
                    "fach": current_subject,
                    "start": start_time,
                    "ende": end_time,
                    "ressourcen": {
                        "webseiten": [],
                        "anwendungen": []
                    }
                })
        elif default_start_time:
            # Keine Zeit gefunden, verwende default
            lessons.append({
                "fach": current_subject,
                "start": default_start_time,
                "ende": calculate_end_time(default_start_time, 90),
                "ressourcen": {
                    "webseiten": [],
                    "anwendungen": []
                }
            })
    
    return lessons


def parse_lesson_cell(cell_text, default_start_time=None):
    """
    Extrahiert Fachinformationen aus einer Tabellenzelle
    
    Args:
        cell_text: Text der Zelle
        default_start_time: Standard-Startzeit falls nicht in Zelle enthalten
        
    Returns:
        Dictionary mit Fach, Start- und Endzeit oder None
    """
    if not cell_text or cell_text.strip() == '':
        return None
    
    # Bereinige den Text
    text = str(cell_text).strip()
    
    # Suche nach Zeitangaben im Format HH:MM-HH:MM oder HH:MM - HH:MM
    time_pattern = r'(\d{2}):(\d{2})\s*[-–]\s*(\d{2}):(\d{2})'
    time_match = re.search(time_pattern, text)
    
    if time_match:
        start_time = f"{time_match.group(1)}:{time_match.group(2)}"
        end_time = f"{time_match.group(3)}:{time_match.group(4)}"
        
        # Entferne Zeitangaben aus dem Text um Fachnamen zu extrahieren
        subject_text = re.sub(time_pattern, '', text).strip()
    else:
        # Keine explizite Zeit gefunden, verwende default
        if not default_start_time:
            return None
        start_time = default_start_time
        end_time = calculate_end_time(start_time, 90)  # Standard: 90 Minuten
        subject_text = text
    
    # Extrahiere Fachnamen (erster Teil vor " - " oder Zeilenumbruch)
    subject_match = re.match(r'^([A-ZÄÖÜa-zäöü&\s]+)', subject_text)
    if subject_match:
        subject = subject_match.group(1).strip()
    else:
        subject = subject_text.split('\n')[0].strip()
    
    # Filtere zu kurze oder ungültige Fachnamen
    if len(subject) < 2 or subject.isdigit():
        return None
    
    return {
        "fach": subject,
        "start": start_time,
        "ende": end_time,
        "ressourcen": {
            "webseiten": [],
            "anwendungen": []
        }
    }


def calculate_end_time(start_time, duration_minutes):
    """
    Berechnet die Endzeit basierend auf Startzeit und Dauer
    
    Args:
        start_time: Startzeit im Format "HH:MM"
        duration_minutes: Dauer in Minuten
        
    Returns:
        Endzeit im Format "HH:MM"
    """
    try:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.fromtimestamp(start.timestamp() + duration_minutes * 60)
        return end.strftime("%H:%M")
    except:
        return "12:00"  # Fallback


def is_duplicate_lesson(lessons, new_lesson):
    """
    Prüft ob eine Lektion bereits in der Liste existiert
    
    Args:
        lessons: Liste existierender Lektionen
        new_lesson: Neue Lektion zum Prüfen
        
    Returns:
        True wenn Duplikat, sonst False
    """
    for lesson in lessons:
        # Exaktes Duplikat: Gleiches Fach UND gleiche Startzeit
        if (lesson['fach'] == new_lesson['fach'] and 
            lesson['start'] == new_lesson['start']):
            return True
        
        # Zeitlicher Overlap: Gleiches Fach mit überlappenden Zeiten
        if lesson['fach'] == new_lesson['fach']:
            # Konvertiere zu Minuten seit Mitternacht für Vergleich
            def time_to_minutes(time_str):
                h, m = time_str.split(':')
                return int(h) * 60 + int(m)
            
            lesson_start = time_to_minutes(lesson['start'])
            lesson_end = time_to_minutes(lesson['ende'])
            new_start = time_to_minutes(new_lesson['start'])
            new_end = time_to_minutes(new_lesson['ende'])
            
            # Prüfe auf Überlappung
            if not (new_end <= lesson_start or new_start >= lesson_end):
                # Es gibt eine Überlappung - behalte die spezifischere Zeit
                # (kleinere Zeitspanne ist normalerweise korrekter)
                existing_duration = lesson_end - lesson_start
                new_duration = new_end - new_start
                
                if new_duration < existing_duration:
                    # Neue Lektion ist spezifischer - ersetze alte
                    lessons.remove(lesson)
                    return False
                else:
                    # Alte Lektion ist spezifischer oder gleich - überspringe neue
                    return True
    
    return False


def display_parsed_timetable(timetable):
    """
    Zeigt den geparsten Stundenplan übersichtlich an
    """
    print("\n" + "=" * 60)
    print("GEPARSTER STUNDENPLAN")
    print("=" * 60)
    
    for day, lessons in timetable.items():
        print(f"\n{day}:")
        if not lessons:
            print("  (keine Unterrichtsstunden)")
        else:
            for lesson in lessons:
                print(f"  {lesson['start']} - {lesson['ende']}: {lesson['fach']}")


if __name__ == "__main__":
    # Test mit dem vorhandenen PDF
    import os
    
    pdf_path = os.path.join("stundenplaene", "bzu-timetable-20251201.pdf")
    
    if os.path.exists(pdf_path):
        print(f"Analysiere {pdf_path}...\n")
        timetable = parse_timetable_pdf(pdf_path)
        
        if timetable:
            display_parsed_timetable(timetable)
    else:
        print(f"[FEHLER] PDF nicht gefunden: {pdf_path}")
