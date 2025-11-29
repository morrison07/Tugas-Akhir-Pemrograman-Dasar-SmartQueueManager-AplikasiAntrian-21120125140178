# Aplikasi Antrian / Tugas Akhir Praktikum Pemrograman

import tkinter as tk
from tkinter import messagebox, simpledialog

# --------------------------
# DATA STRUKTUR
# --------------------------

queue = []
history = []
counter = 1  # Nomor awal A001


def format_number(n):
    return f"A{n:03d}"


# --------------------------
# FUNGSI INTI
# --------------------------

def add_to_queue():
    global counter

    name = entry_name.get().strip()
    if not name:
        messagebox.showwarning("Peringatan", "Nama tidak boleh kosong.")
        return

    queue.append({"number": counter, "name": name})
    listbox_queue.insert(tk.END, f"{format_number(counter)} - {name}")

    counter += 1  # PENTING! Agar nomor antrian naik setiap input
    entry_name.delete(0, tk.END)

    update_total()


def call_queue():
    if not queue:
        messagebox.showwarning("Kosong", "Tidak ada antrian untuk dipanggil.")
        return

    item = queue.pop(0)
    history.append(item)

    label_current.config(text=f"Antrian Dipanggil: {format_number(item['number'])} - {item['name']}")

    listbox_queue.delete(0)  # hapus baris pertama

    update_total()


def reset_number_only():
    """Reset nomor antrian tetapi tidak menghapus queue/history."""
    global counter

    # Menyimpan riwayat reset
    with open("reset_log.txt", "a", encoding="utf-8") as f:
        f.write("Nomor reset ke 1\n")

    counter = 1
    messagebox.showinfo("Reset", "Nomor antrian berhasil di-reset ke A001.")


def update_total():
    label_total.config(text=f"Total Antrian: {len(queue)}")


# --------------------------
# UI SETUP
# --------------------------

root = tk.Tk()
root.title("Aplikasi Antrian")
root.geometry("400x500")

# Input
label_title = tk.Label(root, text="Selamat Datang, Tuan/Nyonya. Semoga Hari Anda Semakin Girang", font=("Arial", 16, "bold"))
label_title.pack(pady=10)

frame_input = tk.Frame(root)
frame_input.pack(pady=5)

label_name = tk.Label(frame_input, text="Nama:")
label_name.grid(row=0, column=0)

entry_name = tk.Entry(frame_input, width=25)
entry_name.grid(row=0, column=1, padx=5)

btn_add = tk.Button(root, text="Tambah Antrian", command=add_to_queue, width=30)
btn_add.pack(pady=5)

btn_call = tk.Button(root, text="Panggil Antrian", command=call_queue, width=30)
btn_call.pack(pady=5)

# Current
label_current = tk.Label(root, text="Antrian Dipanggil: -", font=("Arial", 12))
label_current.pack(pady=10)

# Listbox
listbox_queue = tk.Listbox(root, width=40, height=10)
listbox_queue.pack(pady=10)

label_total = tk.Label(root, text="Total Antrian: 0")
label_total.pack(pady=5)

# Reset number button
btn_reset_num = tk.Button(root, text="Reset Nomor Antrian", command=reset_number_only, width=30)
btn_reset_num.pack(pady=10)

root.mainloop()




