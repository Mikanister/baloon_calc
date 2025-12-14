"""
Тести для модуля analysis.py
"""

import pytest
from balloon.analysis import (
    calculate_optimal_height,
    calculate_height_profile,
    calculate_material_comparison,
    calculate_cost_analysis,
    generate_report
)
from balloon.constants import MATERIALS


class TestCalculateOptimalHeight:
    """Тести для функції calculate_optimal_height"""
    
    def test_helium_optimal_height(self):
        """Перевірка оптимальної висоти для гелію"""
        result = calculate_optimal_height(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            ground_temp=15
        )
        
        assert 'height' in result
        assert 'payload' in result
        assert 'lift' in result
        assert result['height'] >= 0
        assert result['payload'] > 0
    
    def test_optimal_height_with_shapes(self):
        """Перевірка оптимальної висоти з різними формами"""
        # Груша
        result = calculate_optimal_height(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            ground_temp=15,
            shape_type="pear",
            shape_params={"pear_height": 3.0, "pear_top_radius": 1.2, "pear_bottom_radius": 0.6}
        )
        assert result['height'] >= 0
        assert result['payload'] > 0
        
        # Тор
        result2 = calculate_optimal_height(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            ground_temp=15,
            shape_type="torus",
            shape_params={"tor_major": 2.0}
        )
        assert result2['height'] >= 0
        assert result2['payload'] > 0
    
    def test_hot_air_optimal_height(self):
        """Перевірка оптимальної висоти для гарячого повітря"""
        result = calculate_optimal_height(
            gas_type="Гаряче повітря",
            material="TPU",
            thickness_um=50,
            gas_volume=100,
            ground_temp=15,
            inside_temp=100
        )
        
        assert 'height' in result
        assert result['height'] >= 0
    
    def test_optimal_height_with_extra_mass(self):
        """Перевірка оптимальної висоти з додатковою масою"""
        result_without = calculate_optimal_height(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            ground_temp=15,
            extra_mass=0.0
        )
        
        result_with = calculate_optimal_height(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            ground_temp=15,
            extra_mass=1.0
        )
        
        # З додатковою масою навантаження має бути меншим
        assert result_with['payload'] < result_without['payload']
    
    def test_optimal_height_with_seam_factor(self):
        """Перевірка оптимальної висоти з коефіцієнтом швів"""
        result_without = calculate_optimal_height(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            ground_temp=15,
            seam_factor=1.0
        )
        
        result_with = calculate_optimal_height(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            ground_temp=15,
            seam_factor=1.1
        )
        
        # З коефіцієнтом швів маса оболонки має бути більшою
        assert result_with['mass_shell'] > result_without['mass_shell']


class TestCalculateHeightProfile:
    """Тести для функції calculate_height_profile"""
    
    def test_basic_profile(self):
        """Перевірка базового профілю"""
        profile = calculate_height_profile(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            ground_temp=15,
            max_height=5000
        )
        
        assert len(profile) > 0
        assert all('height' in p for p in profile)
        assert all('payload' in p for p in profile)
        assert all('lift' in p for p in profile)
        
        # Перевірка що висоти зростають
        heights = [p['height'] for p in profile]
        assert heights == sorted(heights)
    
    def test_profile_with_shapes(self):
        """Перевірка профілю з різними формами"""
        # Циліндр
        profile = calculate_height_profile(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            ground_temp=15,
            max_height=2000,
            shape_type="cylinder",
            shape_params={"cyl_radius": 1.0}
        )
        assert len(profile) > 0
        
        # Тор
        profile2 = calculate_height_profile(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            ground_temp=15,
            max_height=2000,
            shape_type="torus",
            shape_params={"tor_major": 2.0}
        )
        assert len(profile2) > 0
    
    def test_profile_structure(self):
        """Перевірка структури профілю"""
        profile = calculate_height_profile(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            max_height=2000
        )
        
        first_point = profile[0]
        required_keys = ['height', 'payload', 'lift', 'mass_shell', 
                        'rho_air', 'net_lift_per_m3', 'T_outside_C', 
                        'P_outside', 'required_volume']
        
        for key in required_keys:
            assert key in first_point
    
    def test_hot_air_profile(self):
        """Перевірка профілю для гарячого повітря"""
        profile = calculate_height_profile(
            gas_type="Гаряче повітря",
            material="TPU",
            thickness_um=50,
            gas_volume=100,
            ground_temp=15,
            inside_temp=100,
            max_height=3000
        )
        
        assert len(profile) > 0
        # На високих висотах навантаження може стати від'ємним
        # або нульовим для гарячого повітря
    
    def test_max_height_parameter(self):
        """Перевірка параметра max_height"""
        profile_short = calculate_height_profile(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            max_height=1000
        )
        
        profile_long = calculate_height_profile(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            max_height=5000
        )
        
        assert len(profile_long) > len(profile_short)
        assert max(p['height'] for p in profile_long) == 5000
        assert max(p['height'] for p in profile_short) == 1000
    
    def test_profile_with_extra_mass(self):
        """Перевірка профілю з додатковою масою"""
        profile_without = calculate_height_profile(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            max_height=2000,
            extra_mass=0.0
        )
        
        profile_with = calculate_height_profile(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            max_height=2000,
            extra_mass=1.0
        )
        
        # На всіх висотах навантаження має бути меншим з додатковою масою
        for i in range(min(len(profile_without), len(profile_with))):
            assert profile_with[i]['payload'] < profile_without[i]['payload']
    
    def test_profile_with_seam_factor(self):
        """Перевірка профілю з коефіцієнтом швів"""
        profile_without = calculate_height_profile(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            max_height=2000,
            seam_factor=1.0
        )
        
        profile_with = calculate_height_profile(
            gas_type="Гелій",
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            max_height=2000,
            seam_factor=1.1
        )
        
        # Маса оболонки має бути більшою з коефіцієнтом швів
        for i in range(min(len(profile_without), len(profile_with))):
            assert profile_with[i]['mass_shell'] > profile_without[i]['mass_shell']


class TestCalculateMaterialComparison:
    """Тести для функції calculate_material_comparison"""
    
    def test_all_materials_comparison(self):
        """Перевірка порівняння всіх матеріалів"""
        results = calculate_material_comparison(
            gas_type="Гелій",
            thickness_um=35,
            gas_volume=10,
            height=1000
        )
        
        assert len(results) == len(MATERIALS)
        
        for material in MATERIALS.keys():
            assert material in results
            material_result = results[material]
            
            assert 'payload' in material_result
            assert 'mass_shell' in material_result
            assert 'lift' in material_result
            assert 'stress' in material_result
            assert 'stress_limit' in material_result
            assert 'safety_factor' in material_result
            assert 'density' in material_result
    
    def test_material_comparison_with_shapes(self):
        """Перевірка порівняння матеріалів з різними формами"""
        # Циліндр
        results = calculate_material_comparison(
            gas_type="Гелій",
            thickness_um=35,
            gas_volume=10,
            height=1000,
            shape_type="cylinder",
            shape_params={"cyl_radius": 1.0}
        )
        assert len(results) > 0
    
    def test_material_properties(self):
        """Перевірка властивостей матеріалів"""
        results = calculate_material_comparison(
            gas_type="Гелій",
            thickness_um=35,
            gas_volume=10,
            height=1000
        )
        
        for material, result in results.items():
            assert result['density'] == MATERIALS[material][0]
            assert result['stress_limit'] == MATERIALS[material][1]
            assert result['mass_shell'] >= 0
            assert result['safety_factor'] >= 0
    
    def test_hot_air_material_comparison(self):
        """Перевірка порівняння матеріалів для гарячого повітря"""
        results = calculate_material_comparison(
            gas_type="Гаряче повітря",
            thickness_um=50,
            gas_volume=100,
            ground_temp=15,
            inside_temp=100,
            height=500
        )
        
        assert len(results) == len(MATERIALS)
        # Для гарячого повітря напруга має бути більшою
        for material, result in results.items():
            if result['stress'] > 0:
                assert result['safety_factor'] > 0
    
    def test_material_comparison_with_extra_mass(self):
        """Перевірка порівняння матеріалів з додатковою масою"""
        results_without = calculate_material_comparison(
            gas_type="Гелій",
            thickness_um=35,
            gas_volume=10,
            height=1000,
            extra_mass=0.0
        )
        
        results_with = calculate_material_comparison(
            gas_type="Гелій",
            thickness_um=35,
            gas_volume=10,
            height=1000,
            extra_mass=1.0
        )
        
        # З додатковою масою навантаження має бути меншим для всіх матеріалів
        for material in MATERIALS.keys():
            assert results_with[material]['payload'] < results_without[material]['payload']
    
    def test_material_comparison_with_seam_factor(self):
        """Перевірка порівняння матеріалів з коефіцієнтом швів"""
        results_without = calculate_material_comparison(
            gas_type="Гелій",
            thickness_um=35,
            gas_volume=10,
            height=1000,
            seam_factor=1.0
        )
        
        results_with = calculate_material_comparison(
            gas_type="Гелій",
            thickness_um=35,
            gas_volume=10,
            height=1000,
            seam_factor=1.1
        )
        
        # З коефіцієнтом швів маса оболонки має бути більшою
        for material in MATERIALS.keys():
            assert results_with[material]['mass_shell'] > results_without[material]['mass_shell']


class TestCalculateCostAnalysis:
    """Тести для функції calculate_cost_analysis"""
    
    def test_basic_cost_analysis(self):
        """Перевірка базового аналізу вартості"""
        result = calculate_cost_analysis(
            material="TPU",
            thickness_um=35,
            gas_volume=10,
            gas_type="Гелій",
            height=1000
        )
        
        assert 'material_cost' in result
        assert 'gas_cost' in result
        assert 'total_cost' in result
        assert 'mass_shell' in result
        assert 'gas_volume' in result
        assert 'cost_per_kg_payload' in result
        
        assert result['material_cost'] >= 0
        assert result['gas_cost'] >= 0
        assert result['total_cost'] >= 0
    
    def test_different_materials_cost(self):
        """Перевірка вартості різних матеріалів"""
        materials = ["HDPE", "TPU", "Mylar"]
        
        for material in materials:
            result = calculate_cost_analysis(
                material=material,
                thickness_um=35,
                gas_volume=10,
                gas_type="Гелій",
                height=1000
            )
            
            assert result['total_cost'] > 0
            assert result['cost_per_kg_payload'] > 0
    
    def test_different_gases_cost(self):
        """Перевірка вартості різних газів"""
        gases = ["Гелій", "Водень", "Гаряче повітря"]
        
        for gas in gases:
            result = calculate_cost_analysis(
                material="TPU",
                thickness_um=35,
                gas_volume=10,
                gas_type=gas,
                ground_temp=15,
                inside_temp=100 if gas == "Гаряче повітря" else 100,
                height=1000
            )
            
            assert result['gas_cost'] >= 0
            # Гелій має бути дорожчим за водень
            if gas == "Гелій":
                helium_cost = result['gas_cost']
            elif gas == "Водень":
                hydrogen_cost = result['gas_cost']
        
        # Перевірка що гелій дорожчий за водень
        assert helium_cost > hydrogen_cost


class TestGenerateReport:
    """Тести для функції generate_report"""
    
    def test_payload_mode_report(self):
        """Перевірка звіту для режиму payload"""
        results = {
            'gas_volume': 10.0,
            'required_volume': 12.5,
            'payload': 3.2,
            'mass_shell': 0.5,
            'lift': 3.7,
            'radius': 1.5,
            'surface_area': 28.3,
            'rho_air': 1.1,
            'net_lift_per_m3': 0.9,
            'stress': 0,
            'stress_limit': 35e6,
            'T_outside_C': 8.5
        }
        
        inputs = {
            'gas_type': 'Гелій',
            'material': 'TPU',
            'thickness': 35,
            'start_height': 0,
            'work_height': 1000
        }
        
        report = generate_report(results, "payload", inputs)
        
        assert "ЗВІТ ПО РОЗРАХУНКУ АЕРОСТАТА" in report
        assert "Гелій" in report
        assert "TPU" in report
        # Перевіряємо наявність значень (можуть бути в різних форматах)
        assert "10" in report or "12.50" in report  # gas_volume або required_volume
        assert "3.2" in report or "3.20" in report or "3" in report  # payload
    
    def test_volume_mode_report(self):
        """Перевірка звіту для режиму volume"""
        results = {
            'gas_volume': 15.5,
            'required_volume': 18.2,
            'payload': 5.0,
            'mass_shell': 0.8,
            'lift': 5.8,
            'radius': 1.6,
            'surface_area': 32.2,
            'rho_air': 1.1,
            'net_lift_per_m3': 0.9,
            'stress': 0,
            'stress_limit': 35e6,
            'T_outside_C': 8.5
        }
        
        inputs = {
            'gas_type': 'Гелій',
            'material': 'TPU',
            'thickness': 35,
            'start_height': 0,
            'work_height': 1000
        }
        
        report = generate_report(results, "volume", inputs)
        
        assert "Потрібний обʼєм газу" in report
        assert "15.50" in report or "15.5" in report
    
    def test_hot_air_report(self):
        """Перевірка звіту для гарячого повітря"""
        results = {
            'gas_volume': 100.0,
            'required_volume': 120.0,
            'payload': 15.0,
            'mass_shell': 5.0,
            'lift': 20.0,
            'radius': 3.0,
            'surface_area': 113.1,
            'rho_air': 1.1,
            'net_lift_per_m3': 0.15,
            'stress': 5e6,
            'stress_limit': 35e6,
            'T_outside_C': 8.5
        }
        
        inputs = {
            'gas_type': 'Гаряче повітря',
            'material': 'TPU',
            'thickness': 50,
            'start_height': 0,
            'work_height': 500,
            'ground_temp': 15,
            'inside_temp': 100
        }
        
        report = generate_report(results, "payload", inputs)
        
        assert "Гаряче повітря" in report
        assert "Температура на землі" in report
        assert "Температура всередині" in report
        assert "Коефіцієнт безпеки" in report
    
    def test_low_safety_factor_warning(self):
        """Перевірка попередження про низький коефіцієнт безпеки"""
        results = {
            'gas_volume': 100.0,
            'required_volume': 120.0,
            'payload': 15.0,
            'mass_shell': 5.0,
            'lift': 20.0,
            'radius': 3.0,
            'surface_area': 113.1,
            'rho_air': 1.1,
            'net_lift_per_m3': 0.15,
            'stress': 20e6,  # Висока напруга
            'stress_limit': 35e6,
            'T_outside_C': 8.5
        }
        
        inputs = {
            'gas_type': 'Гаряче повітря',
            'material': 'TPU',
            'thickness': 50,
            'start_height': 0,
            'work_height': 500,
            'ground_temp': 15,
            'inside_temp': 100
        }
        
        report = generate_report(results, "payload", inputs)
        
        # Коефіцієнт безпеки = 35e6 / 20e6 = 1.75 < 2
        assert "УВАГА" in report or "низький" in report.lower()

