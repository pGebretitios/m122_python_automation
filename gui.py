"""Stundenplan-GUI"""
import tkinter as tk
from tkinter import ttk, messagebox
import json, subprocess, webbrowser, threading, time
from datetime import datetime

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
                            self.open(l)
                            self.opened.add(k)
            time.sleep(10)
    
    def open(self, l):
        apps = {"onenote":"onenote","word":"winword","excel":"excel","powerpoint":"powerpnt",
                "outlook":"outlook","teams":"teams","chrome":"chrome","firefox":"firefox",
                "edge":"msedge","code":"code","notepad":"notepad","calculator":"calc"}
        for url in l['ressourcen']['webseiten']:
            webbrowser.open(url)
            self.log_msg(f"🌐 {url[:30]}")
            time.sleep(0.2)
        for app in l['ressourcen']['anwendungen']:
            subprocess.Popen(apps.get(app.lower(), app), shell=True)
            self.log_msg(f"💻 {app}")
            time.sleep(0.1)
        messagebox.showinfo("✓", f"{l['fach']} geöffnet!")

if __name__ == "__main__":
    root = tk.Tk()
    GUI(root)
    root.mainloop()
