#!/usr/bin/env python3
"""
Entry point для запуску калькулятора аеростатів як модуля:
    python -m balloon
"""

import sys
import os

def main():
    """Головна функція запуску"""
    try:
        print("="*60)
        print("Запуск калькулятора аеростатів...")
        print("="*60)
        
        # Перевірка frozen режиму
        if getattr(sys, 'frozen', False):
            print(f"Режим: EXE (frozen)")
            print(f"Executable: {sys.executable}")
            print(f"MEIPASS: {getattr(sys, '_MEIPASS', 'N/A')}")
        else:
            print("Режим: Python скрипт")
        
        # Використовуємо Rich для красивого виводу, якщо доступний
        try:
            from balloon.utils import print_success, print_error
            print_success("Запуск калькулятора аеростатів...")
        except ImportError:
            print("Rich недоступний, використовуємо стандартний вивід")
        
        print("Імпорт GUI модулів...")
        # Імпортуємо GUI
        from balloon.gui_main import BalloonCalculatorGUI
        
        print("Створення GUI об'єкта...")
        app = BalloonCalculatorGUI()
        
        print("Запуск GUI...")
        app.run()
    except Exception as e:
        try:
            from balloon.utils import print_error
            print_error(f"Помилка запуску: {e}")
        except ImportError:
            print(f"Помилка запуску: {e}")
        import traceback
        traceback.print_exc()
        # Завжди чекаємо натискання Enter перед закриттям (навіть в exe)
        print("\n" + "="*50)
        print("ПРОГРАМА ЗАКРИЛАСЬ З ПОМИЛКОЮ")
        print("="*50)
        input("Натисніть Enter для виходу...")
        sys.exit(1)

if __name__ == "__main__":
    main()

