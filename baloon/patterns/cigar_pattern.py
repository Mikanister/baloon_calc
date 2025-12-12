"""
Патерн для сигароподібної форми
"""

import math
from typing import Dict, Any


def calculate_cigar_pattern(length: float, radius: float, num_gores: int = 12) -> Dict[str, Any]:
    """
    Розраховує патерн гобеленових сегментів (gores) для сигароподібної оболонки
    
    Сигара моделюється як циліндр з двома півсферичними кінцями.
    Використовуємо метод gores, подібний до сфери.
    
    Args:
        length: Загальна довжина сигари (м)
        radius: Радіус сигари (м)
        num_gores: Кількість сегментів (рекомендовано 8-16)
    
    Returns:
        Словник з координатами точок для кожного сегмента та параметрами
    """
    if num_gores < 4:
        num_gores = 4
    if num_gores > 32:
        num_gores = 32
    
    # Кут між сегментами
    theta_step = 2 * math.pi / num_gores
    
    # Довжина циліндричної частини
    cylinder_length = length - 2 * radius
    
    # Координати для одного сегмента
    num_points = 50  # Кількість точок для апроксимації кривої
    gore_points = []
    
    for i in range(num_points + 1):
        # Параметр від 0 до 1 (від одного кінця до іншого)
        t = i / num_points
        
        # Координата Y (вертикальна, вздовж осі сигари)
        y = t * length  # Від 0 до length
        
        # Радіус на цій позиції
        if y < radius:
            # Півсферичний кінець (знизу)
            r_at_height = math.sqrt(radius**2 - (radius - y)**2)
        elif y > length - radius:
            # Півсферичний кінець (зверху)
            r_at_height = math.sqrt(radius**2 - (y - (length - radius))**2)
        else:
            # Циліндрична частина
            r_at_height = radius
        
        # Ширина сегмента на цій висоті (довжина дуги)
        width_at_height = r_at_height * theta_step / 2
        
        # Координата X (горизонтальна, від центру до краю) - це половина ширини сегмента
        x = width_at_height
        
        gore_points.append((x, y))
    
    # Розраховуємо розміри для друку
    max_width = max(x for x, y in gore_points)
    total_height = length
    
    # Площа одного сегмента (приблизно)
    gore_area = 0.0
    for i in range(len(gore_points) - 1):
        x1, y1 = gore_points[i]
        x2, y2 = gore_points[i + 1]
        # Приблизна площа трапеції
        segment_area = (x1 + x2) * abs(y2 - y1) / 2
        gore_area += segment_area
    
    # Загальна площа поверхні (приблизно)
    total_area = gore_area * num_gores * 2  # * 2 бо кожен сегмент має дві сторони
    
    return {
        'pattern_type': 'cigar_gore',
        'num_gores': num_gores,
        'points': gore_points,
        'length': length,
        'radius': radius,
        'max_width': max_width,
        'total_height': total_height,
        'gore_area': gore_area,
        'total_area': total_area,
        'description': f'Сигароподібна оболонка: {num_gores} сегментів, довжина {length:.2f} м, радіус {radius:.2f} м'
    }

