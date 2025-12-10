"""Stundenplan-GUI"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, webbrowser, threading, time
from datetime import datetime
import sys, os

class GUI:
    def __init__(self, root):
        root.title("Stundenplan")
        root.geometry("650x450")
        root.configure(bg='#2b2b2b')
        try:
            with open("stundenplan.json", encoding='utf-8') as f:
                self.tt = json.load(f)['stundenplan']
        except:
            messagebox.showerror("Fehler", "stundenplan.json fehlt!")
            return
        self.running = False
        self.opened = set()
        
        # Header
        tk.Label(root, text="📚 Stundenplan", font=('Segoe UI', 16, 'bold'), 
                bg='#2b2b2b', fg='white').pack(pady=15)
        
        # Tabs
        nb = ttk.Notebook(root)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#2b2b2b', borderwidth=0)
        style.configure('TNotebook.Tab', background='#3c3c3c', foreground='white', padding=[12,6])
        style.map('TNotebook.Tab', background=[('selected', '#1e1e1e')])
        
        # Heute
        t1 = tk.Frame(nb, bg='#2b2b2b')
        nb.add(t1, text="Heute")
        day = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"][datetime.now().weekday()]
        tk.Label(t1, text=day, font=('Segoe UI',12,'bold'), bg='#2b2b2b', fg='white').pack(pady=10)
        
        canvas = tk.Canvas(t1, bg='#2b2b2b', highlightthickness=0)
        scroll = ttk.Scrollbar(t1, command=canvas.yview)
        frame = tk.Frame(canvas, bg='#2b2b2b')
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scroll.pack(side="right", fill="y")
        
        for l in self.tt.get(day, []):
            c = tk.Frame(frame, bg='#3c3c3c', relief=tk.RAISED, bd=1)
            c.pack(fill=tk.X, pady=6)
            h = tk.Frame(c, bg='#1e1e1e')
            h.pack(fill=tk.X)
            tk.Label(h, text=l['fach'], font=('Segoe UI',11,'bold'), bg='#1e1e1e', fg='white').pack(side=tk.LEFT, padx=10, pady=6)
            tk.Label(h, text=f"{l['start']}-{l['ende']}", font=('Segoe UI',8), bg='#1e1e1e', fg='#aaa').pack(side=tk.LEFT)
            btn = tk.Button(c, text="Öffnen", command=lambda x=l: self.open(x), bg='#0e639c', fg='white', 
                          font=('Segoe UI',9,'bold'), relief=tk.FLAT, padx=12, pady=4, cursor='hand2')
            btn.pack(pady=6)
            btn.bind("<Enter>", lambda e,b=btn: b.config(bg='#1177bb'))
            btn.bind("<Leave>", lambda e,b=btn: b.config(bg='#0e639c'))
        
        # Auto
        t2 = tk.Frame(nb, bg='#2b2b2b')
        nb.add(t2, text="Auto")
        self.status = tk.Label(t2, text="⏸️ Stop", font=('Segoe UI',14,'bold'), bg='#2b2b2b', fg='#ff6b6b')
        self.status.pack(pady=20)
        self.clock = tk.Label(t2, text="", font=('Segoe UI',20), bg='#2b2b2b', fg='white')
        self.clock.pack(pady=8)
        self.tick()
        self.btn = tk.Button(t2, text="▶️ Start", command=self.toggle, bg='#51cf66', fg='white',
                            font=('Segoe UI',11,'bold'), relief=tk.FLAT, padx=25, pady=10, cursor='hand2')
        self.btn.pack(pady=15)
        
        self.log = tk.Text(t2, height=7, bg='#1e1e1e', fg='white', font=('Consolas',8), relief=tk.FLAT, padx=6, pady=6)
        self.log.pack(fill=tk.BOTH, expand=True, padx=15, pady=(10,15))
        self.log_msg("GUI gestartet")
        
        # Bearbeiten
        t3 = tk.Frame(nb, bg='#2b2b2b')
        nb.add(t3, text="Bearbeiten")
        tk.Label(t3, text="Tag wählen:", font=('Segoe UI',10,'bold'), bg='#2b2b2b', fg='white').pack(pady=(15,5))
        self.day_var = tk.StringVar(value="Montag")
        days = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag"]
        day_menu = ttk.Combobox(t3, textvariable=self.day_var, values=days, state='readonly', width=15)
        day_menu.pack(pady=5)
        day_menu.bind("<<ComboboxSelected>>", lambda e: self.load_day())
        
        self.edit_frame = tk.Frame(t3, bg='#2b2b2b')
        self.edit_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.load_day()
        
        # Import
        t4 = tk.Frame(nb, bg='#2b2b2b')
        nb.add(t4, text="Import")
        tk.Label(t4, text="📄 PDF-Import", font=('Segoe UI',14,'bold'), bg='#2b2b2b', fg='white').pack(pady=30)
        tk.Label(t4, text="Wähle deine Stundenplan-PDF aus und\ndie Fächer werden automatisch eingelesen.", 
                font=('Segoe UI',10), bg='#2b2b2b', fg='#aaa', justify=tk.CENTER).pack(pady=10)
        
        tk.Button(t4, text="📁 PDF auswählen", command=self.import_pdf, bg='#0e639c', fg='white',
                 font=('Segoe UI',11,'bold'), relief=tk.FLAT, padx=30, pady=12, cursor='hand2').pack(pady=20)
        
        self.import_log = tk.Text(t4, height=12, bg='#1e1e1e', fg='white', font=('Consolas',8), 
                                 relief=tk.FLAT, padx=8, pady=8, state='disabled')
        self.import_log.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10,20))
    
    def tick(self):
        self.clock.config(text=datetime.now().strftime("%H:%M:%S"))
        self.clock.after(1000, self.tick)
    
    def log_msg(self, m):
        self.log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {m}\n")
        self.log.see(tk.END)
    
    def toggle(self):
        if not self.running:
            self.running = True
            self.status.config(text="▶️ Läuft", fg='#51cf66')
            self.btn.config(text="⏹️ Stop", bg='#ff6b6b')
            self.log_msg("Auto gestartet")
            threading.Thread(target=self.loop, daemon=True).start()
        else:
            self.running = False
            self.status.config(text="⏸️ Stop", fg='#ff6b6b')
            self.btn.config(text="▶️ Start", bg='#51cf66')
            self.log_msg("Auto gestoppt")
    
    def loop(self):
        last = None
        while self.running:
            # Lade JSON neu
            try:
                with open("stundenplan.json", encoding='utf-8') as f:
                    self.tt = json.load(f)['stundenplan']
            except:
                pass
            
            now = datetime.now()
            curr = now.strftime("%H:%M")
            day = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"][now.weekday()]
            if curr != last and day in self.tt:
                last = curr
                for l in self.tt[day]:
                    if l['start'] == curr:
                        k = f"{day}_{curr}"
                        if k not in self.opened:
                            self.log_msg(f"⏰ {l['fach']}")
                            self.open(l, show_popup=False)
                            self.opened.add(k)
            time.sleep(10)
    
    def open(self, l, show_popup=True):
        for url in l['ressourcen']['webseiten']:
            webbrowser.open(url)
            self.log_msg(f"🌐 {url[:30]}")
            time.sleep(0.2)
        if show_popup:
            messagebox.showinfo("✓", f"{l['fach']} geöffnet!")
    
    def load_day(self):
        for w in self.edit_frame.winfo_children():
            w.destroy()
        day = self.day_var.get()
        lessons = self.tt.get(day, [])
        
        canvas = tk.Canvas(self.edit_frame, bg='#2b2b2b', highlightthickness=0)
        scroll = ttk.Scrollbar(self.edit_frame, command=canvas.yview)
        frame = tk.Frame(canvas, bg='#2b2b2b')
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        for i, l in enumerate(lessons):
            c = tk.Frame(frame, bg='#3c3c3c', relief=tk.RAISED, bd=1)
            c.pack(fill=tk.X, pady=5)
            tk.Label(c, text=f"{l['fach']} ({l['start']}-{l['ende']})", font=('Segoe UI',10,'bold'), 
                    bg='#3c3c3c', fg='white').pack(anchor='w', padx=10, pady=5)
            tk.Label(c, text=f"Web: {', '.join(l['ressourcen']['webseiten']) or 'keine'}", 
                    font=('Segoe UI',8), bg='#3c3c3c', fg='#aaa', wraplength=500).pack(anchor='w', padx=10, pady=(0,5))
            bf = tk.Frame(c, bg='#3c3c3c')
            bf.pack(pady=5)
            tk.Button(bf, text="✏️ Edit", command=lambda x=day,y=i: self.edit_lesson(x,y), 
                     bg='#0e639c', fg='white', font=('Segoe UI',8,'bold'), relief=tk.FLAT, padx=8, pady=3).pack(side=tk.LEFT, padx=2)
            tk.Button(bf, text="🗑️ Löschen", command=lambda x=day,y=i: self.del_lesson(x,y), 
                     bg='#ff6b6b', fg='white', font=('Segoe UI',8,'bold'), relief=tk.FLAT, padx=8, pady=3).pack(side=tk.LEFT, padx=2)
        
        tk.Button(frame, text="➕ Neue Lektion", command=lambda: self.add_lesson(day), 
                 bg='#51cf66', fg='white', font=('Segoe UI',9,'bold'), relief=tk.FLAT, padx=15, pady=6).pack(pady=10)
    
    def edit_lesson(self, day, idx):
        l = self.tt[day][idx]
        win = tk.Toplevel(bg='#2b2b2b')
        win.title("Lektion bearbeiten")
        win.geometry("400x350")
        
        tk.Label(win, text="Fach:", bg='#2b2b2b', fg='white').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        fach = tk.Entry(win, width=30)
        fach.insert(0, l['fach'])
        fach.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(win, text="Start:", bg='#2b2b2b', fg='white').grid(row=1, column=0, padx=10, pady=5, sticky='w')
        start = tk.Entry(win, width=30)
        start.insert(0, l['start'])
        start.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(win, text="Ende:", bg='#2b2b2b', fg='white').grid(row=2, column=0, padx=10, pady=5, sticky='w')
        ende = tk.Entry(win, width=30)
        ende.insert(0, l['ende'])
        ende.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(win, text="Webseiten:", bg='#2b2b2b', fg='white').grid(row=3, column=0, padx=10, pady=5, sticky='nw')
        web = tk.Text(win, width=30, height=6)
        web.insert('1.0', '\n'.join(l['ressourcen']['webseiten']))
        web.grid(row=3, column=1, padx=10, pady=5)
        
        def save():
            self.tt[day][idx] = {
                'fach': fach.get(),
                'start': start.get(),
                'ende': ende.get(),
                'ressourcen': {
                    'webseiten': [w.strip() for w in web.get('1.0','end').strip().split('\n') if w.strip()],
                    'anwendungen': []
                }
            }
            self.save_json()
            win.destroy()
            self.load_day()
        
        tk.Button(win, text="💾 Speichern", command=save, bg='#51cf66', fg='white', 
                 font=('Segoe UI',10,'bold'), relief=tk.FLAT, padx=20, pady=8).grid(row=4, column=0, columnspan=2, pady=15)
    
    def add_lesson(self, day):
        win = tk.Toplevel(bg='#2b2b2b')
        win.title("Neue Lektion")
        win.geometry("400x350")
        
        tk.Label(win, text="Fach:", bg='#2b2b2b', fg='white').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        fach = tk.Entry(win, width=30)
        self.add_placeholder(fach, 'z.B. Mathematik')
        fach.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(win, text="Start (HH:MM):", bg='#2b2b2b', fg='white').grid(row=1, column=0, padx=10, pady=5, sticky='w')
        start = tk.Entry(win, width=30)
        self.add_placeholder(start, '08:00')
        start.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(win, text="Ende (HH:MM):", bg='#2b2b2b', fg='white').grid(row=2, column=0, padx=10, pady=5, sticky='w')
        ende = tk.Entry(win, width=30)
        self.add_placeholder(ende, '09:00')
        ende.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(win, text="Webseiten:", bg='#2b2b2b', fg='white').grid(row=3, column=0, padx=10, pady=5, sticky='nw')
        web = tk.Text(win, width=30, height=6)
        self.add_text_placeholder(web, 'z.B.:\nhttps://moodle.ch\nhttps://teams.microsoft.com')
        web.grid(row=3, column=1, padx=10, pady=5)
        
        def save():
            if not fach.get() or not start.get() or not ende.get():
                messagebox.showerror("Fehler", "Fach, Start und Ende sind Pflichtfelder!")
                return
            # Entferne Placeholder wenn nicht geändert
            f = fach.get() if fach.get() != 'z.B. Mathematik' else ''
            s = start.get() if start.get() != '08:00' and start.cget('fg') != 'grey' else ''
            e = ende.get() if ende.get() != '09:00' and ende.cget('fg') != 'grey' else ''
            if not f or not s or not e:
                messagebox.showerror("Fehler", "Bitte alle Felder ausfüllen!")
                return
            
            web_text = web.get('1.0','end-1c')
            
            # Filtere Placeholder raus
            if 'z.B.' in web_text:
                web_list = []
            else:
                web_list = [w.strip() for w in web_text.split('\n') if w.strip()]
            
            self.tt[day].append({
                'fach': f,
                'start': s,
                'ende': e,
                'ressourcen': {
                    'webseiten': web_list,
                    'anwendungen': []
                }
            })
            self.save_json()
            win.destroy()
            self.load_day()
        
        tk.Button(win, text="➕ Hinzufügen", command=save, bg='#51cf66', fg='white', 
                 font=('Segoe UI',10,'bold'), relief=tk.FLAT, padx=20, pady=8).grid(row=4, column=0, columnspan=2, pady=15)
    
    def del_lesson(self, day, idx):
        if messagebox.askyesno("Löschen", f"Lektion '{self.tt[day][idx]['fach']}' wirklich löschen?"):
            del self.tt[day][idx]
            self.save_json()
            self.load_day()
    
    def save_json(self):
        with open("stundenplan.json", 'w', encoding='utf-8') as f:
            json.dump({'stundenplan': self.tt, 'erstellt_am': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, f, indent=2, ensure_ascii=False)
    
    def add_placeholder(self, entry, text):
        """Fügt grauen Placeholder zu Entry hinzu"""
        entry.insert(0, text)
        entry.config(fg='grey')
        entry.bind('<FocusIn>', lambda e: self.on_entry_click(entry, text))
        entry.bind('<FocusOut>', lambda e: self.on_focusout(entry, text))
    
    def on_entry_click(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg='black')
    
    def on_focusout(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg='grey')
    
    def add_text_placeholder(self, text_widget, placeholder):
        """Fügt grauen Placeholder zu Text-Widget hinzu"""
        text_widget.insert('1.0', placeholder)
        text_widget.config(fg='grey')
        text_widget.bind('<FocusIn>', lambda e: self.on_text_click(text_widget, placeholder))
        text_widget.bind('<FocusOut>', lambda e: self.on_text_focusout(text_widget, placeholder))
    
    def on_text_click(self, widget, placeholder):
        if widget.get('1.0', 'end-1c') == placeholder:
            widget.delete('1.0', tk.END)
            widget.config(fg='black')
    
    def on_text_focusout(self, widget, placeholder):
        if not widget.get('1.0', 'end-1c').strip():
            widget.insert('1.0', placeholder)
            widget.config(fg='grey')
    
    def import_pdf(self):
        """PDF auswählen und importieren"""
        pdf_path = filedialog.askopenfilename(
            title="PDF auswählen",
            filetypes=[("PDF Dateien", "*.pdf"), ("Alle Dateien", "*.*")]
        )
        if not pdf_path:
            return
        
        self.import_log.config(state='normal')
        self.import_log.delete('1.0', tk.END)
        self.import_log.insert(tk.END, f"📄 PDF: {os.path.basename(pdf_path)}\n")
        self.import_log.insert(tk.END, "⏳ Lese PDF...\n\n")
        self.import_log.config(state='disabled')
        
        # Import in Thread um GUI nicht zu blockieren
        threading.Thread(target=self.do_import, args=(pdf_path,), daemon=True).start()
    
    def do_import(self, pdf_path):
        """Führt PDF-Import durch"""
        try:
            # Importiere pdf_parser
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from pdf_parser import parse_timetable_pdf
            
            self.log_import("🔍 Parse PDF...\n")
            result = parse_timetable_pdf(pdf_path)
            
            if not result:
                self.log_import("❌ Fehler beim Parsen!\n")
                return
            
            # Zähle gefundene Lektionen
            total = sum(len(lessons) for lessons in result.values())
            self.log_import(f"✅ {total} Lektionen gefunden!\n\n")
            
            # Zeige gefundene Fächer
            for day, lessons in result.items():
                if lessons:
                    self.log_import(f"{day}:\n")
                    for l in lessons:
                        self.log_import(f"  • {l['start']}-{l['ende']}: {l['fach']}\n")
                    self.log_import("\n")
            
            # Überschreibe timetable
            self.tt = result
            
            # Speichere JSON
            with open("stundenplan.json", 'w', encoding='utf-8') as f:
                json.dump({'stundenplan': self.tt, 'erstellt_am': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, 
                         f, indent=2, ensure_ascii=False)
            
            self.log_import("💾 Gespeichert in stundenplan.json\n")
            self.log_import("✨ Import abgeschlossen!\n")
            
            messagebox.showinfo("Erfolg", f"{total} Lektionen erfolgreich importiert!")
            
        except Exception as e:
            self.log_import(f"❌ Fehler: {str(e)}\n")
            messagebox.showerror("Fehler", f"Import fehlgeschlagen:\n{str(e)}")
    
    def log_import(self, text):
        """Schreibt in Import-Log"""
        self.import_log.config(state='normal')
        self.import_log.insert(tk.END, text)
        self.import_log.see(tk.END)
        self.import_log.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    GUI(root)
    root.mainloop()
