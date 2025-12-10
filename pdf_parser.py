"""PDF-Parser: Extrahiert Stundenplan aus PDF"""
import pdfplumber
import re


def parse_timetable_pdf(pdf_path):
    """Liest Stundenplan-PDF und gibt Dictionary mit Lektionen pro Wochentag zurück"""
    timetable = {day: [] for day in ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]}
    seen = set()  # Track (day, fach, start) um echte Duplikate zu vermeiden
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            table = pdf.pages[0].extract_tables()[0]
            
            # Finde Wochentag-Spalten
            day_cols = {}
            for idx, cell in enumerate(table[0]):
                if cell:
                    for short, full in {"Mo": "Montag", "Di": "Dienstag", "Mi": "Mittwoch", 
                                       "Do": "Donnerstag", "Fr": "Freitag"}.items():
                        if short in cell:
                            day_cols[idx] = full
            
            # Parse jede Zeile
            for table_idx, row in enumerate(table[1:], 1):
                # Versuche Zeit aus Spalte 0 oder 1 zu extrahieren (für Zeilen-basierte Zeitangaben)
                row_time = None
                for col in [0, 1]:
                    if col < len(row) and row[col]:
                        time_match = re.search(r'(\d{2}):(\d{2})\s*[—\-–]\s*(\d{2}):(\d{2})', str(row[col]))
                        if time_match:
                            row_time = (f"{time_match.group(1)}:{time_match.group(2)}", 
                                       f"{time_match.group(3)}:{time_match.group(4)}")
                            break
                
                for col_idx, day in day_cols.items():
                    if col_idx < len(row) and row[col_idx]:
                        cell = str(row[col_idx]).strip()
                        
                        # Ignoriere Zellen die nur Zeit oder Müll sind
                        if not cell or re.match(r'^\d{2}:\d{2}', cell) or len(cell) < 2:
                            continue
                        
                        subject = None
                        # Variante 1: Fach mit " - " Pattern (z.B. "114 - U161D ReuD")
                        if match := re.search(r'^([A-ZÄÖÜa-zäöü&\d\s]+?)\s*[\(\!]*\s*[-–]', cell):
                            subject = match.group(1).strip()
                        # Variante 2: Kurzes Fach mit 1-4 Buchstaben + optional Punkt/Zahl/... (z.B. "En", "S-a", "En...", "M")
                        elif re.match(r'^[A-ZÄÖÜa-zäöü&]{1,4}[\d\-\.]*\.?\s*$', cell.split('\n')[0]):
                            subject = cell.split('\n')[0].strip().rstrip('.')  # Entferne trailing dots
                        
                        if subject:
                            # Zeit: zuerst in Zelle, dann row_time, dann nächste Zeilen durchsuchen
                            time_match = re.search(r'(\d{2}):(\d{2})\s*[-–]\s*(\d{2}):(\d{2})', cell)
                            start, ende = None, None
                            
                            if time_match:
                                start = f"{time_match.group(1)}:{time_match.group(2)}"
                                ende = f"{time_match.group(3)}:{time_match.group(4)}"
                            elif row_time:
                                start, ende = row_time
                            else:
                                # Suche in den nächsten 5 Zeilen nach Zeit
                                for offset in range(1, 6):
                                    next_idx = table_idx + offset
                                    if next_idx < len(table):
                                        next_cell = table[next_idx][col_idx] if col_idx < len(table[next_idx]) else None
                                        if next_cell:
                                            time_match = re.search(r'(\d{2}):(\d{2})\s*[-–]\s*(\d{2}):(\d{2})', str(next_cell))
                                            if time_match:
                                                start = f"{time_match.group(1)}:{time_match.group(2)}"
                                                ende = f"{time_match.group(3)}:{time_match.group(4)}"
                                                break
                            
                            if start and ende:
                                key = (day, subject, start)
                                
                                # Nur echte Duplikate vermeiden
                                if key not in seen:
                                    timetable[day].append({
                                        "fach": subject,
                                        "start": start,
                                        "ende": ende,
                                        "ressourcen": {"webseiten": [], "anwendungen": []}
                                    })
                                    seen.add(key)
        
        return timetable
    except Exception as e:
        print(f"[FEHLER] {e}")
        return None
