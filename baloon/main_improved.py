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
    sys.path.insert(0, application_path)
else:
    # Якщо запущено як скрипт
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Спробуємо локальний імпорт (для exe)
    from gui import BalloonCalculatorGUI
    print("Запуск покращеного калькулятора аеростатів...")
    app = BalloonCalculatorGUI()
    app.run()
except ImportError as e:
    # Спробуємо імпорт з пакету (для запуску як модуль)
    try:
        from baloon.gui import BalloonCalculatorGUI
        print("Запуск покращеного калькулятора аеростатів...")
        app = BalloonCalculatorGUI()
        app.run()
    except ImportError:
        print(f"Помилка імпорту: {e}")
        print("Переконайтеся, що всі файли знаходяться в тій самій директорії")
        import traceback
        traceback.print_exc()
        input("Натисніть Enter для виходу...")
except Exception as e:
    print(f"Помилка запуску: {e}")
    import traceback
    traceback.print_exc()
    input("Натисніть Enter для виходу...") 