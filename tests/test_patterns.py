"""
Тести для модуля patterns.py
"""

import pytest
import math
from balloon.patterns.base import (
    generate_pattern_from_shape,
    calculate_seam_length
)
from balloon.patterns.pillow_pattern import calculate_pillow_pattern
from balloon.patterns.profile_based import generate_pattern_from_shape_profile


class TestSphereGorePattern:
    """Тести для патерну сфери"""
    
    def test_sphere_gore_basic(self):
        """Перевірка базового патерну сфери (через profile_based)"""
        radius = 1.0
        num_gores = 12
        pattern = generate_pattern_from_shape_profile('sphere', {'radius': radius}, num_gores)
        
        assert pattern['pattern_type'] == 'sphere_gore'
        assert pattern['num_gores'] == num_gores
        assert pattern['radius'] == radius
        assert len(pattern['points']) > 0
        # meridian_length = довжина по меридіану (π * radius для сфери)
        meridian_length = pattern.get('meridian_length') or pattern.get('total_height', 0)
        assert meridian_length > 0
        assert meridian_length == pytest.approx(math.pi * radius, rel=0.1)
        # axis_height = геометрична висота (2 * radius для сфери)
        axis_height = pattern.get('axis_height', 0)
        if axis_height > 0:
            assert axis_height == pytest.approx(2 * radius, rel=0.1)
        assert pattern['total_area'] == pytest.approx(4 * math.pi * radius ** 2, rel=0.1)
    
    def test_sphere_gore_min_segments(self):
        """Перевірка мінімальної кількості сегментів"""
        pattern = generate_pattern_from_shape_profile('sphere', {'radius': 1.0}, 2)
        assert pattern['num_gores'] >= 4  # Мінімум 4
    
    def test_sphere_gore_max_segments(self):
        """Перевірка максимальної кількості сегментів"""
        pattern = generate_pattern_from_shape_profile('sphere', {'radius': 1.0}, 50)
        assert pattern['num_gores'] <= 32  # Максимум 32
    
    def test_sphere_gore_points_structure(self):
        """Перевірка структури точок"""
        pattern = generate_pattern_from_shape_profile('sphere', {'radius': 1.0}, 12)
        points = pattern['points']
        
        assert len(points) > 0
        # Перевіряємо, що точки - це кортежі (x, y)
        for point in points:
            assert len(point) == 2
            assert isinstance(point[0], (int, float))
            assert isinstance(point[1], (int, float))
    
    def test_sphere_gore_area_calculation(self):
        """Перевірка розрахунку площі"""
        radius = 2.0
        num_gores = 12
        pattern = generate_pattern_from_shape_profile('sphere', {'radius': radius}, num_gores)
        
        expected_total = 4 * math.pi * radius ** 2
        
        assert pattern['total_area'] == pytest.approx(expected_total, rel=0.1)


class TestPearPattern:
    """Тести для патерну груші (через profile_based)"""
    
    def test_pear_pattern_basic(self):
        """Перевірка базового патерну груші"""
        height = 3.0
        top_radius = 1.2
        bottom_radius = 0.6
        num_gores = 12
        pattern = generate_pattern_from_shape_profile('pear', {
            'pear_height': height,
            'pear_top_radius': top_radius,
            'pear_bottom_radius': bottom_radius
        }, num_gores)
        
        assert pattern['pattern_type'] == 'pear_gore'
        assert pattern['num_gores'] == num_gores
        assert pattern['height'] == height
        assert pattern['top_radius'] == top_radius
        assert pattern['bottom_radius'] == bottom_radius
        assert len(pattern['points']) > 0
    
    def test_pear_pattern_min_segments(self):
        """Перевірка мінімальної кількості сегментів"""
        pattern = generate_pattern_from_shape_profile('pear', {
            'pear_height': 3.0,
            'pear_top_radius': 1.2,
            'pear_bottom_radius': 0.6
        }, 2)
        assert pattern['num_gores'] >= 4  # Мінімум 4
    
    def test_pear_pattern_max_segments(self):
        """Перевірка максимальної кількості сегментів"""
        pattern = generate_pattern_from_shape_profile('pear', {
            'pear_height': 3.0,
            'pear_top_radius': 1.2,
            'pear_bottom_radius': 0.6
        }, 50)
        assert pattern['num_gores'] <= 32  # Максимум 32


class TestCigarPattern:
    """Тести для патерну сигари (через profile_based)"""
    
    def test_cigar_pattern_basic(self):
        """Перевірка базового патерну сигари"""
        length = 5.0
        radius = 1.0
        num_gores = 12
        pattern = generate_pattern_from_shape_profile('cigar', {
            'cigar_length': length,
            'cigar_radius': radius
        }, num_gores)
        
        assert pattern['pattern_type'] == 'cigar_gore'
        assert pattern['num_gores'] == num_gores
        assert pattern['length'] == length
        assert pattern['radius'] == radius
        assert len(pattern['points']) > 0
    
    def test_cigar_pattern_min_segments(self):
        """Перевірка мінімальної кількості сегментів"""
        pattern = generate_pattern_from_shape_profile('cigar', {
            'cigar_length': 5.0,
            'cigar_radius': 1.0
        }, 2)
        assert pattern['num_gores'] >= 4  # Мінімум 4
    
    def test_cigar_pattern_max_segments(self):
        """Перевірка максимальної кількості сегментів"""
        pattern = generate_pattern_from_shape_profile('cigar', {
            'cigar_length': 5.0,
            'cigar_radius': 1.0
        }, 50)
        assert pattern['num_gores'] <= 32  # Максимум 32


class TestPillowPattern:
    """Тести для патерну подушки"""
    
    def test_pillow_pattern_basic(self):
        """Перевірка базового патерну подушки"""
        length = 3.0
        width = 2.0
        pattern = calculate_pillow_pattern(length, width)
        
        assert pattern['pattern_type'] == 'pillow'
        assert pattern['length'] == length
        assert pattern['width'] == width
        assert len(pattern['panels']) == 2
    
    def test_pillow_pattern_panels(self):
        """Перевірка панелей"""
        length = 3.0
        width = 2.0
        pattern = calculate_pillow_pattern(length, width)
        
        panels = pattern['panels']
        assert len(panels) == 2
        
        for panel in panels:
            assert panel['width'] == length
            assert panel['height'] == width
            assert panel['area'] == pytest.approx(length * width, rel=0.01)
    
    def test_pillow_pattern_total_area(self):
        """Перевірка загальної площі"""
        length = 3.0
        width = 2.0
        pattern = calculate_pillow_pattern(length, width)
        
        expected = 2 * length * width
        assert pattern['total_area'] == pytest.approx(expected, rel=0.01)
    
    def test_pillow_pattern_opening_width_side(self):
        """Перевірка отвору на коротшій стороні (ширина)"""
        length = 3.0
        width = 2.0  # width <= length
        pattern = calculate_pillow_pattern(length, width)
        
        assert pattern['opening_side'] == 'width'
        assert pattern['opening_size'] == width
        assert pattern['seam_length'] == pytest.approx(2 * length + width, rel=0.01)
    
    def test_pillow_pattern_opening_length_side(self):
        """Перевірка отвору на коротшій стороні (довжина)"""
        length = 2.0
        width = 3.0  # width > length
        pattern = calculate_pillow_pattern(length, width)
        
        assert pattern['opening_side'] == 'length'
        assert pattern['opening_size'] == length
        assert pattern['seam_length'] == pytest.approx(2 * width + length, rel=0.01)
    
    def test_pillow_pattern_with_thickness(self):
        """Перевірка з товщиною"""
        length = 3.0
        width = 2.0
        thickness = 0.5
        pattern = calculate_pillow_pattern(length, width, thickness)
        
        assert pattern['thickness'] == thickness
        # Товщина не впливає на площу панелей
        assert pattern['total_area'] == pytest.approx(2 * length * width, rel=0.01)


class TestGeneratePatternFromShape:
    """Тести для функції generate_pattern_from_shape"""
    
    def test_generate_sphere_pattern(self):
        """Перевірка генерації патерну сфери (через profile_based)"""
        pattern = generate_pattern_from_shape_profile('sphere', {'radius': 1.0}, 12)
        assert pattern['pattern_type'] == 'sphere_gore'
        assert pattern['radius'] == 1.0
    
    def test_generate_pear_pattern(self):
        """Перевірка генерації патерну груші (через profile_based)"""
        pattern = generate_pattern_from_shape_profile('pear', {
            'pear_height': 3.0,
            'pear_top_radius': 1.2,
            'pear_bottom_radius': 0.6
        }, 12)
        assert pattern['pattern_type'] == 'pear_gore'
        assert pattern['height'] == 3.0
        assert pattern['top_radius'] == 1.2
        assert pattern['bottom_radius'] == 0.6
    
    def test_generate_cigar_pattern(self):
        """Перевірка генерації патерну сигари (через profile_based)"""
        pattern = generate_pattern_from_shape_profile('cigar', {
            'cigar_length': 5.0,
            'cigar_radius': 1.0
        }, 12)
        assert pattern['pattern_type'] == 'cigar_gore'
        assert pattern['length'] == 5.0
        assert pattern['radius'] == 1.0
    
    def test_generate_pillow_pattern(self):
        """Перевірка генерації патерну подушки"""
        pattern = generate_pattern_from_shape('pillow', {
            'pillow_len': 3.0,
            'pillow_wid': 2.0
        }, 12)
        assert pattern['pattern_type'] == 'pillow'
        assert pattern['length'] == 3.0
        assert pattern['width'] == 2.0
    
    def test_generate_pattern_invalid_shape(self):
        """Перевірка обробки невалідної форми"""
        with pytest.raises(ValueError):
            generate_pattern_from_shape('invalid', {}, 12)
        
        with pytest.raises(ValueError):
            generate_pattern_from_shape_profile('invalid', {}, 12)
    
    def test_generate_pattern_default_params(self):
        """Перевірка використання параметрів за замовчуванням"""
        # Сфера без радіусу
        pattern = generate_pattern_from_shape_profile('sphere', {}, 12)
        assert pattern['radius'] == 1.0
        
        # Груша без параметрів
        pattern = generate_pattern_from_shape_profile('pear', {}, 12)
        assert pattern['height'] == 3.0
        assert pattern['top_radius'] == 1.2
        assert pattern['bottom_radius'] == 0.6
        
        # Сигара без параметрів
        pattern = generate_pattern_from_shape_profile('cigar', {}, 12)
        assert pattern['length'] == 5.0
        assert pattern['radius'] == 1.0


class TestCalculateSeamLength:
    """Тести для функції calculate_seam_length"""
    
    def test_seam_length_sphere(self):
        """Перевірка довжини швів для сфери"""
        pattern = generate_pattern_from_shape_profile('sphere', {'radius': 1.0}, 12)
        seam_length = calculate_seam_length(pattern)
        
        # Довжина меридіану для сфери = π * radius
        expected = math.pi * 1.0 * 12  # π * radius * num_gores
        assert seam_length == pytest.approx(expected, rel=0.1)
    
    def test_seam_length_pear(self):
        """Перевірка довжини швів для груші"""
        pattern = generate_pattern_from_shape_profile('pear', {
            'pear_height': 3.0,
            'pear_top_radius': 1.2,
            'pear_bottom_radius': 0.6
        }, 12)
        seam_length = calculate_seam_length(pattern)
        
        # Довжина меридіану (тепер використовується meridian_length з профілю)
        meridian_length = pattern.get('meridian_length') or pattern.get('total_height', 0)
        assert seam_length > 0
        assert seam_length == pytest.approx(meridian_length * 12, rel=0.1)
        # Меридіанна довжина має бути більшою за осьову висоту через нахил
        assert meridian_length > pattern.get('axis_height', 0)
    
    def test_seam_length_cigar(self):
        """Перевірка довжини швів для сигари"""
        pattern = generate_pattern_from_shape_profile('cigar', {
            'cigar_length': 5.0,
            'cigar_radius': 1.0
        }, 12)
        seam_length = calculate_seam_length(pattern)
        
        # Довжина меридіану (тепер використовується meridian_length з профілю)
        meridian_length = pattern.get('meridian_length') or pattern.get('total_height', 0)
        assert seam_length > 0
        assert seam_length == pytest.approx(meridian_length * 12, rel=0.1)
        # Для сигари: нижня півсфера (π*R/2) + циліндр (L-2R) + верхня півсфера (π*R/2)
        # Для L=5, R=1: π/2 + 3 + π/2 = π + 3 ≈ 6.14
        expected_meridian = math.pi * 1.0 + (5.0 - 2 * 1.0)
        assert meridian_length == pytest.approx(expected_meridian, rel=0.1)
        # Меридіанна довжина має бути більшою за осьову довжину через півсфери
        assert meridian_length > pattern.get('axis_height', 0)
    
    def test_seam_length_pillow(self):
        """Перевірка довжини швів для подушки"""
        pattern = calculate_pillow_pattern(3.0, 2.0)
        seam_length = calculate_seam_length(pattern)
        
        # Периметр мінус одна сторона (отвір)
        expected = 2 * 3.0 + 2.0  # 2 * length + width (оскільки width <= length)
        assert seam_length == pytest.approx(expected, rel=0.01)
    
    def test_seam_length_pillow_reverse(self):
        """Перевірка довжини швів для подушки (довжина < ширина)"""
        pattern = calculate_pillow_pattern(2.0, 3.0)
        seam_length = calculate_seam_length(pattern)
        
        # Периметр мінус одна сторона (отвір)
        expected = 2 * 3.0 + 2.0  # 2 * width + length (оскільки length < width)
        assert seam_length == pytest.approx(expected, rel=0.01)
    
    def test_seam_length_unknown_pattern(self):
        """Перевірка обробки невідомого типу патерну"""
        pattern = {'pattern_type': 'unknown'}
        seam_length = calculate_seam_length(pattern)
        assert seam_length == 0.0

