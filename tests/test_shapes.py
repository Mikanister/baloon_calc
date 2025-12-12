"""
Тести для модуля shapes.py
"""

import pytest
import math
from baloon.shapes import (
    sphere_volume,
    sphere_surface_area,
    cylinder_volume,
    cylinder_surface_area,
    torus_volume,
    torus_surface_area,
    pillow_volume,
    pillow_surface_area,
    sphere_radius_from_volume,
    cylinder_dimensions_from_volume,
    torus_dimensions_from_volume,
    pillow_dimensions_from_volume,
)


class TestSphereFunctions:
    """Тести для функцій сфери"""
    
    def test_sphere_volume(self):
        """Перевірка об'єму сфери"""
        r = 1.0
        volume = sphere_volume(r)
        expected = (4/3) * math.pi * r**3
        assert volume == pytest.approx(expected, rel=0.01)
    
    def test_sphere_surface_area(self):
        """Перевірка площі поверхні сфери"""
        r = 1.0
        surface = sphere_surface_area(r)
        expected = 4 * math.pi * r**2
        assert surface == pytest.approx(expected, rel=0.01)
    
    def test_sphere_radius_from_volume(self):
        """Перевірка розрахунку радіусу за об'ємом"""
        volume = 10.0
        r = sphere_radius_from_volume(volume)
        # Перевіряємо, що об'єм відповідає
        calculated_volume = sphere_volume(r)
        assert calculated_volume == pytest.approx(volume, rel=0.01)
    
    def test_sphere_radius_from_volume_zero(self):
        """Перевірка при нульовому об'ємі"""
        r = sphere_radius_from_volume(0)
        assert r == 0.0


class TestCylinderFunctions:
    """Тести для функцій циліндра"""
    
    def test_cylinder_volume(self):
        """Перевірка об'єму циліндра"""
        r, h = 1.0, 2.0
        volume = cylinder_volume(r, h)
        expected = math.pi * r**2 * h
        assert volume == pytest.approx(expected, rel=0.01)
    
    def test_cylinder_surface_area(self):
        """Перевірка площі поверхні циліндра"""
        r, h = 1.0, 2.0
        surface = cylinder_surface_area(r, h, include_ends=True)
        expected = 2 * math.pi * r * h + 2 * math.pi * r**2
        assert surface == pytest.approx(expected, rel=0.01)
    
    def test_cylinder_dimensions_from_volume_with_radius(self):
        """Перевірка розрахунку висоти за об'ємом та радіусом"""
        volume = 10.0
        radius = 1.0
        r, h = cylinder_dimensions_from_volume(volume, radius=radius)
        assert r == pytest.approx(radius, rel=0.01)
        # Перевіряємо об'єм
        calculated_volume = cylinder_volume(r, h)
        assert calculated_volume == pytest.approx(volume, rel=0.01)
    
    def test_cylinder_dimensions_from_volume_with_height(self):
        """Перевірка розрахунку радіусу за об'ємом та висотою"""
        volume = 10.0
        height = 2.0
        r, h = cylinder_dimensions_from_volume(volume, height=height)
        assert h == pytest.approx(height, rel=0.01)
        # Перевіряємо об'єм
        calculated_volume = cylinder_volume(r, h)
        assert calculated_volume == pytest.approx(volume, rel=0.01)
    
    def test_cylinder_dimensions_from_volume_auto(self):
        """Перевірка автоматичного розрахунку розмірів"""
        volume = 10.0
        r, h = cylinder_dimensions_from_volume(volume)
        # Перевіряємо об'єм
        calculated_volume = cylinder_volume(r, h)
        assert calculated_volume == pytest.approx(volume, rel=0.01)
        # Перевіряємо співвідношення (h = 2r)
        assert h == pytest.approx(2 * r, rel=0.1)


class TestTorusFunctions:
    """Тести для функцій тора"""
    
    def test_torus_volume(self):
        """Перевірка об'єму тора"""
        R, r = 2.0, 0.5
        volume = torus_volume(R, r)
        expected = 2 * math.pi**2 * R * r**2
        assert volume == pytest.approx(expected, rel=0.01)
    
    def test_torus_surface_area(self):
        """Перевірка площі поверхні тора"""
        R, r = 2.0, 0.5
        surface = torus_surface_area(R, r)
        expected = 4 * math.pi**2 * R * r
        assert surface == pytest.approx(expected, rel=0.01)
    
    def test_torus_dimensions_from_volume_with_major(self):
        """Перевірка розрахунку minor за об'ємом та major"""
        volume = 10.0
        major = 2.0
        R, r = torus_dimensions_from_volume(volume, major_radius=major)
        assert R == pytest.approx(major, rel=0.01)
        # Перевіряємо об'єм
        calculated_volume = torus_volume(R, r)
        assert calculated_volume == pytest.approx(volume, rel=0.01)
    
    def test_torus_dimensions_from_volume_with_minor(self):
        """Перевірка розрахунку major за об'ємом та minor"""
        volume = 10.0
        minor = 0.5
        R, r = torus_dimensions_from_volume(volume, minor_radius=minor)
        assert r == pytest.approx(minor, rel=0.01)
        # Перевіряємо об'єм
        calculated_volume = torus_volume(R, r)
        assert calculated_volume == pytest.approx(volume, rel=0.01)
    
    def test_torus_dimensions_from_volume_auto(self):
        """Перевірка автоматичного розрахунку розмірів"""
        volume = 10.0
        R, r = torus_dimensions_from_volume(volume)
        # Перевіряємо об'єм
        calculated_volume = torus_volume(R, r)
        assert calculated_volume == pytest.approx(volume, rel=0.01)
        # Перевіряємо співвідношення (R = 4r)
        assert R == pytest.approx(4 * r, rel=0.1)


class TestPillowFunctions:
    """Тести для функцій подушки"""
    
    def test_pillow_volume(self):
        """Перевірка об'єму подушки"""
        L, W, H = 3.0, 2.0, 1.0
        volume = pillow_volume(L, W, H)
        expected = L * W * H
        assert volume == pytest.approx(expected, rel=0.01)
    
    def test_pillow_volume_without_thickness(self):
        """Перевірка об'єму подушки без товщини (використовується дефолт)"""
        L, W = 3.0, 2.0
        volume = pillow_volume(L, W)  # thickness за замовчуванням = 1.0
        expected = L * W * 1.0
        assert volume == pytest.approx(expected, rel=0.01)
    
    def test_pillow_surface_area(self):
        """Перевірка площі поверхні подушки"""
        L, W = 3.0, 2.0
        surface = pillow_surface_area(L, W)
        # Площа = 2 прямокутні панелі
        expected = 2 * L * W
        assert surface == pytest.approx(expected, rel=0.01)
    
    def test_pillow_surface_area_with_thickness(self):
        """Перевірка площі поверхні подушки з товщиною (не впливає на площу)"""
        L, W, H = 3.0, 2.0, 1.0
        surface = pillow_surface_area(L, W, H)
        # Площа все одно = 2 прямокутні панелі (товщина не враховується)
        expected = 2 * L * W
        assert surface == pytest.approx(expected, rel=0.01)
    
    def test_pillow_dimensions_from_volume_with_two_params(self):
        """Перевірка розрахунку третього параметра"""
        volume = 6.0
        length = 3.0
        width = 2.0
        L, W, H = pillow_dimensions_from_volume(volume, length=length, width=width)
        assert L == pytest.approx(length, rel=0.01)
        assert W == pytest.approx(width, rel=0.01)
        # Перевіряємо об'єм
        calculated_volume = pillow_volume(L, W, H)
        assert calculated_volume == pytest.approx(volume, rel=0.01)
    
    def test_pillow_dimensions_from_volume_with_one_param(self):
        """Перевірка розрахунку двох параметрів за одним"""
        volume = 6.0
        length = 3.0
        L, W, H = pillow_dimensions_from_volume(volume, length=length)
        # Перевіряємо об'єм
        calculated_volume = pillow_volume(L, W, H)
        assert calculated_volume == pytest.approx(volume, rel=0.01)
    
    def test_pillow_dimensions_from_volume_auto(self):
        """Перевірка автоматичного розрахунку розмірів"""
        volume = 6.0
        L, W, H = pillow_dimensions_from_volume(volume)
        # Перевіряємо об'єм
        calculated_volume = pillow_volume(L, W, H)
        assert calculated_volume == pytest.approx(volume, rel=0.01)
        # Перевіряємо співвідношення (L:W:H = 3:2:1)
        assert L == pytest.approx(3 * H, rel=0.1)
        assert W == pytest.approx(2 * H, rel=0.1)

