"""
Функції для тороїдальної форми (для тестів, не використовується в основному коді)
"""

import math


def torus_volume(major_radius: float, minor_radius: float) -> float:
    """
    Об'єм тороїда
    
    Args:
        major_radius: Великий радіус (від центру до центру труби)
        minor_radius: Малий радіус (радіус перерізу труби)
    
    Returns:
        Об'єм тороїда (м³)
    """
    return 2 * math.pi**2 * major_radius * minor_radius**2


def torus_surface_area(major_radius: float, minor_radius: float) -> float:
    """Площа поверхні тороїда"""
    return 4 * math.pi**2 * major_radius * minor_radius


def torus_dimensions_from_volume(volume: float, major_radius: float = None, minor_radius: float = None) -> tuple:
    """
    Розраховує розміри тора за об'ємом
    
    Args:
        volume: Об'єм тора (м³)
        major_radius: Якщо задано, розраховується minor_radius
        minor_radius: Якщо задано, розраховується major_radius
    
    Returns:
        (major_radius, minor_radius) в метрах
    """
    if volume <= 0:
        return (0.0, 0.0)
    if major_radius is not None and major_radius > 0:
        # V = 2π²Rr², тому r = sqrt(V/(2π²R))
        minor_radius = (volume / (2 * math.pi**2 * major_radius)) ** 0.5
        return (major_radius, minor_radius)
    elif minor_radius is not None and minor_radius > 0:
        # V = 2π²Rr², тому R = V/(2π²r²)
        major_radius = volume / (2 * math.pi**2 * minor_radius**2)
        return (major_radius, minor_radius)
    else:
        # Якщо не задано жодного параметра, використовуємо співвідношення 4:1 (major:minor)
        # V = 2π²Rr², якщо R = 4r, то V = 8π²r³, r = (V/(8π²))^(1/3)
        minor_radius = (volume / (8 * math.pi**2)) ** (1 / 3)
        major_radius = 4 * minor_radius
        return (major_radius, minor_radius)

