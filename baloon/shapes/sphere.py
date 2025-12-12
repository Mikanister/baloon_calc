"""
Функції для сферичної форми
"""

import math


def sphere_volume(radius: float) -> float:
    """Об'єм сфери"""
    return (4/3) * math.pi * radius**3


def sphere_surface_area(radius: float) -> float:
    """Площа поверхні сфери"""
    return 4 * math.pi * radius**2


def sphere_radius_from_volume(volume: float) -> float:
    """Розраховує радіус сфери за об'ємом"""
    if volume <= 0:
        return 0.0
    return (3 * volume / (4 * math.pi)) ** (1 / 3)

