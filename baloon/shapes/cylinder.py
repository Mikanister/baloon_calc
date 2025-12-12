"""
Функції для циліндричної форми (для тестів, не використовується в основному коді)
"""

import math


def cylinder_volume(radius: float, height: float) -> float:
    """Об'єм циліндра"""
    return math.pi * radius**2 * height


def cylinder_surface_area(radius: float, height: float, include_ends: bool = True) -> float:
    """Площа поверхні циліндра"""
    lateral = 2 * math.pi * radius * height
    if include_ends:
        ends = 2 * math.pi * radius**2
        return lateral + ends
    return lateral


def cylinder_dimensions_from_volume(volume: float, radius: float = None, height: float = None) -> tuple:
    """
    Розраховує розміри циліндра за об'ємом
    
    Args:
        volume: Об'єм циліндра (м³)
        radius: Якщо задано, розраховується висота
        height: Якщо задано, розраховується радіус
    
    Returns:
        (radius, height) в метрах
    """
    if volume <= 0:
        return (0.0, 0.0)
    if radius is not None and radius > 0:
        height = volume / (math.pi * radius**2)
        return (radius, height)
    elif height is not None and height > 0:
        radius = (volume / (math.pi * height)) ** 0.5
        return (radius, height)
    else:
        # Якщо не задано жодного параметра, використовуємо співвідношення 2:1 (висота:радіус)
        # V = πr²h, якщо h = 2r, то V = 2πr³, r = (V/(2π))^(1/3)
        radius = (volume / (2 * math.pi)) ** (1 / 3)
        height = 2 * radius
        return (radius, height)

