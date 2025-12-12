"""
Функції для грушоподібної форми
"""

import math


def pear_volume(height: float, top_radius: float, bottom_radius: float) -> float:
    """
    Об'єм грушоподібної форми
    
    Груша моделюється як обертання кривої навколо вертикальної осі.
    Використовуємо наближення через об'єм двох частин:
    - Верхня частина (сферична): полусфера з радіусом top_radius
    - Нижня частина (конусоподібна): зрізаний конус між top_radius та bottom_radius
    
    Args:
        height: Висота груші (м)
        top_radius: Радіус верхньої частини (ширша, м)
        bottom_radius: Радіус нижньої частини (вужча, м)
    
    Returns:
        Об'єм груші (м³)
    """
    # Розділяємо грушу на дві частини
    # Верхня частина - приблизно полусфера (40% висоти)
    h_top = height * 0.4
    V_top = (2/3) * math.pi * top_radius**3  # Об'єм полусфери
    
    # Нижня частина - зрізаний конус (60% висоти)
    h_bottom = height * 0.6
    # Об'єм зрізаного конуса: V = (πh/3) * (R² + Rr + r²)
    V_bottom = (math.pi * h_bottom / 3) * (top_radius**2 + top_radius * bottom_radius + bottom_radius**2)
    
    return V_top + V_bottom


def pear_surface_area(height: float, top_radius: float, bottom_radius: float) -> float:
    """
    Площа поверхні грушоподібної форми
    
    Args:
        height: Висота груші (м)
        top_radius: Радіус верхньої частини (ширша, м)
        bottom_radius: Радіус нижньої частини (вужча, м)
    
    Returns:
        Площа поверхні груші (м²)
    """
    # Розділяємо на дві частини
    h_top = height * 0.4
    h_bottom = height * 0.6
    
    # Верхня частина - полусфера
    S_top = 2 * math.pi * top_radius**2  # Площа поверхні полусфери
    
    # Нижня частина - бічна поверхня зрізаного конуса
    # S = π(R + r) * l, де l - твірна конуса
    l = math.sqrt(h_bottom**2 + (top_radius - bottom_radius)**2)
    S_bottom = math.pi * (top_radius + bottom_radius) * l
    
    return S_top + S_bottom


def pear_dimensions_from_volume(volume: float, height: float = None, top_radius: float = None, bottom_radius: float = None) -> tuple:
    """
    Розраховує розміри груші за об'ємом
    
    Args:
        volume: Об'єм груші (м³)
        height: Якщо задано, розраховуються радіуси
        top_radius: Якщо задано, розраховується bottom_radius або height
        bottom_radius: Якщо задано, розраховується top_radius або height
    
    Returns:
        (height, top_radius, bottom_radius) в метрах
    """
    if volume <= 0:
        return (0.0, 0.0, 0.0)
    
    # Підраховуємо скільки параметрів задано
    given = sum(1 for x in [height, top_radius, bottom_radius] if x is not None and x > 0)
    
    if given == 3:
        # Всі параметри задані
        return (height, top_radius, bottom_radius)
    elif given == 2:
        # Задано два параметри, розраховуємо третій
        if height is None:
            # Потрібно розрахувати height
            # Використовуємо ітераційний підхід або наближення
            # Для простоти, використаємо співвідношення height = 2 * top_radius
            height = 2 * top_radius
            # Перевіряємо об'єм та коригуємо
            test_volume = pear_volume(height, top_radius, bottom_radius)
            if test_volume > 0:
                scale = (volume / test_volume) ** (1/3)
                height = height * scale
        elif top_radius is None:
            # Потрібно розрахувати top_radius
            # Використовуємо співвідношення top_radius = 2 * bottom_radius
            top_radius = 2 * bottom_radius
            # Перевіряємо об'єм та коригуємо
            test_volume = pear_volume(height, top_radius, bottom_radius)
            if test_volume > 0:
                scale = (volume / test_volume) ** (1/3)
                top_radius = top_radius * scale
                bottom_radius = bottom_radius * scale
        elif bottom_radius is None:
            # Потрібно розрахувати bottom_radius
            # Використовуємо співвідношення bottom_radius = top_radius / 2
            bottom_radius = top_radius / 2
            # Перевіряємо об'єм та коригуємо
            test_volume = pear_volume(height, top_radius, bottom_radius)
            if test_volume > 0:
                scale = (volume / test_volume) ** (1/3)
                top_radius = top_radius * scale
                bottom_radius = bottom_radius * scale
        
        return (height, top_radius, bottom_radius)
    elif given == 1:
        # Задано один параметр
        if height is not None and height > 0:
            # Використовуємо співвідношення: top_radius = height / 2.5, bottom_radius = top_radius / 2
            top_radius = height / 2.5
            bottom_radius = top_radius / 2
        elif top_radius is not None and top_radius > 0:
            # Використовуємо співвідношення: height = 2.5 * top_radius, bottom_radius = top_radius / 2
            height = 2.5 * top_radius
            bottom_radius = top_radius / 2
        elif bottom_radius is not None and bottom_radius > 0:
            # Використовуємо співвідношення: top_radius = 2 * bottom_radius, height = 2.5 * top_radius
            top_radius = 2 * bottom_radius
            height = 2.5 * top_radius
        else:
            return (0.0, 0.0, 0.0)
        
        # Перевіряємо об'єм та коригуємо
        test_volume = pear_volume(height, top_radius, bottom_radius)
        if test_volume > 0:
            scale = (volume / test_volume) ** (1/3)
            height = height * scale
            top_radius = top_radius * scale
            bottom_radius = bottom_radius * scale
        
        return (height, top_radius, bottom_radius)
    else:
        # Не задано жодного параметра, використовуємо співвідношення
        # Для груші: height = 2.5 * top_radius, bottom_radius = top_radius / 2
        # Наближено: V ≈ 0.8 * π * top_radius^3 (для типової груші)
        top_radius = (volume / (0.8 * math.pi)) ** (1/3)
        height = 2.5 * top_radius
        bottom_radius = top_radius / 2
        
        return (height, top_radius, bottom_radius)

