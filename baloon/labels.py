# labels.py
"""
Централізовані підписи, підказки, дефолти, тексти для GUI калькулятора аеростатів
"""

try:
    from baloon.constants import (
        DEFAULT_THICKNESS, DEFAULT_START_HEIGHT, DEFAULT_WORK_HEIGHT,
        DEFAULT_GROUND_TEMP, DEFAULT_INSIDE_TEMP, DEFAULT_PAYLOAD, DEFAULT_GAS_VOLUME,
        DEFAULT_SHAPE_TYPE,
        DEFAULT_PILLOW_LEN, DEFAULT_PILLOW_WID,
        DEFAULT_PEAR_HEIGHT, DEFAULT_PEAR_TOP_RADIUS, DEFAULT_PEAR_BOTTOM_RADIUS,
        DEFAULT_CIGAR_LENGTH, DEFAULT_CIGAR_RADIUS,
        DEFAULT_EXTRA_MASS, DEFAULT_SEAM_FACTOR
    )
except ImportError:
    from constants import (
        DEFAULT_THICKNESS, DEFAULT_START_HEIGHT, DEFAULT_WORK_HEIGHT,
        DEFAULT_GROUND_TEMP, DEFAULT_INSIDE_TEMP, DEFAULT_PAYLOAD, DEFAULT_GAS_VOLUME,
        DEFAULT_SHAPE_TYPE,
        DEFAULT_PILLOW_LEN, DEFAULT_PILLOW_WID,
        DEFAULT_PEAR_HEIGHT, DEFAULT_PEAR_TOP_RADIUS, DEFAULT_PEAR_BOTTOM_RADIUS,
        DEFAULT_CIGAR_LENGTH, DEFAULT_CIGAR_RADIUS,
        DEFAULT_EXTRA_MASS, DEFAULT_SEAM_FACTOR
    )

# Підписи для полів
FIELD_LABELS = {
    'payload': "Корисне навантаження (кг)",
    'gas_volume': "Обʼєм газу (м³)",
    'density': "Щільність оболонки (кг/м³)",
    'thickness': "Товщина оболонки (мкм)",
    'start_height': "Висота пуску над рівнем моря (м)",
    'work_height': "Висота польоту відносно пуску (м)",
    'ground_temp': "T на землі (°C)",
    'inside_temp': "T всередині (°C)",
    'duration': "Тривалість польоту (год)",
    'perm_mult': "Множник проникності",
    'shape_type': "Форма оболонки",
    'pillow_len': "Довжина подушки (м, опціонально)",
    'pillow_wid': "Ширина подушки (м, опціонально)",
    'pear_height': "Висота груші (м, опціонально)",
    'pear_top_radius': "Радіус верхньої частини (м, опціонально)",
    'pear_bottom_radius': "Радіус нижньої частини (м, опціонально)",
    'cigar_length': "Довжина сигари (м, опціонально)",
    'cigar_radius': "Радіус сигари (м, опціонально)",
    'extra_mass': "Додаткова маса обладнання (кг)",
    'seam_factor': "Коефіцієнт втрат через шви"
}

# Пояснення/підказки для полів
FIELD_TOOLTIPS = {
    'payload': 'Корисне навантаження, яке має підняти аеростат (кг)',
    'gas_volume': 'Обʼєм газу, який закачується в аеростат (м³)',
    'density': 'Щільність матеріалу оболонки (кг/м³)',
    'thickness': 'Товщина оболонки (мікрометри)',
    'start_height': 'Висота пуску над рівнем моря (м)',
    'work_height': 'Висота польоту відносно пуску (м)',
    'ground_temp': 'Температура повітря на землі (°C)',
    'inside_temp': 'Температура газу всередині кулі (°C)',
    'perm_mult': 'Множник проникності оболонки (1 — типова, 10 — у 10 разів гірша, 100 — у 100 разів гірша тощо)',
    'duration': 'Тривалість польоту в годинах (враховується для втрат газу)',
    'shape_type': 'Геометрія оболонки: сфера, мішкоподібна форма (подушка), груша або сигара',
    'pillow_len': 'Довжина подушки (м). Якщо не задано, розраховується на основі об\'єму',
    'pillow_wid': 'Ширина подушки (м). Якщо не задано, розраховується на основі об\'єму',
    'pear_height': 'Висота груші (м). Якщо не задано, розраховується на основі об\'єму',
    'pear_top_radius': 'Радіус верхньої частини груші (ширша частина, м). Якщо не задано, розраховується на основі об\'єму',
    'pear_bottom_radius': 'Радіус нижньої частини груші (вужча частина, м). Якщо не задано, розраховується на основі об\'єму',
    'cigar_length': 'Загальна довжина сигари (м). Якщо не задано, розраховується на основі об\'єму',
    'cigar_radius': 'Радіус сигари (м). Якщо не задано, розраховується на основі об\'єму',
    'extra_mass': 'Додаткова маса обладнання: кріплення, клапани, шнури, вентиляційні отвори тощо (кг)',
    'seam_factor': 'Множник для площі поверхні через шви та з\'єднання. 1.0 = без втрат, 1.05 = +5%, 1.10 = +10%'
}

# Значення за замовчуванням для полів
FIELD_DEFAULTS = {
    'payload': str(DEFAULT_PAYLOAD),
    'gas_volume': str(DEFAULT_GAS_VOLUME),
    'thickness': str(DEFAULT_THICKNESS),
    'start_height': str(DEFAULT_START_HEIGHT),
    'work_height': str(DEFAULT_WORK_HEIGHT),
    'ground_temp': str(DEFAULT_GROUND_TEMP),
    'inside_temp': str(DEFAULT_INSIDE_TEMP),
    'duration': "24",
    'perm_mult': "1",
    'shape_type': DEFAULT_SHAPE_TYPE,
    'pillow_len': str(DEFAULT_PILLOW_LEN),
    'pillow_wid': str(DEFAULT_PILLOW_WID),
    'pear_height': str(DEFAULT_PEAR_HEIGHT),
    'pear_top_radius': str(DEFAULT_PEAR_TOP_RADIUS),
    'pear_bottom_radius': str(DEFAULT_PEAR_BOTTOM_RADIUS),
    'cigar_length': str(DEFAULT_CIGAR_LENGTH),
    'cigar_radius': str(DEFAULT_CIGAR_RADIUS),
    'extra_mass': str(DEFAULT_EXTRA_MASS),
    'seam_factor': str(DEFAULT_SEAM_FACTOR)
}

# Варіанти для комбобоксів
COMBOBOX_VALUES = {
    'perm_mult': ["1", "10", "100", "1000"],
    'shape_type': [
        "Сфера",
        "Подушка/мішок",
        "Груша",
        "Сигара",
    ]
}

# Тексти для About-діалогу
ABOUT_TEXT = (
    "Калькулятор аеростатів v2.0\n"
    "Автори: Братство дисидентів БРТ\n"
    "\n"
    "Ця програма дозволяє розраховувати параметри аеростатів,\n"
    "будувати графіки залежностей та зберігати налаштування.\n"
    "\n"
    "Підказки:\n"
    "- Всі поля мають підказки при наведенні.\n"
    "- Для гарячого повітря обов'язково вкажіть температуру всередині.\n"
)

# Тексти для кнопок
BUTTON_LABELS = {
    'calculate': "Обрахувати",
    'show_graph': "Показати графік",
    'save_settings': "Зберегти налаштування",
    'clear': "Очистити",
    'about': "Про програму",
    'compare_materials': "Порівняти матеріали",
    'optimal_height': "Оптимальна висота",
    'flight_time': "Час польоту",
    'help': "Довідка"
}

# Тексти для секцій
SECTION_LABELS = {
    'mode': "Режим розрахунку",
    'params': "Параметри аеростата",
    'results': "Результати розрахунків"
}

# Пояснення для множника проникності
PERM_MULT_HINT = "1 — типова якість, 10 — у 10 разів гірша, 100 — у 100 разів гірша тощо" 