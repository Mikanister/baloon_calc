"""
Функції для сигароподібної форми
"""

import math


def cigar_volume(length: float, radius: float) -> float:
    """
    Об'єм сигароподібної форми
    
    Сигара моделюється як циліндр з двома півсферичними кінцями.
    
    Args:
        length: Загальна довжина сигари (м)
        radius: Радіус сигари (м)
    
    Returns:
        Об'єм сигари (м³)
    """
    if length <= 0 or radius <= 0:
        return 0.0
    
    # Довжина циліндричної частини
    cylinder_length = length - 2 * radius
    
    if cylinder_length < 0:
        # Якщо довжина менша за 2*радіус, то це просто сфера
        return (4/3) * math.pi * radius**3
    
    # Об'єм циліндричної частини
    V_cylinder = math.pi * radius**2 * cylinder_length
    
    # Об'єм двох півсфер (разом = одна сфера)
    V_spheres = (4/3) * math.pi * radius**3
    
    return V_cylinder + V_spheres


def cigar_surface_area(length: float, radius: float) -> float:
    """
    Площа поверхні сигароподібної форми
    
    Args:
        length: Загальна довжина сигари (м)
        radius: Радіус сигари (м)
    
    Returns:
        Площа поверхні сигари (м²)
    """
    if length <= 0 or radius <= 0:
        return 0.0
    
    # Довжина циліндричної частини
    cylinder_length = length - 2 * radius
    
    if cylinder_length < 0:
        # Якщо довжина менша за 2*радіус, то це просто сфера
        return 4 * math.pi * radius**2
    
    # Бічна поверхня циліндра
    S_cylinder = 2 * math.pi * radius * cylinder_length
    
    # Площа поверхні двох півсфер (разом = площа сфери)
    S_spheres = 4 * math.pi * radius**2
    
    return S_cylinder + S_spheres


def cigar_dimensions_from_volume(volume: float, length: float = None, radius: float = None) -> tuple:
    """
    Розраховує розміри сигари за об'ємом
    
    Args:
        volume: Об'єм сигари (м³)
        length: Якщо задано, розраховується radius
        radius: Якщо задано, розраховується length
    
    Returns:
        (length, radius) в метрах
    """
    if volume <= 0:
        return (0.0, 0.0)
    
    # Підраховуємо скільки параметрів задано
    given = sum(1 for x in [length, radius] if x is not None and x > 0)
    
    if given == 2:
        # Всі параметри задані
        return (length, radius)
    elif given == 1:
        # Задано один параметр
        if length is not None and length > 0:
            # Потрібно розрахувати radius
            # Використовуємо співвідношення: radius = length / 5 (типова сигара)
            radius = length / 5
            # Перевіряємо об'єм та коригуємо
            test_volume = cigar_volume(length, radius)
            if test_volume > 0:
                # Використовуємо ітераційний підхід для точного розрахунку
                # V = π*R²*(L - 2*R) + (4/3)*π*R³
                # Для заданого L, це кубічне рівняння відносно R
                # Для спрощення, використаємо наближення через масштабування
                scale = (volume / test_volume) ** (1/3)
                radius = radius * scale
        elif radius is not None and radius > 0:
            # Потрібно розрахувати length
            # Використовуємо співвідношення: length = 5 * radius (типова сигара)
            length = 5 * radius
            # Перевіряємо об'єм та коригуємо
            test_volume = cigar_volume(length, radius)
            if test_volume > 0:
                # V = π*R²*(L - 2*R) + (4/3)*π*R³
                # L = (V - (4/3)*π*R³) / (π*R²) + 2*R
                sphere_volume = (4/3) * math.pi * radius**3
                cylinder_volume = volume - sphere_volume
                if cylinder_volume > 0:
                    cylinder_length = cylinder_volume / (math.pi * radius**2)
                    length = cylinder_length + 2 * radius
                else:
                    # Якщо об'єм менший за об'єм сфери, то це просто сфера
                    length = 2 * radius
        else:
            return (0.0, 0.0)
        
        return (length, radius)
    else:
        # Не задано жодного параметра, використовуємо співвідношення
        # Для сигари: length = 5 * radius
        # V = π*R²*(5*R - 2*R) + (4/3)*π*R³ = π*R²*3*R + (4/3)*π*R³ = 3*π*R³ + (4/3)*π*R³ = (13/3)*π*R³
        radius = (3 * volume / (13 * math.pi)) ** (1/3)
        length = 5 * radius
        
        return (length, radius)

