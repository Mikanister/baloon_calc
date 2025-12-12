"""
Тести для модуля calculations.py
"""

import pytest
import math
from baloon.calculations import (
    air_density_at_height,
    calc_stress,
    required_balloon_volume,
    calculate_hot_air_density,
    calculate_gas_loss,
    calculate_balloon_parameters
)
from baloon.constants import (
    T0, SEA_LEVEL_PRESSURE, SEA_LEVEL_AIR_DENSITY,
    GAS_CONSTANT, GAS_DENSITY, MATERIALS
)


class TestAirDensityAtHeight:
    """Тести для функції air_density_at_height"""
    
    def test_sea_level(self):
        """Перевірка на рівні моря"""
        temp, rho, pressure = air_density_at_height(0, 15)
        assert temp == pytest.approx(15, abs=0.1)
        assert pressure == pytest.approx(SEA_LEVEL_PRESSURE, rel=0.01)
        assert rho == pytest.approx(SEA_LEVEL_AIR_DENSITY, rel=0.01)
    
    def test_1000m_height(self):
        """Перевірка на висоті 1000м"""
        temp, rho, pressure = air_density_at_height(1000, 15)
        assert temp < 15  # Температура знижується з висотою
        assert pressure < SEA_LEVEL_PRESSURE  # Тиск знижується
        assert rho < SEA_LEVEL_AIR_DENSITY  # Щільність знижується
        assert temp == pytest.approx(8.5, abs=1.0)  # Приблизно -6.5°C на км
    
    def test_negative_height(self):
        """Перевірка на від'ємній висоті (нижче рівня моря)"""
        temp, rho, pressure = air_density_at_height(-100, 15)
        assert temp > 15
        assert pressure > SEA_LEVEL_PRESSURE
        assert rho > SEA_LEVEL_AIR_DENSITY


class TestCalcStress:
    """Тести для функції calc_stress"""
    
    def test_zero_thickness(self):
        """Перевірка при нульовій товщині"""
        stress = calc_stress(101325, 101325, 1.0, 0.0)
        assert stress == 0.0
    
    def test_zero_pressure_difference(self):
        """Перевірка при рівних тисках"""
        stress = calc_stress(101325, 101325, 1.0, 0.001)
        assert stress == 0.0
    
    def test_positive_pressure_difference(self):
        """Перевірка при позитивній різниці тисків"""
        p_internal = 102000  # Па
        p_external = 101000  # Па
        radius = 1.0  # м
        thickness = 0.001  # м (1 мм)
        stress = calc_stress(p_internal, p_external, radius, thickness)
        expected = (p_internal - p_external) * radius / (2 * thickness)
        assert stress == pytest.approx(expected, rel=0.01)
    
    def test_negative_pressure_difference(self):
        """Перевірка при негативній різниці тисків (здута куля)"""
        stress = calc_stress(100000, 101325, 1.0, 0.001)
        assert stress == 0.0  # Напруга не може бути від'ємною


class TestRequiredBalloonVolume:
    """Тести для функції required_balloon_volume"""
    
    def test_sea_level(self):
        """Перевірка на рівні моря"""
        volume = required_balloon_volume(10, 15, SEA_LEVEL_PRESSURE, 15 + T0)
        assert volume == pytest.approx(10, rel=0.01)
    
    def test_higher_altitude(self):
        """Перевірка на висоті"""
        _, _, pressure = air_density_at_height(1000, 15)
        temp_C, _, _ = air_density_at_height(1000, 15)
        temp_K = temp_C + T0
        
        volume = required_balloon_volume(10, 15, pressure, temp_K)
        assert volume > 10  # Об'єм збільшується з висотою


class TestCalculateHotAirDensity:
    """Тести для функції calculate_hot_air_density"""
    
    def test_100_degrees(self):
        """Перевірка для 100°C"""
        rho = calculate_hot_air_density(100)
        expected = SEA_LEVEL_AIR_DENSITY * T0 / (100 + T0)
        assert rho == pytest.approx(expected, rel=0.01)
        assert rho < SEA_LEVEL_AIR_DENSITY  # Гаряче повітря легше
    
    def test_room_temperature(self):
        """Перевірка для кімнатної температури"""
        rho = calculate_hot_air_density(20)
        assert rho == pytest.approx(SEA_LEVEL_AIR_DENSITY, rel=0.1)


class TestCalculateGasLoss:
    """Тести для функції calculate_gas_loss"""
    
    def test_zero_duration(self):
        """Перевірка при нульовій тривалості"""
        loss = calculate_gas_loss(1e-13, 100, 1000, 0, 0.000035)
        assert loss == 0.0
    
    def test_positive_loss(self):
        """Перевірка позитивних втрат"""
        permeability = 1e-13  # м²/(с·Па)
        surface_area = 100  # м²
        delta_p = 1000  # Па
        duration = 24  # год
        thickness = 0.000035  # м (35 мкм)
        
        loss = calculate_gas_loss(permeability, surface_area, delta_p, duration, thickness)
        assert loss > 0
        # Перевірка формули: Q = permeability * surface_area * delta_p * t_sec / thickness
        expected = permeability * surface_area * delta_p * (duration * 3600) / thickness
        assert loss == pytest.approx(expected, rel=0.01)


class TestCalculateBalloonParameters:
    """Тести для основної функції calculate_balloon_parameters"""
    
    def test_helium_payload_mode(self):
        """Перевірка розрахунку для гелію в режимі payload"""
        results = calculate_balloon_parameters(
            gas_type="Гелій",
            gas_volume=10,
            material="TPU",
            thickness_mm=35,
            start_height=0,
            work_height=1000,
            mode="payload"
        )
        
        assert 'payload' in results
        assert 'lift' in results
        assert 'mass_shell' in results
        assert 'radius' in results
        assert results['lift'] > results['mass_shell']  # Підйомна сила більша за масу оболонки
        assert results['payload'] > 0  # Корисне навантаження позитивне
        assert results['radius'] > 0
        assert results['surface_area'] > 0
    
    def test_helium_volume_mode(self):
        """Перевірка розрахунку для гелію в режимі volume"""
        results = calculate_balloon_parameters(
            gas_type="Гелій",
            gas_volume=3,  # кг навантаження
            material="TPU",
            thickness_mm=35,
            start_height=0,
            work_height=1000,
            mode="volume"
        )
        
        assert 'gas_volume' in results
        assert results['gas_volume'] > 0
        assert results['payload'] == pytest.approx(3, rel=0.1)  # Наближено до заданого навантаження
    
    def test_hot_air_balloon(self):
        """Перевірка розрахунку для гарячого повітря"""
        results = calculate_balloon_parameters(
            gas_type="Гаряче повітря",
            gas_volume=100,
            material="TPU",
            thickness_mm=50,
            start_height=0,
            work_height=500,
            ground_temp=15,
            inside_temp=100,
            mode="payload"
        )
        
        assert 'stress' in results
        assert 'stress_limit' in results
        assert results['stress'] >= 0
        assert results['stress_limit'] > 0
    
    def test_gas_loss_calculation(self):
        """Перевірка розрахунку втрат газу"""
        results = calculate_balloon_parameters(
            gas_type="Гелій",
            gas_volume=10,
            material="TPU",
            thickness_mm=35,
            start_height=0,
            work_height=1000,
            duration=24,
            perm_mult=1.0,
            mode="payload"
        )
        
        assert 'gas_loss' in results
        assert 'final_gas_volume' in results
        assert 'lift_end' in results
        assert 'payload_end' in results
        assert results['gas_loss'] >= 0
        assert results['final_gas_volume'] <= results['gas_volume']
    
    def test_invalid_gas_type(self):
        """Перевірка обробки невалідного типу газу"""
        with pytest.raises(ValueError):
            calculate_balloon_parameters(
                gas_type="Невідомий газ",
                gas_volume=10,
                material="TPU",
                thickness_mm=35,
                start_height=0,
                work_height=1000
            )
    
    def test_negative_gas_volume(self):
        """Перевірка обробки від'ємного об'єму"""
        with pytest.raises(ValueError):
            calculate_balloon_parameters(
                gas_type="Гелій",
                gas_volume=-10,
                material="TPU",
                thickness_mm=35,
                start_height=0,
                work_height=1000
            )
    
    def test_hot_air_temperature_validation(self):
        """Перевірка валідації температури для гарячого повітря"""
        with pytest.raises(ValueError):
            calculate_balloon_parameters(
                gas_type="Гаряче повітря",
                gas_volume=100,
                material="TPU",
                thickness_mm=50,
                start_height=0,
                work_height=500,
                ground_temp=100,
                inside_temp=50  # Менше за ground_temp
            )
    
    def test_different_materials(self):
        """Перевірка різних матеріалів"""
        materials = ["HDPE", "TPU", "Mylar", "Nylon", "PET"]
        
        for material in materials:
            results = calculate_balloon_parameters(
                gas_type="Гелій",
                gas_volume=10,
                material=material,
                thickness_mm=35,
                start_height=0,
                work_height=1000,
                mode="payload"
            )
            
            assert results['mass_shell'] > 0
            assert results['stress_limit'] == MATERIALS[material][1]
    
    def test_different_heights(self):
        """Перевірка різних висот"""
        heights = [0, 1000, 5000, 10000]
        
        for height in heights:
            results = calculate_balloon_parameters(
                gas_type="Гелій",
                gas_volume=10,
                material="TPU",
                thickness_mm=35,
                start_height=0,
                work_height=height,
                mode="payload"
            )
            
            assert results['required_volume'] > 0
            # На більшій висоті об'єм кулі має бути більшим
            if height > 0:
                results_low = calculate_balloon_parameters(
                    gas_type="Гелій",
                    gas_volume=10,
                    material="TPU",
                    thickness_mm=35,
                    start_height=0,
                    work_height=0,
                    mode="payload"
                )
                assert results['required_volume'] > results_low['required_volume']
    
    def test_sphere_shape(self):
        """Перевірка сферичної форми"""
        results = calculate_balloon_parameters(
            gas_type="Гелій",
            gas_volume=10,
            material="TPU",
            thickness_mm=35,
            start_height=0,
            work_height=1000,
            mode="payload",
            shape_type="sphere"
        )
        
        assert 'shape_type' in results
        assert results['shape_type'] == "sphere"
        assert 'shape_params' in results
        assert 'radius' in results['shape_params']
        assert results['radius'] > 0
    
    def test_pear_shape(self):
        """Перевірка грушоподібної форми"""
        # Тест з заданими параметрами
        results = calculate_balloon_parameters(
            gas_type="Гелій",
            gas_volume=10,
            material="TPU",
            thickness_mm=35,
            start_height=0,
            work_height=1000,
            mode="payload",
            shape_type="pear",
            shape_params={'pear_height': 3.0}
        )
        
        assert results['shape_type'] == "pear"
        assert 'shape_params' in results
        assert 'pear_height' in results['shape_params']
        assert 'pear_top_radius' in results['shape_params']
        assert 'pear_bottom_radius' in results['shape_params']
        assert results['shape_params']['pear_height'] > 0
        assert results['shape_params']['pear_top_radius'] > 0
        assert results['shape_params']['pear_bottom_radius'] > 0
        
        # Тест без параметрів (автоматичний розрахунок)
        results2 = calculate_balloon_parameters(
            gas_type="Гелій",
            gas_volume=10,
            material="TPU",
            thickness_mm=35,
            start_height=0,
            work_height=1000,
            mode="payload",
            shape_type="pear",
            shape_params={}
        )
        
        assert results2['shape_type'] == "pear"
        assert 'pear_height' in results2['shape_params']
        assert 'pear_top_radius' in results2['shape_params']
        assert 'pear_bottom_radius' in results2['shape_params']
    
    def test_cigar_shape(self):
        """Перевірка сигароподібної форми"""
        results = calculate_balloon_parameters(
            gas_type="Гелій",
            gas_volume=10,
            material="TPU",
            thickness_mm=35,
            start_height=0,
            work_height=1000,
            mode="payload",
            shape_type="cigar",
            shape_params={'cigar_radius': 1.0}
        )
        
        assert results['shape_type'] == "cigar"
        assert 'shape_params' in results
        assert 'cigar_length' in results['shape_params']
        assert 'cigar_radius' in results['shape_params']
        assert results['shape_params']['cigar_length'] > 0
        assert results['shape_params']['cigar_radius'] > 0
    
    def test_pillow_shape(self):
        """Перевірка форми подушки"""
        results = calculate_balloon_parameters(
            gas_type="Гелій",
            gas_volume=10,
            material="TPU",
            thickness_mm=35,
            start_height=0,
            work_height=1000,
            mode="payload",
            shape_type="pillow",
            shape_params={'pillow_len': 3.0, 'pillow_wid': 2.0}
        )
        
        assert results['shape_type'] == "pillow"
        assert 'shape_params' in results
        assert 'pillow_len' in results['shape_params']
        assert 'pillow_wid' in results['shape_params']
        # Товщина розраховується з об'єму, але не повертається як параметр форми
    
    def test_extra_mass(self):
        """Перевірка додаткової маси обладнання"""
        results_without = calculate_balloon_parameters(
            gas_type="Гелій",
            gas_volume=10,
            material="TPU",
            thickness_mm=35,
            start_height=0,
            work_height=1000,
            mode="payload",
            extra_mass=0.0
        )
        
        results_with = calculate_balloon_parameters(
            gas_type="Гелій",
            gas_volume=10,
            material="TPU",
            thickness_mm=35,
            start_height=0,
            work_height=1000,
            mode="payload",
            extra_mass=1.0
        )
        
        # З додатковою масою навантаження має бути меншим
        assert results_with['payload'] < results_without['payload']
        assert results_with['payload'] == pytest.approx(results_without['payload'] - 1.0, rel=0.01)
        assert results_with.get('extra_mass', 0) == 1.0
    
    def test_seam_factor(self):
        """Перевірка коефіцієнта втрат через шви"""
        results_without = calculate_balloon_parameters(
            gas_type="Гелій",
            gas_volume=10,
            material="TPU",
            thickness_mm=35,
            start_height=0,
            work_height=1000,
            mode="payload",
            seam_factor=1.0
        )
        
        results_with = calculate_balloon_parameters(
            gas_type="Гелій",
            gas_volume=10,
            material="TPU",
            thickness_mm=35,
            start_height=0,
            work_height=1000,
            mode="payload",
            seam_factor=1.1  # +10%
        )
        
        # З коефіцієнтом швів маса оболонки має бути більшою
        assert results_with['mass_shell'] > results_without['mass_shell']
        
        # Ефективна площа поверхні має бути більшою
        effective_with = results_with.get('effective_surface_area', results_with.get('surface_area', 0))
        effective_without = results_without.get('effective_surface_area', results_without.get('surface_area', 0))
        assert effective_with > effective_without
        
        # Для гелію втрати газу також мають бути більшими (якщо вони є)
        if 'gas_loss' in results_with and 'gas_loss' in results_without:
            if results_without['gas_loss'] > 0:  # Тільки якщо є втрати
                assert results_with['gas_loss'] > results_without['gas_loss']

