# Aplikasi Antrian Rumah Sakit / Tugas Akhir Praktikum Pemrograman

import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import csv
import os
import sys
import threading
import time

# ---------- Optional TTS ----------
try:
    import pyttsx3
    TTS_AVAILABLE = True
    tts_engine = pyttsx3.init()
except Exception:
    TTS_AVAILABLE = False

# ---------- Sound fallback for Windows ----------
try:
    import winsound
    WINSOUND_AVAILABLE = True
except Exception:
    WINSOUND_AVAILABLE = False

class SmartQueue:
    def __init__(self):
        # menyimpan dict: {"number": int, "name": str}
        self.queue = []

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.queue.pop(0)
        return None

    def is_empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)

    def get_all(self):
        return list(self.queue)

    def clear(self):
        self.queue = []

class HistoryStack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        return None

    def is_empty(self):
        return len(self.stack) == 0

    def get_all(self):
        return list(reversed(self.stack))  # newest first

    def clear(self):
        self.stack = []

def format_number(n):
    # Format: A001, A002...
    return f"A{n:03d}"

def speak_text(text):
    # Use TTS if available, else try winsound, else bell.
    if TTS_AVAILABLE:
        # run in thread since pyttsx3 is blocking
        def tts():
            try:
                tts_engine.say(text)
                tts_engine.runAndWait()
            except Exception:
                try_beep()
        threading.Thread(target=tts, daemon=True).start()
    else:
        try_beep()

def try_beep():
    if WINSOUND_AVAILABLE:
        # simple beep (frequency 1000, duration 400 ms)
        try:
            winsound.Beep(1000, 400)
        except Exception:
            pass
    else:
        # fallback: system bell (non-blocking)
        try:
            root = tk._get_default_root()
            if root:
                root.bell()
        except Exception:
            pass

def modern_button(parent, text, command, width=26):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=parent.master.primary_color,
        fg=parent.master.fg_color,
        activebackground=parent.master.primary_active,
        font=("Segoe UI", 10, "bold"),
        padx=8,
        pady=6,
        relief="flat",
        bd=0,
        width=width
    )

class SmartQueueGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Your Smart Queue Manager")
        self.root.geometry("620x640")
        self.root.resizable(True, True)

        # Theme colors (light by default)
        self.light_bg = "#F4F4FF"
        self.light_panel = "#FFFFFF"
        self.dark_bg = "#1E1E2E"
        self.dark_panel = "#2A2A3A"

        # Colors that will be referenced in widgets
        self.is_dark = False
        self.primary_color = "#6C63FF"
        self.primary_active = "#574BFF"
        self.fg_color = "white"

        self.apply_theme()  # sets root colors

        # Data structures
        self.queue = SmartQueue()
        self.history = HistoryStack()
        self.current_number = 0

        header = tk.Frame(self.root, bg=self.panel_color, pady=12)
        header.pack(fill="x")
        title_label = tk.Label(
            header,
            text="Selamat Datang, Semoga Harimu Menyenangkan!",
            font=("Segoe UI", 20, "bold"),
            bg=self.panel_color,
            fg=self.title_color
        )
        title_label.pack()

        # ---------- Current display ----------
        self.current_label = tk.Label(
            self.root,
            text="Antrian Saat Ini: -",
            font=("Segoe UI", 18, "bold"),
            bg=self.root_bg,
            fg=self.title_color
        )
        self.current_label.pack(pady=12)

        # ---------- Buttons area ----------
        button_frame = tk.Frame(self.root, bg=self.root_bg)
        button_frame.pack(pady=8)

        modern_button(button_frame, "Tambah Antrian", self.add_queue).pack(pady=6)
        modern_button(button_frame, "Panggil Antrian", self.call_queue).pack(pady=6)
        modern_button(button_frame, "Undo Panggilan", self.undo_call).pack(pady=6)
        modern_button(button_frame, "Lihat Daftar Antrian", self.show_queue).pack(pady=6)
        modern_button(button_frame, "Lihat History", self.show_history).pack(pady=6)

        # ---------- Export / Import ----------
        file_frame = tk.Frame(self.root, bg=self.root_bg)
        file_frame.pack(pady=10)

        modern_button(file_frame, "Export Antrian (CSV)", self.export_queue_csv, width=18).pack(side="left", padx=6)
        modern_button(file_frame, "Import Antrian (CSV)", self.import_queue_csv, width=18).pack(side="left", padx=6)
        modern_button(file_frame, "Export History (TXT)", self.export_history_txt, width=18).pack(side="left", padx=6)

        # ---------- Controls ----------
        control_frame = tk.Frame(self.root, bg=self.root_bg)
        control_frame.pack(pady=10)

        modern_button(control_frame, "Reset Semua", self.reset_all, width=18).pack(side="left", padx=6)
        modern_button(control_frame, "Toggle Dark Mode", self.toggle_theme, width=18).pack(side="left", padx=6)

        # ---------- Visual area: queue list & history preview ----------
        panel = tk.Frame(self.root, bg=self.panel_color, padx=12, pady=12)
        panel.pack(padx=20, pady=12, fill="both", expand=False)

        # Queue List
        q_label = tk.Label(panel, text="Daftar Antrian (Selanjutnya):", font=("Segoe UI", 11, "bold"),
                           bg=self.panel_color, fg=self.title_color)
        q_label.grid(row=0, column=0, sticky="w")
        self.queue_listbox = tk.Listbox(panel, height=8, width=40, font=("Segoe UI", 11),
                                        bg=self.panel_color, fg=self.title_color, bd=0, highlightthickness=0)
        self.queue_listbox.grid(row=1, column=0, padx=6, pady=6)

        # History preview
        h_label = tk.Label(panel, text="Preview History (Terbaru 10):", font=("Segoe UI", 11, "bold"),
                           bg=self.panel_color, fg=self.title_color)
        h_label.grid(row=0, column=1, sticky="w", padx=(20,0))
        self.history_listbox = tk.Listbox(panel, height=8, width=30, font=("Segoe UI", 11),
                                          bg=self.panel_color, fg=self.title_color, bd=0, highlightthickness=0)
        self.history_listbox.grid(row=1, column=1, padx=(20,0), pady=6)

        # ---------- Footer: total ----------
        self.total_label = tk.Label(self.root, text="Total Antrian: 0", font=("Segoe UI", 13),
                                    bg=self.root_bg, fg=self.title_color)
        self.total_label.pack(pady=10)

        # initial update
        self.update_display()

    # ---------- Theme / style ----------
    def apply_theme(self):
        if self.is_dark:
            self.root_bg = self.dark_bg
            self.panel_color = self.dark_panel
            self.title_color = "#E6E6FA"
            self.root.configure(bg=self.dark_bg)
            self.primary_color = "#8A79FF"
            self.primary_active = "#6F61FF"
            self.fg_color = "white"
        else:
            self.root_bg = self.light_bg
            self.panel_color = self.light_panel
            self.title_color = "#2C2C54"
            self.root.configure(bg=self.light_bg)
            self.primary_color = "#6C63FF"
            self.primary_active = "#574BFF"
            self.fg_color = "white"

        # expose to button factory via root
        self.root.primary_color = self.primary_color
        self.root.primary_active = self.primary_active
        self.root.fg_color = self.fg_color

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.apply_theme()
        # rebuild simple parts' colors
        self.root.configure(bg=self.root_bg)
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg=self.root_bg)
            except Exception:
                pass
        # update panel & listboxes colors explicitly
        for w in self.root.winfo_children():
            if isinstance(w, tk.Frame):
                for child in w.winfo_children():
                    try:
                        child.configure(bg=self.panel_color if isinstance(child, tk.Listbox) or isinstance(child, tk.Label) else self.root_bg)
                    except Exception:
                        pass
        # More robust: destroy and recreate UI would be cleaner, but this toggles main colors:
        self.update_display()

    # ---------- Core features ----------
    def add_queue(self):
        name = simpledialog.askstring("Tambah Antrian", "Masukkan nama orang:")
        if name is None:   # user cancelled
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("Gagal", "Nama tidak boleh kosong.")
            return

        self.current_number += 1
        new_item = {"number": self.current_number, "name": name}
        self.queue.enqueue(new_item)
        messagebox.showinfo("Berhasil", f"Antrian {format_number(self.current_number)} - {name} ditambahkan.")
        self.update_display()

    def call_queue(self):
        if self.queue.is_empty():
            messagebox.showwarning("Kosong", "Tidak ada antrian yang dapat dipanggil.")
            return

        called = self.queue.dequeue()
        # push to history (stack)
        self.history.push(called)

        nomor = called["number"]
        nama = called["name"]
        display_text = f"{format_number(nomor)} - {nama}"
        self.current_label.config(text=f"Antrian Saat Ini: {display_text}")

        # Animation: scale current_label up then back
        self.animate_label(self.current_label)

        # Sound / TTS notification (non-blocking)
        threading.Thread(target=lambda: speak_text(f"Nomor {format_number(nomor)}, silakan {nama}"), daemon=True).start()

        self.update_display()

    def undo_call(self):
        if self.history.is_empty():
            messagebox.showwarning("Undo Gagal", "Tidak ada panggilan untuk di-undo.")
            return

        last = self.history.pop()
        self.queue.enqueue(last)
        messagebox.showinfo("Undo Berhasil", f"{format_number(last['number'])} - {last['name']} dikembalikan ke antrian.")
        self.update_display()

    def show_queue(self):
        if self.queue.is_empty():
            messagebox.showinfo("Daftar Antrian", "Antrian kosong.")
            return
        daftar = "\n".join([f"{format_number(q['number'])} - {q['name']}" for q in self.queue.get_all()])
        # show in a scrollable window (simple)
        self._popup_text("Daftar Antrian", daftar)

    def show_history(self):
        if self.history.is_empty():
            messagebox.showinfo("History", "Belum ada history.")
            return
        daftar = "\n".join([f"{format_number(h['number'])} - {h['name']}" for h in self.history.get_all()])
        self._popup_text("History Panggilan", daftar)

    # ---------- Export / Import ----------
    def export_queue_csv(self):
        if self.queue.is_empty():
            messagebox.showinfo("Export CSV", "Tidak ada data antrian untuk diexport.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV file","*.csv")])
        if not path:
            return
        try:
            with open(path, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["number", "name"])
                for q in self.queue.get_all():
                    writer.writerow([q["number"], q["name"]])
            messagebox.showinfo("Export CSV", f"Berhasil export antrian ke {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export CSV:\n{e}")

    def import_queue_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV file","*.csv"), ("Text file","*.txt")])
        if not path:
            return
        try:
            imported = []
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if "number" in row and "name" in row:
                        # try parse number
                        try:
                            num = int(row["number"])
                        except Exception:
                            # skip invalid row
                            continue
                        name = row["name"].strip()
                        if name:
                            imported.append({"number": num, "name": name})
            if not imported:
                messagebox.showwarning("Import", "Tidak ada data valid yang ditemukan di file.")
                return
            # append to current queue
            for item in imported:
                self.queue.enqueue(item)
            # update current_number to avoid duplicate numbers
            max_imported = max(item["number"] for item in imported)
            if max_imported > self.current_number:
                self.current_number = max_imported
            messagebox.showinfo("Import CSV", f"Berhasil mengimpor {len(imported)} baris dari file.")
            self.update_display()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal import:\n{e}")

    def export_history_txt(self):
        if self.history.is_empty():
            messagebox.showinfo("Export History", "Belum ada history untuk diexport.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text file","*.txt")])
        if not path:
            return
        try:
            with open(path, "w", encoding='utf-8') as f:
                for h in self.history.get_all():
                    f.write(f"{format_number(h['number'])} - {h['name']}\n")
            messagebox.showinfo("Export History", f"Berhasil export history ke {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export history:\n{e}")

    # ---------- Reset ----------
    def reset_all(self):
        confirm = messagebox.askyesno("Reset Semua", "Yakin ingin mereset antrian dan history?")
        if not confirm:
            return
        self.queue.clear()
        self.history.clear()
        self.current_number = 0
        self.current_label.config(text="Antrian Saat Ini: -")
        self.update_display()

    # ---------- UI helpers ----------
    def _popup_text(self, title, text):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("420x360")
        win.configure(bg=self.panel_color)
        txt = tk.Text(win, wrap="word", bg=self.panel_color, fg=self.title_color, font=("Segoe UI", 11))
        txt.pack(expand=True, fill="both", padx=8, pady=8)
        txt.insert("1.0", text)
        txt.configure(state="disabled")
        tk.Button(win, text="Tutup", command=win.destroy, bg=self.primary_color, fg=self.fg_color, relief="flat").pack(pady=6)

    def update_display(self):
        # update listbox and history preview
        self.queue_listbox.delete(0, tk.END)
        for q in self.queue.get_all():
            self.queue_listbox.insert(tk.END, f"{format_number(q['number'])} - {q['name']}")

        self.history_listbox.delete(0, tk.END)
        hist = self.history.get_all()[:10]
        for h in hist:
            self.history_listbox.insert(tk.END, f"{format_number(h['number'])} - {h['name']}")

        self.total_label.config(text=f"Total Antrian: {self.queue.size()}")

    # ---------- Simple animation ----------
    def animate_label(self, widget, max_scale=1.4, steps=6, speed=30):
        # Animate font size scaling for widget (non-blocking)
        try:
            current_font = widget.cget("font").split()
            # font tuple like ("Segoe UI", 18, "bold") as string, safer to store original
            base_size = 18
            # create sequence of sizes up then down
            sizes = [int(base_size + (max_scale - 1) * base_size * (i/steps)) for i in range(steps)]
            sizes += list(reversed(sizes))
        except Exception:
            return

        def step(i=0):
            if i >= len(sizes):
                widget.config(font=("Segoe UI", base_size, "bold"))
                return
            widget.config(font=("Segoe UI", sizes[i], "bold"))
            widget.after(speed, lambda: step(i+1))

        step(0)

# ==========================
# RUN APP
# ==========================
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartQueueGUI(root)
    root.mainloop()
