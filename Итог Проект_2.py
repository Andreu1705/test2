import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

# Файл для сохранения истории
HISTORY_FILE = "password_history.json"

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # История паролей
        self.history = self.load_history()

        # Интерфейс
        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        # Рамка настроек
        frame_settings = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        frame_settings.pack(fill="x", padx=10, pady=5)

        # Длина пароля
        ttk.Label(frame_settings, text="Длина пароля:").grid(row=0, column=0, sticky="w", pady=5)
        self.length_var = tk.IntVar(value=12)
        self.length_spin = ttk.Spinbox(frame_settings, from_=4, to=64, textvariable=self.length_var, width=10)
        self.length_spin.grid(row=0, column=1, sticky="w", padx=10)

        # Чекбоксы
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)

        ttk.Checkbutton(frame_settings, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(frame_settings, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(frame_settings, text="Спецсимволы (!@#$%^&*)", variable=self.use_symbols).grid(row=1, column=2, sticky="w")

        # Кнопка генерации
        self.generate_btn = ttk.Button(frame_settings, text="Сгенерировать пароль", command=self.generate_password)
        self.generate_btn.grid(row=2, column=0, columnspan=3, pady=10)

        # Поле вывода пароля
        ttk.Label(self.root, text="Сгенерированный пароль:").pack(anchor="w", padx=10)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.root, textvariable=self.password_var, font=("Courier", 12), state="readonly")
        self.password_entry.pack(fill="x", padx=10, pady=5)

        # Кнопка копирования
        self.copy_btn = ttk.Button(self.root, text="Копировать в буфер", command=self.copy_to_clipboard)
        self.copy_btn.pack(pady=5)

        # Таблица истории
        ttk.Label(self.root, text="История паролей:").pack(anchor="w", padx=10, pady=(10, 0))
        frame_table = ttk.Frame(self.root)
        frame_table.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Дата", "Пароль", "Длина", "Настройки")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Пароль", text="Пароль")
        self.tree.heading("Длина", text="Длина")
        self.tree.heading("Настройки", text="Настройки")

        self.tree.column("Дата", width=140)
        self.tree.column("Пароль", width=200)
        self.tree.column("Длина", width=60)
        self.tree.column("Настройки", width=200)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка очистки истории
        self.clear_btn = ttk.Button(self.root, text="Очистить историю", command=self.clear_history)
        self.clear_btn.pack(pady=5)

    def generate_password(self):
        length = self.length_var.get()
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля — 4 символа")
            return
        if length > 64:
            messagebox.showerror("Ошибка", "Максимальная длина пароля — 64 символа")
            return

        chars = ""
        if self.use_digits.get():
            chars += string.digits
        if self.use_letters.get():
            chars += string.ascii_letters
        if self.use_symbols.get():
            chars += "!@#$%^&*()-_=+[]{};:?/<>"

        if not chars:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
            return

        password = ''.join(random.choice(chars) for _ in range(length))
        self.password_var.set(password)

        # Сохраняем в историю
        settings = []
        if self.use_digits.get(): settings.append("цифры")
        if self.use_letters.get(): settings.append("буквы")
        if self.use_symbols.get(): settings.append("спецсимволы")
        settings_str = ", ".join(settings)

        self.history.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "password": password,
            "length": length,
            "settings": settings_str
        })
        self.save_history()
        self.update_history_table()

    def copy_to_clipboard(self):
        pwd = self.password_var.get()
        if pwd:
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена")
        else:
            messagebox.showwarning("Предупреждение", "Нет сгенерированного пароля")

    def update_history_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for entry in reversed(self.history[-20:]):  # показываем последние 20
            self.tree.insert("", "end", values=(
                entry["date"],
                entry["password"],
                entry["length"],
                entry["settings"]
            ))

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю паролей?"):
            self.history = []
            self.save_history()
            self.update_history_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()
