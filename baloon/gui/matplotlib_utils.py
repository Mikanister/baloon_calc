"""
Утиліти для роботи з matplotlib
"""

# Lazy import для matplotlib (щоб працювало в exe)
_plt = None

def get_plt():
    """Отримує matplotlib.pyplot з lazy loading"""
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

