"""
Модуль для розрахунку викрійок/патернів для виготовлення оболонки аеростата
"""

import math
from typing import List, Tuple, Dict, Any

try:
    from baloon.shapes import sphere_surface_area, pillow_surface_area
except ImportError:
    from shapes import sphere_surface_area, pillow_surface_area


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


def calculate_pillow_pattern(length: float, width: float, thickness: float = None) -> Dict[str, Any]:
    """
    Розраховує патерн для подушкоподібної оболонки
    
    Подушка складається з двох прямокутних сегментів однакового розміру,
    з'єднаних по кромці, з отвором на одній зі сторін для заповнення.
    
    Args:
        length: Довжина подушки (м)
        width: Ширина подушки (м)
        thickness: Товщина подушки (м) - не використовується для викрійки, лише для опису
    
    Returns:
        Словник з координатами для прямокутних панелей
    """
    # Подушка складається з 2 прямокутних панелей однакового розміру
    panel_area = length * width
    
    # Довжина швів: периметр прямокутника мінус одна сторона (отвір - незакрита ділянка кромки)
    # Зазвичай отвір роблять на коротшій стороні для зручності заповнення
    if width <= length:
        # Отвір на коротшій стороні (ширина) - ця сторона не зшивається
        seam_length = 2 * length + width  # Дві довгі сторони + одна коротка
        opening_side = 'width'
        opening_size = width
    else:
        # Отвір на коротшій стороні (довжина) - ця сторона не зшивається
        seam_length = 2 * width + length  # Дві широкі сторони + одна коротка
        opening_side = 'length'
        opening_size = length
    
    panels = [
        {
            'name': 'Панель 1 (верх/низ)',
            'width': length,
            'height': width,
            'area': panel_area,
            'position': 'top_or_bottom'
        },
        {
            'name': 'Панель 2 (верх/низ)',
            'width': length,
            'height': width,
            'area': panel_area,
            'position': 'top_or_bottom'
        }
    ]
    
    # Загальна площа = 2 панелі
    total_area = 2 * panel_area
    
    return {
        'pattern_type': 'pillow',
        'panels': panels,
        'length': length,
        'width': width,
        'thickness': thickness,
        'total_area': total_area,
        'seam_length': seam_length,
        'opening_side': opening_side,
        'opening_size': opening_size,
        'description': f'Подушкоподібна оболонка: {length:.2f}×{width:.2f} м (2 панелі, незакрита кромка на стороні {opening_side})'
    }


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
        # Для груші використовуємо плавну інтерполяцію
        r_at_height = top_radius * (1 - t) + bottom_radius * t
        
        # Ширина сегмента на цій висоті
        # Використовуємо довжину дуги кола: arc_length = r * theta
        # Для половини сегмента: width = r * sin(theta/2) * 2 = r * 2 * sin(pi/num_gores)
        width_at_height = r_at_height * 2 * math.sin(math.pi / num_gores)
        
        # Координата X (горизонтальна, від центру до краю) - це половина ширини сегмента
        x = width_at_height / 2
        
        gore_points.append((x, y))
    
    # Розраховуємо розміри для друку
    max_width = max(x for x, y in gore_points)
    total_height = height
    
    # Площа одного сегмента (приблизно)
    # Використовуємо наближення через інтеграл
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
            # Півсферичний кінець (перший)
            # y від 0 до radius, h - відстань від центру півсфери
            h = radius - y  # h від radius до 0
            r_at_height = math.sqrt(radius**2 - h**2)
        elif y > length - radius:
            # Півсферичний кінець (другий)
            # y від (length - radius) до length
            h = radius - (length - y)  # h від 0 до radius
            r_at_height = math.sqrt(radius**2 - h**2)
        else:
            # Циліндрична частина
            r_at_height = radius
        
        # Ширина сегмента на цій висоті
        # Використовуємо довжину дуги кола: width = r * 2 * sin(pi/num_gores)
        width_at_height = r_at_height * 2 * math.sin(math.pi / num_gores)
        
        # Координата X (горизонтальна, від центру до краю) - це половина ширини сегмента
        x = width_at_height / 2
        
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


def generate_pattern_from_shape(shape_type: str, shape_params: dict, num_segments: int = 12) -> Dict[str, Any]:
    """
    Генерує патерн на основі типу форми та параметрів
    
    Args:
        shape_type: Тип форми ('sphere', 'pillow', 'pear', 'cigar')
        shape_params: Параметри форми
        num_segments: Кількість сегментів (для сфери, груші та сигари)
    
    Returns:
        Словник з патерном
    """
    if shape_type == 'sphere':
        radius = shape_params.get('radius', 1.0)
        return calculate_sphere_gore_pattern(radius, num_segments)
    
    elif shape_type == 'pillow':
        length = shape_params.get('pillow_len', 3.0)
        width = shape_params.get('pillow_wid', 2.0)
        # Для подушки товщина розраховується з об'єму, але для викрійки не потрібна
        # Використовуємо мінімальну товщину для розрахунку (не впливає на викрійку)
        thickness = 0.1  # Мінімальна товщина для розрахунку (не використовується для викрійки)
        return calculate_pillow_pattern(length, width, thickness)
    
    elif shape_type == 'pear':
        height = shape_params.get('pear_height', 3.0)
        top_radius = shape_params.get('pear_top_radius', 1.2)
        bottom_radius = shape_params.get('pear_bottom_radius', 0.6)
        return calculate_pear_pattern(height, top_radius, bottom_radius, num_segments)
    
    elif shape_type == 'cigar':
        length = shape_params.get('cigar_length', 5.0)
        radius = shape_params.get('cigar_radius', 1.0)
        return calculate_cigar_pattern(length, radius, num_segments)
    
    else:
        raise ValueError(f"Невідомий тип форми: {shape_type}")


def calculate_seam_length(pattern: Dict[str, Any]) -> float:
    """
    Розраховує загальну довжину швів для патерну
    
    Args:
        pattern: Патерн оболонки
    
    Returns:
        Загальна довжина швів (м)
    """
    pattern_type = pattern.get('pattern_type')
    
    if pattern_type == 'sphere_gore':
        num_gores = pattern.get('num_gores', 12)
        radius = pattern.get('radius', 1.0)
        # Довжина одного шва = півколо від полюса до полюса
        seam_length_per_gore = math.pi * radius
        return seam_length_per_gore * num_gores
    
    elif pattern_type == 'pillow':
        # Шви між двома панелями (периметр мінус одна сторона - отвір)
        seam_length = pattern.get('seam_length', 0.0)
        if seam_length > 0:
            return seam_length
        # Якщо seam_length не задано, розраховуємо
        length = pattern.get('length', 3.0)
        width = pattern.get('width', 2.0)
        # Отвір зазвичай на коротшій стороні
        if width <= length:
            return 2 * length + width  # Дві довгі сторони + одна коротка
        else:
            return 2 * width + length  # Дві широкі сторони + одна коротка
    
    elif pattern_type == 'pear_gore':
        num_gores = pattern.get('num_gores', 12)
        height = pattern.get('height', 3.0)
        # Довжина одного шва = висота груші (від верху до низу)
        seam_length_per_gore = height
        return seam_length_per_gore * num_gores
    
    elif pattern_type == 'cigar_gore':
        num_gores = pattern.get('num_gores', 12)
        length = pattern.get('length', 5.0)
        # Довжина одного шва = довжина сигари (вздовж осі)
        seam_length_per_gore = length
        return seam_length_per_gore * num_gores
    
    return 0.0

