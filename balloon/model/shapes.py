"""
Модель форм: об'єм, площа поверхні, розміри

Використовує Shape Registry як єдине джерело правди.
"""

from typing import Dict, Any, Optional, Literal, Tuple
import math

from balloon.shapes.registry import (
    get_shape_entry,
    get_shape_volume as registry_get_volume,
    get_shape_area as registry_get_area,
    get_shape_dimensions_from_volume as registry_get_dimensions,
    validate_shape_params,
)


class ShapeGeometry:
    """
    Геометрія форми оболонки
    
    Attributes:
        shape_type: Тип форми ("sphere", "pillow", "pear", "cigar")
        volume: Об'єм (м³)
        surface_area: Площа поверхні (м²)
        characteristic_radius: Характерний радіус (м)
        dimensions: Словник з розмірами форми
    """
    
    def __init__(
        self,
        shape_type: Literal["sphere", "pillow", "pear", "cigar"],
        volume: float,
        surface_area: float,
        characteristic_radius: float,
        dimensions: Dict[str, float]
    ):
        self.shape_type = shape_type
        self.volume = volume
        self.surface_area = surface_area
        self.characteristic_radius = characteristic_radius
        self.dimensions = dimensions


def get_shape_volume(
    shape_type: Literal["sphere", "pillow", "pear", "cigar"],
    dimensions: Dict[str, float]
) -> float:
    """
    Розраховує об'єм форми через Shape Registry
    
    Args:
        shape_type: Тип форми
        dimensions: Словник з розмірами форми
    
    Returns:
        Об'єм (м³)
    """
    # Використовуємо реєстр замість if/elif логіки
    return registry_get_volume(shape_type, dimensions)


def get_shape_surface_area(
    shape_type: Literal["sphere", "pillow", "pear", "cigar"],
    dimensions: Dict[str, float]
) -> float:
    """
    Розраховує площу поверхні форми через Shape Registry
    
    Args:
        shape_type: Тип форми
        dimensions: Словник з розмірами форми
    
    Returns:
        Площа поверхні (м²)
    """
    # Використовуємо реєстр замість if/elif логіки
    return registry_get_area(shape_type, dimensions)


def get_shape_dimensions_from_volume(
    shape_type: Literal["sphere", "pillow", "pear", "cigar"],
    target_volume: float,
    partial_params: Optional[Dict[str, float]] = None
) -> Tuple[float, float, float, Dict[str, float]]:
    """
    Розраховує розміри форми на основі об'єму через Shape Registry
    
    Args:
        shape_type: Тип форми
        target_volume: Цільовий об'єм (м³)
        partial_params: Часткові параметри (якщо задані, використовуються)
    
    Returns:
        Tuple[об'єм, площа_поверхні, характерний_радіус, словник_розмірів]
    """
    partial_params = partial_params or {}
    
    # Отримуємо розміри через реєстр
    dimensions = registry_get_dimensions(shape_type, target_volume, partial_params)
    
    # Розраховуємо площу поверхні
    surface = registry_get_area(shape_type, dimensions)
    
    # Обчислюємо характерний радіус
    entry = get_shape_entry(shape_type)
    if entry is None:
        raise ValueError(f"Невідома форма: {shape_type}")
    
    if shape_type == "sphere":
        char_r = dimensions.get("radius", 0)
    elif shape_type == "pillow":
        char_r = min(dimensions.get("pillow_len", 0), dimensions.get("pillow_wid", 0)) / 2
    elif shape_type == "pear":
        char_r = (dimensions.get("pear_top_radius", 0) + dimensions.get("pear_bottom_radius", 0)) / 2
    elif shape_type == "cigar":
        char_r = dimensions.get("cigar_radius", 0)
    else:
        char_r = 0.0
    
    return target_volume, surface, char_r, dimensions

