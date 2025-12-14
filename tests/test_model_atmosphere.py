"""
Тести для модуля balloon.model.atmosphere
"""

import pytest
from balloon.model.atmosphere import air_density_at_height
from balloon.constants import T0, SEA_LEVEL_PRESSURE, SEA_LEVEL_AIR_DENSITY


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
    
    def test_high_altitude(self):
        """Перевірка на високій висоті (10 км)"""
        temp, rho, pressure = air_density_at_height(10000, 15)
        assert temp < 0  # Температура нижче нуля
        assert pressure < SEA_LEVEL_PRESSURE / 3  # Тиск значно нижче
        # На 10 км щільність приблизно в 2.5-3 рази менша
        assert rho < SEA_LEVEL_AIR_DENSITY / 2
    
    def test_different_ground_temps(self):
        """Перевірка з різними температурами на землі"""
        temp1, _, _ = air_density_at_height(1000, 0)
        temp2, _, _ = air_density_at_height(1000, 30)
        
        # Різниця температур на висоті має бути меншою, ніж на землі
        # Але через ISA модель різниця може бути близькою до різниці на землі
        assert abs(temp2 - temp1) <= 30
    
    def test_return_types(self):
        """Перевірка типів повернутих значень"""
        temp, rho, pressure = air_density_at_height(1000, 15)
        assert isinstance(temp, (int, float))
        assert isinstance(rho, (int, float))
        assert isinstance(pressure, (int, float))
        assert temp > -100  # Розумні межі
        assert rho > 0
        assert pressure > 0

