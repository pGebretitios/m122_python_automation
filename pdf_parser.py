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
                for col_idx, day in day_cols.items():
                    if col_idx < len(row) and row[col_idx]:
                        cell = str(row[col_idx]).strip()
                        
                        # Fach mit " - " Pattern
                        if match := re.search(r'^([A-ZÄÖÜa-zäöü&\d\s]+?)\s*[\(\!]*\s*[-–]', cell):
                            subject = match.group(1).strip()
                            
                            # Zeit: in Zelle oder nächste Zeilen durchsuchen
                            time_match = re.search(r'(\d{2}):(\d{2})\s*[-–]\s*(\d{2}):(\d{2})', cell)
                            if not time_match:
                                # Suche in den nächsten 3 Zeilen nach Zeit
                                for offset in range(1, 4):
                                    next_idx = table_idx + offset
                                    if next_idx < len(table):
                                        next_cell = table[next_idx][col_idx] if col_idx < len(table[next_idx]) else None
                                        if next_cell:
                                            time_match = re.match(r'^\s*(\d{2}):(\d{2})\s*[-–]\s*(\d{2}):(\d{2})\s*$', str(next_cell))
                                            if time_match:
                                                break
                            
                            if time_match:
                                start = f"{time_match.group(1)}:{time_match.group(2)}"
                                ende = f"{time_match.group(3)}:{time_match.group(4)}"
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
