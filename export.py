"""Stundenplan-Exporter: Liest PDF und erstellt JSON mit Ressourcen"""
import json
import os
from datetime import datetime
from pdf_parser import parse_timetable_pdf


def get_resources():
    """Fragt Ressourcen für ein Fach ab"""
    res = {"webseiten": []}
    
    while url := input("  URL (Enter=fertig): ").strip():
        res["webseiten"].append(url)
    
    return res


def main():
    print("\n=== STUNDENPLAN-EXPORTER ===\n")
    
    # PDF importieren
    pdf_dir = "stundenplaene"
    pdfs = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')] if os.path.exists(pdf_dir) else []
    
    if not pdfs:
        print("[FEHLER] Keine PDFs gefunden!")
        return
    
    print(f"Importiere: {pdfs[0]}")
    timetable = parse_timetable_pdf(os.path.join(pdf_dir, pdfs[0]))
    
    if not timetable:
        return
    
    # Ressourcen hinzufügen
    print(f"\n=== RESSOURCEN HINZUFÜGEN ===\n")
    subjects = {}
    
    for lessons in timetable.values():
        for lesson in lessons:
            if lesson['fach'] not in subjects:
                print(f"\n{lesson['fach']}:")
                subjects[lesson['fach']] = get_resources()
    
    # Ressourcen zuordnen
    for lessons in timetable.values():
        for lesson in lessons:
            lesson['ressourcen'] = subjects[lesson['fach']]
    
    # Speichern
    filename = input("\nDateiname (Enter='stundenplan.json'): ").strip() or "stundenplan.json"
    if not filename.endswith('.json'):
        filename += '.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({"erstellt_am": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                   "version": "1.0", "stundenplan": timetable}, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] Gespeichert: {filename}")


if __name__ == "__main__":
    main()
