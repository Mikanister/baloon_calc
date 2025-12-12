"""
Функції для подушкоподібної форми
"""

import math


def pillow_volume(length: float, width: float, thickness: float = 1.0) -> float:
    """
    Об'єм плоскої подушки/мішка
    
    Args:
        length: Довжина подушки (м)
        width: Ширина подушки (м)
        thickness: Товщина подушки (м), за замовчуванням 1.0
    """
    return length * width * thickness


def pillow_surface_area(length: float, width: float, thickness: float = None) -> float:
    """
    Площа поверхні плоскої подушки/мішка
    
    Подушка складається з двох прямокутних сегментів однакового розміру,
    з'єднаних по кромці. Площа = 2 × (length × width)
    
    Args:
        length: Довжина подушки (м)
        width: Ширина подушки (м)
        thickness: Товщина подушки (м) - не використовується для розрахунку площі, але може бути для сумісності
    """
    # Площа двох прямокутних панелей
    return 2 * length * width


def pillow_dimensions_from_volume(volume: float, length: float = None, width: float = None) -> tuple:
    """
    Розраховує розміри подушки за об'ємом
    
    Подушка складається з двох прямокутних сегментів однакового розміру.
    Товщина (відстань між панелями) розраховується з об'єму: thickness = volume / (length × width)
    
    Args:
        volume: Об'єм подушки (м³)
        length: Якщо задано, розраховується width або використовується співвідношення
        width: Якщо задано, розраховується length або використовується співвідношення
    
    Returns:
        (length, width, thickness) в метрах, де thickness розраховується з об'єму
    """
    if volume <= 0:
        return (0.0, 0.0, 0.0)
    
    # Підраховуємо скільки параметрів задано
    given = sum(1 for x in [length, width] if x is not None and x > 0)
    
    if given == 2:
        # Якщо задано обидва параметри, розраховуємо товщину
        if length > 0 and width > 0:
            thickness = volume / (length * width)
            return (length, width, thickness)
        return (length or 0.0, width or 0.0, 0.0)
    elif given == 1:
        # Якщо задано один параметр, використовуємо співвідношення 3:2 (length:width)
        if length is not None and length > 0:
            width = length * 2 / 3
        elif width is not None and width > 0:
            length = width * 3 / 2
        else:
            return (0.0, 0.0, 0.0)
        
        # Розраховуємо товщину з об'єму
        if length > 0 and width > 0:
            thickness = volume / (length * width)
            return (length, width, thickness)
        return (length or 0.0, width or 0.0, 0.0)
    else:
        # Якщо не задано жодного параметра, використовуємо співвідношення 3:2
        # V = L*W*H, якщо L:W = 3:2, то L = 3W/2, V = (3W/2)*W*H = (3W²H)/2
        # Для зручності приймаємо H = W/2 (товщина = половині ширини)
        # Тоді V = (3W² * W/2)/2 = 3W³/4, W = (4V/3)^(1/3)
        width = (4 * volume / 3) ** (1 / 3)
        length = width * 3 / 2
        thickness = volume / (length * width)
        return (length, width, thickness)

