"""
Тести для модуля balloon.shapes.registry
"""

import pytest
from balloon.shapes.registry import (
    get_shape_entry,
    get_all_shape_codes,
    get_all_display_names,
    get_shape_code_from_display,
    validate_shape_params,
    get_shape_profile_from_registry,
    get_shape_volume,
    get_shape_area,
    get_shape_dimensions_from_volume
)


class TestShapeRegistry:
    """Тести для реєстру форм"""
    
    def test_get_all_shape_codes(self):
        """Перевірка отримання всіх кодів форм"""
        codes = get_all_shape_codes()
        assert isinstance(codes, list)
        assert "sphere" in codes
        assert "pillow" in codes
        assert "pear" in codes
        assert "cigar" in codes
    
    def test_get_all_display_names(self):
        """Перевірка отримання всіх назв форм"""
        names = get_all_display_names()
        assert isinstance(names, list)
        assert len(names) == 4
    
    def test_get_shape_entry(self):
        """Перевірка отримання запису форми"""
        entry = get_shape_entry("sphere")
        assert entry is not None
        assert entry.shape_code == "sphere"
        assert entry.display_name is not None
    
    def test_get_shape_entry_invalid(self):
        """Перевірка обробки невалідного коду"""
        entry = get_shape_entry("invalid_shape")
        assert entry is None
    
    def test_get_shape_code_from_display(self):
        """Перевірка отримання коду з назви"""
        code = get_shape_code_from_display("Сфера")
        assert code == "sphere"
    
    def test_get_shape_code_from_display_invalid(self):
        """Перевірка обробки невалідної назви"""
        code = get_shape_code_from_display("Невалідна форма")
        assert code is None


class TestValidateShapeParams:
    """Тести для валідації параметрів форм"""
    
    def test_sphere_params(self):
        """Валідація параметрів сфери"""
        params = validate_shape_params("sphere", {"radius": 1.0})
        assert params["radius"] == 1.0
    
    def test_sphere_params_invalid(self):
        """Валідація невалідних параметрів сфери"""
        with pytest.raises(Exception):
            validate_shape_params("sphere", {"radius": -1.0})
    
    def test_pillow_params(self):
        """Валідація параметрів подушки"""
        params = validate_shape_params("pillow", {
            "pillow_len": 3.0,
            "pillow_wid": 2.0
        })
        assert params["pillow_len"] == 3.0
        assert params["pillow_wid"] == 2.0


class TestShapeRegistryFunctions:
    """Тести для функцій реєстру"""
    
    def test_get_shape_volume(self):
        """Перевірка отримання об'єму форми"""
        volume = get_shape_volume("sphere", {"radius": 1.0})
        assert volume > 0
        assert volume == pytest.approx((4/3) * 3.14159, rel=0.01)
    
    def test_get_shape_area(self):
        """Перевірка отримання площі форми"""
        area = get_shape_area("sphere", {"radius": 1.0})
        assert area > 0
        assert area == pytest.approx(4 * 3.14159, rel=0.01)
    
    def test_get_shape_dimensions_from_volume(self):
        """Перевірка отримання розмірів з об'єму"""
        dims = get_shape_dimensions_from_volume("sphere", 10.0, {})
        assert "radius" in dims
        assert dims["radius"] > 0
    
    def test_get_shape_profile_from_registry(self):
        """Перевірка отримання профілю форми"""
        profile = get_shape_profile_from_registry("sphere", {"radius": 1.0})
        assert profile is not None
        assert hasattr(profile, 'r_func')
        assert hasattr(profile, 'z_range')

