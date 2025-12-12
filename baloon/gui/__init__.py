"""
GUI модуль для калькулятора аеростатів
"""

# Експортуємо з gui_main.py (перейменований з gui.py, щоб уникнути конфлікту з папкою gui/)
import sys
import os
import importlib
import importlib.util

def _import_gui_main():
    """Імпортує BalloonCalculatorGUI з gui_main.py"""
    # Знаходимо шлях до gui_main.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    gui_main_path = os.path.join(parent_dir, 'gui_main.py')
    
    # Для exe середовища
    if hasattr(sys, '_MEIPASS'):
        meipass_gui = os.path.join(sys._MEIPASS, 'baloon', 'gui_main.py')
        if os.path.exists(meipass_gui):
            gui_main_path = meipass_gui
            # Додаємо baloon до sys.path для правильних імпортів
            baloon_path = os.path.join(sys._MEIPASS, 'baloon')
            if baloon_path not in sys.path:
                sys.path.insert(0, baloon_path)
    
    if os.path.exists(gui_main_path):
        # Завантажуємо модуль через spec_from_file_location
        # Це дозволяє правильно налаштувати sys.path перед завантаженням
        spec = importlib.util.spec_from_file_location("baloon.gui_main", gui_main_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Не вдалося створити spec для {gui_main_path}")
        
        # Додаємо батьківську директорію до sys.path для правильних імпортів
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        gui_module = importlib.util.module_from_spec(spec)
        # Встановлюємо __package__ для правильних відносних імпортів
        gui_module.__package__ = 'baloon'
        spec.loader.exec_module(gui_module)
        return gui_module
    else:
        # Fallback - спробуємо через звичайний імпорт
        try:
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            return importlib.import_module('baloon.gui_main')
        except ImportError:
            raise ImportError(f"Не вдалося знайти або імпортувати gui_main.py за шляхом: {gui_main_path}")

gui_module = _import_gui_main()
BalloonCalculatorGUI = gui_module.BalloonCalculatorGUI

__all__ = ['BalloonCalculatorGUI']
