"""
Патерн для сферичної форми
"""

import math
from typing import Dict, Any


def calculate_sphere_gore_pattern(radius: float, num_gores: int = 12) -> Dict[str, Any]:
    """
    Розраховує патерн гобеленових сегментів (gores) для сферичної оболонки
    
    Гобеновий метод - це спосіб виготовлення сфери з вертикальних сегментів,
    які склеюються разом уздовж меридіанів.
    
    Args:
        radius: Радіус сфери (м)
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
    
    # Координати для одного сегмента (від північного полюса до південного)
    num_points = 50  # Кількість точок для апроксимації кривої
    gore_points = []
    
    for i in range(num_points + 1):
        # Параметр від 0 до π (від північного до південного полюса)
        phi = math.pi * i / num_points
        
        # Координата Y (вертикальна)
        y = radius * math.cos(phi)
        
        # Ширина сегмента на цій висоті
        # На екваторі ширина максимальна, на полюсах = 0
        width_at_height = radius * math.sin(phi) * math.sin(theta_step / 2)
        
        # Координата X (горизонтальна, від центру до краю)
        x = width_at_height
        
        gore_points.append((x, y))
    
    # Розраховуємо розміри для друку
    max_width = max(x for x, y in gore_points)
    total_height = 2 * radius
    
    # Площа одного сегмента (приблизно)
    gore_area = (4 * math.pi * radius ** 2) / num_gores
    
    return {
        'pattern_type': 'sphere_gore',
        'num_gores': num_gores,
        'points': gore_points,
        'radius': radius,
        'max_width': max_width,
        'total_height': total_height,
        'gore_area': gore_area,
        'total_area': 4 * math.pi * radius ** 2,
        'description': f'Сферична оболонка: {num_gores} сегментів, радіус {radius:.2f} м'
    }

