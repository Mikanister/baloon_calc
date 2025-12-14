"""
Тести для модуля balloon.model.shapes
"""

import pytest
from balloon.model.shapes import (
    ShapeGeometry,
    get_shape_volume,
    get_shape_surface_area,
    get_shape_dimensions_from_volume
)


class TestShapeGeometry:
    """Тести для класу ShapeGeometry"""
    
    def test_initialization(self):
        """Перевірка ініціалізації"""
        geom = ShapeGeometry(
            shape_type="sphere",
            volume=10.0,
            surface_area=20.0,
            characteristic_radius=1.0,
            dimensions={"radius": 1.0}
        )
        assert geom.volume == 10.0
        assert geom.surface_area == 20.0
        assert geom.characteristic_radius == 1.0


class TestGetShapeVolume:
    """Тести для функції get_shape_volume"""
    
    def test_sphere_volume(self):
        """Перевірка об'єму сфери"""
        volume = get_shape_volume("sphere", {"radius": 1.0})
        expected = (4/3) * 3.14159 * 1.0**3
        assert volume == pytest.approx(expected, rel=0.01)
    
    def test_pillow_volume(self):
        """Перевірка об'єму подушки"""
        volume = get_shape_volume("pillow", {
            "pillow_len": 3.0,
            "pillow_wid": 2.0,
            "thickness": 1.0
        })
        expected = 3.0 * 2.0 * 1.0
        assert volume == pytest.approx(expected, rel=0.01)
    
    def test_pear_volume(self):
        """Перевірка об'єму груші"""
        volume = get_shape_volume("pear", {
            "pear_height": 3.0,
            "pear_top_radius": 1.2,
            "pear_bottom_radius": 0.6
        })
        assert volume > 0
    
    def test_cigar_volume(self):
        """Перевірка об'єму сигари"""
        volume = get_shape_volume("cigar", {
            "cigar_length": 5.0,
            "cigar_radius": 1.0
        })
        assert volume > 0
    
    def test_invalid_shape(self):
        """Перевірка обробки невалідної форми"""
        with pytest.raises(ValueError):
            get_shape_volume("invalid_shape", {})


class TestGetShapeSurfaceArea:
    """Тести для функції get_shape_surface_area"""
    
    def test_sphere_surface_area(self):
        """Перевірка площі поверхні сфери"""
        area = get_shape_surface_area("sphere", {"radius": 1.0})
        expected = 4 * 3.14159 * 1.0**2
        assert area == pytest.approx(expected, rel=0.01)
    
    def test_pillow_surface_area(self):
        """Перевірка площі поверхні подушки"""
        area = get_shape_surface_area("pillow", {
            "pillow_len": 3.0,
            "pillow_wid": 2.0
        })
        assert area > 0


class TestGetShapeDimensionsFromVolume:
    """Тести для функції get_shape_dimensions_from_volume"""
    
    def test_sphere_from_volume(self):
        """Розрахунок розмірів сфери з об'єму"""
        volume, surface, radius, dims = get_shape_dimensions_from_volume(
            "sphere", 10.0, {}
        )
        
        assert volume == pytest.approx(10.0, rel=0.01)
        assert radius > 0
        assert 'radius' in dims
        assert dims['radius'] == pytest.approx(radius, rel=0.01)
    
    def test_pillow_from_volume(self):
        """Розрахунок розмірів подушки з об'єму"""
        volume, surface, radius, dims = get_shape_dimensions_from_volume(
            "pillow", 6.0, {"pillow_len": 3.0, "pillow_wid": 2.0}
        )
        
        assert volume == pytest.approx(6.0, rel=0.01)
        assert 'pillow_len' in dims
        assert 'pillow_wid' in dims

