import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

DATA_FILE = "weather_data.json"


class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary (Дневник погоды)")
        self.root.geometry("750x550")

        self.records = []

        # --- Фрейм ввода ---
        input_frame = ttk.LabelFrame(root, text="Новая запись", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(input_frame, text="Температура (°C):").grid(row=1, column=0, sticky="w")
        self.temp_entry = ttk.Entry(input_frame, width=15)
        self.temp_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(input_frame, text="Описание:").grid(row=2, column=0, sticky="w")
        self.desc_entry = ttk.Entry(input_frame, width=30)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        self.precip_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var).grid(
            row=2, column=2, padx=10, sticky="w"
        )

        ttk.Button(input_frame, text="Добавить запись", command=self.add_record).grid(
            row=3, column=0, columnspan=3, pady=10
        )

        # --- Таблица ---
        table_frame = ttk.LabelFrame(root, text="Список записей", padding=10)
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        columns = ("date", "temp", "desc", "precip")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура, °C")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("precip", text="Осадки")
        self.tree.column("date", width=100)
        self.tree.column("temp", width=100)
        self.tree.column("desc", width=250)
        self.tree.column("precip", width=80)
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # --- Фильтры ---
        filter_frame = ttk.LabelFrame(root, text="Фильтры", padding=10)
        filter_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(filter_frame, text="По дате (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w")
        self.filter_date = ttk.Entry(filter_frame, width=12)
        self.filter_date.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Темп. выше:").grid(row=0, column=2, padx=(20, 5))
        self.filter_temp = ttk.Entry(filter_frame, width=7)
        self.filter_temp.grid(row=0, column=3)

        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(
            row=0, column=4, padx=15
        )
        ttk.Button(filter_frame, text="Сбросить фильтр", command=self.load_records_to_tree).grid(
            row=0, column=5, padx=5
        )

        # --- Управление данными ---
        ctrl_frame = ttk.Frame(root)
        ctrl_frame.grid(row=3, column=0, pady=10)

        ttk.Button(ctrl_frame, text="Сохранить в JSON", command=self.save_to_json).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(ctrl_frame, text="Загрузить из JSON", command=self.load_from_json).pack(
            side=tk.LEFT, padx=5
        )

        # Растяжение
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.load_from_json()

    def add_record(self):
        date_str = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = self.precip_var.get()

        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
            formatted_date = date_obj.strftime("%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ДД.ММ.ГГГГ")
            return

        try:
            temp = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        if not desc:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        record = {
            "date": formatted_date,
            "temperature": temp,
            "description": desc,
            "precipitation": precip
        }

        self.records.append(record)
        self.tree.insert("", tk.END, values=(formatted_date, temp, desc, "Да" if precip else "Нет"))

        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

        messagebox.showinfo("Успех", "Запись добавлена")

    def save_to_json(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def load_from_json(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.records = json.load(f)
            self.load_records_to_tree()
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))

    def load_records_to_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rec in self.records:
            self.tree.insert("", tk.END, values=(
                rec["date"],
                rec["temperature"],
                rec["description"],
                "Да" if rec["precipitation"] else "Нет"
            ))

    def apply_filter(self):
        date_filter = self.filter_date.get().strip()
        temp_filter = self.filter_temp.get().strip()

        filter_date_formatted = None
        if date_filter:
            try:
                dt = datetime.strptime(date_filter, "%d.%m.%Y")
                filter_date_formatted = dt.strftime("%d.%m.%Y")
            except ValueError:
                messagebox.showerror("Ошибка", "Дата фильтра должна быть в формате ДД.ММ.ГГГГ")
                return

        min_temp = None
        if temp_filter:
            try:
                min_temp = float(temp_filter)
            except ValueError:
                messagebox.showerror("Ошибка", "Температура фильтра должна быть числом")
                return

        filtered = []
        for rec in self.records:
            if filter_date_formatted and rec["date"] != filter_date_formatted:
                continue
            if min_temp is not None and rec["temperature"] <= min_temp:
                continue
            filtered.append(rec)

        for row in self.tree.get_children():
            self.tree.delete(row)
        for rec in filtered:
            self.tree.insert("", tk.END, values=(
                rec["date"],
                rec["temperature"],
                rec["description"],
                "Да" if rec["precipitation"] else "Нет"
            ))


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()