"""
Базові функції для роботи з патернами
"""

import math
from typing import Dict, Any

try:
    from baloon.patterns.sphere_pattern import calculate_sphere_gore_pattern
    from baloon.patterns.pillow_pattern import calculate_pillow_pattern
    from baloon.patterns.pear_pattern import calculate_pear_pattern
    from baloon.patterns.cigar_pattern import calculate_cigar_pattern
except ImportError:
    from patterns.sphere_pattern import calculate_sphere_gore_pattern
    from patterns.pillow_pattern import calculate_pillow_pattern
    from patterns.pear_pattern import calculate_pear_pattern
    from patterns.cigar_pattern import calculate_cigar_pattern


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

