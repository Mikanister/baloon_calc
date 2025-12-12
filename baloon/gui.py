"""
Покращений GUI для калькулятора аеростатів
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any
import json
import os

# Lazy import для matplotlib (щоб працювало в exe)
_plt = None
def get_plt():
    global _plt
    if _plt is None:
        try:
            import matplotlib
            matplotlib.use('TkAgg')  # Встановлюємо backend перед імпортом pyplot
            import matplotlib.pyplot as plt
            _plt = plt
        except ImportError as e:
            import logging
            logging.error(f"Не вдалося імпортувати matplotlib: {e}")
            raise
    return _plt
try:
    from baloon.analysis import (
        calculate_height_profile,
        calculate_material_comparison,
        calculate_optimal_height,
        calculate_max_flight_time
    )
    from baloon.constants import *
    from baloon.calculations import calculate_balloon_parameters
    from baloon.validators import validate_all_inputs, ValidationError
    from baloon.labels import FIELD_LABELS, FIELD_TOOLTIPS, FIELD_DEFAULTS, COMBOBOX_VALUES, ABOUT_TEXT, BUTTON_LABELS, SECTION_LABELS, PERM_MULT_HINT
    from baloon.help_texts import HELP_FORMULAS, HELP_PARAMETERS, HELP_SAFETY, HELP_EXAMPLES, HELP_FAQ, ABOUT_TEXT_EXTENDED
except ImportError:
    # Для сумісності з локальними запусками
    from analysis import (
        calculate_height_profile,
        calculate_material_comparison,
        calculate_optimal_height,
        calculate_max_flight_time
    )
    from constants import *
    from calculations import calculate_balloon_parameters
    from validators import validate_all_inputs, ValidationError
    from labels import FIELD_LABELS, FIELD_TOOLTIPS, FIELD_DEFAULTS, COMBOBOX_VALUES, ABOUT_TEXT, BUTTON_LABELS, SECTION_LABELS, PERM_MULT_HINT
    from help_texts import HELP_FORMULAS, HELP_PARAMETERS, HELP_SAFETY, HELP_EXAMPLES, HELP_FAQ, ABOUT_TEXT_EXTENDED

import logging

logging.basicConfig(
    filename='balloon.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

class BalloonCalculatorGUI:
    """Головний клас GUI для калькулятора аеростатів"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Калькулятор аеростатів v2.0")
        self.root.geometry("650x750")
        self.root.minsize(600, 700)
        
        # Налаштування темної теми
        self.setup_dark_theme()
        
        # Змінна для теми
        self.dark_mode = True
        # Змінні
        self.mode_var = tk.StringVar(value="payload")
        self.material_var = tk.StringVar(value="TPU")
        self.gas_var = tk.StringVar(value="Гелій")
        self.material_density_var = tk.StringVar()
        self.result_var = tk.StringVar()
        # Віджети
        self.entries = {}
        self.labels = {}
        self.setup_ui()
        self.setup_bindings()
        self.load_settings()
        # Викликаємо update_fields для правильної початкової видимості полів
        self.update_fields()
    
    def setup_dark_theme(self):
        """Налаштування темної теми"""
        # Базова сучасна палітра
        style = ttk.Style()
        style.theme_use('clam')
        
        # Кольори для темної теми
        bg_color = "#2b2b2b"
        fg_color = "#ffffff"
        entry_bg = "#1e1e1e"
        select_bg = "#404040"
        accent = "#4a90e2"
        card_bg = "#303030"
        
        # Налаштування стилів
        default_font = ("Segoe UI", 10)
        self.root.option_add("*Font", default_font)
        
        style.configure('TFrame', background=bg_color)
        style.configure('Card.TFrame', background=card_bg, relief="ridge")
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('Heading.TLabel', background=bg_color, foreground=fg_color, font=("Segoe UI Semibold", 12))
        style.configure('Subheading.TLabel', background=bg_color, foreground=fg_color, font=("Segoe UI Semibold", 11))
        
        style.configure('TButton', background="#3a3a3a", foreground=fg_color, padding=6)
        style.map('TButton',
                  background=[('active', '#4b4b4b'), ('pressed', '#2f2f2f')])
        
        style.configure('Accent.TButton', background=accent, foreground="#ffffff", padding=7)
        style.map('Accent.TButton',
                  background=[('active', '#5aa1f3'), ('pressed', '#3b7ccc')])
        
        style.configure('TEntry', fieldbackground=entry_bg, foreground=fg_color,
                       bordercolor="#555555", insertcolor=fg_color, padding=4)
        style.configure('TCombobox', fieldbackground=entry_bg, foreground=fg_color,
                       bordercolor="#555555", arrowcolor=fg_color, padding=4)
        style.map('TCombobox',
                  fieldbackground=[('readonly', entry_bg), ('!disabled', entry_bg)],
                  foreground=[('readonly', fg_color), ('!disabled', fg_color)],
                  selectbackground=[('readonly', entry_bg)],
                  selectforeground=[('readonly', fg_color)],
                  background=[('readonly', entry_bg)])
        style.configure('TRadiobutton', background=bg_color, foreground=fg_color,
                       selectcolor=select_bg)
        style.configure('TSeparator', background="#555555")
        style.configure('TNotebook', background=bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', background="#404040", foreground=fg_color,
                       padding=[10, 5])
        style.map('TNotebook.Tab',
                  background=[('selected', bg_color)],
                  expand=[('selected', [1, 1, 1, 0])])
        
        # Налаштування фону головного вікна
        self.root.configure(bg=bg_color)
        
    def setup_ui(self):
        """Налаштування інтерфейсу"""
        main_frame = ttk.Frame(self.root, padding="12")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Сітка: хедер зверху на 2 колонки, під ним ліва колонка (форми) та права (результати)
        main_frame.columnconfigure(0, weight=1, uniform="cols")
        main_frame.columnconfigure(1, weight=1, uniform="cols")
        main_frame.rowconfigure(1, weight=1)
        
        header_frame = ttk.Frame(main_frame, style="Card.TFrame", padding="10")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        left_frame.columnconfigure(0, weight=1)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(6, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        mode_frame = ttk.Frame(left_frame, style="Card.TFrame", padding="12")
        mode_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        
        params_frame = ttk.Frame(left_frame, style="Card.TFrame", padding="12")
        params_frame.grid(row=1, column=0, sticky="ew", pady=4)
        
        buttons_frame = ttk.Frame(left_frame, style="Card.TFrame", padding="10")
        buttons_frame.grid(row=2, column=0, sticky="ew", pady=4)
        
        left_frame.rowconfigure(3, weight=1)
        
        results_frame = ttk.Frame(right_frame, style="Card.TFrame", padding="10")
        results_frame.grid(row=0, column=0, sticky="nsew")
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        
        self.create_header_section(header_frame)
        self.create_mode_section(mode_frame)
        self.create_input_section(params_frame)
        self.create_button_section(buttons_frame, 0)
        self.create_result_section(results_frame, 0)
        
    def create_mode_section(self, parent):
        """Створення секції вибору режиму"""
        row = 0
        parent.columnconfigure(1, weight=1)
        # Заголовок
        ttk.Label(parent, text=SECTION_LABELS['mode'], style="Heading.TLabel").grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(0, 5)
        )
        row += 1
        # Радіокнопки
        ttk.Radiobutton(
            parent, text="Обʼєм ➜ навантаження",
            variable=self.mode_var, value="payload",
            command=self.update_fields
        ).grid(row=row, column=1, sticky="w")
        row += 1
        ttk.Radiobutton(
            parent, text="Навантаження ➜ обʼєм",
            variable=self.mode_var, value="volume",
            command=self.update_fields
        ).grid(row=row, column=1, sticky="w")
        row += 1
        # Роздільник
        ttk.Separator(parent, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=10
        )
        row += 1
        return row
    
    def create_header_section(self, parent):
        """Хедер із швидким доступом до довідки та інформації"""
        parent.columnconfigure(0, weight=1)
        ttk.Label(parent, text="Калькулятор аеростатів v2.0", style="Heading.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        btn_frame = ttk.Frame(parent, style="Card.TFrame")
        btn_frame.grid(row=0, column=1, sticky="e")
        ttk.Button(btn_frame, text=BUTTON_LABELS['help'], command=self.show_help).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text=BUTTON_LABELS['about'], command=self.show_about).pack(side="left")
        
    def _add_entry_row(self, parent, key: str, label_text: str, row: int, default=None, **entry_kwargs) -> int:
        """Створити рядок Label + Entry та повернути наступний row"""
        self.labels[key] = ttk.Label(parent, text=label_text)
        self.labels[key].grid(row=row, column=0, sticky="w")
        entry = ttk.Entry(parent, **entry_kwargs)
        if default is not None:
            entry.insert(0, default)
        entry.grid(row=row, column=1, sticky="ew", padx=(10, 0))
        self.entries[key] = entry
        return row + 1
    
    def _add_combo_row(self, parent, key: str, label_text: str, row: int, values, textvariable=None) -> int:
        """Створити рядок Label + Combobox та повернути наступний row"""
        self.labels[key] = ttk.Label(parent, text=label_text)
        self.labels[key].grid(row=row, column=0, sticky="w")
        combo = ttk.Combobox(
            parent,
            textvariable=textvariable,
            values=values,
            state="readonly"
        )
        combo.grid(row=row, column=1, sticky="ew", padx=(10, 0))
        self.entries[key] = combo
        return row + 1
        
    def create_input_section(self, parent):
        """Створення секції введення даних"""
        row = 0
        parent.columnconfigure(1, weight=1)
        # Заголовок
        ttk.Label(parent, text=SECTION_LABELS['params'], style="Heading.TLabel").grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(0, 5)
        )
        row += 1
        # Поля - спочатку об'єм газу
        row = self._add_entry_row(parent, 'gas_volume', FIELD_LABELS['gas_volume'], row, FIELD_DEFAULTS['gas_volume'])
        
        # Температури (тільки для гарячого повітря)
        self.labels['ground_temp'] = ttk.Label(parent, text=FIELD_LABELS['ground_temp'])
        self.entries['ground_temp'] = ttk.Entry(parent)
        self.entries['ground_temp'].insert(0, FIELD_DEFAULTS['ground_temp'])
        # Не додаємо до grid одразу - буде показуватися тільки для гарячого повітря
        
        self.labels['inside_temp'] = ttk.Label(parent, text=FIELD_LABELS['inside_temp'])
        self.entries['inside_temp'] = ttk.Entry(parent)
        self.entries['inside_temp'].insert(0, FIELD_DEFAULTS['inside_temp'])
        # Не додаємо до grid одразу - буде показуватися тільки для гарячого повітря
        # Запам'ятовуємо базовий рядок для температур і резервуємо місце
        self.temp_row_base = row
        row += 2  # резервуємо два рядки під температури, навіть якщо вони приховані
        
        # Навантаження (залежить від режиму)
        self.labels['payload'] = ttk.Label(parent, text=FIELD_LABELS['payload'])
        self.entries['payload'] = ttk.Entry(parent)
        self.entries['payload'].insert(0, FIELD_DEFAULTS['payload'])
        
        row = self._add_combo_row(
            parent=parent,
            key='material',
            label_text="Матеріал оболонки",
            row=row,
            values=list(MATERIALS.keys()),
            textvariable=self.material_var
        )
        # density з текстовою змінною, лише для читання
        self.labels['density'] = ttk.Label(parent, text=FIELD_LABELS['density'])
        self.labels['density'].grid(row=row, column=0, sticky="w")
        self.entries['density'] = ttk.Entry(parent, textvariable=self.material_density_var, state="readonly")
        self.entries['density'].grid(row=row, column=1, sticky="ew", padx=(10, 0))
        row += 1
        row = self._add_entry_row(parent, 'thickness', FIELD_LABELS['thickness'], row, FIELD_DEFAULTS['thickness'])
        row = self._add_entry_row(parent, 'start_height', FIELD_LABELS['start_height'], row, FIELD_DEFAULTS['start_height'])
        row = self._add_entry_row(parent, 'work_height', FIELD_LABELS['work_height'], row, FIELD_DEFAULTS['work_height'])
        row = self._add_combo_row(
            parent=parent,
            key='gas',
            label_text="Газ",
            row=row,
            values=list(GAS_DENSITY.keys()),
            textvariable=self.gas_var
        )
        row = self._add_entry_row(parent, 'duration', FIELD_LABELS['duration'], row, FIELD_DEFAULTS['duration'])
        row = self._add_entry_row(parent, 'perm_mult', FIELD_LABELS['perm_mult'], row, FIELD_DEFAULTS['perm_mult'], width=8)
        perm_mult_hint = ttk.Label(parent, text=PERM_MULT_HINT, font=("Segoe UI", 9), foreground="#4a90e2")
        perm_mult_hint.grid(row=row, column=0, columnspan=2, sticky="w", pady=(2, 16))
        row += 2
        return row
        
    def create_button_section(self, parent, row):
        """Створення секції кнопок"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")
        
        # Перший рядок кнопок
        row1_frame = ttk.Frame(button_frame)
        row1_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Button(
            row1_frame, text=BUTTON_LABELS['calculate'],
            command=self.calculate, style="Accent.TButton"
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            row1_frame, text=BUTTON_LABELS['show_graph'],
            command=self.show_graph
        ).pack(side="left", padx=(0, 10))
        
        # Другий рядок кнопок
        row2_frame = ttk.Frame(button_frame)
        row2_frame.pack(fill="x")
        
        ttk.Button(
            row2_frame, text=BUTTON_LABELS['save_settings'],
            command=self.save_settings
        ).pack(side="left", padx=(0, 10))
        # about/help винесені у хедер
        
        row += 1
        return row
        
    def create_result_section(self, parent, row):
        """Створення секції результатів"""
        ttk.Label(parent, text=SECTION_LABELS['results'], font=("Arial", 12, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(0, 5)
        )
        row += 1
        
        self.status_label = ttk.Label(parent, text="Статус: очікує результат", foreground="#4a90e2")
        self.status_label.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 6))
        row += 1
        
        # Створюємо Frame для результатів з прокруткою
        result_frame = ttk.Frame(parent)
        result_frame.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=5)
        parent.rowconfigure(row, weight=1, minsize=260)
        
        # Text widget для результатів з можливістю кольорового форматування
        result_text = tk.Text(
            result_frame, 
            wrap="word",
            font=("Courier New", 11),
            bg="#1e1e1e",
            fg="#ffffff",
            relief="sunken",
            borderwidth=2,
            padx=10,
            pady=10,
            state="disabled"
        )
        result_text.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=result_text.yview)
        scrollbar.pack(side="right", fill="y")
        result_text.configure(yscrollcommand=scrollbar.set)
        
        # Зберігаємо посилання на text widget
        self.result_text_widget = result_text
        
    def setup_bindings(self):
        """Налаштування прив'язок подій"""
        self.add_tooltips()
        self.material_var.trace_add("write", self.update_density)
        self.gas_var.trace_add("write", self.update_fields)
        self.mode_var.trace_add("write", self.update_fields)
        
        # Валідація в реальному часі для числових полів
        numeric_fields = ['thickness', 'start_height', 'work_height', 'ground_temp', 
                         'inside_temp', 'duration', 'payload', 'gas_volume', 'perm_mult']
        for field in numeric_fields:
            if field in self.entries:
                self.entries[field].bind('<KeyRelease>', lambda e, f=field: self.validate_field(f))
                self.entries[field].bind('<FocusOut>', lambda e, f=field: self.validate_field(f))
        
        # Початкова ініціалізація
        self.update_density()
        self.update_fields()
    
    def validate_field(self, field_name):
        """Валідація поля в реальному часі"""
        if field_name not in self.entries:
            return
        
        entry = self.entries[field_name]
        value = entry.get()
        
        # Скидаємо колір
        entry.configure(style='TEntry')
        
        if not value:
            return
        
        try:
            float(value)
            # Валідація додаткових обмежень
            if field_name == 'thickness':
                if not (1 <= float(value) <= 1000):
                    entry.configure(style='Invalid.TEntry')
            elif field_name in ['start_height', 'work_height']:
                if float(value) < 0:
                    entry.configure(style='Invalid.TEntry')
            elif field_name == 'ground_temp':
                if not (-50 <= float(value) <= 50):
                    entry.configure(style='Invalid.TEntry')
            elif field_name == 'inside_temp':
                if not (0 <= float(value) <= 500):
                    entry.configure(style='Invalid.TEntry')
        except ValueError:
            entry.configure(style='Invalid.TEntry')
        
        # Налаштування стилю для невалідних значень
        try:
            style = ttk.Style()
            style.configure('Invalid.TEntry', fieldbackground='#ffcccc')
        except:
            pass
        
    def update_density(self, *args):
        """Оновлення щільності при зміні матеріалу"""
        mat = self.material_var.get()
        if mat in MATERIALS:
            self.material_density_var.set(str(MATERIALS[mat][0]))
            
    def update_fields(self, *args):
        """Оновлення видимості полів"""
        gas = self.gas_var.get()
        hot_air = gas == "Гаряче повітря"
        is_payload_mode = self.mode_var.get() == "payload"
        
        # Поля температури тільки для гарячого повітря
        current_row = getattr(self, "temp_row_base", 5)  # Після gas_volume (row=4)
        if hot_air:
            self.labels['ground_temp'].grid(row=current_row, column=0, sticky="w")
            self.entries['ground_temp'].grid(row=current_row, column=1, sticky="ew", padx=(10, 0))
            current_row += 1
            self.labels['inside_temp'].grid(row=current_row, column=0, sticky="w")
            self.entries['inside_temp'].grid(row=current_row, column=1, sticky="ew", padx=(10, 0))
            current_row += 1
        else:
            self.labels['ground_temp'].grid_remove()
            self.entries['ground_temp'].grid_remove()
            self.labels['inside_temp'].grid_remove()
            self.entries['inside_temp'].grid_remove()
            
        # Поле payload показується/приховується залежно від режиму
        if is_payload_mode:
            self.labels['payload'].grid_remove()
            self.entries['payload'].grid_remove()
        else:
            self.labels['payload'].grid(row=current_row, column=0, sticky="w")
            self.entries['payload'].grid(row=current_row, column=1, sticky="ew", padx=(10, 0))
            
    def calculate(self):
        """Виконання розрахунків"""
        try:
            logging.info("Початок розрахунку. Вхідні дані: %s", {k: v.get() if hasattr(v, 'get') else v for k, v in self.entries.items()})
            # Збір даних з полів
            # Отримуємо gas_volume залежно від режиму
            if self.mode_var.get() == "payload":
                gas_volume_val = self.entries['gas_volume'].get()
            else:
                gas_volume_val = self.entries['payload'].get()
            
            # Для не-гарячого повітря використовуємо значення за замовчуванням
            gas_type = self.gas_var.get()
            if gas_type == "Гаряче повітря":
                ground_temp_val = self.entries['ground_temp'].get()
                inside_temp_val = self.entries['inside_temp'].get()
            else:
                # Для гелію/водню використовуємо стандартні значення
                ground_temp_val = FIELD_DEFAULTS['ground_temp']
                inside_temp_val = FIELD_DEFAULTS['ground_temp']  # Для гелію/водню температура всередині = зовнішня
            
            inputs = {
                'gas_type': gas_type,
                'gas_volume': gas_volume_val,
                'material': self.material_var.get(),
                'thickness': self.entries['thickness'].get(),
                'start_height': self.entries['start_height'].get(),
                'work_height': self.entries['work_height'].get(),
                'ground_temp': ground_temp_val,
                'inside_temp': inside_temp_val,
                'duration': self.entries['duration'].get(),
                'mode': self.mode_var.get()
            }
            perm_mult_str = self.entries['perm_mult'].get()
            try:
                perm_mult = float(perm_mult_str)
                if perm_mult <= 0:
                    raise ValueError
            except Exception:
                raise ValidationError("Множник проникності має бути додатним числом")
            # Валідація
            validated_numbers, validated_strings = validate_all_inputs(**inputs)
            # Розрахунки
            results = calculate_balloon_parameters(
                gas_type=validated_strings['gas_type'],
                gas_volume=validated_numbers['gas_volume'],
                material=validated_strings['material'],
                thickness_mm=validated_numbers['thickness'],
                start_height=validated_numbers['start_height'],
                work_height=validated_numbers['work_height'],
                ground_temp=validated_numbers['ground_temp'],
                inside_temp=validated_numbers['inside_temp'],
                duration=validated_numbers['duration'],
                perm_mult=perm_mult,
                mode=validated_strings['mode']
            )
            
            # Розрахунок максимального часу польоту для гелію/водню
            if validated_strings['gas_type'] in ("Гелій", "Водень"):
                try:
                    flight_time_info = calculate_max_flight_time(
                        gas_type=validated_strings['gas_type'],
                        material=validated_strings['material'],
                        thickness_mm=validated_numbers['thickness'],
                        gas_volume=validated_numbers['gas_volume'],
                        start_height=validated_numbers['start_height'],
                        work_height=validated_numbers['work_height'],
                        ground_temp=validated_numbers['ground_temp'],
                        inside_temp=validated_numbers['inside_temp'],
                        perm_mult=perm_mult
                    )
                    results['flight_time_info'] = flight_time_info
                except Exception as e:
                    logging.warning(f"Помилка розрахунку часу польоту: {e}")
                    results['flight_time_info'] = None
            
            self.format_results(results, validated_strings['mode'])
            logging.info("Розрахунок успішно завершено.")
        except ValidationError as e:
            logging.warning("Помилка валідації: %s", str(e))
            messagebox.showerror("Помилка валідації", str(e))
        except Exception as e:
            logging.error("Помилка розрахунку: %s", str(e), exc_info=True)
            messagebox.showerror("Помилка розрахунку", str(e))
            
    def format_results(self, results: Dict[str, Any], mode: str):
        """Форматування результатів для відображення з кольоровим кодуванням"""
        # Налаштування кольорів
        normal_color = "#ffffff"
        warning_color = "#ffaa00"
        error_color = "#ff4444"
        success_color = "#44ff44"
        header_color = "#4a9eff"
        
        # Очищаємо попередні результати
        self.result_text_widget.config(state="normal")
        self.result_text_widget.delete(1.0, tk.END)
        
        # Встановлюємо ширину для підпису та значення
        label_width = 32
        value_width = 10
        def fmt(label, value, unit=""):
            return f"{label:<{label_width}} {value:>{value_width}} {unit}".rstrip()
        
        def add_line(text, color=normal_color, bold=False):
            """Додає рядок з кольором"""
            self.result_text_widget.insert(tk.END, text + "\n", color)
            if bold:
                # Встановлюємо жирний шрифт для останнього рядка
                start = self.result_text_widget.index(f"end-{len(text)+2}c")
                end = self.result_text_widget.index("end-1c")
                self.result_text_widget.tag_add("bold", start, end)
        
        # Налаштування тегів для кольорів
        self.result_text_widget.tag_config(normal_color, foreground=normal_color)
        self.result_text_widget.tag_config(warning_color, foreground=warning_color)
        self.result_text_widget.tag_config(error_color, foreground=error_color)
        self.result_text_widget.tag_config(success_color, foreground=success_color)
        self.result_text_widget.tag_config(header_color, foreground=header_color)
        self.result_text_widget.tag_config("bold", font=("Courier New", 10, "bold"))
        
        # Заголовок
        add_line("=" * 60, header_color, True)
        add_line("РЕЗУЛЬТАТИ РОЗРАХУНКУ", header_color, True)
        add_line("=" * 60, header_color, True)
        add_line("", normal_color)
        
        # Основні параметри
        if mode == "volume":
            add_line(fmt("Потрібний обʼєм газу:", f"{results['gas_volume']:.2f}", "м³"), normal_color)
        
        add_line(fmt("Необхідний обʼєм кулі:", f"{results['required_volume']:.2f}", "м³"), normal_color)
        add_line(fmt("Корисне навантаження (старт):", f"{results['payload']:.2f}", "кг"), 
                success_color if results['payload'] > 0 else error_color)
        add_line(fmt("Маса оболонки:", f"{results['mass_shell']:.2f}", "кг"), normal_color)
        add_line(fmt("Підйомна сила (старт):", f"{results['lift']:.2f}", "кг"), normal_color)
        add_line(fmt("Радіус кулі:", f"{results['radius']:.2f}", "м"), normal_color)
        add_line(fmt("Площа поверхні:", f"{results['surface_area']:.2f}", "м²"), normal_color)
        add_line(fmt("Щільність повітря:", f"{results['rho_air']:.4f}", "кг/м³"), normal_color)
        add_line(fmt("Підйомна сила на м³:", f"{results['net_lift_per_m3']:.4f}", "кг/м³"), normal_color)
        
        # Втрати газу для гелію/водню
        if self.gas_var.get() in ("Гелій", "Водень"):
            add_line("", normal_color)
            add_line("─" * 60, header_color)
            add_line("АНАЛІЗ ВТРАТ ГАЗУ", header_color, True)
            add_line("─" * 60, header_color)
            add_line(fmt("Втрати газу за політ:", f"{results['gas_loss']:.6f}", "м³"), 
                    warning_color if results['gas_loss'] > 0.1 else normal_color)
            if results['gas_loss'] < 0.01:
                add_line("Втрати газу дуже малі для цих параметрів (менше 0.01 м³)", normal_color)
            add_line(fmt("Обʼєм газу в кінці:", f"{results['final_gas_volume']:.2f}", "м³"), normal_color)
            add_line(fmt("Підйомна сила (кінець):", f"{results['lift_end']:.2f}", "кг"), normal_color)
            payload_end_color = success_color if results['payload_end'] > 0 else error_color
            add_line(fmt("Корисне навантаження (кінець):", f"{results['payload_end']:.2f}", "кг"), payload_end_color)
            if results['payload_end'] < 0:
                add_line("⚠️  УВАГА: Куля втратить підйомну силу до кінця польоту!", error_color, True)
            
            # Інформація про максимальний час польоту
            if 'flight_time_info' in results and results['flight_time_info']:
                flight_info = results['flight_time_info']
                add_line("", normal_color)
                add_line("─" * 60, header_color)
                add_line("ЧАС ПОЛЬОТУ", header_color, True)
                add_line("─" * 60, header_color)
                if flight_info.get('max_time_hours') == float('inf'):
                    add_line("Час польоту не обмежений втратами газу", success_color)
                else:
                    max_time = flight_info.get('max_time_hours', 0)
                    time_to_zero = flight_info.get('time_to_zero_payload', 0)
                    loss_rate = flight_info.get('gas_loss_rate_per_hour', 0)
                    
                    if max_time > 0:
                        add_line(fmt("Макс. час польоту:", f"{max_time:.1f}", "год"), 
                                success_color if max_time >= 24 else warning_color)
                        add_line(fmt("Макс. час польоту:", f"{max_time/24:.1f}", "днів"), 
                                success_color if max_time >= 24 else warning_color)
                    
                    if time_to_zero > 0 and time_to_zero != float('inf'):
                        add_line(fmt("Час до нульового навантаження:", f"{time_to_zero:.1f}", "год"), warning_color)
                        add_line(fmt("Час до нульового навантаження:", f"{time_to_zero/24:.1f}", "днів"), warning_color)
                    
                    if loss_rate > 0:
                        add_line(fmt("Втрати газу за годину:", f"{loss_rate:.6f}", "м³/год"), normal_color)
        
        # Аналіз безпеки для гарячого повітря
        if self.gas_var.get() == "Гаряче повітря":
            add_line("", normal_color)
            add_line("─" * 60, header_color)
            add_line("АНАЛІЗ БЕЗПЕКИ", header_color, True)
            add_line("─" * 60, header_color)
            add_line(fmt("T зовні:", f"{results['T_outside_C']:.1f}", "°C"), normal_color)
            add_line(fmt("Макс. напруга:", f"{results['stress'] / 1e6:.2f}", "МПа"), normal_color)
            add_line(fmt("Допустима напруга:", f"{results['stress_limit'] / 1e6:.1f}", "МПа"), normal_color)
            
            # Розрахунок коефіцієнта безпеки
            if results['stress'] > 0:
                safety_factor = results['stress_limit'] / results['stress']
                safety_color = success_color if safety_factor >= 2 else (warning_color if safety_factor >= 1.5 else error_color)
                safety_text = f"Коефіцієнт безпеки: {safety_factor:.2f}"
                if safety_factor < 1.5:
                    safety_text += " ⚠️ КРИТИЧНО НИЗЬКИЙ!"
                elif safety_factor < 2:
                    safety_text += " ⚠️ Низький (рекомендується ≥ 2)"
                else:
                    safety_text += " ✅ Безпечний"
                add_line(safety_text, safety_color, True)
            else:
                add_line("✅ Коефіцієнт безпеки: ∞ (дуже високий, напруга ≈ 0)", success_color, True)
        
        # Загальний аналіз безпеки
        add_line("", normal_color)
        add_line("─" * 60, header_color)
        add_line("ЗАГАЛЬНА ОЦІНКА", header_color, True)
        add_line("─" * 60, header_color)
        
        # Перевірка критичних параметрів
        warnings = []
        errors = []
        
        if results['payload'] <= 0:
            errors.append("Корисне навантаження від'ємне або нульове")
        elif results['payload'] < 0.1:
            warnings.append("Дуже мале навантаження (< 0.1 кг)")
        
        if self.gas_var.get() in ("Гелій", "Водень") and results['payload_end'] < 0:
            errors.append("Втрата підйомної сили до кінця польоту")
        
        if self.gas_var.get() == "Гаряче повітря" and results['stress'] > 0:
            safety_factor = results['stress_limit'] / results['stress']
            if safety_factor < 1.5:
                errors.append(f"Критично низький коефіцієнт безпеки ({safety_factor:.2f})")
            elif safety_factor < 2:
                warnings.append(f"Низький коефіцієнт безпеки ({safety_factor:.2f})")
        
        if errors:
            for error in errors:
                add_line(f"❌ ПОМИЛКА: {error}", error_color, True)
        if warnings:
            for warning in warnings:
                add_line(f"⚠️  ПОПЕРЕДЖЕННЯ: {warning}", warning_color)
        
        if not errors and not warnings:
            add_line("✅ Всі параметри в межах безпеки", success_color, True)
        
        # Оновити статус-бейдж
        if hasattr(self, 'status_label'):
            if errors:
                self.status_label.config(text="Статус: критично", foreground="#ff6b6b")
            elif warnings:
                self.status_label.config(text="Статус: попередження", foreground="#ffcc66")
            else:
                self.status_label.config(text="Статус: все ок", foreground="#66d17c")
        
        self.result_text_widget.config(state="disabled")
        
    def save_settings(self):
        """Збереження налаштувань"""
        settings = {
            'mode': self.mode_var.get(),
            'material': self.material_var.get(),
            'gas': self.gas_var.get(),
            'thickness': self.entries['thickness'].get(),
            'start_height': self.entries['start_height'].get(),
            'work_height': self.entries['work_height'].get(),
            'ground_temp': self.entries['ground_temp'].get(),
            'inside_temp': self.entries['inside_temp'].get(),
            'payload': self.entries['payload'].get(),
            'gas_volume': self.entries['gas_volume'].get(),
            'perm_mult': self.entries['perm_mult'].get()
        }
        
        try:
            with open('balloon_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            logging.info("Налаштування збережено: %s", settings)
            messagebox.showinfo("Успіх", "Налаштування збережено")
        except Exception as e:
            logging.error("Не вдалося зберегти налаштування: %s", str(e), exc_info=True)
            messagebox.showerror("Помилка", f"Не вдалося зберегти налаштування: {e}")
            
    def load_settings(self):
        """Завантаження налаштувань"""
        try:
            if os.path.exists('balloon_settings.json'):
                with open('balloon_settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                logging.info("Завантажено налаштування: %s", settings)
                
                # Встановлення значень
                self.mode_var.set(settings.get('mode', 'payload'))
                self.material_var.set(settings.get('material', 'TPU'))
                self.gas_var.set(settings.get('gas', 'Гелій'))
                
                if 'thickness' in settings:
                    self.entries['thickness'].delete(0, tk.END)
                    self.entries['thickness'].insert(0, settings['thickness'])
                    
                if 'start_height' in settings:
                    self.entries['start_height'].delete(0, tk.END)
                    self.entries['start_height'].insert(0, settings['start_height'])
                    
                if 'work_height' in settings:
                    self.entries['work_height'].delete(0, tk.END)
                    self.entries['work_height'].insert(0, settings['work_height'])
                    
                if 'ground_temp' in settings:
                    self.entries['ground_temp'].delete(0, tk.END)
                    self.entries['ground_temp'].insert(0, settings['ground_temp'])
                    
                if 'inside_temp' in settings:
                    self.entries['inside_temp'].delete(0, tk.END)
                    self.entries['inside_temp'].insert(0, settings['inside_temp'])
                    
                if 'payload' in settings:
                    self.entries['payload'].delete(0, tk.END)
                    self.entries['payload'].insert(0, settings['payload'])
                    
                if 'gas_volume' in settings:
                    self.entries['gas_volume'].delete(0, tk.END)
                    self.entries['gas_volume'].insert(0, settings['gas_volume'])
                    
                if 'perm_mult' in settings:
                    self.entries['perm_mult'].set(settings['perm_mult'])
                    
        except Exception as e:
            logging.error("Помилка завантаження налаштувань: %s", str(e), exc_info=True)
            print(f"Помилка завантаження налаштувань: {e}")
            
    def clear_fields(self):
        """Очищення всіх полів"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.entries['thickness'].insert(0, FIELD_DEFAULTS['thickness'])
        self.entries['start_height'].insert(0, FIELD_DEFAULTS['start_height'])
        self.entries['work_height'].insert(0, FIELD_DEFAULTS['work_height'])
        self.entries['ground_temp'].insert(0, FIELD_DEFAULTS['ground_temp'])
        self.entries['inside_temp'].insert(0, FIELD_DEFAULTS['inside_temp'])
        self.entries['payload'].insert(0, FIELD_DEFAULTS['payload'])
        self.entries['gas_volume'].insert(0, FIELD_DEFAULTS['gas_volume'])
        self.entries['perm_mult'].set(FIELD_DEFAULTS['perm_mult'])
        
        # Очищаємо результати
        if hasattr(self, 'result_text_widget'):
            self.result_text_widget.config(state="normal")
            self.result_text_widget.delete(1.0, tk.END)
            self.result_text_widget.config(state="disabled")
        
    def run(self):
        """Запуск додатку"""
        self.root.mainloop()

    def show_graph(self):
        """Показати покращений графік залежності параметрів від висоти"""
        try:
            # Валідація перед побудовою графіка
            inputs = {
                'gas_type': self.gas_var.get(),
                'gas_volume': self.entries['gas_volume' if self.mode_var.get() == "payload" else 'payload'].get(),
                'material': self.material_var.get(),
                'thickness': self.entries['thickness'].get(),
                'start_height': self.entries['start_height'].get(),
                'work_height': self.entries['work_height'].get(),
                'ground_temp': self.entries['ground_temp'].get() if self.gas_var.get() == "Гаряче повітря" else "15",
                'inside_temp': self.entries['inside_temp'].get() if self.gas_var.get() == "Гаряче повітря" else "100",
                'mode': self.mode_var.get()
            }
            # Валідація вхідних даних
            validated_numbers, validated_strings = validate_all_inputs(**inputs)
            
            # Збір даних для графіка
            graph_inputs = {
                'gas_type': validated_strings['gas_type'],
                'material': validated_strings['material'],
                'thickness_mm': validated_numbers['thickness'],
                'gas_volume': validated_numbers['gas_volume'],
                'ground_temp': validated_numbers['ground_temp'],
                'inside_temp': validated_numbers['inside_temp'],
                'max_height': 10000  # Збільшено до 10 км
            }
            profile = calculate_height_profile(**graph_inputs)
            heights = [p['height'] for p in profile]
            payloads = [p['payload'] for p in profile]
            lifts = [p['lift'] for p in profile]
            net_lifts = [p['net_lift_per_m3'] for p in profile]
            volumes = [p.get('required_volume', 0) for p in profile]
            # Пошук ключових точок
            zero_payload_height = next((h for h, p in zip(heights, payloads) if p <= 0), None)
            payload_max = max(payloads) if payloads else None
            payload_max_h = heights[payloads.index(payload_max)] if payload_max is not None else None

            # Створюємо subplots для кращої візуалізації
            plt = get_plt()
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle('Залежність параметрів аеростата від висоти', fontsize=14, fontweight='bold')
            
            # Графік 1: Навантаження та підйомна сила
            ax1 = axes[0, 0]
            ax1.plot(heights, payloads, 'b-', label='Корисне навантаження (кг)', linewidth=2)
            ax1.plot(heights, lifts, 'g-', label='Підйомна сила (кг)', linewidth=2)
            ax1.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Нульове навантаження')
            # Маркери ключових точок
            if payload_max is not None:
                ax1.plot(payload_max_h, payload_max, 'bo')
                ax1.annotate(f"max {payload_max:.1f} кг", xy=(payload_max_h, payload_max),
                             xytext=(payload_max_h, payload_max + 1),
                             arrowprops=dict(arrowstyle="->", color='blue'), color='blue')
            if zero_payload_height is not None:
                ax1.plot(zero_payload_height, 0, 'ro')
                ax1.annotate(f"0 кг @ {zero_payload_height} м", xy=(zero_payload_height, 0),
                             xytext=(zero_payload_height, max(payloads)*0.1 if payloads else 1),
                             arrowprops=dict(arrowstyle="->", color='red'), color='red')
            ax1.set_xlabel('Висота, м')
            ax1.set_ylabel('Маса, кг')
            ax1.set_title('Навантаження та підйомна сила')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Графік 2: Підйомна сила на м³
            ax2 = axes[0, 1]
            ax2.plot(heights, net_lifts, 'm-', label='Підйомна сила на м³', linewidth=2)
            target_net = 0.5
            ax2.axhline(y=target_net, color='orange', linestyle='--', alpha=0.6, label='Орієнтир 0.5 кг/м³')
            ax2.set_xlabel('Висота, м')
            ax2.set_ylabel('Підйомна сила, кг/м³')
            ax2.set_title('Підйомна сила на одиницю об\'єму')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Графік 3: Об'єм кулі
            ax3 = axes[1, 0]
            ax3.plot(heights, volumes, 'c-', label='Об\'єм кулі', linewidth=2)
            ax3.set_xlabel('Висота, м')
            ax3.set_ylabel('Об\'єм, м³')
            ax3.set_title('Зміна об\'єму кулі з висотою')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # Графік 4: Комбінований
            ax4 = axes[1, 1]
            ax4_twin = ax4.twinx()
            line1 = ax4.plot(heights, payloads, 'b-', label='Навантаження (кг)', linewidth=2)
            line2 = ax4_twin.plot(heights, volumes, 'r-', label='Об\'єм (м³)', linewidth=2)
            ax4.set_xlabel('Висота, м')
            ax4.set_ylabel('Навантаження, кг', color='b')
            ax4_twin.set_ylabel('Об\'єм, м³', color='r')
            ax4.set_title('Навантаження та об\'єм')
            ax4.tick_params(axis='y', labelcolor='b')
            ax4_twin.tick_params(axis='y', labelcolor='r')
            ax4.spines['left'].set_color('b')
            ax4.spines['right'].set_color('r')
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax4.legend(lines, labels, loc='upper left', framealpha=0.9)
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Помилка графіка", str(e))
    
    def show_material_comparison(self):
        """Показати порівняння матеріалів"""
        try:
            # Завжди читаємо актуальні дані з полів
            logging.info("Порівняння матеріалів: читання даних з полів")
            
            # Отримуємо gas_volume залежно від режиму
            mode = self.mode_var.get()
            if mode == "payload":
                gas_volume_val = self.entries['gas_volume'].get()
            else:
                # Якщо режим "volume", то gas_volume розраховується з payload
                # Спочатку валідуємо дані для розрахунку об'єму
                payload_val = self.entries['payload'].get()
                if not payload_val or float(payload_val) <= 0:
                    messagebox.showerror("Помилка", "Введіть коректне навантаження для розрахунку об'єму")
                    return
                
                # Використовуємо поточний матеріал для попереднього розрахунку об'єму
                # (потім цей об'єм використаємо для порівняння всіх матеріалів)
                try:
                    temp_inputs = {
                        'gas_type': self.gas_var.get(),
                        'gas_volume': payload_val,  # Тимчасово передаємо навантаження як gas_volume
                        'material': self.material_var.get(),
                        'thickness': self.entries['thickness'].get(),
                        'start_height': self.entries['start_height'].get(),
                        'work_height': self.entries['work_height'].get(),
                        'ground_temp': FIELD_DEFAULTS['ground_temp'] if self.gas_var.get() != "Гаряче повітря" else self.entries['ground_temp'].get(),
                        'inside_temp': FIELD_DEFAULTS['ground_temp'] if self.gas_var.get() != "Гаряче повітря" else self.entries['inside_temp'].get(),
                        'mode': 'volume'
                    }
                    temp_validated, _ = validate_all_inputs(**temp_inputs)
                    
                    # Розраховуємо об'єм з навантаження використовуючи поточний матеріал
                    temp_result = calculate_balloon_parameters(
                        gas_type=temp_inputs['gas_type'],
                        gas_volume=temp_validated['gas_volume'],
                        material=temp_inputs['material'],
                        thickness_mm=temp_validated['thickness'],
                        start_height=temp_validated['start_height'],
                        work_height=temp_validated['work_height'],
                        ground_temp=temp_validated['ground_temp'],
                        inside_temp=temp_validated['inside_temp'],
                        mode='volume'
                    )
                    # Отримуємо об'єм газу з результату
                    gas_volume_val = str(temp_result.get('gas_volume', payload_val))
                    logging.info(f"Порівняння матеріалів: розраховано об'єм {gas_volume_val} м³ з навантаження {payload_val} кг")
                except Exception as e:
                    logging.error(f"Помилка розрахунку об'єму з навантаження: {e}")
                    messagebox.showerror("Помилка", f"Не вдалося розрахувати об'єм з навантаження: {e}")
                    return
            
            # Для не-гарячого повітря використовуємо значення за замовчуванням
            gas_type = self.gas_var.get()
            if gas_type == "Гаряче повітря":
                ground_temp_val = self.entries['ground_temp'].get()
                inside_temp_val = self.entries['inside_temp'].get()
            else:
                ground_temp_val = FIELD_DEFAULTS['ground_temp']
                inside_temp_val = FIELD_DEFAULTS['ground_temp']
            
            # Читаємо всі дані з полів
            inputs = {
                'gas_type': gas_type,
                'gas_volume': gas_volume_val,
                'material': self.material_var.get(),  # Потрібен для валідації, хоча не використовується в порівнянні
                'thickness': self.entries['thickness'].get(),
                'start_height': self.entries['start_height'].get(),
                'work_height': self.entries['work_height'].get(),
                'ground_temp': ground_temp_val,
                'inside_temp': inside_temp_val,
            }
            
            logging.info(f"Порівняння матеріалів: вхідні дані: {inputs}")
            validated_numbers, validated_strings = validate_all_inputs(**inputs)
            logging.info(f"Порівняння матеріалів: валідовані дані: {validated_numbers}, {validated_strings}")
            
            total_height = validated_numbers['start_height'] + validated_numbers['work_height']
            
            logging.info(f"Порівняння матеріалів: виклик calculate_material_comparison з gas_volume={validated_numbers['gas_volume']}, height={total_height}")
            comparison = calculate_material_comparison(
                gas_type=validated_strings['gas_type'],
                thickness_mm=validated_numbers['thickness'],
                gas_volume=validated_numbers['gas_volume'],
                ground_temp=validated_numbers['ground_temp'],
                inside_temp=validated_numbers['inside_temp'],
                height=total_height
            )
            logging.info(f"Порівняння матеріалів: отримано результатів: {len(comparison)}")
            
            # Закриваємо попереднє вікно, якщо воно існує
            if hasattr(self, '_material_comparison_window') and self._material_comparison_window.winfo_exists():
                self._material_comparison_window.destroy()
            
            # Створюємо нове вікно з результатами
            comp_window = tk.Toplevel(self.root)
            self._material_comparison_window = comp_window  # Зберігаємо посилання
            comp_window.title("Порівняння матеріалів")
            comp_window.geometry("800x600")
            
            # Створюємо Treeview для таблиці
            tree = ttk.Treeview(comp_window, columns=('Матеріал', 'Навантаження', 'Маса оболонки', 'Підйомна сила', 'Коеф. безпеки'), show='headings')
            tree.heading('Матеріал', text='Матеріал')
            tree.heading('Навантаження', text='Навантаження (кг)')
            tree.heading('Маса оболонки', text='Маса оболонки (кг)')
            tree.heading('Підйомна сила', text='Підйомна сила (кг)')
            tree.heading('Коеф. безпеки', text='Коеф. безпеки')
            
            tree.column('Матеріал', width=120)
            tree.column('Навантаження', width=120)
            tree.column('Маса оболонки', width=120)
            tree.column('Підйомна сила', width=120)
            tree.column('Коеф. безпеки', width=120)
            
            # Сортуємо за навантаженням
            sorted_materials = sorted(comparison.items(), key=lambda x: x[1]['payload'], reverse=True)
            
            for material, data in sorted_materials:
                safety = f"{data['safety_factor']:.1f}" if data['safety_factor'] != float('inf') else "∞"
                tree.insert('', 'end', values=(
                    material,
                    f"{data['payload']:.2f}",
                    f"{data['mass_shell']:.3f}",
                    f"{data['lift']:.2f}",
                    safety
                ))
            
            tree.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Додаємо графік
            plt = get_plt()
            fig, ax = plt.subplots(figsize=(10, 6))
            materials = [m[0] for m in sorted_materials]
            payloads = [m[1]['payload'] for m in sorted_materials]
            colors = plt.cm.viridis(range(len(materials)))
            
            bars = ax.bar(materials, payloads, color=colors)
            ax.set_xlabel('Матеріал')
            ax.set_ylabel('Корисне навантаження (кг)')
            ax.set_title('Порівняння матеріалів за навантаженням')
            ax.grid(True, alpha=0.3, axis='y')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Помилка порівняння", str(e))
    
    def show_optimal_height(self):
        """Показати оптимальну висоту польоту"""
        try:
            # Отримуємо gas_volume залежно від режиму
            mode = self.mode_var.get()
            if mode == "payload":
                gas_volume_val = self.entries['gas_volume'].get()
            else:
                # Якщо режим "volume", розраховуємо об'єм із навантаження
                payload_val = self.entries['payload'].get()
                if not payload_val or float(payload_val) <= 0:
                    messagebox.showerror("Помилка", "Введіть коректне навантаження для розрахунку об'єму")
                    return
                try:
                    temp_inputs = {
                        'gas_type': self.gas_var.get(),
                        'gas_volume': payload_val,  # тимчасово передаємо навантаження як gas_volume
                        'material': self.material_var.get(),
                        'thickness': self.entries['thickness'].get(),
                        'start_height': self.entries['start_height'].get(),
                        'work_height': self.entries['work_height'].get(),
                        'ground_temp': FIELD_DEFAULTS['ground_temp'] if self.gas_var.get() != "Гаряче повітря" else self.entries['ground_temp'].get(),
                        'inside_temp': FIELD_DEFAULTS['ground_temp'] if self.gas_var.get() != "Гаряче повітря" else self.entries['inside_temp'].get(),
                        'mode': 'volume'
                    }
                    temp_validated, _ = validate_all_inputs(**temp_inputs)
                    temp_result = calculate_balloon_parameters(
                        gas_type=temp_inputs['gas_type'],
                        gas_volume=temp_validated['gas_volume'],
                        material=temp_inputs['material'],
                        thickness_mm=temp_validated['thickness'],
                        start_height=temp_validated['start_height'],
                        work_height=temp_validated['work_height'],
                        ground_temp=temp_validated['ground_temp'],
                        inside_temp=temp_validated['inside_temp'],
                        mode='volume'
                    )
                    gas_volume_val = str(temp_result.get('gas_volume', payload_val))
                    logging.info(f"Оптимальна висота: розраховано об'єм {gas_volume_val} м³ з навантаження {payload_val} кг")
                except Exception as e:
                    logging.error(f"Помилка розрахунку об'єму з навантаження: {e}")
                    messagebox.showerror("Помилка", f"Не вдалося розрахувати об'єм з навантаження: {e}")
                    return
            
            # Для не-гарячого повітря використовуємо значення за замовчуванням
            gas_type = self.gas_var.get()
            if gas_type == "Гаряче повітря":
                ground_temp_val = self.entries['ground_temp'].get()
                inside_temp_val = self.entries['inside_temp'].get()
            else:
                ground_temp_val = FIELD_DEFAULTS['ground_temp']
                inside_temp_val = FIELD_DEFAULTS['ground_temp']
            
            inputs = {
                'gas_type': gas_type,
                'gas_volume': gas_volume_val,
                'material': self.material_var.get(),
                'thickness': self.entries['thickness'].get(),
                'start_height': self.entries['start_height'].get(),
                'work_height': self.entries['work_height'].get(),
                'ground_temp': ground_temp_val,
                'inside_temp': inside_temp_val,
            }
            validated_numbers, validated_strings = validate_all_inputs(**inputs)
            
            optimal = calculate_optimal_height(
                gas_type=validated_strings['gas_type'],
                material=validated_strings['material'],
                thickness_mm=validated_numbers['thickness'],
                gas_volume=validated_numbers['gas_volume'],
                ground_temp=validated_numbers['ground_temp'],
                inside_temp=validated_numbers['inside_temp']
            )
            
            if not optimal or 'height' not in optimal:
                messagebox.showinfo("Результат", "Не вдалося знайти оптимальну висоту")
                return
            
            result_text = (
                f"Оптимальна висота польоту: {optimal['height']:.0f} м\n\n"
                f"Параметри на оптимальній висоті:\n"
                f"• Корисне навантаження: {optimal['payload']:.2f} кг\n"
                f"• Підйомна сила: {optimal['lift']:.2f} кг\n"
                f"• Маса оболонки: {optimal['mass_shell']:.3f} кг\n"
                f"• Щільність повітря: {optimal['rho_air']:.4f} кг/м³\n"
                f"• Підйомна сила на м³: {optimal['net_lift_per_m3']:.4f} кг/м³\n"
                f"• Температура: {optimal['T_outside_C']:.1f} °C\n"
                f"• Тиск: {optimal['P_outside']/1000:.1f} кПа"
            )
            
            messagebox.showinfo("Оптимальна висота", result_text)
            
        except Exception as e:
            messagebox.showerror("Помилка розрахунку", str(e))
    
    def show_flight_time(self):
        """Показати максимальний час польоту"""
        try:
            # Отримуємо gas_volume залежно від режиму
            if self.mode_var.get() == "payload":
                gas_volume_val = self.entries['gas_volume'].get()
            else:
                gas_volume_val = self.entries['gas_volume'].get() or self.entries['payload'].get()
            
            # Для не-гарячого повітря використовуємо значення за замовчуванням
            gas_type = self.gas_var.get()
            if gas_type == "Гаряче повітря":
                ground_temp_val = self.entries['ground_temp'].get()
                inside_temp_val = self.entries['inside_temp'].get()
            else:
                ground_temp_val = FIELD_DEFAULTS['ground_temp']
                inside_temp_val = FIELD_DEFAULTS['ground_temp']
            
            inputs = {
                'gas_type': gas_type,
                'gas_volume': gas_volume_val,
                'material': self.material_var.get(),
                'thickness': self.entries['thickness'].get(),
                'start_height': self.entries['start_height'].get(),
                'work_height': self.entries['work_height'].get(),
                'ground_temp': ground_temp_val,
                'inside_temp': inside_temp_val,
            }
            validated_numbers, validated_strings = validate_all_inputs(**inputs)
            
            perm_mult_str = self.entries['perm_mult'].get()
            try:
                perm_mult = float(perm_mult_str)
            except:
                perm_mult = 1.0
            
            flight_time = calculate_max_flight_time(
                gas_type=validated_strings['gas_type'],
                material=validated_strings['material'],
                thickness_mm=validated_numbers['thickness'],
                gas_volume=validated_numbers['gas_volume'],
                start_height=validated_numbers['start_height'],
                work_height=validated_numbers['work_height'],
                ground_temp=validated_numbers['ground_temp'],
                inside_temp=validated_numbers['inside_temp'],
                perm_mult=perm_mult
            )
            
            if flight_time['max_time_hours'] == float('inf'):
                result_text = flight_time.get('message', 'Час польоту не обмежений')
            else:
                result_text = (
                    f"{flight_time.get('message', '')}\n\n"
                    f"Деталі:\n"
                    f"• Початкове навантаження: {flight_time.get('initial_payload', 0):.2f} кг\n"
                    f"• Втрати газу за годину: {flight_time.get('gas_loss_rate_per_hour', 0):.6f} м³/год\n"
                    f"• Час до нульового навантаження: {flight_time.get('time_to_zero_payload', 0):.2f} год ({flight_time.get('time_to_zero_payload', 0)/24:.2f} днів)"
                )
            
            messagebox.showinfo("Час польоту", result_text)
            
        except Exception as e:
            messagebox.showerror("Помилка розрахунку", str(e))

    def show_help(self):
        """Показати довідку"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Довідка")
        help_window.geometry("800x600")
        help_window.configure(bg="#2b2b2b")
        
        # Notebook для вкладок
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Вкладка "Формули"
        formulas_frame = tk.Frame(notebook, bg="#2b2b2b")
        formulas_text = tk.Text(
            formulas_frame, 
            wrap="word", 
            bg="#1e1e1e", 
            fg="#ffffff",
            font=("Courier New", 10),
            padx=10,
            pady=10
        )
        formulas_text.insert(1.0, HELP_FORMULAS)
        formulas_text.config(state="disabled")
        formulas_text.pack(fill="both", expand=True)
        notebook.add(formulas_frame, text="Формули")
        
        # Вкладка "Параметри"
        params_frame = tk.Frame(notebook, bg="#2b2b2b")
        params_text = tk.Text(
            params_frame, 
            wrap="word", 
            bg="#1e1e1e", 
            fg="#ffffff",
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        params_text.insert(1.0, HELP_PARAMETERS)
        params_text.config(state="disabled")
        params_text.pack(fill="both", expand=True)
        notebook.add(params_frame, text="Параметри")
        
        # Вкладка "Безпека"
        safety_frame = tk.Frame(notebook, bg="#2b2b2b")
        safety_text = tk.Text(
            safety_frame, 
            wrap="word", 
            bg="#1e1e1e", 
            fg="#ffffff",
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        safety_text.insert(1.0, HELP_SAFETY)
        safety_text.config(state="disabled")
        safety_text.pack(fill="both", expand=True)
        notebook.add(safety_frame, text="Безпека")
        
        # Вкладка "Приклади"
        examples_frame = tk.Frame(notebook, bg="#2b2b2b")
        examples_text = tk.Text(
            examples_frame, 
            wrap="word", 
            bg="#1e1e1e", 
            fg="#ffffff",
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        examples_text.insert(1.0, HELP_EXAMPLES)
        examples_text.config(state="disabled")
        examples_text.pack(fill="both", expand=True)
        notebook.add(examples_frame, text="Приклади")
        
        # Вкладка "FAQ"
        faq_frame = tk.Frame(notebook, bg="#2b2b2b")
        faq_text = tk.Text(
            faq_frame, 
            wrap="word", 
            bg="#1e1e1e", 
            fg="#ffffff",
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        faq_text.insert(1.0, HELP_FAQ)
        faq_text.config(state="disabled")
        faq_text.pack(fill="both", expand=True)
        notebook.add(faq_frame, text="FAQ")
    
    def show_about(self):
        """Показати інформацію про програму"""
        messagebox.showinfo(BUTTON_LABELS['about'], ABOUT_TEXT_EXTENDED)

    def add_tooltips(self):
        """Додає підказки до всіх полів"""
        for key, entry in self.entries.items():
            if key in FIELD_TOOLTIPS:
                self.create_tooltip(entry, FIELD_TOOLTIPS[key])

    def create_tooltip(self, widget, text):
        """Створює підказку для віджета"""
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1, font=("Arial", 9))
        label.pack(ipadx=1)
        def enter(event):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()
        def leave(event):
            tooltip.withdraw()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)


if __name__ == "__main__":
    app = BalloonCalculatorGUI()
    app.run() 