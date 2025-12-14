"""
Тести для перевірки виправлених математичних формул
"""

import pytest
import math
from balloon.model.atmosphere import air_density_at_height
from balloon.model.gas import calculate_gas_density_at_altitude
from balloon.shapes.sphere import sphere_surface_area
from balloon.constants import (
    GAS_SPECIFIC_CONSTANT,
    SEA_LEVEL_PRESSURE,
    T0
)


class TestSphereSurfaceArea:
    """Тести для правильної формули площі поверхні сфери"""
    
    def test_surface_area_formula(self):
        """Перевірка правильності формули площі поверхні"""
        # Для сфери з радіусом 1 м
        radius = 1.0
        surface_area = sphere_surface_area(radius)
        
        # Правильна формула: S = 4πr²
        expected = 4 * math.pi * radius**2
        assert surface_area == pytest.approx(expected, rel=1e-10)
        
        # Альтернативна перевірка через об'єм
        volume = (4/3) * math.pi * radius**3
        expected_from_volume = (36 * math.pi * volume**2) ** (1/3)
        assert surface_area == pytest.approx(expected_from_volume, rel=1e-10)
    
    def test_surface_area_known_values(self):
        """Перевірка на відомих значеннях"""
        # Сфера з радіусом 1 м: S = 12.566 м²
        radius = 1.0
        surface_area = sphere_surface_area(radius)
        expected = 12.566370614359172  # 4π
        assert surface_area == pytest.approx(expected, rel=1e-5)
        
        # Сфера з радіусом 2 м: S = 50.27 м²
        radius = 2.0
        surface_area = sphere_surface_area(radius)
        expected = 50.26548245743669  # 4π * 4
        assert surface_area == pytest.approx(expected, rel=1e-5)
    
    def test_zero_radius(self):
        """Перевірка при нульовому радіусі"""
        assert sphere_surface_area(0) == 0.0
    
    def test_old_vs_new_formula(self):
        """Порівняння старої та нової формули"""
        radius = 1.0
        volume = (4/3) * math.pi * radius**3
        
        # Стара (неправильна) формула через об'єм
        old_formula = (volume * 6 / math.pi) ** (2 / 3)
        
        # Нова (правильна) формула через радіус
        new_formula = sphere_surface_area(radius)
        
        # Нова формула має давати більший результат
        assert new_formula > old_formula
        
        # Різниця має бути помітною (нова формула точніша)
        ratio = new_formula / old_formula
        # Співвідношення може бути різним залежно від радіусу
        # Головне - нова формула має давати більший результат
        assert ratio > 1.0


class TestGasDensityAtAltitude:
    """Тести для розрахунку щільності газу на висоті"""
    
    def test_helium_at_sea_level(self):
        """Перевірка щільності гелію на рівні моря"""
        pressure = SEA_LEVEL_PRESSURE  # 101325 Па
        temperature = 15 + T0  # 288.15 К
        
        rho = calculate_gas_density_at_altitude("Гелій", pressure, temperature)
        
        # Очікувана щільність: ρ = P/(R_specific * T)
        # R_specific для гелію = 2077 Дж/(кг·К)
        expected = pressure / (GAS_SPECIFIC_CONSTANT["Гелій"] * temperature)
        assert rho == pytest.approx(expected, rel=1e-10)
        
        # Перевірка з відомим значенням (приблизно 0.1786 кг/м³ при STP)
        assert rho == pytest.approx(0.1786, abs=0.01)
    
    def test_hydrogen_at_sea_level(self):
        """Перевірка щільності водню на рівні моря"""
        pressure = SEA_LEVEL_PRESSURE
        temperature = 15 + T0
        
        rho = calculate_gas_density_at_altitude("Водень", pressure, temperature)
        
        # Очікувана щільність
        expected = pressure / (GAS_SPECIFIC_CONSTANT["Водень"] * temperature)
        assert rho == pytest.approx(expected, rel=1e-10)
        
        # Перевірка з відомим значенням (приблизно 0.0899 кг/м³ при STP)
        assert rho == pytest.approx(0.0899, abs=0.01)
    
    def test_helium_at_altitude(self):
        """Перевірка щільності гелію на висоті"""
        # На висоті 10 км
        _, _, pressure = air_density_at_height(10000, 15)
        temp_C, _, _ = air_density_at_height(10000, 15)
        temperature = temp_C + T0
        
        rho = calculate_gas_density_at_altitude("Гелій", pressure, temperature)
        
        # На висоті щільність має бути меншою
        rho_sea_level = calculate_gas_density_at_altitude(
            "Гелій", SEA_LEVEL_PRESSURE, 15 + T0
        )
        
        assert rho < rho_sea_level
        # На 10 км щільність має бути приблизно в 2.5 рази меншою
        ratio = rho_sea_level / rho
        assert 2.0 < ratio < 3.0
    
    def test_density_decreases_with_altitude(self):
        """Перевірка що щільність зменшується з висотою"""
        heights = [0, 1000, 5000, 10000]
        densities = []
        
        for h in heights:
            _, _, pressure = air_density_at_height(h, 15)
            temp_C, _, _ = air_density_at_height(h, 15)
            temperature = temp_C + T0
            
            rho = calculate_gas_density_at_altitude("Гелій", pressure, temperature)
            densities.append(rho)
        
        # Перевірка що щільність зменшується
        for i in range(1, len(densities)):
            assert densities[i] < densities[i-1]
    
    def test_hot_air_density(self):
        """Перевірка щільності гарячого повітря"""
        pressure = SEA_LEVEL_PRESSURE
        temperature = 100 + T0  # 373.15 К
        
        rho = calculate_gas_density_at_altitude("Гаряче повітря", pressure, temperature)
        
        # Для повітря: ρ = P/(R * T), де R = 287.05 Дж/(кг·К)
        from balloon.constants import GAS_CONSTANT
        expected = pressure / (GAS_CONSTANT * temperature)
        assert rho == pytest.approx(expected, rel=1e-10)
        
        # Гаряче повітря має бути легшим за холодне
        rho_cold = calculate_gas_density_at_altitude(
            "Гаряче повітря", pressure, 15 + T0
        )
        assert rho < rho_cold
    
    def test_invalid_gas_type(self):
        """Перевірка обробки невалідного типу газу"""
        with pytest.raises(ValueError):
            calculate_gas_density_at_altitude("Невідомий газ", 101325, 288.15)


class TestLiftCalculationCorrection:
    """Тести для перевірки правильності розрахунку підйомної сили"""
    
    def test_lift_with_corrected_density(self):
        """Перевірка що підйомна сила розраховується правильно"""
        from balloon.model.solve import solve_volume_to_payload
        
        # Розрахунок на рівні моря
        results_sea = solve_volume_to_payload(
            gas_type="Гелій",
            gas_volume=10.0,
            material="TPU",
            thickness_um=35,
            start_height=0.0,
            work_height=0.0,
            ground_temp=15.0,
            inside_temp=15.0,
            duration=0.0,
            perm_mult=1.0,
            shape_type="sphere",
            shape_params={},
            extra_mass=0.0,
            seam_factor=1.0
        )
        
        # Розрахунок на висоті 10 км
        results_alt = solve_volume_to_payload(
            gas_type="Гелій",
            gas_volume=10.0,
            material="TPU",
            thickness_um=35,
            start_height=0.0,
            work_height=10000.0,
            ground_temp=15.0,
            inside_temp=15.0,
            duration=0.0,
            perm_mult=1.0,
            shape_type="sphere",
            shape_params={},
            extra_mass=0.0,
            seam_factor=1.0
        )
        
        # На висоті підйомна сила має бути меншою
        # (бо щільність повітря зменшується швидше ніж щільність гелію)
        # Але об'єм кулі збільшується, тому результат може бути різним
        
        # Перевірка що щільність повітря на висоті менша
        assert results_alt['rho_air'] < results_sea['rho_air']
        
        # Перевірка що щільність гелію на висоті теж менша
        # (але це тепер враховується правильно!)
        assert results_alt['net_lift_per_m3'] < results_sea['net_lift_per_m3']

