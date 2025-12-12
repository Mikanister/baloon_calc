"""
Тести для модуля validators.py
"""

import pytest
from baloon.validators import (
    ValidationError,
    validate_float,
    validate_material,
    validate_gas_type,
    validate_temperature_difference,
    validate_height_parameters,
    validate_all_inputs
)
from baloon.constants import MATERIALS, GAS_DENSITY


class TestValidateFloat:
    """Тести для функції validate_float"""
    
    def test_valid_float(self):
        """Перевірка валідного числа"""
        result = validate_float("10.5", "test_field")
        assert result == 10.5
    
    def test_integer_string(self):
        """Перевірка цілого числа як рядка"""
        result = validate_float("10", "test_field")
        assert result == 10.0
    
    def test_invalid_string(self):
        """Перевірка невалідного рядка"""
        with pytest.raises(ValidationError, match="має містити число"):
            validate_float("abc", "test_field")
    
    def test_empty_string(self):
        """Перевірка порожнього рядка"""
        with pytest.raises(ValidationError):
            validate_float("", "test_field")
    
    def test_min_value_constraint(self):
        """Перевірка мінімального значення"""
        result = validate_float("10", "test_field", min_value=5)
        assert result == 10.0
        
        with pytest.raises(ValidationError, match="не менше"):
            validate_float("3", "test_field", min_value=5)
    
    def test_max_value_constraint(self):
        """Перевірка максимального значення"""
        result = validate_float("10", "test_field", max_value=20)
        assert result == 10.0
        
        with pytest.raises(ValidationError, match="не більше"):
            validate_float("25", "test_field", max_value=20)
    
    def test_both_constraints(self):
        """Перевірка обох обмежень"""
        result = validate_float("10", "test_field", min_value=5, max_value=15)
        assert result == 10.0
        
        with pytest.raises(ValidationError):
            validate_float("3", "test_field", min_value=5, max_value=15)
        
        with pytest.raises(ValidationError):
            validate_float("20", "test_field", min_value=5, max_value=15)


class TestValidateMaterial:
    """Тести для функції validate_material"""
    
    def test_valid_materials(self):
        """Перевірка валідних матеріалів"""
        for material in MATERIALS.keys():
            result = validate_material(material)
            assert result == material
    
    def test_invalid_material(self):
        """Перевірка невалідного матеріалу"""
        with pytest.raises(ValidationError, match="Непідтримуваний матеріал"):
            validate_material("Невідомий матеріал")
    
    def test_case_sensitive(self):
        """Перевірка чутливості до регістру"""
        with pytest.raises(ValidationError):
            validate_material("tpu")  # Маленькі літери


class TestValidateGasType:
    """Тести для функції validate_gas_type"""
    
    def test_valid_gases(self):
        """Перевірка валідних газів"""
        for gas in GAS_DENSITY.keys():
            result = validate_gas_type(gas)
            assert result == gas
    
    def test_invalid_gas(self):
        """Перевірка невалідного газу"""
        with pytest.raises(ValidationError, match="Непідтримуваний тип газу"):
            validate_gas_type("Невідомий газ")


class TestValidateTemperatureDifference:
    """Тести для функції validate_temperature_difference"""
    
    def test_valid_difference(self):
        """Перевірка валідної різниці температур"""
        validate_temperature_difference(100, 15)  # Не має викликати помилку
    
    def test_equal_temperatures(self):
        """Перевірка рівних температур"""
        with pytest.raises(ValidationError):
            validate_temperature_difference(15, 15)
    
    def test_inside_cooler_than_ground(self):
        """Перевірка коли всередині холодніше"""
        with pytest.raises(ValidationError):
            validate_temperature_difference(10, 15)


class TestValidateHeightParameters:
    """Тести для функції validate_height_parameters"""
    
    def test_valid_heights(self):
        """Перевірка валідних висот"""
        validate_height_parameters(0, 1000)  # Не має викликати помилку
        validate_height_parameters(100, 5000)
    
    def test_negative_start_height(self):
        """Перевірка від'ємної висоти пуску"""
        with pytest.raises(ValidationError, match="не може бути від'ємною"):
            validate_height_parameters(-100, 1000)
    
    def test_negative_work_height(self):
        """Перевірка від'ємної висоти польоту"""
        with pytest.raises(ValidationError, match="не може бути від'ємною"):
            validate_height_parameters(0, -100)
    
    def test_too_high_total_height(self):
        """Перевірка занадто високої загальної висоти"""
        with pytest.raises(ValidationError, match="не може перевищувати"):
            validate_height_parameters(0, 60000)  # 60 км


class TestValidateAllInputs:
    """Тести для функції validate_all_inputs"""
    
    def test_valid_inputs_payload_mode(self):
        """Перевірка валідних вхідних даних в режимі payload"""
        numbers, strings = validate_all_inputs(
            gas_type="Гелій",
            gas_volume="10",
            material="TPU",
            thickness="35",
            start_height="0",
            work_height="1000",
            mode="payload"
        )
        
        assert numbers['gas_volume'] == 10.0
        assert numbers['thickness'] == 35.0
        assert strings['gas_type'] == "Гелій"
        assert strings['material'] == "TPU"
        assert strings['mode'] == "payload"
    
    def test_valid_inputs_volume_mode(self):
        """Перевірка валідних вхідних даних в режимі volume"""
        numbers, strings = validate_all_inputs(
            gas_type="Гелій",
            gas_volume="3",
            material="TPU",
            thickness="35",
            start_height="0",
            work_height="1000",
            mode="volume"
        )
        
        assert numbers['gas_volume'] == 3.0
        assert strings['mode'] == "volume"
    
    def test_valid_hot_air_inputs(self):
        """Перевірка валідних даних для гарячого повітря"""
        numbers, strings = validate_all_inputs(
            gas_type="Гаряче повітря",
            gas_volume="100",
            material="TPU",
            thickness="50",
            start_height="0",
            work_height="500",
            ground_temp="15",
            inside_temp="100"
        )
        
        assert numbers['ground_temp'] == 15.0
        assert numbers['inside_temp'] == 100.0
        assert strings['gas_type'] == "Гаряче повітря"
    
    def test_invalid_gas_type(self):
        """Перевірка невалідного типу газу"""
        with pytest.raises(ValidationError):
            validate_all_inputs(
                gas_type="Невідомий газ",
                gas_volume="10",
                material="TPU",
                thickness="35",
                start_height="0",
                work_height="1000"
            )
    
    def test_invalid_material(self):
        """Перевірка невалідного матеріалу"""
        with pytest.raises(ValidationError):
            validate_all_inputs(
                gas_type="Гелій",
                gas_volume="10",
                material="Невідомий матеріал",
                thickness="35",
                start_height="0",
                work_height="1000"
            )
    
    def test_invalid_thickness(self):
        """Перевірка невалідної товщини"""
        with pytest.raises(ValidationError):
            validate_all_inputs(
                gas_type="Гелій",
                gas_volume="10",
                material="TPU",
                thickness="0.5",  # Занадто мала
                start_height="0",
                work_height="1000"
            )
        
        with pytest.raises(ValidationError):
            validate_all_inputs(
                gas_type="Гелій",
                gas_volume="10",
                material="TPU",
                thickness="2000",  # Занадто велика
                start_height="0",
                work_height="1000"
            )
    
    def test_invalid_temperature_for_hot_air(self):
        """Перевірка невалідної температури для гарячого повітря"""
        with pytest.raises(ValidationError):
            validate_all_inputs(
                gas_type="Гаряче повітря",
                gas_volume="100",
                material="TPU",
                thickness="50",
                start_height="0",
                work_height="500",
                ground_temp="100",
                inside_temp="50"  # Менше за ground_temp
            )
    
    def test_invalid_height_parameters(self):
        """Перевірка невалідних параметрів висоти"""
        with pytest.raises(ValidationError):
            validate_all_inputs(
                gas_type="Гелій",
                gas_volume="10",
                material="TPU",
                thickness="35",
                start_height="-100",
                work_height="1000"
            )
        
        with pytest.raises(ValidationError):
            validate_all_inputs(
                gas_type="Гелій",
                gas_volume="10",
                material="TPU",
                thickness="35",
                start_height="0",
                work_height="60000"  # Занадто висока
            )
    
    def test_invalid_gas_volume(self):
        """Перевірка невалідного об'єму газу"""
        with pytest.raises(ValidationError):
            validate_all_inputs(
                gas_type="Гелій",
                gas_volume="0",  # Нульовий об'єм
                material="TPU",
                thickness="35",
                start_height="0",
                work_height="1000"
            )
        
        with pytest.raises(ValidationError):
            validate_all_inputs(
                gas_type="Гелій",
                gas_volume="-10",  # Від'ємний об'єм
                material="TPU",
                thickness="35",
                start_height="0",
                work_height="1000"
            )
    
    def test_invalid_duration(self):
        """Перевірка невалідної тривалості"""
        with pytest.raises(ValidationError):
            validate_all_inputs(
                gas_type="Гелій",
                gas_volume="10",
                material="TPU",
                thickness="35",
                start_height="0",
                work_height="1000",
                duration="0"  # Нульова тривалість
            )
        
        with pytest.raises(ValidationError):
            validate_all_inputs(
                gas_type="Гелій",
                gas_volume="10",
                material="TPU",
                thickness="35",
                start_height="0",
                work_height="1000",
                duration="20000"  # Занадто велика
            )

