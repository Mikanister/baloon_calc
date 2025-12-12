"""
Покращений GUI для калькулятора аеростатів
"""

import tkinter as tk
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    from tkinter import ttk
    TTKBOOTSTRAP_AVAILABLE = False
from tkinter import messagebox
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
    from baloon.patterns import generate_pattern_from_shape, calculate_seam_length
except ImportError:
    # Для сумісності з локальними запусками
    try:
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
        from patterns import generate_pattern_from_shape, calculate_seam_length
    except ImportError:
        # Останній fallback
        pass

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
        # Використовуємо TTKBootstrap, якщо доступний
        if TTKBOOTSTRAP_AVAILABLE:
            self.root = ttk.Window(themename="darkly")
        else:
            self.root = tk.Tk()
        
        self.root.title("Калькулятор аеростатів v2.0")
        self.root.geometry("650x750")
        self.root.minsize(600, 700)
        
        # Налаштування темної теми (тільки якщо TTKBootstrap недоступний)
        if not TTKBOOTSTRAP_AVAILABLE:
            self.setup_dark_theme()
        
        # Змінна для теми
        self.dark_mode = True
        # Змінні
        self.mode_var = tk.StringVar(value="payload")
        self.material_var = tk.StringVar(value="TPU")
        self.gas_var = tk.StringVar(value="Гелій")
        self.shape_var = tk.StringVar(value="Сфера")
        self.material_density_var = tk.StringVar()
        self.result_var = tk.StringVar()
        self.shape_code_map = {
            "Сфера": "sphere",
            "Подушка/мішок": "pillow",
            "Груша": "pear",
            "Сигара": "cigar",
        }
        # Віджети
        self.entries = {}
        self.labels = {}
        self.preview_update_pending = False  # Для обмеження частоти оновлення
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
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Хедер зверху
        header_frame = ttk.Frame(main_frame, style="Card.TFrame", padding="10")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        
        # Notebook для вкладок
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        
        # Вкладка "Розрахунки"
        calc_frame = ttk.Frame(self.notebook)
        self.notebook.add(calc_frame, text="Розрахунки")
        calc_frame.columnconfigure(0, weight=1, uniform="cols")
        calc_frame.columnconfigure(1, weight=1, uniform="cols")
        calc_frame.rowconfigure(0, weight=1)
        
        # Вкладка "Викрійки"
        patterns_frame = ttk.Frame(self.notebook)
        self.notebook.add(patterns_frame, text="Викрійки")
        patterns_frame.columnconfigure(0, weight=1)
        patterns_frame.rowconfigure(0, weight=1)
        
        # Створюємо layout для розрахунків
        left_frame = ttk.Frame(calc_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left_frame.columnconfigure(0, weight=1)
        
        right_frame = ttk.Frame(calc_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
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
        
        # Створюємо layout для викрійок
        self.create_patterns_section(patterns_frame)
        
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
        help_btn = ttk.Button(btn_frame, text=BUTTON_LABELS['help'], command=self.show_help)
        if TTKBOOTSTRAP_AVAILABLE:
            help_btn.configure(bootstyle=SECONDARY)
        help_btn.pack(side="left", padx=(0, 8))
        
        about_btn = ttk.Button(btn_frame, text=BUTTON_LABELS['about'], command=self.show_about)
        if TTKBOOTSTRAP_AVAILABLE:
            about_btn.configure(bootstyle=SECONDARY)
        about_btn.pack(side="left")
        
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
        
        # Вибір форми
        shape_values = COMBOBOX_VALUES['shape_type']
        self.shape_display_to_code = {
            "Сфера": "sphere",
            "Подушка/мішок": "pillow",
        }
        self.shape_code_to_display = {v: k for k, v in self.shape_display_to_code.items()}
        self.labels['shape_type'] = ttk.Label(parent, text=FIELD_LABELS['shape_type'])
        self.labels['shape_type'].grid(row=row, column=0, sticky="w")
        shape_combo = ttk.Combobox(parent, values=shape_values, state="readonly", textvariable=self.shape_var)
        shape_combo.grid(row=row, column=1, sticky="ew", padx=(10, 0))
        if FIELD_DEFAULTS['shape_type'] in self.shape_code_to_display:
            self.shape_var.set(self.shape_code_to_display[FIELD_DEFAULTS['shape_type']])
        else:
            self.shape_var.set(shape_values[0])
        self.entries['shape_type'] = shape_combo
        row += 1
        
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
        # Зберігаємо рядок для payload (після температур або форми)
        self.payload_row = row
        
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
        perm_mult_hint.grid(row=row, column=0, columnspan=2, sticky="w", pady=(2, 5))
        row += 1
        row = self._add_entry_row(parent, 'extra_mass', FIELD_LABELS['extra_mass'], row, FIELD_DEFAULTS['extra_mass'])
        row = self._add_entry_row(parent, 'seam_factor', FIELD_LABELS['seam_factor'], row, FIELD_DEFAULTS['seam_factor'], width=8)
        row += 1
        
        # Параметри форм (показуються/ховаються)
        self.shape_rows = {}
        self.shape_rows['pillow_len'] = self._add_entry_row(parent, 'pillow_len', FIELD_LABELS['pillow_len'], row, FIELD_DEFAULTS['pillow_len']); row = self.shape_rows['pillow_len']
        self.shape_rows['pillow_wid'] = self._add_entry_row(parent, 'pillow_wid', FIELD_LABELS['pillow_wid'], row, FIELD_DEFAULTS['pillow_wid']); row = self.shape_rows['pillow_wid']
        self.shape_rows['pear_height'] = self._add_entry_row(parent, 'pear_height', FIELD_LABELS['pear_height'], row, FIELD_DEFAULTS['pear_height']); row = self.shape_rows['pear_height']
        self.shape_rows['pear_top_radius'] = self._add_entry_row(parent, 'pear_top_radius', FIELD_LABELS['pear_top_radius'], row, FIELD_DEFAULTS['pear_top_radius']); row = self.shape_rows['pear_top_radius']
        self.shape_rows['pear_bottom_radius'] = self._add_entry_row(parent, 'pear_bottom_radius', FIELD_LABELS['pear_bottom_radius'], row, FIELD_DEFAULTS['pear_bottom_radius']); row = self.shape_rows['pear_bottom_radius']

        return row
        
    def create_button_section(self, parent, row):
        """Створення секції кнопок"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")
        
        # Перший рядок кнопок
        row1_frame = ttk.Frame(button_frame)
        row1_frame.pack(fill="x", pady=(0, 5))
        
        calc_btn = ttk.Button(
            row1_frame, text=BUTTON_LABELS['calculate'],
            command=self.calculate
        )
        if TTKBOOTSTRAP_AVAILABLE:
            calc_btn.configure(bootstyle=SUCCESS)
        else:
            calc_btn.configure(style="Accent.TButton")
        calc_btn.pack(side="left", padx=(0, 10))
        
        graph_btn = ttk.Button(
            row1_frame, text=BUTTON_LABELS['show_graph'],
            command=self.show_graph
        )
        if TTKBOOTSTRAP_AVAILABLE:
            graph_btn.configure(bootstyle=INFO)
        graph_btn.pack(side="left", padx=(0, 10))
        
        # Кнопка експорту результатів
        export_results_btn = ttk.Button(
            row1_frame, text="Експорт результатів",
            command=self.export_results
        )
        if TTKBOOTSTRAP_AVAILABLE:
            export_results_btn.configure(bootstyle=WARNING)
        export_results_btn.pack(side="left", padx=(0, 10))
        
        # Другий рядок кнопок
        row2_frame = ttk.Frame(button_frame)
        row2_frame.pack(fill="x")
        
        save_btn = ttk.Button(
            row2_frame, text=BUTTON_LABELS['save_settings'],
            command=self.save_settings
        )
        if TTKBOOTSTRAP_AVAILABLE:
            save_btn.configure(bootstyle=PRIMARY)
        save_btn.pack(side="left", padx=(0, 10))
        # about/help винесені у хедер
        
        row += 1
        return row
    
    def create_3d_preview_section(self, parent):
        """Створення секції з 3D прев'ю моделі"""
        # Заголовок
        ttk.Label(parent, text="3D Модель", style="Subheading.TLabel").pack(anchor="w", pady=(0, 5))
        
        # Frame для matplotlib canvas
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill="both", expand=True)
        
        # Створюємо matplotlib figure та canvas
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import numpy as np
            
            # Створюємо невелику фігуру
            self.preview_fig = Figure(figsize=(4, 3), facecolor='#1e1e1e', dpi=80)
            self.preview_ax = self.preview_fig.add_subplot(111, projection='3d')
            self.preview_ax.set_facecolor('#1e1e1e')
            
            # Налаштування темної теми
            self.preview_ax.xaxis.pane.fill = False
            self.preview_ax.yaxis.pane.fill = False
            self.preview_ax.zaxis.pane.fill = False
            self.preview_ax.xaxis.pane.set_edgecolor('#333333')
            self.preview_ax.yaxis.pane.set_edgecolor('#333333')
            self.preview_ax.zaxis.pane.set_edgecolor('#333333')
            self.preview_ax.xaxis.label.set_color('#ffffff')
            self.preview_ax.yaxis.label.set_color('#ffffff')
            self.preview_ax.zaxis.label.set_color('#ffffff')
            self.preview_ax.tick_params(colors='#ffffff', labelsize=6)
            self.preview_ax.grid(True, color='#444444', linestyle='--', alpha=0.3)
            
            # Прибираємо підписи осей для компактності
            self.preview_ax.set_xticklabels([])
            self.preview_ax.set_yticklabels([])
            self.preview_ax.set_zticklabels([])
            
            # Canvas для відображення
            self.preview_canvas = FigureCanvasTkAgg(self.preview_fig, canvas_frame)
            self.preview_canvas.draw()
            self.preview_canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Зберігаємо посилання для оновлення
            self.preview_canvas_widget = self.preview_canvas.get_tk_widget()
            
        except Exception as e:
            logging.warning(f"Не вдалося створити 3D прев'ю: {e}")
            ttk.Label(canvas_frame, text="3D прев'ю недоступне", foreground="#888888").pack()
            self.preview_fig = None
            self.preview_ax = None
            self.preview_canvas = None
        
        # Початкове відображення
        self.update_3d_preview()
    
    def update_3d_preview(self):
        """Оновлює 3D прев'ю моделі на основі поточної форми (з розділу викрійок)"""
        if not hasattr(self, 'preview_ax') or self.preview_ax is None:
            return
        
        # Обмежуємо частоту оновлення (не більше раз на 300мс)
        if hasattr(self, 'preview_update_pending') and self.preview_update_pending:
            return
        
        self.preview_update_pending = True
        self.root.after(300, lambda: setattr(self, 'preview_update_pending', False))
        
        try:
            # Очищаємо попередній графік
            self.preview_ax.clear()
            
            # Отримуємо поточну форму з розділу викрійок
            shape_display = self.pattern_shape_var.get()
            # Використовуємо shape_code_map для перетворення
            shape_code = self.shape_code_map.get(shape_display, 'sphere')
            # Логування для діагностики
            logging.info(f"update_3d_preview: shape_display={shape_display}, shape_code={shape_code}")
            
            # Отримуємо параметри форми з розділу викрійок або з останнього розрахунку
            shape_params = {}
            
            # Спочатку спробуємо отримати з останнього розрахунку
            if hasattr(self, 'last_calculation_results'):
                results = self.last_calculation_results
                calc_shape_code = results.get('shape_type', '')
                if calc_shape_code == shape_code:
                    shape_params = results.get('shape_params', {}) or {}
                    # Додатково перевіряємо, чи є параметри в results напряму
                    if shape_code == 'pear' and not shape_params:
                        shape_params = {
                            'pear_height': results.get('pear_height', 3.0),
                            'pear_top_radius': results.get('pear_top_radius', 1.2),
                            'pear_bottom_radius': results.get('pear_bottom_radius', 0.6)
                        }
                    elif shape_code == 'cigar' and not shape_params:
                        shape_params = {
                            'cigar_length': results.get('cigar_length', 5.0),
                            'cigar_radius': results.get('cigar_radius', 1.0)
                        }
            
            # Якщо немає параметрів, спробуємо з полів вводу розрахунків
            if not shape_params:
                if shape_code == 'sphere':
                    if hasattr(self, 'last_calculation_results') and 'radius' in self.last_calculation_results:
                        radius = self.last_calculation_results['radius']
                    else:
                        try:
                            gas_volume = float(self.entries.get('gas_volume', ttk.Entry()).get() or "1.0")
                            from baloon.shapes import sphere_radius_from_volume
                            radius = sphere_radius_from_volume(gas_volume)
                        except:
                            radius = 1.0
                    shape_params = {'radius': radius}
                    
                elif shape_code == 'pillow':
                    try:
                        shape_params = {
                            'pillow_len': float(self.entries.get('pillow_len', ttk.Entry()).get() or "3.0"),
                            'pillow_wid': float(self.entries.get('pillow_wid', ttk.Entry()).get() or "2.0")
                        }
                    except:
                        shape_params = {'pillow_len': 3.0, 'pillow_wid': 2.0}
                        
                elif shape_code == 'pear':
                    try:
                        shape_params = {
                            'pear_height': float(self.entries.get('pear_height', ttk.Entry()).get() or "3.0"),
                            'pear_top_radius': float(self.entries.get('pear_top_radius', ttk.Entry()).get() or "1.2"),
                            'pear_bottom_radius': float(self.entries.get('pear_bottom_radius', ttk.Entry()).get() or "0.6")
                        }
                    except:
                        shape_params = {'pear_height': 3.0, 'pear_top_radius': 1.2, 'pear_bottom_radius': 0.6}
                        
                elif shape_code == 'cigar':
                    try:
                        shape_params = {
                            'cigar_length': float(self.entries.get('cigar_length', ttk.Entry()).get() or "5.0"),
                            'cigar_radius': float(self.entries.get('cigar_radius', ttk.Entry()).get() or "1.0")
                        }
                    except:
                        shape_params = {'cigar_length': 5.0, 'cigar_radius': 1.0}
            
            # Малюємо модель
            import numpy as np
            self._draw_preview_3d(shape_code, shape_params)
            
            # Оновлюємо canvas
            if self.preview_canvas:
                self.preview_canvas.draw()
                
        except Exception as e:
            logging.warning(f"Помилка оновлення 3D прев'ю: {e}")
    
    def _draw_preview_3d(self, shape_code: str, shape_params: dict):
        """Малює 3D модель в прев'ю"""
        import numpy as np
        
        # Логування для діагностики
        logging.info(f"_draw_preview_3d: shape_code={shape_code}, shape_params={shape_params}")
        
        # Налаштування темної теми
        self.preview_ax.set_facecolor('#1e1e1e')
        self.preview_ax.xaxis.pane.fill = False
        self.preview_ax.yaxis.pane.fill = False
        self.preview_ax.zaxis.pane.fill = False
        self.preview_ax.xaxis.pane.set_edgecolor('#333333')
        self.preview_ax.yaxis.pane.set_edgecolor('#333333')
        self.preview_ax.zaxis.pane.set_edgecolor('#333333')
        self.preview_ax.tick_params(colors='#ffffff', labelsize=6)
        self.preview_ax.grid(True, color='#444444', linestyle='--', alpha=0.3)
        self.preview_ax.set_xticklabels([])
        self.preview_ax.set_yticklabels([])
        self.preview_ax.set_zticklabels([])
        
        if shape_code == 'sphere':
            radius = shape_params.get('radius', 1.0)
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            x = radius * np.outer(np.cos(u), np.sin(v))
            y = radius * np.outer(np.sin(u), np.sin(v))
            z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
            self.preview_ax.plot_surface(x, y, z, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.3)
            
        elif shape_code == 'pillow':
            length = shape_params.get('pillow_len', 3.0)
            width = shape_params.get('pillow_wid', 2.0)
            thickness = width * 0.3
            
            # Еліпсоїд
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            u_grid, v_grid = np.meshgrid(u, v)
            
            a = length / 2
            b = width / 2
            c = thickness / 2
            
            x = a * np.cos(u_grid) * np.sin(v_grid)
            y = b * np.sin(u_grid) * np.sin(v_grid)
            z = c * np.cos(v_grid)
            
            x = x - a + length / 2
            y = y - b + width / 2
            z = z - c + thickness / 2
            
            self.preview_ax.plot_surface(x, y, z, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.3)
            
        elif shape_code == 'pear':
            height = shape_params.get('pear_height', 3.0)
            top_radius = shape_params.get('pear_top_radius', 1.2)
            bottom_radius = shape_params.get('pear_bottom_radius', 0.6)
            
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, 1, 20)
            u_grid, v_grid = np.meshgrid(u, v)
            
            r_at_height = top_radius * (1 - v_grid) + bottom_radius * v_grid
            
            x = r_at_height * np.cos(u_grid)
            y = r_at_height * np.sin(u_grid)
            z = height * v_grid
            
            self.preview_ax.plot_surface(x, y, z, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.3)
            
        elif shape_code == 'cigar':
            length = shape_params.get('cigar_length', 5.0)
            radius = shape_params.get('cigar_radius', 1.0)
            
            cylinder_length = max(0, length - 2 * radius)
            
            # Циліндрична частина
            if cylinder_length > 0:
                u_cyl = np.linspace(0, 2 * np.pi, 20)
                z_cyl = np.linspace(radius, length - radius, 10)
                u_grid_cyl, z_grid_cyl = np.meshgrid(u_cyl, z_cyl)
                
                x_cyl = radius * np.cos(u_grid_cyl)
                y_cyl = radius * np.sin(u_grid_cyl)
                z_cyl = z_grid_cyl
                
                self.preview_ax.plot_surface(x_cyl, y_cyl, z_cyl, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.3)
            
            # Півсферичні кінці
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi / 2, 10)
            u_grid, v_grid = np.meshgrid(u, v)
            
            # Нижній кінець
            x1 = radius * np.cos(u_grid) * np.sin(v_grid)
            y1 = radius * np.sin(u_grid) * np.sin(v_grid)
            z1 = radius * (1 - np.cos(v_grid))
            self.preview_ax.plot_surface(x1, y1, z1, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.3)
            
            # Верхній кінець
            x2 = radius * np.cos(u_grid) * np.sin(v_grid)
            y2 = radius * np.sin(u_grid) * np.sin(v_grid)
            z2 = (length - radius) + radius * np.cos(v_grid)
            self.preview_ax.plot_surface(x2, y2, z2, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.3)
        
        # Налаштування масштабу в залежності від форми
        if shape_code == 'sphere':
            radius = shape_params.get('radius', 1.0)
            max_dim = radius * 1.5
            self.preview_ax.set_xlim([-max_dim, max_dim])
            self.preview_ax.set_ylim([-max_dim, max_dim])
            self.preview_ax.set_zlim([-max_dim, max_dim])
            self.preview_ax.set_box_aspect([1, 1, 1])
        elif shape_code == 'pillow':
            length = shape_params.get('pillow_len', 3.0)
            width = shape_params.get('pillow_wid', 2.0)
            thickness = width * 0.3
            max_dim = max(length, width, thickness) * 1.2
            self.preview_ax.set_xlim([0, max_dim])
            self.preview_ax.set_ylim([0, max_dim])
            self.preview_ax.set_zlim([0, max_dim])
            self.preview_ax.set_box_aspect([length, width, thickness])
        elif shape_code == 'pear':
            height = shape_params.get('pear_height', 3.0)
            max_radius = max(shape_params.get('pear_top_radius', 1.2), shape_params.get('pear_bottom_radius', 0.6))
            max_dim = max(height, max_radius * 2) * 1.2
            self.preview_ax.set_xlim([-max_dim/2, max_dim/2])
            self.preview_ax.set_ylim([-max_dim/2, max_dim/2])
            self.preview_ax.set_zlim([0, max_dim])
            self.preview_ax.set_box_aspect([max_radius*2, max_radius*2, height])
        elif shape_code == 'cigar':
            length = shape_params.get('cigar_length', 5.0)
            radius = shape_params.get('cigar_radius', 1.0)
            max_dim = max(length, radius * 2) * 1.2
            self.preview_ax.set_xlim([-max_dim/2, max_dim/2])
            self.preview_ax.set_ylim([-max_dim/2, max_dim/2])
            self.preview_ax.set_zlim([0, max_dim])
            self.preview_ax.set_box_aspect([radius*2, radius*2, length])
        
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
        self.shape_var.trace_add("write", self.update_fields)
        if 'shape_type' in self.entries:
            self.entries['shape_type'].bind("<<ComboboxSelected>>", lambda e: self.update_fields())
        
        # Валідація в реальному часі для числових полів
        numeric_fields = ['thickness', 'start_height', 'work_height', 'ground_temp', 
                         'inside_temp', 'duration', 'payload', 'gas_volume', 'perm_mult',
                         'extra_mass', 'seam_factor',
                         'pillow_len','pillow_wid','pear_height','pear_top_radius','pear_bottom_radius','cigar_length','cigar_radius']
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
            elif field_name == 'extra_mass':
                if float(value) < 0:
                    entry.configure(style='Invalid.TEntry')
            elif field_name == 'seam_factor':
                if not (1.0 <= float(value) <= 2.0):
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
        shape_display = self.entries['shape_type'].get()
        shape_code = self.shape_display_to_code.get(shape_display, 'sphere')
        
        # Поле gas_volume показується тільки в режимі "payload" (Об'єм -> навантаження)
        # В режимі "volume" (Навантаження -> об'єм) воно приховане, бо об'єм розраховується
        if is_payload_mode:
            if 'gas_volume' in self.labels and 'gas_volume' in self.entries:
                self.labels['gas_volume'].grid()
                self.entries['gas_volume'].grid(sticky="ew", padx=(10, 0))
        else:
            if 'gas_volume' in self.labels and 'gas_volume' in self.entries:
                self.labels['gas_volume'].grid_remove()
                self.entries['gas_volume'].grid_remove()
        
        # Поля температури тільки для гарячого повітря
        # Знаходимо поточний рядок після gas_volume або payload
        if is_payload_mode:
            # В режимі payload gas_volume видиме, тому temp_row_base після нього
            current_row = getattr(self, "temp_row_base", 5)  # Після gas_volume (row=4)
        else:
            # В режимі volume gas_volume приховане, payload видиме
            # Знаходимо рядок payload (після форми)
            current_row = getattr(self, "payload_row", 4)  # Після форми
        
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
            # Зберігаємо рядок payload для подальших розрахунків
            self.payload_row = current_row
        
        # Поля параметрів форми
        shape_display = self.entries['shape_type'].get()
        shape_code = self.shape_display_to_code.get(shape_display, 'sphere')
        def show_field(key):
            if key in self.labels and key in self.entries:
                self.labels[key].grid()
                self.entries[key].grid(sticky="ew", padx=(10, 0))
        def hide_field(key):
            if key in self.labels and key in self.entries:
                self.labels[key].grid_remove()
                self.entries[key].grid_remove()
        
        all_shape_keys = ['pillow_len','pillow_wid','pear_height','pear_top_radius','pear_bottom_radius','cigar_length','cigar_radius']
        for k in all_shape_keys:
            hide_field(k)
        if shape_code == "pillow":
            show_field('pillow_len'); show_field('pillow_wid')
        elif shape_code == "pear":
            show_field('pear_height'); show_field('pear_top_radius'); show_field('pear_bottom_radius')
        elif shape_code == "cigar":
            show_field('cigar_length'); show_field('cigar_radius')
        
            
    def calculate(self):
        """Виконання розрахунків"""
        try:
            logging.info("Початок розрахунку. Вхідні дані: %s", {k: v.get() if hasattr(v, 'get') else v for k, v in self.entries.items()})
            # Збір даних з полів
            # Отримуємо gas_volume залежно від режиму
            if self.mode_var.get() == "payload":
                gas_volume_val = self.entries['gas_volume'].get()
            else:
                # В режимі "volume" gas_volume не потрібен (об'єм розраховується з навантаження)
                # Передаємо None або пустий рядок
                gas_volume_val = ""  # Або можна передати None, але валідація очікує рядок
            
            # Для не-гарячого повітря використовуємо значення за замовчуванням
            gas_type = self.gas_var.get()
            if gas_type == "Гаряче повітря":
                ground_temp_val = self.entries['ground_temp'].get()
                inside_temp_val = self.entries['inside_temp'].get()
            else:
                # Для гелію/водню використовуємо стандартні значення
                ground_temp_val = FIELD_DEFAULTS['ground_temp']
                inside_temp_val = FIELD_DEFAULTS['ground_temp']  # Для гелію/водню температура всередині = зовнішня
            
            shape_display = self.entries['shape_type'].get()
            shape_code = self.shape_display_to_code.get(shape_display, 'sphere')
            shape_params_raw = {
                'pillow_len': self.entries.get('pillow_len', None).get() if 'pillow_len' in self.entries else None,
                'pillow_wid': self.entries.get('pillow_wid', None).get() if 'pillow_wid' in self.entries else None,
                'pear_height': self.entries.get('pear_height', None).get() if 'pear_height' in self.entries else None,
                'pear_top_radius': self.entries.get('pear_top_radius', None).get() if 'pear_top_radius' in self.entries else None,
                'pear_bottom_radius': self.entries.get('pear_bottom_radius', None).get() if 'pear_bottom_radius' in self.entries else None,
                'cigar_length': self.entries.get('cigar_length', None).get() if 'cigar_length' in self.entries else None,
                'cigar_radius': self.entries.get('cigar_radius', None).get() if 'cigar_radius' in self.entries else None,
            }
            
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
                'mode': self.mode_var.get(),
                'shape_type': shape_code,
                'shape_params': shape_params_raw,
                'extra_mass': self.entries.get('extra_mass', None).get() if 'extra_mass' in self.entries else "0",
                'seam_factor': self.entries.get('seam_factor', None).get() if 'seam_factor' in self.entries else "1.0",
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
            validated_shape_params = {k: v for k, v in validated_numbers.items() if k in shape_params_raw}
            # Розрахунки
            # В режимі "volume" gas_volume розраховується з payload
            # В режимі "payload" gas_volume береться з поля gas_volume
            if validated_strings['mode'] == 'volume':
                # В режимі "volume" передаємо payload як gas_volume (функція сама розбереться)
                payload_val = self.entries['payload'].get()
                try:
                    gas_volume_for_calc = float(payload_val) if payload_val else 0
                except:
                    gas_volume_for_calc = 0
            else:
                # В режимі "payload" використовуємо gas_volume
                gas_volume_for_calc = validated_numbers.get('gas_volume', 0)
            
            results = calculate_balloon_parameters(
                gas_type=validated_strings['gas_type'],
                gas_volume=gas_volume_for_calc,
                material=validated_strings['material'],
                thickness_mm=validated_numbers['thickness'],
                start_height=validated_numbers['start_height'],
                work_height=validated_numbers['work_height'],
                ground_temp=validated_numbers['ground_temp'],
                inside_temp=validated_numbers['inside_temp'],
                duration=validated_numbers['duration'],
                perm_mult=perm_mult,
                mode=validated_strings['mode'],
                shape_type=shape_code,
                shape_params=validated_shape_params,
                extra_mass=validated_numbers.get('extra_mass', 0.0),
                seam_factor=validated_numbers.get('seam_factor', 1.0),
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
                        perm_mult=perm_mult,
                        shape_type=shape_code,
                        shape_params=validated_shape_params,
                        extra_mass=validated_numbers.get('extra_mass', 0.0),
                        seam_factor=validated_numbers.get('seam_factor', 1.0),
                    )
                    results['flight_time_info'] = flight_time_info
                except Exception as e:
                    logging.warning(f"Помилка розрахунку часу польоту: {e}")
                    results['flight_time_info'] = None
            
            # Оновлюємо поля з розрахованими розмірами
            calculated_shape_params = results.get('shape_params', {})
            if calculated_shape_params:
                shape_code = validated_strings.get('shape_type', 'sphere')
                if shape_code == "pillow":
                    if 'pillow_len' in calculated_shape_params and 'pillow_len' in self.entries:
                        self.entries['pillow_len'].delete(0, tk.END)
                        self.entries['pillow_len'].insert(0, f"{calculated_shape_params['pillow_len']:.2f}")
                    if 'pillow_wid' in calculated_shape_params and 'pillow_wid' in self.entries:
                        self.entries['pillow_wid'].delete(0, tk.END)
                        self.entries['pillow_wid'].insert(0, f"{calculated_shape_params['pillow_wid']:.2f}")
                elif shape_code == "pear":
                    if 'pear_height' in calculated_shape_params and 'pear_height' in self.entries:
                        self.entries['pear_height'].delete(0, tk.END)
                        self.entries['pear_height'].insert(0, f"{calculated_shape_params['pear_height']:.2f}")
                    if 'pear_top_radius' in calculated_shape_params and 'pear_top_radius' in self.entries:
                        self.entries['pear_top_radius'].delete(0, tk.END)
                        self.entries['pear_top_radius'].insert(0, f"{calculated_shape_params['pear_top_radius']:.2f}")
                    if 'pear_bottom_radius' in calculated_shape_params and 'pear_bottom_radius' in self.entries:
                        self.entries['pear_bottom_radius'].delete(0, tk.END)
                        self.entries['pear_bottom_radius'].insert(0, f"{calculated_shape_params['pear_bottom_radius']:.2f}")
                elif shape_code == "cigar":
                    if 'cigar_length' in calculated_shape_params and 'cigar_length' in self.entries:
                        self.entries['cigar_length'].delete(0, tk.END)
                        self.entries['cigar_length'].insert(0, f"{calculated_shape_params['cigar_length']:.2f}")
                    if 'cigar_radius' in calculated_shape_params and 'cigar_radius' in self.entries:
                        self.entries['cigar_radius'].delete(0, tk.END)
                        self.entries['cigar_radius'].insert(0, f"{calculated_shape_params['cigar_radius']:.2f}")
            
            # Зберігаємо результати для використання в викрійках
            self.last_calculation_results = results
            
            self.format_results(results, validated_strings['mode'])
            
            # Оновлюємо 3D прев'ю в розділі викрійок, якщо форма збігається
            if hasattr(self, 'preview_ax') and self.preview_ax is not None:
                pattern_shape = self.pattern_shape_var.get()
                calc_shape = self.shape_display_to_code.get(self.entries['shape_type'].get(), 'sphere')
                if self.shape_display_to_code.get(pattern_shape, 'sphere') == calc_shape:
                    self.update_3d_preview()
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
        
        # Форма
        shape_code = results.get('shape_type', 'sphere')
        shape_display = self.shape_code_to_display.get(shape_code, shape_code)
        add_line(fmt("Форма оболонки:", shape_display, ""), normal_color)
        shape_params = results.get('shape_params', {}) or {}
        if shape_code == "pillow":
            add_line(fmt("Довжина подушки:", f"{shape_params.get('pillow_len', 0):.2f}", "м"), normal_color)
            add_line(fmt("Ширина подушки:", f"{shape_params.get('pillow_wid', 0):.2f}", "м"), normal_color)
            # Товщина розраховується з об'єму, але для викрійки не потрібна
        elif shape_code == "pear":
            add_line(fmt("Висота груші:", f"{shape_params.get('pear_height', 0):.2f}", "м"), normal_color)
            add_line(fmt("Радіус верхньої частини:", f"{shape_params.get('pear_top_radius', 0):.2f}", "м"), normal_color)
            add_line(fmt("Радіус нижньої частини:", f"{shape_params.get('pear_bottom_radius', 0):.2f}", "м"), normal_color)
        elif shape_code == "cigar":
            add_line(fmt("Довжина сигари:", f"{shape_params.get('cigar_length', 0):.2f}", "м"), normal_color)
            add_line(fmt("Радіус сигари:", f"{shape_params.get('cigar_radius', 0):.2f}", "м"), normal_color)
        add_line("", normal_color)
        
        # Основні параметри
        if mode == "volume":
            add_line(fmt("Потрібний обʼєм газу:", f"{results['gas_volume']:.2f}", "м³"), normal_color)
        
        add_line(fmt("Необхідний обʼєм кулі:", f"{results['required_volume']:.2f}", "м³"), normal_color)
        add_line(fmt("Корисне навантаження (старт):", f"{results['payload']:.2f}", "кг"), 
                success_color if results['payload'] > 0 else error_color)
        add_line(fmt("Маса оболонки:", f"{results['mass_shell']:.2f}", "кг"), normal_color)
        if results.get('extra_mass', 0) > 0:
            add_line(fmt("Додаткова маса обладнання:", f"{results['extra_mass']:.2f}", "кг"), normal_color)
        add_line(fmt("Підйомна сила (старт):", f"{results['lift']:.2f}", "кг"), normal_color)
        add_line(fmt("Радіус кулі:", f"{results['radius']:.2f}", "м"), normal_color)
        add_line(fmt("Площа поверхні:", f"{results['surface_area']:.2f}", "м²"), normal_color)
        if results.get('effective_surface_area', 0) > 0 and results.get('effective_surface_area', 0) != results.get('surface_area', 0):
            add_line(fmt("Ефективна площа (з урахуванням швів):", f"{results['effective_surface_area']:.2f}", "м²"), normal_color)
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
        try:
            # Спробуємо використати Pydantic Settings
            try:
                from baloon.settings import BalloonSettings
            except ImportError:
                from settings import BalloonSettings
            
            settings = BalloonSettings(
                mode=self.mode_var.get(),
                material=self.material_var.get(),
                gas=self.gas_var.get(),
                shape_type=self.entries['shape_type'].get(),
                thickness=self.entries['thickness'].get(),
                start_height=self.entries['start_height'].get(),
                work_height=self.entries['work_height'].get(),
                ground_temp=self.entries['ground_temp'].get(),
                inside_temp=self.entries['inside_temp'].get(),
                payload=self.entries['payload'].get(),
                gas_volume=self.entries['gas_volume'].get(),
                perm_mult=self.entries['perm_mult'].get(),
                extra_mass=self.entries.get('extra_mass').get() if 'extra_mass' in self.entries else "0",
                seam_factor=self.entries.get('seam_factor').get() if 'seam_factor' in self.entries else "1.0",
                pillow_len=self.entries.get('pillow_len').get() if 'pillow_len' in self.entries else "",
                pillow_wid=self.entries.get('pillow_wid').get() if 'pillow_wid' in self.entries else "",
                pear_height=self.entries.get('pear_height').get() if 'pear_height' in self.entries else "",
                pear_top_radius=self.entries.get('pear_top_radius').get() if 'pear_top_radius' in self.entries else "",
                pear_bottom_radius=self.entries.get('pear_bottom_radius').get() if 'pear_bottom_radius' in self.entries else "",
                cigar_length=self.entries.get('cigar_length').get() if 'cigar_length' in self.entries else "",
                cigar_radius=self.entries.get('cigar_radius').get() if 'cigar_radius' in self.entries else "",
            )
            settings.save_to_file()
            logging.info("Налаштування збережено через Pydantic Settings")
            messagebox.showinfo("Успіх", "Налаштування збережено")
        except ImportError:
            # Fallback на старий спосіб
            settings = {
                'mode': self.mode_var.get(),
                'material': self.material_var.get(),
                'gas': self.gas_var.get(),
                'shape_type': self.entries['shape_type'].get(),
                'thickness': self.entries['thickness'].get(),
                'start_height': self.entries['start_height'].get(),
                'work_height': self.entries['work_height'].get(),
                'ground_temp': self.entries['ground_temp'].get(),
                'inside_temp': self.entries['inside_temp'].get(),
                'payload': self.entries['payload'].get(),
                'gas_volume': self.entries['gas_volume'].get(),
                'perm_mult': self.entries['perm_mult'].get(),
                'extra_mass': self.entries.get('extra_mass').get() if 'extra_mass' in self.entries else "0",
                'seam_factor': self.entries.get('seam_factor').get() if 'seam_factor' in self.entries else "1.0",
                'pillow_len': self.entries.get('pillow_len').get() if 'pillow_len' in self.entries else "",
                'pillow_wid': self.entries.get('pillow_wid').get() if 'pillow_wid' in self.entries else "",
                'pear_height': self.entries.get('pear_height').get() if 'pear_height' in self.entries else "",
                'pear_top_radius': self.entries.get('pear_top_radius').get() if 'pear_top_radius' in self.entries else "",
                'pear_bottom_radius': self.entries.get('pear_bottom_radius').get() if 'pear_bottom_radius' in self.entries else "",
            }
            try:
                with open('balloon_settings.json', 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                logging.info("Налаштування збережено: %s", settings)
                messagebox.showinfo("Успіх", "Налаштування збережено")
            except Exception as e:
                logging.error("Не вдалося зберегти налаштування: %s", str(e), exc_info=True)
                messagebox.showerror("Помилка", f"Не вдалося зберегти налаштування: {e}")
        except Exception as e:
            logging.error("Не вдалося зберегти налаштування: %s", str(e), exc_info=True)
            messagebox.showerror("Помилка", f"Не вдалося зберегти налаштування: {e}")
            
    def load_settings(self):
        """Завантаження налаштувань"""
        try:
            # Спробуємо використати Pydantic Settings
            try:
                from baloon.settings import BalloonSettings
                settings_obj = BalloonSettings.load_from_file()
                settings = settings_obj.to_dict()
                logging.info("Завантажено налаштування через Pydantic Settings")
            except ImportError:
                # Fallback на старий спосіб
                if os.path.exists('balloon_settings.json'):
                    with open('balloon_settings.json', 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    logging.info("Завантажено налаштування: %s", settings)
                else:
                    return
                
            # Встановлення значень (для обох випадків)
            self.mode_var.set(settings.get('mode', 'payload'))
            self.material_var.set(settings.get('material', 'TPU'))
            self.gas_var.set(settings.get('gas', 'Гелій'))
            if 'shape_type' in settings:
                self.shape_var.set(settings.get('shape_type'))
            
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
                
                if 'extra_mass' in settings and 'extra_mass' in self.entries:
                    self.entries['extra_mass'].delete(0, tk.END)
                    self.entries['extra_mass'].insert(0, settings['extra_mass'])
                
                if 'seam_factor' in settings and 'seam_factor' in self.entries:
                    self.entries['seam_factor'].delete(0, tk.END)
                    self.entries['seam_factor'].insert(0, settings['seam_factor'])
                
                # Форма та параметри
                for key in ['pillow_len','pillow_wid','pear_height','pear_top_radius','pear_bottom_radius','cigar_length','cigar_radius']:
                    if key in settings and key in self.entries:
                        self.entries[key].delete(0, tk.END)
                        self.entries[key].insert(0, settings[key])
                    
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
        # Форма
        if 'shape_type' in self.entries:
            self.entries['shape_type'].set(self.shape_code_to_display.get(FIELD_DEFAULTS['shape_type'], "Сфера"))
        for key in ['pillow_len','pillow_wid','pear_height','pear_top_radius','pear_bottom_radius','cigar_length','cigar_radius']:
            if key in self.entries:
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, FIELD_DEFAULTS.get(key, ""))
        
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
                'mode': self.mode_var.get(),
                'shape_type': self.shape_display_to_code.get(self.entries['shape_type'].get(), 'sphere'),
                'shape_params': {
                    'pillow_len': self.entries.get('pillow_len').get() if 'pillow_len' in self.entries else None,
                    'pillow_wid': self.entries.get('pillow_wid').get() if 'pillow_wid' in self.entries else None,
                }
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
                'max_height': 10000,  # Збільшено до 10 км
                'shape_type': validated_strings.get('shape_type', 'sphere'),
                'shape_params': {k: validated_numbers[k] for k in validated_numbers if k.startswith('pillow_') and k != 'pillow_height'},
                'extra_mass': validated_numbers.get('extra_mass', 0.0),
                'seam_factor': validated_numbers.get('seam_factor', 1.0),
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
                height=total_height,
                extra_mass=validated_numbers.get('extra_mass', 0.0),
                seam_factor=validated_numbers.get('seam_factor', 1.0),
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
                inside_temp=validated_numbers['inside_temp'],
                extra_mass=validated_numbers.get('extra_mass', 0.0),
                seam_factor=validated_numbers.get('seam_factor', 1.0),
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
    
    def create_patterns_section(self, parent):
        """Створення розділу для викрійок/патернів"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=0)  # control_frame не розтягується
        parent.rowconfigure(1, weight=1)  # content_frame розтягується
        
        # Верхня панель з параметрами
        control_frame = ttk.Frame(parent, style="Card.TFrame", padding="12")
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        control_frame.columnconfigure(0, minsize=150)  # Мінімальна ширина для лейблів
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(2, weight=0)  # Колонка для підказок
        
        # Заголовок
        ttk.Label(control_frame, text="Розрахунок викрійок/патернів", style="Heading.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )
        
        # Параметри для викрійок
        row = 1
        ttk.Label(control_frame, text="Форма:").grid(row=row, column=0, sticky="w")
        self.pattern_shape_var = tk.StringVar(value="Сфера")
        pattern_shape_combo = ttk.Combobox(
            control_frame,
            textvariable=self.pattern_shape_var,
            values=COMBOBOX_VALUES['shape_type'],
            state="readonly",
            width=20
        )
        pattern_shape_combo.grid(row=row, column=1, sticky="w", padx=(10, 0))
        pattern_shape_combo.bind("<<ComboboxSelected>>", lambda e: self.update_3d_preview())
        row += 1
        
        ttk.Label(control_frame, text="Кількість сегментів:").grid(row=row, column=0, sticky="w")
        self.pattern_segments_var = tk.StringVar(value="12")
        pattern_segments_entry = ttk.Entry(control_frame, textvariable=self.pattern_segments_var, width=10)
        pattern_segments_entry.grid(row=row, column=1, sticky="w", padx=(10, 0))
        ttk.Label(control_frame, text="(для сфери)", font=("Segoe UI", 8), foreground="#888888").grid(
            row=row, column=2, sticky="w", padx=(5, 0)
        )
        row += 1
        
        # Кнопка генерації
        generate_btn = ttk.Button(
            control_frame,
            text="Згенерувати викрійку",
            command=self.generate_pattern,
            style="Accent.TButton"
        )
        generate_btn.grid(row=row, column=0, columnspan=3, pady=(15, 5), sticky="ew", padx=5)
        if TTKBOOTSTRAP_AVAILABLE:
            generate_btn.configure(bootstyle=SUCCESS)
        
        # Область для візуалізації та інформації
        content_frame = ttk.Frame(parent)
        content_frame.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        content_frame.columnconfigure(0, weight=2)  # Візуалізація патерну
        content_frame.columnconfigure(1, weight=1)  # 3D модель
        content_frame.columnconfigure(2, weight=1)  # Інформація
        content_frame.rowconfigure(0, weight=1)
        
        # Ліва частина - візуалізація патерну
        viz_frame = ttk.Frame(content_frame, style="Card.TFrame", padding="10")
        viz_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(1, weight=1)
        
        ttk.Label(viz_frame, text="Візуалізація патерну", style="Subheading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )
        
        # Canvas для малювання патерну
        self.pattern_canvas = tk.Canvas(
            viz_frame,
            bg="#1e1e1e",
            highlightthickness=1,
            highlightbackground="#555555"
        )
        self.pattern_canvas.grid(row=1, column=0, sticky="nsew")
        
        # Обробка зміни розміру canvas
        def on_canvas_configure(event):
            if hasattr(self, 'current_pattern'):
                self.visualize_pattern(self.current_pattern)
        self.pattern_canvas.bind('<Configure>', on_canvas_configure)
        
        # Середня частина - 3D модель
        model_frame = ttk.Frame(content_frame, style="Card.TFrame", padding="10")
        model_frame.grid(row=0, column=1, sticky="nsew", padx=6)
        self.create_3d_preview_section(model_frame)
        
        # Права частина - інформація
        info_frame = ttk.Frame(content_frame, style="Card.TFrame", padding="10")
        info_frame.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Інформація про патерн", style="Subheading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )
        
        # Text widget для інформації
        self.pattern_info_text = tk.Text(
            info_frame,
            wrap="word",
            font=("Courier New", 10),
            bg="#1e1e1e",
            fg="#ffffff",
            relief="sunken",
            borderwidth=2,
            padx=10,
            pady=10,
            state="disabled"
        )
        self.pattern_info_text.grid(row=1, column=0, sticky="nsew")
        
        # Scrollbar для тексту
        pattern_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.pattern_info_text.yview)
        pattern_scrollbar.grid(row=1, column=1, sticky="ns")
        self.pattern_info_text.configure(yscrollcommand=pattern_scrollbar.set)
        
        # Кнопки експорту
        export_frame = ttk.Frame(parent)
        export_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(
            export_frame,
            text="Експортувати викрійку (PNG)",
            command=self.export_pattern
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            export_frame,
            text="Експортувати дані (CSV)",
            command=self.export_pattern_data
        ).pack(side="left")
    
    def generate_pattern(self):
        """Генерує викрійку на основі параметрів"""
        try:
            # Отримуємо параметри з полів розрахунків або з полів викрійок
            shape_display = self.pattern_shape_var.get()
            shape_code = self.shape_display_to_code.get(shape_display, 'sphere')
            
            # Спробуємо отримати параметри з результатів розрахунків
            shape_params = {}
            
            if shape_code == "sphere":
                # Для сфери потрібен радіус
                if hasattr(self, 'last_calculation_results') and 'radius' in self.last_calculation_results:
                    radius = self.last_calculation_results['radius']
                    shape_params = {'radius': radius}
                else:
                    # Спробуємо розрахувати з об'єму
                    try:
                        gas_volume = float(self.entries['gas_volume'].get())
                        from baloon.shapes import sphere_radius_from_volume
                        radius = sphere_radius_from_volume(gas_volume)
                        shape_params = {'radius': radius}
                    except:
                        messagebox.showerror("Помилка", "Не вдалося визначити радіус сфери. Спочатку виконайте розрахунок.")
                        return
            
            elif shape_code == "pillow":
                if hasattr(self, 'last_calculation_results'):
                    shape_params = self.last_calculation_results.get('shape_params', {})
                if not shape_params:
                    try:
                        shape_params = {
                            'pillow_len': float(self.entries.get('pillow_len', ttk.Entry()).get() or "3.0"),
                            'pillow_wid': float(self.entries.get('pillow_wid', ttk.Entry()).get() or "2.0")
                        }
                    except:
                        messagebox.showerror("Помилка", "Введіть параметри подушки або виконайте розрахунок.")
                        return
            
            elif shape_code == "pear":
                if hasattr(self, 'last_calculation_results'):
                    shape_params = self.last_calculation_results.get('shape_params', {})
                if not shape_params:
                    try:
                        shape_params = {
                            'pear_height': float(self.entries.get('pear_height', ttk.Entry()).get() or "3.0"),
                            'pear_top_radius': float(self.entries.get('pear_top_radius', ttk.Entry()).get() or "1.2"),
                            'pear_bottom_radius': float(self.entries.get('pear_bottom_radius', ttk.Entry()).get() or "0.6")
                        }
                    except:
                        messagebox.showerror("Помилка", "Введіть параметри груші або виконайте розрахунок.")
                        return
            
            elif shape_code == "cigar":
                if hasattr(self, 'last_calculation_results'):
                    shape_params = self.last_calculation_results.get('shape_params', {})
                if not shape_params:
                    try:
                        shape_params = {
                            'cigar_length': float(self.entries.get('cigar_length', ttk.Entry()).get() or "5.0"),
                            'cigar_radius': float(self.entries.get('cigar_radius', ttk.Entry()).get() or "1.0")
                        }
                    except:
                        messagebox.showerror("Помилка", "Введіть параметри сигари або виконайте розрахунок.")
                        return
            
            # Кількість сегментів
            try:
                num_segments = int(self.pattern_segments_var.get())
                if num_segments < 4:
                    num_segments = 4
                if num_segments > 32:
                    num_segments = 32
            except:
                num_segments = 12
            
            # Генеруємо патерн
            pattern = generate_pattern_from_shape(shape_code, shape_params, num_segments)
            self.current_pattern = pattern
            
            # Візуалізуємо
            self.visualize_pattern(pattern)
            
            # Оновлюємо 3D прев'ю
            self.update_3d_preview()
            
            # Показуємо інформацію
            self.show_pattern_info(pattern)
            
        except Exception as e:
            import logging
            logging.error(f"Помилка генерації викрійки: {e}", exc_info=True)
            messagebox.showerror("Помилка", f"Не вдалося згенерувати викрійку: {e}")
    
    def visualize_pattern(self, pattern):
        """Візуалізує патерн на canvas"""
        self.pattern_canvas.delete("all")
        
        canvas_width = self.pattern_canvas.winfo_width()
        canvas_height = self.pattern_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 400
            canvas_height = 500
        
        pattern_type = pattern.get('pattern_type')
        
        if pattern_type == 'sphere_gore':
            self._draw_sphere_gore(pattern, canvas_width, canvas_height)
        elif pattern_type == 'pillow':
            self._draw_pillow_pattern(pattern, canvas_width, canvas_height)
        elif pattern_type == 'pear_gore':
            self._draw_pear_pattern(pattern, canvas_width, canvas_height)
        elif pattern_type == 'cigar_gore':
            self._draw_cigar_pattern(pattern, canvas_width, canvas_height)
    
    def _draw_sphere_gore(self, pattern, width, height):
        """Малює гобеновий сегмент для сфери"""
        points = pattern.get('points', [])
        if not points:
            return
        
        max_y = max(abs(y) for x, y in points)
        max_x = max(abs(x) for x, y in points)
        
        scale_x = (width * 0.8) / (2 * max_x) if max_x > 0 else 1
        scale_y = (height * 0.8) / (2 * max_y) if max_y > 0 else 1
        scale = min(scale_x, scale_y)
        
        center_x = width / 2
        center_y = height / 2
        
        path = []
        for x, y in points:
            px = center_x + x * scale
            py = center_y - y * scale
            path.append((px, py))
        
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            self.pattern_canvas.create_line(x1, y1, x2, y2, fill="#4a90e2", width=2)
        
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            self.pattern_canvas.create_line(
                center_x - (x1 - center_x), y1,
                center_x - (x2 - center_x), y2,
                fill="#4a90e2", width=2
            )
        
        if path:
            first_x, first_y = path[0]
            last_x, last_y = path[-1]
            self.pattern_canvas.create_line(
                center_x, first_y, center_x, last_y,
                fill="#ffffff", width=1, dash=(5, 5)
            )
        
        # Додаємо розміри та анотації
        radius = pattern.get('radius', 0)
        max_width = pattern.get('max_width', 0)
        total_height = pattern.get('total_height', 0)
        
        self.pattern_canvas.create_text(
            center_x, 20, text=f"Сегмент (1 з {pattern.get('num_gores', 12)})",
            fill="#ffffff", font=("Arial", 11, "bold")
        )
        
        # Показуємо розміри
        if max_width > 0:
            # Максимальна ширина
            max_width_x = center_x + max_width * scale / 2
            self.pattern_canvas.create_line(
                center_x, center_y - max_width * scale / 2,
                max_width_x, center_y - max_width * scale / 2,
                fill="#66d17c", width=1, dash=(3, 3)
            )
            self.pattern_canvas.create_text(
                (center_x + max_width_x) / 2, center_y - max_width * scale / 2 - 10,
                text=f"Макс. ширина: {max_width:.2f} м",
                fill="#66d17c", font=("Arial", 8)
            )
        
        if total_height > 0:
            # Висота
            self.pattern_canvas.create_line(
                center_x + max_x * scale + 10, center_y - total_height * scale / 2,
                center_x + max_x * scale + 10, center_y + total_height * scale / 2,
                fill="#66d17c", width=1, dash=(3, 3)
            )
            self.pattern_canvas.create_text(
                center_x + max_x * scale + 15, center_y,
                text=f"Висота: {total_height:.2f} м",
                fill="#66d17c", font=("Arial", 8), anchor="w"
            )
        
        if radius > 0:
            self.pattern_canvas.create_text(
                center_x, height - 30,
                text=f"Радіус сфери: {radius:.2f} м",
                fill="#888888", font=("Arial", 9)
            )
    
    def _draw_pillow_pattern(self, pattern, width, height):
        """Малює патерн для подушки - два прямокутники з позначенням отвору"""
        panels = pattern.get('panels', [])
        if not panels:
            return
        
        # Малюємо два прямокутники однакового розміру
        panel_w = panels[0].get('width', 0) if panels else 0
        panel_h = panels[0].get('height', 0) if panels else 0
        
        if panel_w <= 0 or panel_h <= 0:
            return
        
        # Масштабування для обох панелей
        max_dim = max(panel_w, panel_h)
        scale_w = (width * 0.7) / max_dim if max_dim > 0 else 1
        scale_h = (height * 0.35) / max_dim if max_dim > 0 else 1
        scale = min(scale_w, scale_h)
        
        w = panel_w * scale
        h = panel_h * scale
        
        # Центруємо
        center_x = width / 2
        spacing = 20  # Відстань між панелями
        
        # Перша панель (верхня)
        x1_1 = center_x - w / 2
        y1_1 = height * 0.15
        x2_1 = x1_1 + w
        y2_1 = y1_1 + h
        
        self.pattern_canvas.create_rectangle(x1_1, y1_1, x2_1, y2_1, outline="#4a90e2", width=2)
        self.pattern_canvas.create_text(
            center_x, y1_1 - 15, text="Панель 1",
            fill="#ffffff", font=("Arial", 10, "bold")
        )
        
        # Друга панель (нижня)
        x1_2 = center_x - w / 2
        y1_2 = y2_1 + spacing
        x2_2 = x1_2 + w
        y2_2 = y1_2 + h
        
        self.pattern_canvas.create_rectangle(x1_2, y1_2, x2_2, y2_2, outline="#4a90e2", width=2)
        self.pattern_canvas.create_text(
            center_x, y1_2 - 15, text="Панель 2",
            fill="#ffffff", font=("Arial", 10, "bold")
        )
        
        # Позначаємо отвір (незакрита ділянка кромки)
        opening_side = pattern.get('opening_side', 'width')
        opening_size = pattern.get('opening_size', 0)
        
        # Позначаємо лінії з'єднання (шви) - зеленою пунктирною лінією
        seam_color = "#66d17c"
        
        if opening_side == 'width':
            # Отвір на коротшій стороні (ширина) - ліва сторона не зшивається
            # Шви: верх, низ, права сторона
            self.pattern_canvas.create_line(x1_2, y1_2, x2_2, y1_2, fill=seam_color, width=2, dash=(5, 3))  # Верх
            self.pattern_canvas.create_line(x1_2, y2_2, x2_2, y2_2, fill=seam_color, width=2, dash=(5, 3))  # Низ
            self.pattern_canvas.create_line(x2_2, y1_2, x2_2, y2_2, fill=seam_color, width=2, dash=(5, 3))  # Права
            
            # Позначаємо незакриту кромку (отвір) - ліва сторона
            opening_y = y1_2 + h / 2
            self.pattern_canvas.create_line(
                x1_2, y1_2,
                x1_2, y2_2,
                fill="#ff6b6b", width=3, dash=(10, 5)
            )
            self.pattern_canvas.create_text(
                x1_2 - 15, opening_y, text="НЕ ЗШИВАТИ\n(отвір)",
                fill="#ff6b6b", font=("Arial", 9, "bold"), anchor="e", justify="center"
            )
        else:
            # Отвір на довгій стороні (довжина) - верхня сторона не зшивається
            # Шви: ліва, права, низ
            self.pattern_canvas.create_line(x1_2, y1_2, x1_2, y2_2, fill=seam_color, width=2, dash=(5, 3))  # Ліва
            self.pattern_canvas.create_line(x2_2, y1_2, x2_2, y2_2, fill=seam_color, width=2, dash=(5, 3))  # Права
            self.pattern_canvas.create_line(x1_2, y2_2, x2_2, y2_2, fill=seam_color, width=2, dash=(5, 3))  # Низ
            
            # Позначаємо незакриту кромку (отвір) - верхня сторона
            opening_x = center_x
            self.pattern_canvas.create_line(
                x1_2, y1_2,
                x2_2, y1_2,
                fill="#ff6b6b", width=3, dash=(10, 5)
            )
            self.pattern_canvas.create_text(
                opening_x, y1_2 - 20, text="НЕ ЗШИВАТИ (отвір)",
                fill="#ff6b6b", font=("Arial", 9, "bold"), anchor="s"
            )
    
    def _draw_pear_pattern(self, pattern, width, height):
        """Малює гобеновий сегмент для груші"""
        points = pattern.get('points', [])
        if not points:
            return
        
        max_y = max(y for x, y in points) if points else 1
        max_x = max(x for x, y in points) if points else 1
        
        scale_x = (width * 0.8) / (2 * max_x) if max_x > 0 else 1
        scale_y = (height * 0.8) / max_y if max_y > 0 else 1
        scale = min(scale_x, scale_y)
        
        center_x = width / 2
        center_y = height / 2
        
        # Малюємо сегмент
        coords = []
        for x, y in points:
            # Для груші y йде від низу (0) до верху (height)
            # Перетворюємо координати
            screen_x = center_x + x * scale
            screen_y = center_y + (y - max_y / 2) * scale  # Y від низу до верху
            coords.append((screen_x, screen_y))
        
        # Малюємо ліву половину сегмента
        if len(coords) > 1:
            for i in range(len(coords) - 1):
                x1, y1 = coords[i]
                x2, y2 = coords[i + 1]
                self.pattern_canvas.create_line(x1, y1, x2, y2, fill="#4a90e2", width=2)
        
        # Малюємо праву половину (дзеркально)
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            # Дзеркалюємо відносно центру
            x1_mirror = center_x - (x1 - center_x)
            x2_mirror = center_x - (x2 - center_x)
            self.pattern_canvas.create_line(x1_mirror, y1, x2_mirror, y2, fill="#4a90e2", width=2)
        
        # Додаємо підписи
        num_gores = pattern.get('num_gores', 12)
        pear_height = pattern.get('height', 3.0)
        top_radius = pattern.get('top_radius', 1.2)
        bottom_radius = pattern.get('bottom_radius', 0.6)
        
        self.pattern_canvas.create_text(
            center_x, 20, text=f"Сегмент груші ({num_gores} сегментів)",
            fill="#ffffff", font=("Arial", 12, "bold")
        )
        self.pattern_canvas.create_text(
            center_x, height - 40, 
            text=f"Висота: {pear_height:.2f} м\nВерхній радіус: {top_radius:.2f} м\nНижній радіус: {bottom_radius:.2f} м",
            fill="#cccccc", font=("Arial", 9), justify="center"
        )
    
    def _draw_cigar_pattern(self, pattern, width, height):
        """Малює гобеновий сегмент для сигари"""
        points = pattern.get('points', [])
        if not points:
            return
        
        max_y = max(y for x, y in points) if points else 1
        max_x = max(x for x, y in points) if points else 1
        
        scale_x = (width * 0.8) / (2 * max_x) if max_x > 0 else 1
        scale_y = (height * 0.8) / max_y if max_y > 0 else 1
        scale = min(scale_x, scale_y)
        
        center_x = width / 2
        center_y = height / 2
        
        # Малюємо сегмент
        coords = []
        for x, y in points:
            # Для сигари y йде вздовж осі (від 0 до length)
            screen_x = center_x + x * scale
            screen_y = center_y + (y - max_y / 2) * scale  # Y від низу до верху
            coords.append((screen_x, screen_y))
        
        # Малюємо ліву половину сегмента
        if len(coords) > 1:
            for i in range(len(coords) - 1):
                x1, y1 = coords[i]
                x2, y2 = coords[i + 1]
                self.pattern_canvas.create_line(x1, y1, x2, y2, fill="#4a90e2", width=2)
        
        # Малюємо праву половину (дзеркально)
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            # Дзеркалюємо відносно центру
            x1_mirror = center_x - (x1 - center_x)
            x2_mirror = center_x - (x2 - center_x)
            self.pattern_canvas.create_line(x1_mirror, y1, x2_mirror, y2, fill="#4a90e2", width=2)
        
        # Додаємо підписи
        num_gores = pattern.get('num_gores', 12)
        cigar_length = pattern.get('length', 5.0)
        radius = pattern.get('radius', 1.0)
        
        self.pattern_canvas.create_text(
            center_x, 20, text=f"Сегмент сигари ({num_gores} сегментів)",
            fill="#ffffff", font=("Arial", 12, "bold")
        )
        self.pattern_canvas.create_text(
            center_x, height - 40, 
            text=f"Довжина: {cigar_length:.2f} м\nРадіус: {radius:.2f} м",
            fill="#cccccc", font=("Arial", 9), justify="center"
        )
    
    def show_pattern_info(self, pattern):
        """Показує інформацію про патерн"""
        self.pattern_info_text.config(state="normal")
        self.pattern_info_text.delete(1.0, tk.END)
        
        info = []
        info.append("=" * 50)
        info.append("ІНФОРМАЦІЯ ПРО ВИКРІЙКУ")
        info.append("=" * 50)
        info.append("")
        info.append(f"Тип: {pattern.get('description', '')}")
        info.append("")
        
        pattern_type = pattern.get('pattern_type')
        
        if pattern_type == 'sphere_gore':
            info.append(f"Кількість сегментів: {pattern.get('num_gores', 12)}")
            info.append(f"Радіус сфери: {pattern.get('radius', 0):.2f} м")
            info.append(f"Максимальна ширина сегмента: {pattern.get('max_width', 0):.2f} м")
            info.append(f"Висота сегмента: {pattern.get('total_height', 0):.2f} м")
            info.append(f"Площа одного сегмента: {pattern.get('gore_area', 0):.2f} м²")
            info.append(f"Загальна площа: {pattern.get('total_area', 0):.2f} м²")
        
        elif pattern_type == 'pillow':
            panels = pattern.get('panels', [])
            info.append(f"Довжина: {pattern.get('length', 0):.2f} м")
            info.append(f"Ширина: {pattern.get('width', 0):.2f} м")
            info.append(f"Товщина: {pattern.get('thickness', 0):.2f} м")
            info.append("")
            info.append("Панелі (2 шт, однакові):")
            if panels:
                panel = panels[0]
                info.append(f"  Розмір: {panel.get('width', 0):.2f} × {panel.get('height', 0):.2f} м")
                info.append(f"  Площа однієї панелі: {panel.get('area', 0):.2f} м²")
            info.append(f"Загальна площа: {pattern.get('total_area', 0):.2f} м²")
            info.append("")
            opening_side = pattern.get('opening_side', 'width')
            opening_size = pattern.get('opening_size', 0)
            side_name = "ширина" if opening_side == 'width' else "довжина"
            info.append(f"Незакрита кромка (отвір): на стороні '{side_name}', довжина: {opening_size:.2f} м")
            info.append("(ця ділянка кромки не зшивається, для заповнення газу)")
        
        elif pattern_type == 'pear_gore':
            info.append(f"Кількість сегментів: {pattern.get('num_gores', 12)}")
            info.append(f"Висота груші: {pattern.get('height', 0):.2f} м")
            info.append(f"Верхній радіус: {pattern.get('top_radius', 0):.2f} м")
            info.append(f"Нижній радіус: {pattern.get('bottom_radius', 0):.2f} м")
            info.append(f"Максимальна ширина сегмента: {pattern.get('max_width', 0):.2f} м")
            info.append(f"Висота сегмента: {pattern.get('total_height', 0):.2f} м")
            info.append(f"Площа одного сегмента: {pattern.get('gore_area', 0):.2f} м²")
            info.append(f"Загальна площа: {pattern.get('total_area', 0):.2f} м²")
        
        seam_length = calculate_seam_length(pattern)
        info.append("")
        info.append(f"Загальна довжина швів: {seam_length:.2f} м")
        
        self.pattern_info_text.insert(1.0, "\n".join(info))
        self.pattern_info_text.config(state="disabled")
    
    def export_results(self):
        """Експортує результати розрахунку в Excel"""
        if not hasattr(self, 'last_calculation_results') or not self.last_calculation_results:
            messagebox.showwarning("Попередження", "Спочатку виконайте розрахунок")
            return
        
        try:
            from baloon.export import export_results_to_excel
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel файли", "*.xlsx"), ("Всі файли", "*.*")],
                title="Зберегти результати розрахунку"
            )
            
            if filename:
                filepath = export_results_to_excel(self.last_calculation_results, filename)
                messagebox.showinfo("Успіх", f"Результати збережено:\n{filepath}")
        except ImportError:
            messagebox.showerror("Помилка", "Для експорту в Excel потрібна бібліотека pandas. Встановіть: pip install pandas openpyxl")
        except Exception as e:
            logging.error(f"Помилка експорту результатів: {e}", exc_info=True)
            messagebox.showerror("Помилка", f"Не вдалося експортувати результати: {e}")
    
    def export_pattern(self):
        """Експортує викрійку (SVG/PNG)"""
        # Спробуємо також експортувати в Excel, якщо доступний
        try:
            if hasattr(self, 'current_pattern') and self.current_pattern:
                try:
                    from baloon.export import export_pattern_to_excel
                    from tkinter import filedialog
                    
                    # Пропонуємо експорт в Excel
                    result = messagebox.askyesnocancel(
                        "Експорт викрійки",
                        "Оберіть формат експорту:\n\n"
                        "Так - Excel файл\n"
                        "Ні - SVG/PNG файл\n"
                        "Скасувати - вихід"
                    )
                    
                    if result is True:  # Excel
                        filename = filedialog.asksaveasfilename(
                            defaultextension=".xlsx",
                            filetypes=[("Excel файли", "*.xlsx"), ("Всі файли", "*.*")],
                            title="Зберегти викрійку"
                        )
                        if filename:
                            filepath = export_pattern_to_excel(self.current_pattern, filename)
                            messagebox.showinfo("Успіх", f"Викрійку збережено:\n{filepath}")
                            return
                    elif result is False:  # SVG/PNG - продовжуємо старий код
                        pass
                    else:  # Cancel
                        return
                except ImportError:
                    pass  # Якщо pandas недоступний, продовжуємо зі старим експортом
                except Exception as e:
                    logging.warning(f"Помилка експорту в Excel: {e}")
                    # Продовжуємо зі старим експортом
        except Exception:
            pass  # Якщо щось пішло не так, продовжуємо зі старим експортом
        
        # Старий код експорту SVG/PNG
        if not hasattr(self, 'current_pattern'):
            messagebox.showwarning("Попередження", "Спочатку згенеруйте викрійку")
            return
        
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            if filename:
                plt = get_plt()
                fig, ax = plt.subplots(figsize=(10, 12))
                ax.set_aspect('equal')
                ax.axis('off')
                ax.set_facecolor('#1e1e1e')
                fig.patch.set_facecolor('#1e1e1e')
                
                pattern = self.current_pattern
                pattern_type = pattern.get('pattern_type')
                
                if pattern_type == 'sphere_gore':
                    points = pattern.get('points', [])
                    if points:
                        xs = [x for x, y in points]
                        ys = [y for x, y in points]
                        ax.plot(xs, ys, 'b-', linewidth=2)
                        ax.plot([-x for x in xs], ys, 'b-', linewidth=2)
                        ax.axvline(0, color='white', linestyle='--', alpha=0.5)
                
                plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='#1e1e1e')
                plt.close()
                messagebox.showinfo("Успіх", f"Викрійку збережено: {filename}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося експортувати: {e}")
    
    def export_pattern_data(self):
        """Експортує дані викрійки як CSV"""
        if not hasattr(self, 'current_pattern'):
            messagebox.showwarning("Попередження", "Спочатку згенеруйте викрійку")
            return
        
        try:
            import csv
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if filename:
                pattern = self.current_pattern
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Параметр', 'Значення'])
                    writer.writerow(['Тип', pattern.get('description', '')])
                    
                    if pattern.get('pattern_type') == 'sphere_gore':
                        points = pattern.get('points', [])
                        writer.writerow(['', ''])
                        writer.writerow(['Координати сегмента', ''])
                        writer.writerow(['X (м)', 'Y (м)'])
                        for x, y in points:
                            writer.writerow([f"{x:.4f}", f"{y:.4f}"])
                
                messagebox.showinfo("Успіх", f"Дані збережено: {filename}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося експортувати: {e}")
    
    def show_3d_model(self):
        """Показує 3D модель кулі"""
        try:
            # Отримуємо параметри з останнього розрахунку або з поточного патерну
            shape_code = None
            shape_params = {}
            
            if hasattr(self, 'current_pattern'):
                pattern = self.current_pattern
                pattern_type = pattern.get('pattern_type')
                
                if pattern_type == 'sphere_gore':
                    shape_code = 'sphere'
                    radius = pattern.get('radius', 1.0)
                    shape_params = {'radius': radius}
                elif pattern_type == 'pillow':
                    shape_code = 'pillow'
                    shape_params = {
                        'pillow_len': pattern.get('length', 3.0),
                        'pillow_wid': pattern.get('width', 2.0)
                    }
                elif pattern_type == 'pear_gore':
                    shape_code = 'pear'
                    shape_params = {
                        'pear_height': pattern.get('height', 3.0),
                        'pear_top_radius': pattern.get('top_radius', 1.2),
                        'pear_bottom_radius': pattern.get('bottom_radius', 0.6)
                    }
                elif pattern_type == 'cigar_gore':
                    shape_code = 'cigar'
                    shape_params = {
                        'cigar_length': pattern.get('length', 5.0),
                        'cigar_radius': pattern.get('radius', 1.0)
                    }
            
            # Якщо немає патерну, спробуємо отримати з останнього розрахунку
            if not shape_code and hasattr(self, 'last_calculation_results'):
                results = self.last_calculation_results
                shape_code = results.get('shape_type', 'sphere')
                # Отримуємо shape_params з results
                shape_params = results.get('shape_params', {}) or {}
                
                # Якщо shape_params порожній, спробуємо отримати з results напряму
                if not shape_params:
                    if shape_code == 'sphere' and 'radius' in results:
                        shape_params = {'radius': results['radius']}
                    elif shape_code == 'pear':
                        shape_params = {
                            'pear_height': results.get('pear_height', 3.0),
                            'pear_top_radius': results.get('pear_top_radius', 1.2),
                            'pear_bottom_radius': results.get('pear_bottom_radius', 0.6)
                        }
                    elif shape_code == 'cigar':
                        shape_params = {
                            'cigar_length': results.get('cigar_length', 5.0),
                            'cigar_radius': results.get('cigar_radius', 1.0)
                        }
                    elif shape_code == 'pillow':
                        shape_params = {
                            'pillow_len': results.get('pillow_len', 3.0),
                            'pillow_wid': results.get('pillow_wid', 2.0)
                        }
                
                # Якщо все ще немає параметрів, спробуємо з полів
                if shape_code == 'pear' and not shape_params:
                    # Якщо немає параметрів, спробуємо з полів
                    try:
                        shape_params = {
                            'pear_height': float(self.entries.get('pear_height', ttk.Entry()).get() or "3.0"),
                            'pear_top_radius': float(self.entries.get('pear_top_radius', ttk.Entry()).get() or "1.2"),
                            'pear_bottom_radius': float(self.entries.get('pear_bottom_radius', ttk.Entry()).get() or "0.6")
                        }
                    except:
                        shape_params = {'pear_height': 3.0, 'pear_top_radius': 1.2, 'pear_bottom_radius': 0.6}
                elif shape_code == 'cigar' and not shape_params:
                    # Якщо немає параметрів, спробуємо з полів
                    try:
                        shape_params = {
                            'cigar_length': float(self.entries.get('cigar_length', ttk.Entry()).get() or "5.0"),
                            'cigar_radius': float(self.entries.get('cigar_radius', ttk.Entry()).get() or "1.0")
                        }
                    except:
                        shape_params = {'cigar_length': 5.0, 'cigar_radius': 1.0}
                elif shape_code == 'pillow' and not shape_params:
                    # Якщо немає параметрів, спробуємо з полів
                    try:
                        shape_params = {
                            'pillow_len': float(self.entries.get('pillow_len', ttk.Entry()).get() or "3.0"),
                            'pillow_wid': float(self.entries.get('pillow_wid', ttk.Entry()).get() or "2.0")
                        }
                    except:
                        shape_params = {'pillow_len': 3.0, 'pillow_wid': 2.0}
            
            # Якщо все ще немає, спробуємо з полів
            if not shape_code:
                shape_display = self.pattern_shape_var.get()
                shape_code = self.shape_display_to_code.get(shape_display, 'sphere')
                if shape_code == 'sphere':
                    try:
                        if hasattr(self, 'last_calculation_results') and 'radius' in self.last_calculation_results:
                            radius = self.last_calculation_results['radius']
                        else:
                            gas_volume = float(self.entries['gas_volume'].get() or "1.0")
                            from baloon.shapes import sphere_radius_from_volume
                            radius = sphere_radius_from_volume(gas_volume)
                        shape_params = {'radius': radius}
                    except:
                        shape_params = {'radius': 1.0}
                elif shape_code == 'pillow':
                    try:
                        shape_params = {
                            'pillow_len': float(self.entries.get('pillow_len', ttk.Entry()).get() or "3.0"),
                            'pillow_wid': float(self.entries.get('pillow_wid', ttk.Entry()).get() or "2.0")
                        }
                    except:
                        shape_params = {'pillow_len': 3.0, 'pillow_wid': 2.0}
                elif shape_code == 'pear':
                    try:
                        shape_params = {
                            'pear_height': float(self.entries.get('pear_height', ttk.Entry()).get() or "3.0"),
                            'pear_top_radius': float(self.entries.get('pear_top_radius', ttk.Entry()).get() or "1.2"),
                            'pear_bottom_radius': float(self.entries.get('pear_bottom_radius', ttk.Entry()).get() or "0.6")
                        }
                    except:
                        shape_params = {'pear_height': 3.0, 'pear_top_radius': 1.2, 'pear_bottom_radius': 0.6}
                elif shape_code == 'cigar':
                    try:
                        shape_params = {
                            'cigar_length': float(self.entries.get('cigar_length', ttk.Entry()).get() or "5.0"),
                            'cigar_radius': float(self.entries.get('cigar_radius', ttk.Entry()).get() or "1.0")
                        }
                    except:
                        shape_params = {'cigar_length': 5.0, 'cigar_radius': 1.0}
            
            # Якщо все ще немає shape_code, спробуємо з поточного вибору форми
            if not shape_code:
                try:
                    shape_display = self.entries['shape_type'].get()
                    shape_code = self.shape_display_to_code.get(shape_display, 'sphere')
                except:
                    shape_code = 'sphere'
            
            if not shape_code:
                messagebox.showwarning("Попередження", "Спочатку згенеруйте викрійку або виконайте розрахунок")
                return
            
            # Перевіряємо, чи є параметри для форми
            if not shape_params or len(shape_params) == 0:
                # Якщо немає параметрів, спробуємо отримати з полів
                if shape_code == 'pear':
                    try:
                        shape_params = {
                            'pear_height': float(self.entries.get('pear_height', ttk.Entry()).get() or "3.0"),
                            'pear_top_radius': float(self.entries.get('pear_top_radius', ttk.Entry()).get() or "1.2"),
                            'pear_bottom_radius': float(self.entries.get('pear_bottom_radius', ttk.Entry()).get() or "0.6")
                        }
                    except:
                        shape_params = {'pear_height': 3.0, 'pear_top_radius': 1.2, 'pear_bottom_radius': 0.6}
                elif shape_code == 'cigar':
                    try:
                        shape_params = {
                            'cigar_length': float(self.entries.get('cigar_length', ttk.Entry()).get() or "5.0"),
                            'cigar_radius': float(self.entries.get('cigar_radius', ttk.Entry()).get() or "1.0")
                        }
                    except:
                        shape_params = {'cigar_length': 5.0, 'cigar_radius': 1.0}
                elif shape_code == 'pillow':
                    try:
                        shape_params = {
                            'pillow_len': float(self.entries.get('pillow_len', ttk.Entry()).get() or "3.0"),
                            'pillow_wid': float(self.entries.get('pillow_wid', ttk.Entry()).get() or "2.0")
                        }
                    except:
                        shape_params = {'pillow_len': 3.0, 'pillow_wid': 2.0}
                elif shape_code == 'sphere':
                    try:
                        if hasattr(self, 'last_calculation_results') and 'radius' in self.last_calculation_results:
                            radius = self.last_calculation_results['radius']
                        else:
                            gas_volume = float(self.entries['gas_volume'].get() or "1.0")
                            from baloon.shapes import sphere_radius_from_volume
                            radius = sphere_radius_from_volume(gas_volume)
                        shape_params = {'radius': radius}
                    except:
                        shape_params = {'radius': 1.0}
            
            # Додаткова перевірка: якщо shape_code все ще не визначений, спробуємо з поточного вибору
            if not shape_code:
                try:
                    shape_display = self.entries['shape_type'].get()
                    shape_code = self.shape_display_to_code.get(shape_display, 'sphere')
                except:
                    shape_code = 'sphere'
            
            # Логування для діагностики
            logging.info(f"3D візуалізація: shape_code={shape_code}, shape_params={shape_params}")
            
            # Створюємо 3D візуалізацію (спочатку пробуємо Plotly, потім matplotlib)
            self._create_3d_visualization(shape_code, shape_params)
            
        except Exception as e:
            import logging
            logging.error(f"Помилка 3D візуалізації: {e}", exc_info=True)
            messagebox.showerror("Помилка", f"Не вдалося створити 3D модель: {e}")
    
    def _create_3d_visualization(self, shape_code: str, shape_params: dict):
        """Створює 3D візуалізацію кулі (спочатку пробує Plotly, потім matplotlib)"""
        # Спробуємо використати Plotly для інтерактивної візуалізації
        try:
            try:
                from baloon.gui.plotly_3d import create_3d_plotly, show_plotly_3d, is_plotly_available
            except ImportError:
                from gui.plotly_3d import create_3d_plotly, show_plotly_3d, is_plotly_available
            
            if is_plotly_available():
                results = None
                if hasattr(self, 'last_calculation_results'):
                    results = self.last_calculation_results
                
                fig = create_3d_plotly(shape_code, shape_params, results)
                if fig:
                    # Показуємо в браузері
                    show_plotly_3d(fig)
                    return
        except Exception as e:
            import logging
            logging.warning(f"Не вдалося використати Plotly, використовуємо matplotlib: {e}")
        
        # Fallback на matplotlib
        try:
            import numpy as np
            from mpl_toolkits.mplot3d import Axes3D
            
            plt = get_plt()
            fig = plt.figure(figsize=(12, 10))
            ax = fig.add_subplot(111, projection='3d')
            
            # Налаштування темної теми
            fig.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
            ax.xaxis.pane.set_edgecolor('#333333')
            ax.yaxis.pane.set_edgecolor('#333333')
            ax.zaxis.pane.set_edgecolor('#333333')
            ax.xaxis.label.set_color('#ffffff')
            ax.yaxis.label.set_color('#ffffff')
            ax.zaxis.label.set_color('#ffffff')
            ax.tick_params(colors='#ffffff')
            ax.grid(True, color='#444444', linestyle='--', alpha=0.3)
            
            if shape_code == 'sphere':
                radius = shape_params.get('radius', 1.0)
                u = np.linspace(0, 2 * np.pi, 50)
                v = np.linspace(0, np.pi, 50)
                x = radius * np.outer(np.cos(u), np.sin(v))
                y = radius * np.outer(np.sin(u), np.sin(v))
                z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
                ax.plot_surface(x, y, z, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
                ax.set_title(f'Сферична куля\nРадіус: {radius:.2f} м', color='#ffffff', fontsize=14, fontweight='bold')
                
            elif shape_code == 'pillow':
                length = shape_params.get('pillow_len', 3.0)
                width = shape_params.get('pillow_wid', 2.0)
                # Товщина розраховується з об'єму (якщо є)
                # Якщо є об'єм з останнього розрахунку, використовуємо його
                if hasattr(self, 'last_calculation_results'):
                    volume = self.last_calculation_results.get('required_volume', 0)
                    if volume > 0:
                        thickness = volume / (length * width)
                    else:
                        thickness = shape_params.get('thickness', width * 0.3)
                else:
                    thickness = shape_params.get('thickness', width * 0.3)
                
                # Подушка - еліпсоїдна форма (округла форма)
                # Використовуємо параметризацію еліпсоїда
                u = np.linspace(0, 2 * np.pi, 50)
                v = np.linspace(0, np.pi, 50)
                u_grid, v_grid = np.meshgrid(u, v)
                
                # Півосі еліпсоїда
                a = length / 2  # Піввісь по X
                b = width / 2   # Піввісь по Y
                c = thickness / 2  # Піввісь по Z
                
                # Координати еліпсоїда
                x = a * np.cos(u_grid) * np.sin(v_grid)
                y = b * np.sin(u_grid) * np.sin(v_grid)
                z = c * np.cos(v_grid)
                
                # Зсуваємо центр до початку координат
                x = x - a + length / 2
                y = y - b + width / 2
                z = z - c + thickness / 2
                
                ax.plot_surface(x, y, z, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
                
                ax.set_title(f'Подушкоподібна куля (надута)\nДовжина: {length:.2f} м, Ширина: {width:.2f} м, Товщина: {thickness:.2f} м', 
                           color='#ffffff', fontsize=14, fontweight='bold')
            
            elif shape_code == 'pear':
                height = shape_params.get('pear_height', 3.0)
                top_radius = shape_params.get('pear_top_radius', 1.2)
                bottom_radius = shape_params.get('pear_bottom_radius', 0.6)
                
                # Параметризація груші через обертання кривої
                # Використовуємо лінійну інтерполяцію між top_radius та bottom_radius
                u = np.linspace(0, 2 * np.pi, 50)
                v = np.linspace(0, 1, 50)  # Від верху (0) до низу (1)
                u_grid, v_grid = np.meshgrid(u, v)
                
                # Радіус на кожній висоті - лінійна інтерполяція
                r_at_height = top_radius * (1 - v_grid) + bottom_radius * v_grid
                
                # Координати груші (обертання навколо осі Z)
                x = r_at_height * np.cos(u_grid)
                y = r_at_height * np.sin(u_grid)
                z = height * v_grid  # Від низу (0) до верху (height)
                
                # Малюємо поверхню
                ax.plot_surface(x, y, z, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
                
                ax.set_title(f'Грушоподібна куля\nВисота: {height:.2f} м, Верхній радіус: {top_radius:.2f} м, Нижній радіус: {bottom_radius:.2f} м', 
                           color='#ffffff', fontsize=14, fontweight='bold')
            
            elif shape_code == 'cigar':
                length = shape_params.get('cigar_length', 5.0)
                radius = shape_params.get('cigar_radius', 1.0)
                
                # Сигара = циліндр + дві півсфери
                # Довжина циліндричної частини
                cylinder_length = max(0, length - 2 * radius)
                
                # Параметризація для циліндричної частини (якщо вона є)
                if cylinder_length > 0:
                    u_cyl = np.linspace(0, 2 * np.pi, 50)
                    z_cyl = np.linspace(radius, length - radius, 50)
                    u_grid_cyl, z_grid_cyl = np.meshgrid(u_cyl, z_cyl)
                    
                    x_cyl = radius * np.cos(u_grid_cyl)
                    y_cyl = radius * np.sin(u_grid_cyl)
                    z_cyl = z_grid_cyl
                    
                    # Малюємо циліндричну частину
                    ax.plot_surface(x_cyl, y_cyl, z_cyl, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
                
                # Параметризація для півсферичних кінців
                u = np.linspace(0, 2 * np.pi, 50)
                v = np.linspace(0, np.pi / 2, 25)  # Тільки верхня півсфера
                u_grid, v_grid = np.meshgrid(u, v)
                
                # Перший півсферичний кінець (знизу, y=0)
                # Півсфера обертається навколо осі Z, центр на z=radius
                x1 = radius * np.cos(u_grid) * np.sin(v_grid)
                y1 = radius * np.sin(u_grid) * np.sin(v_grid)
                z1 = radius * (1 - np.cos(v_grid))  # Від 0 до radius
                ax.plot_surface(x1, y1, z1, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
                
                # Другий півсферичний кінець (зверху, y=length)
                # Півсфера обертається навколо осі Z, центр на z=length-radius
                x2 = radius * np.cos(u_grid) * np.sin(v_grid)
                y2 = radius * np.sin(u_grid) * np.sin(v_grid)
                z2 = (length - radius) + radius * np.cos(v_grid)  # Від (length-radius) до length
                ax.plot_surface(x2, y2, z2, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
                
                ax.set_title(f'Сигароподібна куля\nДовжина: {length:.2f} м, Радіус: {radius:.2f} м', 
                           color='#ffffff', fontsize=14, fontweight='bold')
            
            # Налаштування осей
            ax.set_xlabel('X (м)', fontsize=10)
            ax.set_ylabel('Y (м)', fontsize=10)
            ax.set_zlabel('Z (м)', fontsize=10)
            
            # Встановлюємо масштаб для осей
            if shape_code == 'sphere':
                max_range = shape_params.get('radius', 1.0) * 1.2
                ax.set_xlim([-max_range, max_range])
                ax.set_ylim([-max_range, max_range])
                ax.set_zlim([-max_range, max_range])
            elif shape_code == 'pillow':
                length = shape_params.get('pillow_len', 3.0)
                width = shape_params.get('pillow_wid', 2.0)
                if hasattr(self, 'last_calculation_results'):
                    volume = self.last_calculation_results.get('required_volume', 0)
                    if volume > 0:
                        thickness = volume / (length * width)
                    else:
                        thickness = shape_params.get('thickness', width * 0.3)
                else:
                    thickness = shape_params.get('thickness', width * 0.3)
                ax.set_xlim([0, length * 1.1])
                ax.set_ylim([0, width * 1.1])
                ax.set_zlim([0, thickness * 1.1])
            elif shape_code == 'pear':
                height = shape_params.get('pear_height', 3.0)
                max_radius = max(shape_params.get('pear_top_radius', 1.2), shape_params.get('pear_bottom_radius', 0.6))
                max_range = max(height, max_radius * 2) * 1.2
                ax.set_xlim([-max_range, max_range])
                ax.set_ylim([-max_range, max_range])
                ax.set_zlim([0, height * 1.1])
            elif shape_code == 'cigar':
                length = shape_params.get('cigar_length', 5.0)
                radius = shape_params.get('cigar_radius', 1.0)
                max_range = max(length, radius * 2) * 1.2
                ax.set_xlim([-max_range, max_range])
                ax.set_ylim([-max_range, max_range])
                ax.set_zlim([0, length * 1.1])
            
            # Додаємо інформацію про об'єм та площу
            if hasattr(self, 'last_calculation_results'):
                results = self.last_calculation_results
                volume = results.get('required_volume', 0)
                surface = results.get('surface_area', 0)
                info_text = f"Об'єм: {volume:.2f} м³\nПлоща поверхні: {surface:.2f} м²"
                ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes, 
                         fontsize=10, verticalalignment='top',
                         bbox=dict(boxstyle='round', facecolor='#2b2b2b', alpha=0.8, edgecolor='#4a90e2'),
                         color='#ffffff')
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            messagebox.showerror("Помилка", "Для 3D візуалізації потрібна бібліотека numpy")
        except Exception as e:
            import logging
            logging.error(f"Помилка 3D візуалізації: {e}", exc_info=True)
            messagebox.showerror("Помилка", f"Не вдалося створити 3D модель: {e}")


if __name__ == "__main__":
    app = BalloonCalculatorGUI()
    app.run() 