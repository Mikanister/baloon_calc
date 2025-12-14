"""
Тести для модуля balloon.model.solve
"""

import pytest
from balloon.model.solve import (
    required_balloon_volume,
    calculate_gas_loss,
    calculate_balloon_state,
    solve_volume_to_payload,
    solve_payload_to_volume
)
from balloon.constants import T0, SEA_LEVEL_PRESSURE


class TestRequiredBalloonVolume:
    """Тести для функції required_balloon_volume"""
    
    def test_basic_expansion(self):
        """Базовий розрахунок розширення"""
        gas_volume_ground = 10.0  # м³
        ground_temp = 15.0  # °C
        P = SEA_LEVEL_PRESSURE / 2  # Тиск на висоті
        T = (15 - 6.5) + T0  # Температура на висоті
        
        volume = required_balloon_volume(gas_volume_ground, ground_temp, P, T)
        
        # Об'єм має збільшитися при зниженні тиску
        assert volume > gas_volume_ground
        assert volume > 0
    
    def test_sea_level(self):
        """Перевірка на рівні моря"""
        gas_volume_ground = 10.0
        ground_temp = 15.0
        P = SEA_LEVEL_PRESSURE
        T = ground_temp + T0
        
        volume = required_balloon_volume(gas_volume_ground, ground_temp, P, T)
        
        # На рівні моря об'єм має бути приблизно рівним початковому
        assert volume == pytest.approx(gas_volume_ground, rel=0.01)


class TestCalculateGasLoss:
    """Тести для функції calculate_gas_loss"""
    
    def test_basic_loss(self):
        """Базовий розрахунок втрат"""
        permeability = 1e-12  # м²/(с·Па)
        surface_area = 100.0  # м²
        delta_p = 10000.0  # Па
        duration_h = 1.0  # год
        thickness_m = 0.0001  # м
        
        loss = calculate_gas_loss(
            permeability=permeability,
            surface_area=surface_area,
            delta_p=delta_p,
            duration_h=duration_h,
            thickness_m=thickness_m
        )
        
        assert loss >= 0
        # Втрати мають бути розумними (об'єм в м³)
        # Для великої площі та високої проникності втрати можуть бути значними
        assert loss < 100.0  # м³ за годину
    
    def test_zero_duration(self):
        """Перевірка при нульовій тривалості"""
        loss = calculate_gas_loss(
            permeability=1e-12,
            surface_area=100.0,
            delta_p=10000.0,
            duration_h=0.0,
            thickness_m=0.0001
        )
        assert loss == 0.0
    
    def test_zero_permeability(self):
        """Перевірка при нульовій проникності"""
        loss = calculate_gas_loss(
            permeability=0.0,
            surface_area=100.0,
            delta_p=10000.0,
            duration_h=1.0,
            thickness_m=0.0001
        )
        assert loss == 0.0
    
    def test_duration_proportionality(self):
        """Перевірка пропорційності тривалості"""
        loss1 = calculate_gas_loss(
            permeability=1e-12,
            surface_area=100.0,
            delta_p=10000.0,
            duration_h=1.0,
            thickness_m=0.0001
        )
        loss2 = calculate_gas_loss(
            permeability=1e-12,
            surface_area=100.0,
            delta_p=10000.0,
            duration_h=2.0,
            thickness_m=0.0001
        )
        
        assert loss2 == pytest.approx(loss1 * 2, rel=0.01)


class TestCalculateBalloonState:
    """Тести для функції calculate_balloon_state"""
    
    def test_helium_basic(self):
        """Базовий розрахунок для гелію"""
        state = calculate_balloon_state(
            gas_type="Гелій",
            gas_volume=10.0,
            material="TPU",
            thickness_m=0.0001,
            total_height=1000.0,
            ground_temp=15.0,
            inside_temp=15.0,
            shape_type="sphere",
            shape_params={},
            extra_mass=0.0,
            seam_factor=1.0
        )
        
        assert 'gas_volume' in state
        assert 'payload' in state
        assert 'mass_shell' in state
        assert 'lift' in state
        assert 'mass_budget' in state
        assert 'lift_budget' in state
        assert state['gas_volume'] > 0
        assert state['payload'] >= 0
    
    def test_hot_air(self):
        """Розрахунок для гарячого повітря"""
        state = calculate_balloon_state(
            gas_type="Гаряче повітря",
            gas_volume=100.0,
            material="TPU",
            thickness_m=0.0001,
            total_height=500.0,
            ground_temp=15.0,
            inside_temp=100.0,
            shape_type="sphere",
            shape_params={},
            extra_mass=0.0,
            seam_factor=1.0
        )
        
        assert state['payload'] >= 0
        # Перевіряємо наявність основних полів
        assert 'rho_air' in state
        assert 'net_lift_per_m3' in state


class TestSolveVolumeToPayload:
    """Тести для функції solve_volume_to_payload"""
    
    def test_helium_payload_mode(self):
        """Розрахунок навантаження з об'єму для гелію"""
        result = solve_volume_to_payload(
            gas_type="Гелій",
            gas_volume=10.0,
            material="TPU",
            thickness_um=100,
            start_height=0.0,
            work_height=1000.0,
            ground_temp=15.0,
            inside_temp=15.0,
            duration=0.0,
            perm_mult=1.0,
            shape_type="sphere",
            shape_params={},
            extra_mass=0.0,
            seam_factor=1.0
        )
        
        assert 'payload' in result
        assert 'gas_volume' in result
        assert result['gas_volume'] == pytest.approx(10.0, rel=0.01)
        assert result['payload'] >= 0


class TestSolvePayloadToVolume:
    """Тести для функції solve_payload_to_volume"""
    
    def test_helium_volume_mode(self):
        """Розрахунок об'єму з навантаження для гелію"""
        result = solve_payload_to_volume(
            gas_type="Гелій",
            target_payload=5.0,
            material="TPU",
            thickness_um=100,
            start_height=0.0,
            work_height=1000.0,
            ground_temp=15.0,
            inside_temp=15.0,
            duration=0.0,
            perm_mult=1.0,
            shape_type="sphere",
            shape_params={},
            extra_mass=0.0,
            seam_factor=1.0
        )
        
        assert 'gas_volume' in result
        assert 'payload' in result
        assert result['gas_volume'] > 0
        assert result['payload'] == pytest.approx(5.0, rel=0.1)

