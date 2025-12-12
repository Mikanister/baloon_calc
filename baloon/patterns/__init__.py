"""
Модуль для розрахунку викрійок/патернів
"""

# Експортуємо функції з окремих модулів
try:
    from baloon.patterns.sphere_pattern import calculate_sphere_gore_pattern
    from baloon.patterns.pillow_pattern import calculate_pillow_pattern
    from baloon.patterns.pear_pattern import calculate_pear_pattern
    from baloon.patterns.cigar_pattern import calculate_cigar_pattern
    from baloon.patterns.base import (
        generate_pattern_from_shape,
        calculate_seam_length
    )
except ImportError:
    from patterns.sphere_pattern import calculate_sphere_gore_pattern
    from patterns.pillow_pattern import calculate_pillow_pattern
    from patterns.pear_pattern import calculate_pear_pattern
    from patterns.cigar_pattern import calculate_cigar_pattern
    from patterns.base import (
        generate_pattern_from_shape,
        calculate_seam_length
    )

__all__ = [
    'calculate_sphere_gore_pattern',
    'calculate_pillow_pattern',
    'calculate_pear_pattern',
    'calculate_cigar_pattern',
    'generate_pattern_from_shape',
    'calculate_seam_length',
]

