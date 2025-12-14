"""
Модуль для розрахунків форм аеростатів

Використовує Shape Registry як єдине джерело правди для форм.
"""

# Експортуємо функції з окремих модулів
from balloon.shapes.sphere import (
    sphere_volume,
    sphere_surface_area,
    sphere_radius_from_volume
)
from balloon.shapes.pillow import (
    pillow_volume,
    pillow_surface_area,
    pillow_dimensions_from_volume
)
from balloon.shapes.pear import (
    pear_volume,
    pear_surface_area,
    pear_dimensions_from_volume
)
from balloon.shapes.cigar import (
    cigar_volume,
    cigar_surface_area,
    cigar_dimensions_from_volume
)

# Експортуємо Shape Registry (рекомендований спосіб)
from balloon.shapes.registry import (
    SHAPE_REGISTRY,
    ShapeRegistryEntry,
    get_shape_entry,
    get_all_shape_codes,
    get_all_display_names,
    get_shape_code_from_display,
    validate_shape_params,
    get_shape_profile_from_registry,
    get_shape_volume,
    get_shape_area,
    get_shape_dimensions_from_volume,
)

# Примітка: cylinder та torus залишені в окремих модулях тільки для тестів,
# але не експортуються та не підтримуються в основному коді.
# Можна видалити, якщо тести більше не потребують цих форм.

__all__ = [
    # Функції для роботи з формами (використовуються через Shape Registry)
    'sphere_volume',
    'sphere_surface_area',
    'sphere_radius_from_volume',
    'pillow_volume',
    'pillow_surface_area',
    'pillow_dimensions_from_volume',
    'pear_volume',
    'pear_surface_area',
    'pear_dimensions_from_volume',
    'cigar_volume',
    'cigar_surface_area',
    'cigar_dimensions_from_volume',
    # Shape Registry (рекомендований спосіб)
    'SHAPE_REGISTRY',
    'ShapeRegistryEntry',
    'get_shape_entry',
    'get_all_shape_codes',
    'get_all_display_names',
    'get_shape_code_from_display',
    'validate_shape_params',
    'get_shape_profile_from_registry',
    'get_shape_volume',
    'get_shape_area',
    'get_shape_dimensions_from_volume',
]

