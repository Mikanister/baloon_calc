"""
Модуль для розрахунків форм аеростатів
"""

# Експортуємо функції з окремих модулів
try:
    from baloon.shapes.sphere import (
        sphere_volume,
        sphere_surface_area,
        sphere_radius_from_volume
    )
    from baloon.shapes.pillow import (
        pillow_volume,
        pillow_surface_area,
        pillow_dimensions_from_volume
    )
    from baloon.shapes.pear import (
        pear_volume,
        pear_surface_area,
        pear_dimensions_from_volume
    )
    from baloon.shapes.cigar import (
        cigar_volume,
        cigar_surface_area,
        cigar_dimensions_from_volume
    )
    # Для сумісності з тестами (не використовуються в основному коді)
    from baloon.shapes.cylinder import (
        cylinder_volume,
        cylinder_surface_area,
        cylinder_dimensions_from_volume
    )
    from baloon.shapes.torus import (
        torus_volume,
        torus_surface_area,
        torus_dimensions_from_volume
    )
except ImportError:
    from shapes.sphere import (
        sphere_volume,
        sphere_surface_area,
        sphere_radius_from_volume
    )
    from shapes.pillow import (
        pillow_volume,
        pillow_surface_area,
        pillow_dimensions_from_volume
    )
    from shapes.pear import (
        pear_volume,
        pear_surface_area,
        pear_dimensions_from_volume
    )
    from shapes.cigar import (
        cigar_volume,
        cigar_surface_area,
        cigar_dimensions_from_volume
    )
    # Для сумісності з тестами
    from shapes.cylinder import (
        cylinder_volume,
        cylinder_surface_area,
        cylinder_dimensions_from_volume
    )
    from shapes.torus import (
        torus_volume,
        torus_surface_area,
        torus_dimensions_from_volume
    )

__all__ = [
    # Sphere
    'sphere_volume',
    'sphere_surface_area',
    'sphere_radius_from_volume',
    # Pillow
    'pillow_volume',
    'pillow_surface_area',
    'pillow_dimensions_from_volume',
    # Pear
    'pear_volume',
    'pear_surface_area',
    'pear_dimensions_from_volume',
    # Cigar
    'cigar_volume',
    'cigar_surface_area',
    'cigar_dimensions_from_volume',
    # Cylinder (для тестів)
    'cylinder_volume',
    'cylinder_surface_area',
    'cylinder_dimensions_from_volume',
    # Torus (для тестів)
    'torus_volume',
    'torus_surface_area',
    'torus_dimensions_from_volume',
]

