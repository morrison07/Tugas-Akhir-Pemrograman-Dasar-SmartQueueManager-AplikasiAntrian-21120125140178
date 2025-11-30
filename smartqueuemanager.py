# Aplikasi Antrian / Tugas Akhir Praktikum Pemrograman

import tkinter as tk
from tkinter import messagebox, simpledialog

class Queue:
    """Queue FIFO"""
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def get_all(self):
        return list(self.items)


class Stack:
    """Stack LIFO"""
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None

    def is_empty(self):
        return len(self.items) == 0

    def get_all(self):
        return list(reversed(self.items))  # newest first


def format_number(n):
    return f"A{n:03d}"


class SmartQueueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Antrian")
        self.root.geometry("400x500")

        # Struktur data
        self.queue = Queue()
        self.history = Stack()
        self.counter = 1

        # ---------- UI ----------
        self.label_title = tk.Label(root, text="Selamat Datang!", font=("Arial", 14, "bold"))
        self.label_title.pack(pady=10)

        frame_input = tk.Frame(root)
        frame_input.pack(pady=5)

        tk.Label(frame_input, text="Nama:").grid(row=0, column=0)
        self.entry_name = tk.Entry(frame_input, width=25)
        self.entry_name.grid(row=0, column=1, padx=5)

        tk.Button(root, text="Tambah Antrian", command=self.add_queue, width=30).pack(pady=5)
        tk.Button(root, text="Panggil Antrian", command=self.call_queue, width=30).pack(pady=5)
        tk.Button(root, text="Undo Panggilan", command=self.undo_call, width=30).pack(pady=5)

        self.label_current = tk.Label(root, text="Antrian Dipanggil: -", font=("Arial", 12))
        self.label_current.pack(pady=10)

        self.listbox_queue = tk.Listbox(root, width=40, height=10)
        self.listbox_queue.pack(pady=10)

        self.label_total = tk.Label(root, text="Total Antrian: 0")
        self.label_total.pack(pady=5)

        tk.Button(root, text="Reset Nomor Antrian", command=self.reset_number_only, width=30).pack(pady=10)

    # ---------- FUNGSI ----------
    def add_queue(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Peringatan", "Nama tidak boleh kosong.")
            return
        item = {"number": self.counter, "name": name}
        self.queue.enqueue(item)
        self.counter += 1
        self.entry_name.delete(0, tk.END)
        self.update_display()

    def call_queue(self):
        if self.queue.is_empty():
            messagebox.showwarning("Kosong", "Tidak ada antrian untuk dipanggil.")
            return
        item = self.queue.dequeue()
        self.history.push(item)
        self.label_current.config(text=f"Antrian Dipanggil: {format_number(item['number'])} - {item['name']}")
        self.update_display()

    def undo_call(self):
        if self.history.is_empty():
            messagebox.showwarning("Undo Gagal", "Tidak ada panggilan untuk di-undo.")
            return
        item = self.history.pop()
        self.queue.enqueue(item)
        self.update_display()

    def reset_number_only(self):
        self.counter = 1
        messagebox.showinfo("Reset", "Nomor antrian berhasil di-reset ke A001.")

    def update_display(self):
        self.listbox_queue.delete(0, tk.END)
        for item in self.queue.get_all():
            self.listbox_queue.insert(tk.END, f"{format_number(item['number'])} - {item['name']}")
        self.label_total.config(text=f"Total Antrian: {self.queue.size()}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartQueueApp(root)
    root.mainloop()







