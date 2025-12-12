#!/usr/bin/env python3
"""
Покращений калькулятор аеростатів
Автор: пан Юрій
Версія: 2.0

Особливості:
- Модульна архітектура
- Валідація введених даних
- Збереження/завантаження налаштувань
- Покращений інтерфейс з темною темою
- Детальні результати розрахунків
- Порівняння матеріалів
- Розрахунок оптимальної висоти
- Розрахунок часу польоту
- Вбудована довідка
- Підтримка неідеальних форм
"""

import sys
import os

# Додаємо поточну директорію до шляху для імпорту
if getattr(sys, 'frozen', False):
    # Якщо запущено як exe
    application_path = sys._MEIPASS
    # Додаємо шлях до модулів baloon
    baloon_path = os.path.join(application_path, 'baloon')
    if os.path.exists(baloon_path):
        sys.path.insert(0, baloon_path)
    sys.path.insert(0, application_path)
    # Також додаємо батьківську директорію для імпорту baloon як пакету
    parent_path = os.path.dirname(application_path)
    if parent_path not in sys.path:
        sys.path.insert(0, parent_path)
else:
    # Якщо запущено як скрипт
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

# Спробуємо різні варіанти імпорту
try:
    # Варіант 1: імпорт з пакету baloon (для запуску як модуль)
    from baloon.gui import BalloonCalculatorGUI
except ImportError:
    try:
        # Варіант 2: прямий імпорт gui (для exe, коли модулі в sys._MEIPASS/baloon)
        from gui import BalloonCalculatorGUI
    except ImportError:
        try:
            # Варіант 3: імпорт через sys.path
            import gui
            BalloonCalculatorGUI = gui.BalloonCalculatorGUI
        except ImportError as e:
            print(f"Помилка імпорту: {e}")
            print(f"sys.path: {sys.path}")
            print(f"Поточна директорія: {os.getcwd()}")
            print(f"__file__: {__file__}")
            if getattr(sys, 'frozen', False):
                print(f"sys._MEIPASS: {sys._MEIPASS}")
            import traceback
            traceback.print_exc()
            input("Натисніть Enter для виходу...")
            sys.exit(1)

try:
    # Використовуємо Rich для красивого виводу, якщо доступний
    try:
        from baloon.utils import print_success, print_error
        print_success("Запуск покращеного калькулятора аеростатів...")
    except ImportError:
        print("Запуск покращеного калькулятора аеростатів...")
    
    app = BalloonCalculatorGUI()
    app.run()
except Exception as e:
    try:
        from baloon.utils import print_error
        print_error(f"Помилка запуску: {e}")
    except ImportError:
        print(f"Помилка запуску: {e}")
    import traceback
    traceback.print_exc()
    input("Натисніть Enter для виходу...") 