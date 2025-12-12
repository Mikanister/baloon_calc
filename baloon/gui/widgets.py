"""
Модуль для створення віджетів GUI
"""

import tkinter as tk
from tkinter import ttk

try:
    from baloon.labels import (
        FIELD_LABELS, FIELD_TOOLTIPS, FIELD_DEFAULTS, COMBOBOX_VALUES,
        SECTION_LABELS, BUTTON_LABELS, PERM_MULT_HINT
    )
    from baloon.constants import MATERIALS, GAS_DENSITY
except ImportError:
    from labels import (
        FIELD_LABELS, FIELD_TOOLTIPS, FIELD_DEFAULTS, COMBOBOX_VALUES,
        SECTION_LABELS, BUTTON_LABELS, PERM_MULT_HINT
    )
    from constants import MATERIALS, GAS_DENSITY


class WidgetBuilder:
    """Клас для створення віджетів GUI"""
    
    def __init__(self, gui_instance):
        """Ініціалізація з посиланням на головний клас GUI"""
        self.gui = gui_instance
    
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
            variable=self.gui.mode_var, value="payload",
            command=self.gui.update_fields
        ).grid(row=row, column=1, sticky="w")
        row += 1
        ttk.Radiobutton(
            parent, text="Навантаження ➜ обʼєм",
            variable=self.gui.mode_var, value="volume",
            command=self.gui.update_fields
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
        ttk.Button(btn_frame, text=BUTTON_LABELS['help'], command=self.gui.show_help).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text=BUTTON_LABELS['about'], command=self.gui.show_about).pack(side="left")
    
    def _add_entry_row(self, parent, key: str, label_text: str, row: int, default=None, **entry_kwargs) -> int:
        """Створити рядок Label + Entry та повернути наступний row"""
        self.gui.labels[key] = ttk.Label(parent, text=label_text)
        self.gui.labels[key].grid(row=row, column=0, sticky="w")
        entry = ttk.Entry(parent, **entry_kwargs)
        if default is not None:
            entry.insert(0, default)
        entry.grid(row=row, column=1, sticky="ew", padx=(10, 0))
        self.gui.entries[key] = entry
        return row + 1
    
    def _add_combo_row(self, parent, key: str, label_text: str, row: int, values, textvariable=None) -> int:
        """Створити рядок Label + Combobox та повернути наступний row"""
        self.gui.labels[key] = ttk.Label(parent, text=label_text)
        self.gui.labels[key].grid(row=row, column=0, sticky="w")
        combo = ttk.Combobox(
            parent,
            textvariable=textvariable,
            values=values,
            state="readonly"
        )
        combo.grid(row=row, column=1, sticky="ew", padx=(10, 0))
        self.gui.entries[key] = combo
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
        self.gui.shape_display_to_code = {
            "Сфера": "sphere",
            "Подушка/мішок": "pillow",
            "Груша": "pear",
            "Сигара": "cigar",
        }
        self.gui.shape_code_to_display = {v: k for k, v in self.gui.shape_display_to_code.items()}
        self.gui.labels['shape_type'] = ttk.Label(parent, text=FIELD_LABELS['shape_type'])
        self.gui.labels['shape_type'].grid(row=row, column=0, sticky="w")
        shape_combo = ttk.Combobox(parent, values=shape_values, state="readonly", textvariable=self.gui.shape_var)
        shape_combo.grid(row=row, column=1, sticky="ew", padx=(10, 0))
        if FIELD_DEFAULTS['shape_type'] in self.gui.shape_code_to_display:
            self.gui.shape_var.set(self.gui.shape_code_to_display[FIELD_DEFAULTS['shape_type']])
        else:
            self.gui.shape_var.set(shape_values[0])
        self.gui.entries['shape_type'] = shape_combo
        row += 1
        
        # Температури (тільки для гарячого повітря)
        self.gui.labels['ground_temp'] = ttk.Label(parent, text=FIELD_LABELS['ground_temp'])
        self.gui.entries['ground_temp'] = ttk.Entry(parent)
        self.gui.entries['ground_temp'].insert(0, FIELD_DEFAULTS['ground_temp'])
        
        self.gui.labels['inside_temp'] = ttk.Label(parent, text=FIELD_LABELS['inside_temp'])
        self.gui.entries['inside_temp'] = ttk.Entry(parent)
        self.gui.entries['inside_temp'].insert(0, FIELD_DEFAULTS['inside_temp'])
        # Запам'ятовуємо базовий рядок для температур і резервуємо місце
        self.gui.temp_row_base = row
        row += 2  # резервуємо два рядки під температури
        
        # Навантаження (залежить від режиму)
        self.gui.labels['payload'] = ttk.Label(parent, text=FIELD_LABELS['payload'])
        self.gui.entries['payload'] = ttk.Entry(parent)
        self.gui.entries['payload'].insert(0, FIELD_DEFAULTS['payload'])
        
        row = self._add_combo_row(
            parent=parent,
            key='material',
            label_text="Матеріал оболонки",
            row=row,
            values=list(MATERIALS.keys()),
            textvariable=self.gui.material_var
        )
        # density з текстовою змінною, лише для читання
        self.gui.labels['density'] = ttk.Label(parent, text=FIELD_LABELS['density'])
        self.gui.labels['density'].grid(row=row, column=0, sticky="w")
        self.gui.entries['density'] = ttk.Entry(parent, textvariable=self.gui.material_density_var, state="readonly")
        self.gui.entries['density'].grid(row=row, column=1, sticky="ew", padx=(10, 0))
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
            textvariable=self.gui.gas_var
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
        self.gui.shape_rows = {}
        self.gui.shape_rows['pillow_len'] = self._add_entry_row(parent, 'pillow_len', FIELD_LABELS['pillow_len'], row, FIELD_DEFAULTS['pillow_len']); row = self.gui.shape_rows['pillow_len']
        self.gui.shape_rows['pillow_wid'] = self._add_entry_row(parent, 'pillow_wid', FIELD_LABELS['pillow_wid'], row, FIELD_DEFAULTS['pillow_wid']); row = self.gui.shape_rows['pillow_wid']
        self.gui.shape_rows['pear_height'] = self._add_entry_row(parent, 'pear_height', FIELD_LABELS['pear_height'], row, FIELD_DEFAULTS['pear_height']); row = self.gui.shape_rows['pear_height']
        self.gui.shape_rows['pear_top_radius'] = self._add_entry_row(parent, 'pear_top_radius', FIELD_LABELS['pear_top_radius'], row, FIELD_DEFAULTS['pear_top_radius']); row = self.gui.shape_rows['pear_top_radius']
        self.gui.shape_rows['pear_bottom_radius'] = self._add_entry_row(parent, 'pear_bottom_radius', FIELD_LABELS['pear_bottom_radius'], row, FIELD_DEFAULTS['pear_bottom_radius']); row = self.gui.shape_rows['pear_bottom_radius']
        self.gui.shape_rows['cigar_length'] = self._add_entry_row(parent, 'cigar_length', FIELD_LABELS['cigar_length'], row, FIELD_DEFAULTS['cigar_length']); row = self.gui.shape_rows['cigar_length']
        self.gui.shape_rows['cigar_radius'] = self._add_entry_row(parent, 'cigar_radius', FIELD_LABELS['cigar_radius'], row, FIELD_DEFAULTS['cigar_radius']); row = self.gui.shape_rows['cigar_radius']

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
            command=self.gui.calculate, style="Accent.TButton"
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            row1_frame, text=BUTTON_LABELS['show_graph'],
            command=self.gui.show_graph
        ).pack(side="left", padx=(0, 10))
        
        # Другий рядок кнопок
        row2_frame = ttk.Frame(button_frame)
        row2_frame.pack(fill="x")
        
        ttk.Button(
            row2_frame, text=BUTTON_LABELS['save_settings'],
            command=self.gui.save_settings
        ).pack(side="left", padx=(0, 10))
        
        row += 1
        return row
    
    def create_result_section(self, parent, row):
        """Створення секції результатів"""
        ttk.Label(parent, text=SECTION_LABELS['results'], font=("Arial", 12, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(0, 5)
        )
        row += 1
        
        self.gui.status_label = ttk.Label(parent, text="Статус: очікує результат", foreground="#4a90e2")
        self.gui.status_label.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 6))
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
        self.gui.result_text_widget = result_text
    
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
    
    def add_tooltips(self):
        """Додає підказки до всіх полів"""
        for key, entry in self.gui.entries.items():
            if key in FIELD_TOOLTIPS:
                self.create_tooltip(entry, FIELD_TOOLTIPS[key])
    
    def create_patterns_section(self, parent):
        """Створення розділу для викрійок/патернів"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Верхня панель з параметрами
        control_frame = ttk.Frame(parent, style="Card.TFrame", padding="12")
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        control_frame.columnconfigure(1, weight=1)
        
        # Заголовок
        ttk.Label(control_frame, text="Розрахунок викрійок/патернів", style="Heading.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )
        
        # Параметри для викрійок
        row = 1
        ttk.Label(control_frame, text="Форма:").grid(row=row, column=0, sticky="w")
        self.gui.pattern_shape_var = tk.StringVar(value="Сфера")
        pattern_shape_combo = ttk.Combobox(
            control_frame,
            textvariable=self.gui.pattern_shape_var,
            values=COMBOBOX_VALUES['shape_type'],
            state="readonly",
            width=20
        )
        pattern_shape_combo.grid(row=row, column=1, sticky="w", padx=(10, 0))
        row += 1
        
        ttk.Label(control_frame, text="Кількість сегментів:").grid(row=row, column=0, sticky="w")
        self.gui.pattern_segments_var = tk.StringVar(value="12")
        pattern_segments_entry = ttk.Entry(control_frame, textvariable=self.gui.pattern_segments_var, width=10)
        pattern_segments_entry.grid(row=row, column=1, sticky="w", padx=(10, 0))
        ttk.Label(control_frame, text="(для сфери)", font=("Segoe UI", 8), foreground="#888888").grid(
            row=row, column=2, sticky="w", padx=(5, 0)
        )
        row += 1
        
        # Кнопка генерації
        ttk.Button(
            control_frame,
            text="Згенерувати викрійку",
            command=self.gui.generate_pattern,
            style="Accent.TButton"
        ).grid(row=row, column=0, columnspan=2, pady=(10, 0), sticky="w")
        
        # Область для візуалізації та інформації
        content_frame = ttk.Frame(parent)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Ліва частина - візуалізація
        viz_frame = ttk.Frame(content_frame, style="Card.TFrame", padding="10")
        viz_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(1, weight=1)
        
        ttk.Label(viz_frame, text="Візуалізація патерну", style="Subheading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )
        
        # Canvas для малювання патерну
        self.gui.pattern_canvas = tk.Canvas(
            viz_frame,
            bg="#1e1e1e",
            highlightthickness=1,
            highlightbackground="#555555"
        )
        self.gui.pattern_canvas.grid(row=1, column=0, sticky="nsew")
        
        # Обробка зміни розміру canvas
        def on_canvas_configure(event):
            if hasattr(self.gui, 'current_pattern'):
                self.gui.visualize_pattern(self.gui.current_pattern)
        self.gui.pattern_canvas.bind('<Configure>', on_canvas_configure)
        
        # Права частина - інформація
        info_frame = ttk.Frame(content_frame, style="Card.TFrame", padding="10")
        info_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Інформація про патерн", style="Subheading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )
        
        # Text widget для інформації
        self.gui.pattern_info_text = tk.Text(
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
        self.gui.pattern_info_text.grid(row=1, column=0, sticky="nsew")
        
        # Scrollbar для тексту
        pattern_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.gui.pattern_info_text.yview)
        pattern_scrollbar.grid(row=1, column=1, sticky="ns")
        self.gui.pattern_info_text.configure(yscrollcommand=pattern_scrollbar.set)
        
        # Кнопки експорту та 3D візуалізації
        export_frame = ttk.Frame(parent)
        export_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(
            export_frame,
            text="3D модель кулі",
            command=self.gui.show_3d_model,
            style="Accent.TButton"
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            export_frame,
            text="Експортувати викрійку (PNG)",
            command=self.gui.export_pattern
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            export_frame,
            text="Експортувати дані (CSV)",
            command=self.gui.export_pattern_data
        ).pack(side="left")

