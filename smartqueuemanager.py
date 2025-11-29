# Aplikasi Antrian Rumah Sakit / Tugas Akhir Praktikum Pemrograman

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import csv
import datetime
import threading

# optional TTS (if installed)
try:
    import pyttsx3
    TTS_AVAILABLE = True
    tts_engine = pyttsx3.init()
except Exception:
    TTS_AVAILABLE = False

# optional winsound (Windows)
try:
    import winsound
    WINSOUND_AVAILABLE = True
except Exception:
    WINSOUND_AVAILABLE = False


# -------------------------
# Data structures
# -------------------------
queue = []        # list of dict: {"number": int, "name": str}
history = []      # list (stack) of dicts
counter = 1       # next number integer (A001)


# -------------------------
# Helpers
# -------------------------
def format_number(n):
    return f"A{n:03d}"


def speak(text):
    """Try TTS, else beep (non-blocking)."""
    if TTS_AVAILABLE:
        def _speak():
            try:
                tts_engine.say(text)
                tts_engine.runAndWait()
            except Exception:
                try_beep()
        threading.Thread(target=_speak, daemon=True).start()
    else:
        try_beep()


def try_beep():
    if WINSOUND_AVAILABLE:
        try:
            winsound.Beep(1000, 250)
        except Exception:
            pass
    else:
        # system bell via root (non-blocking)
        try:
            root.bell()
        except Exception:
            pass


# -------------------------
# Core functions
# -------------------------
def add_to_queue():
    global counter
    name = entry_name.get().strip()
    if not name:
        messagebox.showwarning("Peringatan", "Nama tidak boleh kosong.")
        return

    item = {"number": counter, "name": name}
    queue.append(item)
    listbox_queue.insert(tk.END, f"{format_number(counter)} - {name}")
    entry_name.delete(0, tk.END)
    update_total()


def call_next():
    if not queue:
        messagebox.showinfo("Info", "Tidak ada antrian.")
        return

    item = queue.pop(0)
    history.append(item)

    # remove first item from queue listbox
    if listbox_queue.size() > 0:
        listbox_queue.delete(0)

    label_current_value.set(f"{format_number(item['number'])} - {item['name']}")
    # speak (non-blocking)
    speak(f"Nomor {format_number(item['number'])}, silakan {item['name']}")
    update_history_preview()
    update_total()


def undo_call():
    if not history:
        messagebox.showinfo("Info", "History kosong.")
        return

    item = history.pop()  # last called
    queue.insert(0, item)

    # update UI
    listbox_queue.insert(0, f"{format_number(item['number'])} - {item['name']}")
    update_history_preview()
    update_total()
    messagebox.showinfo("Undo", f"{format_number(item['number'])} dikembalikan ke antrian.")


def reset_number_and_clear_queue():
    global counter, queue
    confirm = messagebox.askyesno("Konfirmasi", "Reset nomor ke A001 dan hapus semua antrian?")
    if not confirm:
        return

    counter = 1
    queue.clear()
    listbox_queue.delete(0, tk.END)

    # log
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("reset_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{now}] RESET: Nomor direset ke A001 & semua antrian dihapus.\n")

    label_current_value.set("-")
    update_history_preview()
    update_total()
    messagebox.showinfo("Reset", "Nomor direset ke A001 dan antrian dikosongkan.")


def export_queue_csv():
    if not queue:
        messagebox.showinfo("Export", "Tidak ada antrian untuk diexport.")
        return
    path = filedialog.asksaveasfilename(defaultextension=".csv",
                                        filetypes=[("CSV files", "*.csv")])
    if not path:
        return
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["number", "name"])
            for it in queue:
                writer.writerow([it["number"], it["name"]])
        messagebox.showinfo("Export", f"Berhasil export ke {path}")
    except Exception as e:
        messagebox.showerror("Error", f"Gagal export:\n{e}")


def import_queue_csv():
    global counter
    path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if not path:
        return
    try:
        imported = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # expect number and name
                if "number" in row and "name" in row:
                    try:
                        num = int(row["number"])
                    except:
                        continue
                    name = row["name"].strip()
                    imported.append({"number": num, "name": name})
        if not imported:
            messagebox.showwarning("Import", "Tidak ada data valid dalam file.")
            return
        # append imported to current queue and update UI
        for it in imported:
            queue.append(it)
            listbox_queue.insert(tk.END, f"{format_number(it['number'])} - {it['name']}")
        # update counter to avoid duplicate numbers
        max_num = max(it["number"] for it in imported)
        if max_num >= counter:
            counter = max_num + 1
        update_total()
        messagebox.showinfo("Import", f"Berhasil import {len(imported)} baris.")
    except Exception as e:
        messagebox.showerror("Error", f"Gagal import:\n{e}")


def show_history_popup():
    if not history:
        messagebox.showinfo("History", "Belum ada history.")
        return
    win = tk.Toplevel(root)
    win.title("History Panggilan")
    txt = tk.Text(win, width=40, height=20)
    txt.pack(padx=8, pady=8)
    # show newest first
    for it in reversed(history):
        txt.insert(tk.END, f"{format_number(it['number'])} - {it['name']}\n")
    txt.config(state="disabled")


# -------------------------
# UI update helpers
# -------------------------
def update_total():
    total_label_value.set(f"Total Antrian: {len(queue)}")


def update_history_preview():
    history_listbox.delete(0, tk.END)
    # preview last 10 newest first
    recent = list(reversed(history))[:10]
    for it in recent:
        history_listbox.insert(tk.END, f"{format_number(it['number'])} - {it['name']}")


# -------------------------
# Build UI
# -------------------------
root = tk.Tk()
root.title("Smart Queue Manager")
root.geometry("720x520")
root.resizable(True, True)

# Use ttk styles for cleaner look
style = ttk.Style()
style.theme_use('default')

# Header
header_frame = ttk.Frame(root, padding=(12, 10))
header_frame.pack(fill="x")
ttk.Label(header_frame, text="Smart Queue Manager", font=("Arial", 18, "bold")).pack(side="left")
label_current_value = tk.StringVar(value="-")
ttk.Label(header_frame, text="Sedang Dipanggil:", font=("Arial", 12)).pack(side="left", padx=(20, 6))
label_current_value_widget = ttk.Label(header_frame, textvariable=label_current_value, font=("Arial", 12, "bold"))
label_current_value_widget.pack(side="left")

# main container
main_frame = ttk.Frame(root, padding=12)
main_frame.pack(fill="both", expand=True)

# left card (controls)
left_card = ttk.Frame(main_frame, padding=12)
left_card.grid(row=0, column=0, sticky="n")

ttk.Label(left_card, text="Tambah Pengunjung", font=("Arial", 12, "bold")).pack(anchor="w")
entry_name = ttk.Entry(left_card, width=30)
entry_name.pack(pady=6)

ttk.Button(left_card, text="Tambah Antrian", command=add_to_queue).pack(fill="x", pady=4)
ttk.Button(left_card, text="Panggil Berikutnya", command=call_next).pack(fill="x", pady=4)
ttk.Button(left_card, text="Undo Panggilan", command=undo_call).pack(fill="x", pady=4)
ttk.Button(left_card, text="Reset Nomor & Hapus Antrian", command=reset_number_and_clear_queue).pack(fill="x", pady=8)

# file ops
ttk.Separator(left_card, orient="horizontal").pack(fill="x", pady=6)
ttk.Button(left_card, text="Export Antrian (CSV)", command=export_queue_csv).pack(fill="x", pady=4)
ttk.Button(left_card, text="Import Antrian (CSV)", command=import_queue_csv).pack(fill="x", pady=4)
ttk.Button(left_card, text="Lihat History (Popup)", command=show_history_popup).pack(fill="x", pady=6)

# right card (lists)
right_card = ttk.Frame(main_frame, padding=12)
right_card.grid(row=0, column=1, sticky="n", padx=(20,0))

ttk.Label(right_card, text="Daftar Antrian", font=("Arial", 12, "bold")).pack(anchor="w")
listbox_queue = tk.Listbox(right_card, width=40, height=12)
listbox_queue.pack(pady=6)

ttk.Label(right_card, text="Preview History", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10,0))
history_listbox = tk.Listbox(right_card, width=40, height=8)
history_listbox.pack(pady=6)

# footer / totals
footer = ttk.Frame(root, padding=8)
footer.pack(fill="x")
total_label_value = tk.StringVar(value="Total Antrian: 0")
ttk.Label(footer, textvariable=total_label_value).pack(side="left")

# helper binding: pressing Enter in entry adds
def on_enter_add(event=None):
    add_to_queue()

entry_name.bind("<Return>", on_enter_add)

# show initial values
label_current_value.set("-")
update_total()

root.mainloop()



