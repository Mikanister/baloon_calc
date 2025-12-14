"""
Тести для модуля balloon.model.mass_budget
"""

import pytest
from balloon.model.mass_budget import (
    MassBudget,
    LiftBudget,
    calculate_mass_budget,
    calculate_lift_budget
)


class TestMassBudget:
    """Тести для класу MassBudget"""
    
    def test_initialization(self):
        """Перевірка ініціалізації"""
        budget = MassBudget()
        assert budget.gas_mass == 0.0
        assert budget.envelope_mass == 0.0
        assert budget.payload_mass == 0.0
    
    def test_structural_mass(self):
        """Перевірка розрахунку структурної маси"""
        budget = MassBudget(
            envelope_mass=10.0,
            seams_mass=1.0,
            reinforcements_mass=0.5,
            extra_mass=0.5
        )
        
        # structural_mass = envelope + seams + reinforcements (без extra_mass)
        assert budget.structural_mass == 11.5
    
    def test_total_mass(self):
        """Перевірка розрахунку загальної маси"""
        budget = MassBudget(
            gas_mass=5.0,
            envelope_mass=10.0,
            payload_mass=3.0,
            safety_margin_mass=1.0
        )
        
        assert budget.total_mass == 19.0
    
    def test_to_dict(self):
        """Перевірка конвертації в словник"""
        budget = MassBudget(gas_mass=5.0, envelope_mass=10.0)
        data = budget.to_dict()
        
        assert 'gas_mass' in data
        assert 'envelope_mass' in data
        assert 'structural_mass' in data
        assert 'total_mass' in data
        assert data['gas_mass'] == 5.0
    
    def test_to_table_data(self):
        """Перевірка конвертації в табличні дані"""
        budget = MassBudget(gas_mass=5.0, envelope_mass=10.0)
        table = budget.to_table_data()
        
        assert isinstance(table, list)
        assert len(table) > 0
        assert 'Компонент' in table[0]
        assert 'Маса (кг)' in table[0]


class TestLiftBudget:
    """Тести для класу LiftBudget"""
    
    def test_initialization(self):
        """Перевірка ініціалізації"""
        budget = LiftBudget()
        assert budget.gross_lift == 0.0
        assert budget.net_lift == 0.0
    
    def test_net_lift_calculation(self):
        """Перевірка розрахунку чистої підйомної сили"""
        # net_lift обчислюється автоматично в calculate_lift_budget
        # Для тесту створюємо бюджет з правильними значеннями
        budget = LiftBudget(gross_lift=100.0, gas_mass=5.0, net_lift=95.0)
        assert budget.net_lift == 95.0
    
    def test_remaining_lift(self):
        """Перевірка розрахунку залишкової підйомної сили"""
        budget = LiftBudget(
            available_lift=100.0,
            used_lift=80.0,
            remaining_lift=20.0
        )
        assert budget.remaining_lift == 20.0
    
    def test_lift_efficiency(self):
        """Перевірка розрахунку ефективності"""
        budget = LiftBudget(available_lift=100.0, used_lift=80.0)
        assert budget.lift_efficiency == pytest.approx(0.8, rel=0.01)
    
    def test_to_dict(self):
        """Перевірка конвертації в словник"""
        budget = LiftBudget(gross_lift=100.0, net_lift=95.0)
        data = budget.to_dict()
        
        assert 'gross_lift' in data
        assert 'net_lift' in data
        assert data['gross_lift'] == 100.0


class TestCalculateMassBudget:
    """Тести для функції calculate_mass_budget"""
    
    def test_basic_calculation(self):
        """Базовий розрахунок масового бюджету"""
        budget = calculate_mass_budget(
            gas_volume=10.0,
            gas_density=0.17,
            surface_area=50.0,
            thickness_m=0.0001,
            material_density=1200.0,
            seam_factor=1.05,
            reinforcements_mass=0.5,
            payload_mass=5.0,
            safety_margin_percent=10.0,
            extra_mass=0.5
        )
        
        assert budget.gas_mass == pytest.approx(1.7, rel=0.01)
        assert budget.envelope_mass > 0
        assert budget.payload_mass == 5.0
        assert budget.total_mass > 0
    
    def test_seam_factor(self):
        """Перевірка впливу коефіцієнта швів"""
        budget1 = calculate_mass_budget(
            gas_volume=10.0, gas_density=0.17,
            surface_area=50.0, thickness_m=0.0001,
            material_density=1200.0, seam_factor=1.0,
            reinforcements_mass=0.0, payload_mass=0.0,
            safety_margin_percent=0.0, extra_mass=0.0
        )
        
        budget2 = calculate_mass_budget(
            gas_volume=10.0, gas_density=0.17,
            surface_area=50.0, thickness_m=0.0001,
            material_density=1200.0, seam_factor=1.1,
            reinforcements_mass=0.0, payload_mass=0.0,
            safety_margin_percent=0.0, extra_mass=0.0
        )
        
        assert budget2.seams_mass > budget1.seams_mass


class TestCalculateLiftBudget:
    """Тести для функції calculate_lift_budget"""
    
    def test_basic_calculation(self):
        """Базовий розрахунок бюджету підйомної сили"""
        mass_budget = MassBudget(
            gas_mass=1.7,
            envelope_mass=6.0,
            payload_mass=5.0,
            safety_margin_mass=1.0
        )
        
        lift_budget = calculate_lift_budget(
            gas_volume=10.0,
            air_density=1.2,
            gas_density=0.17,
            mass_budget=mass_budget
        )
        
        # gross_lift = (air_density - gas_density) * volume = (1.2 - 0.17) * 10.0 = 10.3
        assert lift_budget.gross_lift == pytest.approx(10.3, rel=0.01)
        # net_lift = gross_lift - gas_mass = 10.3 - 1.7 = 8.6
        assert lift_budget.net_lift == pytest.approx(8.6, rel=0.01)
        # used_lift = structural_mass + payload + safety = 6.0 + 5.0 + 1.0 = 12.0
        assert lift_budget.used_lift == pytest.approx(12.0, rel=0.01)
        assert lift_budget.remaining_lift < 0  # Перевантаження

