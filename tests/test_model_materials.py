"""
Тести для модуля balloon.model.materials
"""

import pytest
from balloon.model.materials import (
    get_material_density,
    get_material_stress_limit,
    get_material_permeability,
    calc_stress
)
from balloon.constants import MATERIALS, PERMEABILITY


class TestGetMaterialDensity:
    """Тести для функції get_material_density"""
    
    def test_tpu_density(self):
        """Перевірка щільності TPU"""
        density = get_material_density("TPU")
        assert density > 0
        assert density == pytest.approx(MATERIALS["TPU"][0], rel=0.01)
    
    def test_hdpe_density(self):
        """Перевірка щільності HDPE"""
        density = get_material_density("HDPE")
        assert density > 0
        assert density == pytest.approx(MATERIALS["HDPE"][0], rel=0.01)
    
    def test_invalid_material(self):
        """Перевірка обробки невалідного матеріалу"""
        with pytest.raises(KeyError):
            get_material_density("Невалідний матеріал")
    
    def test_all_materials(self):
        """Перевірка всіх матеріалів"""
        for material in MATERIALS.keys():
            density = get_material_density(material)
            assert density > 0
            assert density < 5000  # Розумні межі (кг/м³)


class TestGetMaterialStressLimit:
    """Тести для функції get_material_stress_limit"""
    
    def test_tpu_stress_limit(self):
        """Перевірка граничної напруги TPU"""
        stress = get_material_stress_limit("TPU")
        assert stress > 0
        assert stress == pytest.approx(MATERIALS["TPU"][1], rel=0.01)
    
    def test_invalid_material(self):
        """Перевірка обробки невалідного матеріалу"""
        with pytest.raises(KeyError):
            get_material_stress_limit("Невалідний матеріал")
    
    def test_all_materials(self):
        """Перевірка всіх матеріалів"""
        for material in MATERIALS.keys():
            stress = get_material_stress_limit(material)
            assert stress > 0
            assert stress < 1e10  # Розумні межі (Па)


class TestGetMaterialPermeability:
    """Тести для функції get_material_permeability"""
    
    def test_tpu_helium_permeability(self):
        """Перевірка проникності TPU для гелію"""
        perm = get_material_permeability("TPU", "Гелій")
        if perm is not None:
            assert perm >= 0
    
    def test_material_without_permeability(self):
        """Перевірка матеріалу без даних про проникність"""
        # Деякі матеріали можуть не мати даних
        perm = get_material_permeability("TPU", "Невалідний газ")
        assert perm is None
    
    def test_invalid_material(self):
        """Перевірка обробки невалідного матеріалу"""
        perm = get_material_permeability("Невалідний матеріал", "Гелій")
        assert perm is None


class TestCalcStress:
    """Тести для функції calc_stress"""
    
    def test_basic_stress(self):
        """Базовий розрахунок напруги"""
        p_internal = 110000  # Па
        p_external = 100000  # Па
        r = 1.0  # м
        t = 0.0001  # м (0.1 мм)
        
        stress = calc_stress(p_internal, p_external, r, t)
        
        # Для тонкостінної оболонки: σ = ΔP * r / (2 * t)
        expected = (p_internal - p_external) * r / (2 * t)
        assert stress == pytest.approx(expected, rel=0.01)
        assert stress > 0
    
    def test_zero_thickness(self):
        """Перевірка при нульовій товщині"""
        stress = calc_stress(110000, 100000, 1.0, 0.0)
        assert stress == 0.0
    
    def test_negative_pressure_difference(self):
        """Перевірка при від'ємній різниці тисків"""
        stress = calc_stress(100000, 110000, 1.0, 0.0001)
        assert stress == 0.0  # Напруга не може бути від'ємною
    
    def test_stress_proportionality(self):
        """Перевірка пропорційності напруги"""
        p_internal1 = 110000
        p_internal2 = 120000
        p_external = 100000
        r = 1.0
        t = 0.0001
        
        stress1 = calc_stress(p_internal1, p_external, r, t)
        stress2 = calc_stress(p_internal2, p_external, r, t)
        
        # Напруга має бути пропорційна різниці тисків
        # stress1 відповідає ΔP=10000, stress2 відповідає ΔP=20000
        assert stress2 == pytest.approx(stress1 * 2, rel=0.01)
    
    def test_stress_inverse_thickness(self):
        """Перевірка оберненої пропорційності товщині"""
        p_internal = 110000
        p_external = 100000
        r = 1.0
        
        stress1 = calc_stress(p_internal, p_external, r, 0.0001)
        stress2 = calc_stress(p_internal, p_external, r, 0.0002)
        
        # Напруга обернено пропорційна товщині
        assert stress1 == pytest.approx(stress2 * 2, rel=0.01)

