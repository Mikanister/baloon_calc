"""
Базові функції для роботи з патернами
"""

import math
from typing import Dict, Any

# Імпорт для pillow (подушка не поверхня обертання)
from balloon.patterns.pillow_pattern import calculate_pillow_pattern

# Використовуємо shapely для правильного normal offset (seam allowance)
try:
    from shapely.geometry import LineString, Polygon
    from shapely.ops import unary_union
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False


def generate_pattern_from_shape(shape_type: str, shape_params: dict, num_segments: int = 12, seam_allowance_mm: float = 10.0) -> Dict[str, Any]:
    """
    Генерує патерн на основі типу форми та параметрів
    
    Примітка: Для sphere/pear/cigar використовуйте generate_pattern_from_shape_profile()
    з balloon.patterns.profile_based для узгодженості з 3D та розрахунками.
    
    Цей метод використовується тільки для pillow (подушка не є поверхнею обертання,
    тому не має профілю r(z)).
    
    Args:
        shape_type: Тип форми ('pillow')
        shape_params: Параметри форми
        num_segments: Кількість сегментів (не використовується для pillow)
        seam_allowance_mm: Припуск на шов (мм) - додається до країв викрійки
    
    Returns:
        Словник з патерном
    
    Raises:
        ValueError: Якщо shape_type не 'pillow'
    """
    if shape_type == 'pillow':
        length = shape_params.get('pillow_len', 3.0)
        width = shape_params.get('pillow_wid', 2.0)
        # Для подушки товщина розраховується з об'єму, але для викрійки не потрібна
        thickness = 0.1  # Мінімальна товщина для розрахунку (не використовується для викрійки)
        pattern = calculate_pillow_pattern(length, width, thickness)
        # Додаємо припуск на шов
        if seam_allowance_mm > 0:
            pattern = _add_seam_allowance_pillow(pattern, seam_allowance_mm / 1000.0)
        return pattern
    else:
        raise ValueError(
            f"Форма '{shape_type}' не підтримується в generate_pattern_from_shape(). "
            f"Для sphere/pear/cigar використовуйте generate_pattern_from_shape_profile() "
            f"з balloon.patterns.profile_based"
        )


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
        # Довжина одного шва = реальна довжина меридіану
        meridian_length = pattern.get('meridian_length')
        if meridian_length and meridian_length > 0:
            seam_length_per_gore = meridian_length
        else:
            # Fallback: обчислюємо приблизно через профіль
            height = pattern.get('height', 3.0)
            top_radius = pattern.get('top_radius', 1.2)
            bottom_radius = pattern.get('bottom_radius', 0.6)
            # Для лінійного профілю: s ≈ height * sqrt(1 + ((top_radius - bottom_radius) / height)^2)
            k = (top_radius - bottom_radius) / height if height > 0 else 0
            seam_length_per_gore = height * math.sqrt(1 + k**2)
        return seam_length_per_gore * num_gores
    
    elif pattern_type == 'cigar_gore':
        num_gores = pattern.get('num_gores', 12)
        # Довжина одного шва = реальна довжина меридіану
        meridian_length = pattern.get('meridian_length')
        if meridian_length and meridian_length > 0:
            seam_length_per_gore = meridian_length
        else:
            # Fallback: обчислюємо приблизно
            length = pattern.get('length', 5.0)
            radius = pattern.get('radius', 1.0)
            cylinder_length = max(0, length - 2 * radius)
            # Довжина меридіану = півколо (нижній кінець) + циліндр + півколо (верхній кінець)
            seam_length_per_gore = math.pi * radius + cylinder_length + math.pi * radius
        return seam_length_per_gore * num_gores
    
    return 0.0


def _add_seam_allowance(pattern: Dict[str, Any], allowance_m: float) -> Dict[str, Any]:
    """
    Додає припуск на шов до викрійки (для gores) по нормалі до контуру
    
    Для кожної точки контуру обчислює дотичну через сусідів,
    нормаль n = (-dy, dx) / ||...|| (перпендикулярна дотичній),
    і зміщує точку p' = p + allowance * n назовні.
    
    Args:
        pattern: Патерн викрійки
        allowance_m: Припуск на шов (м)
    
    Returns:
        Патерн з доданим припуском
    """
    if 'points' not in pattern or len(pattern['points']) < 2:
        return pattern
    
    points = pattern['points']
    new_points = []
    
    for i in range(len(points)):
        x, y = points[i]
        
        # Обчислюємо дотичну до контуру через сусідні точки
        if i == 0:
            # Перша точка: використовуємо наступну
            x_next, y_next = points[i + 1]
            dx = x_next - x
            dy = y_next - y
        elif i == len(points) - 1:
            # Остання точка: використовуємо попередню
            x_prev, y_prev = points[i - 1]
            dx = x - x_prev
            dy = y - y_prev
        else:
            # Середні точки: середнє значення дотичної (краще наближення)
            x_prev, y_prev = points[i - 1]
            x_next, y_next = points[i + 1]
            dx = (x_next - x_prev) / 2
            dy = (y_next - y_prev) / 2
        
        # Нормалізуємо дотичну
        tangent_length = math.sqrt(dx**2 + dy**2)
        if tangent_length > 1e-10:
            dx /= tangent_length
            dy /= tangent_length
        else:
            # Якщо дотична нульова (полюс), використовуємо вертикальну дотичну
            dx = 0.0
            dy = 1.0
        
        # Нормаль до контуру: перпендикулярна дотичній
        # Для дотичної (dx, dy) нормаль = (-dy, dx) або (dy, -dx)
        # Обираємо той, що вказує назовні (для gores: x збільшується назовні)
        # Якщо контур йде вгору (dy > 0), нормаль вправо має мати nx > 0
        nx = -dy  # Перпендикулярна дотичній
        ny = dx
        
        # Перевіряємо напрямок: нормаль має вказувати назовні (nx > 0 для x > 0)
        # Якщо x > 0 і nx < 0, інвертуємо
        if x > 0 and nx < 0:
            nx = -nx
            ny = -ny
        elif x < 0 and nx > 0:
            nx = -nx
            ny = -ny
        
        # Нормалізуємо нормаль
        n_length = math.sqrt(nx**2 + ny**2)
        if n_length > 1e-10:
            nx /= n_length
            ny /= n_length
        else:
            # Якщо нормаль нульова, використовуємо горизонтальну
            nx = 1.0
            ny = 0.0
        
        # Додаємо припуск по нормалі назовні
        new_x = x + allowance_m * nx
        new_y = y + allowance_m * ny
        
        new_points.append((new_x, new_y))
    
    pattern['points'] = new_points
    pattern['max_width'] = max(abs(x) for x, y in new_points)
    pattern['seam_allowance_m'] = allowance_m
    pattern['seam_allowance_method'] = 'manual_normal_offset'
    
    return pattern


def _add_seam_allowance_with_shapely(pattern: Dict[str, Any], allowance_m: float) -> Dict[str, Any]:
    """
    Додає припуск на шов використовуючи shapely для правильного normal offset
    
    Це забезпечує правильний припуск на шов, який йде по нормалі до контуру,
    використовуючи shapely.buffer для точного обчислення.
    """
    points = pattern.get('points', [])
    if not points or len(points) < 2:
        return pattern
    
    # Створюємо LineString з точок (тільки права половина)
    right_points = [(x, y) for x, y in points if x >= 0]
    if len(right_points) < 2:
        # Якщо недостатньо точок, використовуємо ручний метод
        return _add_seam_allowance_manual(pattern, allowance_m)
    
    try:
        # Створюємо лінію з правої половини
        line = LineString(right_points)
        
        # Виконуємо buffer (offset) по нормалі
        buffered = line.buffer(allowance_m, cap_style=2, join_style=2)
        
        # Отримуємо нові точки з буферу
        if buffered.geom_type == 'Polygon':
            exterior = buffered.exterior
            new_right_points = list(exterior.coords)
        elif buffered.geom_type == 'LineString':
            new_right_points = list(buffered.coords)
        else:
            return _add_seam_allowance_manual(pattern, allowance_m)
        
        # Дзеркалюємо для лівої половини та об'єднуємо
        new_points = []
        for x, y in new_right_points:
            if x >= 0:
                new_points.append((x, y))
        
        left_points = [(-x, y) for x, y in reversed(new_right_points) if x >= 0]
        new_points = left_points + new_points
        new_points.sort(key=lambda p: p[1])
        
        pattern['points'] = new_points
        pattern['max_width'] = max(abs(x) for x, y in new_points)
        pattern['seam_allowance_m'] = allowance_m
        pattern['seam_allowance_method'] = 'shapely_normal_offset'
        return pattern
    except Exception:
        return _add_seam_allowance_manual(pattern, allowance_m)


def _add_seam_allowance_manual(pattern: Dict[str, Any], allowance_m: float) -> Dict[str, Any]:
    """Ручний метод додавання припуску (fallback)"""
    return _add_seam_allowance(pattern, allowance_m)


def _add_seam_allowance_pillow(pattern: Dict[str, Any], allowance_m: float) -> Dict[str, Any]:
    """
    Додає припуск на шов до викрійки подушки
    
    Args:
        pattern: Патерн викрійки подушки
        allowance_m: Припуск на шов (м)
    
    Returns:
        Патерн з доданим припуском
    """
    # Для подушки: додаємо припуск по периметру панелей
    if 'panels' in pattern:
        for panel in pattern['panels']:
            # Додаємо припуск до розмірів панелі
            if 'width' in panel:
                panel['width'] = panel['width'] + 2 * allowance_m
            if 'height' in panel:
                panel['height'] = panel['height'] + 2 * allowance_m
    
    pattern['seam_allowance_m'] = allowance_m
    
    return pattern

