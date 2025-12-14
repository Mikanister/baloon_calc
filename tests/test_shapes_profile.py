"""
Тести для модуля balloon.shapes.profile
"""

import pytest
import numpy as np
from balloon.shapes.profile import (
    ShapeProfile,
    create_sphere_profile,
    create_pillow_profile,
    create_pear_profile,
    create_cigar_profile,
    get_shape_profile
)


class TestShapeProfile:
    """Тести для класу ShapeProfile"""
    
    def test_initialization(self):
        """Перевірка ініціалізації"""
        def r_func(z):
            return 1.0
        
        profile = ShapeProfile(
            r_func=r_func,
            z_range=(0.0, 1.0)
        )
        
        assert profile.r_func(0.5) == 1.0
        assert profile.z_range == (0.0, 1.0)
    
    def test_generate_mesh(self):
        """Перевірка генерації 3D сітки"""
        def r_func(z):
            return 1.0
        
        profile = ShapeProfile(
            r_func=r_func,
            z_range=(0.0, 1.0)
        )
        
        X, Y, Z = profile.generate_mesh(num_theta=10, num_z=10)
        
        # З адаптивною дискретизацією кількість точок по Z може відрізнятися
        # Але форма має бути правильною: (num_theta, num_z_points)
        assert X.shape[0] == 10  # num_theta
        assert Y.shape[0] == 10
        assert Z.shape[0] == 10
        assert X.shape == Y.shape == Z.shape  # Всі мають однакову форму
        assert X.shape[1] >= 10  # Може бути більше точок через адаптивну дискретизацію
        assert np.all(Z >= -0.5)  # З центруванням
        assert np.all(Z <= 0.5)


class TestCreateSphereProfile:
    """Тести для функції create_sphere_profile"""
    
    def test_basic_profile(self):
        """Базовий профіль сфери"""
        profile = create_sphere_profile(1.0)
        
        assert profile is not None
        assert profile.z_range[0] == 0.0
        assert profile.z_range[1] == 2.0
        assert profile.r_func(1.0) == pytest.approx(1.0, rel=0.01)  # На центрі
    
    def test_profile_at_poles(self):
        """Перевірка профілю на полюсах"""
        profile = create_sphere_profile(1.0)
        
        # На полюсах радіус має бути 0
        assert profile.r_func(0.0) == pytest.approx(0.0, abs=0.01)
        assert profile.r_func(2.0) == pytest.approx(0.0, abs=0.01)


class TestCreatePillowProfile:
    """Тести для функції create_pillow_profile"""
    
    def test_basic_profile(self):
        """Базовий профіль подушки"""
        profile = create_pillow_profile(3.0, 2.0, 1.0)
        
        assert profile is not None
        # Pillow profile має z_range від 0
        assert profile.z_range[0] == 0.0
        assert profile.z_range[1] > 0.0


class TestCreatePearProfile:
    """Тести для функції create_pear_profile"""
    
    def test_basic_profile(self):
        """Базовий профіль груші"""
        profile = create_pear_profile(3.0, 1.2, 0.6)
        
        assert profile is not None
        assert profile.z_range[0] == 0.0
        assert profile.z_range[1] == 3.0
        assert profile.r_func(0.0) == pytest.approx(0.6, rel=0.01)  # Низ: bottom_radius
        assert profile.r_func(1.8) == pytest.approx(1.2, rel=0.01)  # Межа конус-півсфера: top_radius
        assert profile.r_func(3.0) == pytest.approx(0.0, rel=0.01)  # Вершина: радіус = 0


class TestCreateCigarProfile:
    """Тести для функції create_cigar_profile"""
    
    def test_basic_profile(self):
        """Базовий профіль сигари"""
        profile = create_cigar_profile(5.0, 1.0)
        
        assert profile is not None
        assert profile.z_range[0] == 0.0
        assert profile.z_range[1] == 5.0
        assert profile.r_func(2.5) == pytest.approx(1.0, rel=0.01)  # На центрі циліндра


class TestGetShapeProfile:
    """Тести для функції get_shape_profile"""
    
    def test_sphere_profile(self):
        """Отримання профілю сфери"""
        profile = get_shape_profile("sphere", {"radius": 1.0})
        assert profile is not None
    
    def test_pillow_profile(self):
        """Отримання профілю подушки"""
        profile = get_shape_profile("pillow", {
            "pillow_len": 3.0,
            "pillow_wid": 2.0,
            "thickness": 1.0
        })
        assert profile is not None
    
    def test_invalid_shape(self):
        """Перевірка обробки невалідної форми"""
        profile = get_shape_profile("invalid_shape", {})
        assert profile is None

