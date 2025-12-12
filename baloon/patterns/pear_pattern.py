"""
Патерн для грушоподібної форми
"""

import math
from typing import Dict, Any


def calculate_pear_pattern(height: float, top_radius: float, bottom_radius: float, num_gores: int = 12) -> Dict[str, Any]:
    """
    Розраховує патерн гобеленових сегментів (gores) для грушоподібної оболонки
    
    Груша моделюється як обертання кривої, що звужується зверху вниз.
    Використовуємо метод gores, подібний до сфери, але з іншим профілем.
    
    Args:
        height: Висота груші (м)
        top_radius: Радіус верхньої частини (ширша, м)
        bottom_radius: Радіус нижньої частини (вужча, м)
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
    
    # Координати для одного сегмента (від верхньої частини до нижньої)
    num_points = 50  # Кількість точок для апроксимації кривої
    gore_points = []
    
    for i in range(num_points + 1):
        # Параметр від 0 до 1 (від верху до низу)
        t = i / num_points
        
        # Координата Y (вертикальна, від верху до низу)
        y = height * t  # Від верху (0) до низу (height)
        
        # Радіус на цій висоті - лінійна інтерполяція між top_radius та bottom_radius
        r_at_height = top_radius * (1 - t) + bottom_radius * t
        
        # Ширина сегмента на цій висоті (довжина дуги)
        width_at_height = r_at_height * theta_step / 2
        
        # Координата X (горизонтальна, від центру до краю) - це половина ширини сегмента
        x = width_at_height
        
        gore_points.append((x, y))
    
    # Розраховуємо розміри для друку
    max_width = max(x for x, y in gore_points)
    total_height = height
    
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
        'pattern_type': 'pear_gore',
        'num_gores': num_gores,
        'points': gore_points,
        'height': height,
        'top_radius': top_radius,
        'bottom_radius': bottom_radius,
        'max_width': max_width,
        'total_height': total_height,
        'gore_area': gore_area,
        'total_area': total_area,
        'description': f'Грушоподібна оболонка: {num_gores} сегментів, висота {height:.2f} м, верхній радіус {top_radius:.2f} м, нижній радіус {bottom_radius:.2f} м'
    }

