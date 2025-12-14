"""
Тести для модуля balloon.model.gas
"""

import pytest
from balloon.model.gas import (
    calculate_gas_density_at_altitude,
    calculate_hot_air_density
)
from balloon.constants import T0, SEA_LEVEL_PRESSURE


class TestCalculateGasDensityAtAltitude:
    """Тести для функції calculate_gas_density_at_altitude"""
    
    def test_helium_sea_level(self):
        """Перевірка щільності гелію на рівні моря"""
        pressure = SEA_LEVEL_PRESSURE
        temperature = 15 + T0  # 15°C в Кельвінах
        
        rho = calculate_gas_density_at_altitude("Гелій", pressure, temperature)
        
        # Щільність гелію на рівні моря при 15°C приблизно 0.17 кг/м³
        assert rho == pytest.approx(0.17, rel=0.1)
        assert rho > 0
    
    def test_hydrogen_sea_level(self):
        """Перевірка щільності водню на рівні моря"""
        pressure = SEA_LEVEL_PRESSURE
        temperature = 15 + T0
        
        rho = calculate_gas_density_at_altitude("Водень", pressure, temperature)
        
        # Щільність водню на рівні моря при 15°C приблизно 0.084 кг/м³
        assert rho == pytest.approx(0.084, rel=0.1)
        assert rho > 0
    
    def test_helium_vs_hydrogen(self):
        """Перевірка, що водень легший за гелій"""
        pressure = SEA_LEVEL_PRESSURE
        temperature = 15 + T0
        
        rho_he = calculate_gas_density_at_altitude("Гелій", pressure, temperature)
        rho_h2 = calculate_gas_density_at_altitude("Водень", pressure, temperature)
        
        assert rho_h2 < rho_he
    
    def test_altitude_effect(self):
        """Перевірка впливу висоти на щільність"""
        pressure_sea = SEA_LEVEL_PRESSURE
        pressure_high = SEA_LEVEL_PRESSURE / 2  # На висоті тиск нижче
        temperature = 15 + T0
        
        rho_sea = calculate_gas_density_at_altitude("Гелій", pressure_sea, temperature)
        rho_high = calculate_gas_density_at_altitude("Гелій", pressure_high, temperature)
        
        assert rho_high < rho_sea
    
    def test_temperature_effect(self):
        """Перевірка впливу температури на щільність"""
        pressure = SEA_LEVEL_PRESSURE
        temp_cold = 0 + T0
        temp_hot = 30 + T0
        
        rho_cold = calculate_gas_density_at_altitude("Гелій", pressure, temp_cold)
        rho_hot = calculate_gas_density_at_altitude("Гелій", pressure, temp_hot)
        
        assert rho_cold > rho_hot  # Холодний газ щільніший
    
    def test_invalid_gas_type(self):
        """Перевірка обробки невалідного типу газу"""
        with pytest.raises(ValueError, match="Непідтримуваний"):
            calculate_gas_density_at_altitude("Невалідний газ", SEA_LEVEL_PRESSURE, 15 + T0)


class TestCalculateHotAirDensity:
    """Тести для функції calculate_hot_air_density"""
    
    def test_100_degrees(self):
        """Перевірка щільності гарячого повітря при 100°C"""
        rho = calculate_hot_air_density(100)
        
        # При 100°C щільність повітря приблизно 0.95 кг/м³
        assert rho == pytest.approx(0.95, rel=0.1)
        assert rho > 0
    
    def test_room_temperature(self):
        """Перевірка щільності повітря при кімнатній температурі"""
        rho = calculate_hot_air_density(20)
        
        # При 20°C щільність повітря приблизно 1.2 кг/м³
        assert rho == pytest.approx(1.2, rel=0.1)
    
    def test_temperature_dependence(self):
        """Перевірка залежності від температури"""
        rho_cold = calculate_hot_air_density(50)
        rho_hot = calculate_hot_air_density(150)
        
        assert rho_hot < rho_cold  # Гаряче повітря легше
    
    def test_zero_celsius(self):
        """Перевірка при 0°C"""
        rho = calculate_hot_air_density(0)
        assert rho > 0
        assert rho == pytest.approx(1.29, rel=0.1)
    
    def test_negative_temperature(self):
        """Перевірка при від'ємній температурі"""
        rho = calculate_hot_air_density(-10)
        assert rho > 0
        assert rho > calculate_hot_air_density(0)  # Холодне повітря щільніше

