"""
Валідація введених даних
"""

from typing import Union, Tuple

try:
    from baloon.constants import MATERIALS, GAS_DENSITY
except ImportError:
    from constants import MATERIALS, GAS_DENSITY


class ValidationError(Exception):
    """Користувацька помилка валідації"""
    pass


def validate_float(value: str, field_name: str, min_value: Union[float, None] = None, 
                  max_value: Union[float, None] = None) -> float:
    """
    Валідує та конвертує рядок у число з плаваючою комою
    
    Args:
        value: Рядок для конвертації
        field_name: Назва поля для повідомлення про помилку
        min_value: Мінімальне допустиме значення
        max_value: Максимальне допустиме значення
    
    Returns:
        Конвертоване число
    
    Raises:
        ValidationError: Якщо значення некоректне
    """
    try:
        result = float(value)
    except ValueError:
        raise ValidationError(f"Поле '{field_name}' має містити число")
    
    if min_value is not None and result < min_value:
        raise ValidationError(f"Поле '{field_name}' має бути не менше {min_value}")
    
    if max_value is not None and result > max_value:
        raise ValidationError(f"Поле '{field_name}' має бути не більше {max_value}")
    
    return result


def validate_material(material: str) -> str:
    """
    Валідує матеріал оболонки
    
    Args:
        material: Назва матеріалу
    
    Returns:
        Назва матеріалу
    
    Raises:
        ValidationError: Якщо матеріал не підтримується
    """
    if material not in MATERIALS:
        raise ValidationError(f"Непідтримуваний матеріал: {material}")
    return material


def validate_gas_type(gas_type: str) -> str:
    """
    Валідує тип газу
    
    Args:
        gas_type: Тип газу
    
    Returns:
        Тип газу
    
    Raises:
        ValidationError: Якщо тип газу не підтримується
    """
    if gas_type not in GAS_DENSITY:
        raise ValidationError(f"Непідтримуваний тип газу: {gas_type}")
    return gas_type


def validate_temperature_difference(inside_temp: float, ground_temp: float) -> None:
    """
    Валідує різницю температур для гарячого повітря
    
    Args:
        inside_temp: Температура всередині (°C)
        ground_temp: Температура на землі (°C)
    
    Raises:
        ValidationError: Якщо температура всередині не більша за температуру на землі
    """
    if inside_temp <= ground_temp:
        raise ValidationError(
            f"Температура всередині ({inside_temp}°C) має бути більшою за "
            f"температуру на землі ({ground_temp}°C)"
        )


def validate_height_parameters(start_height: float, work_height: float) -> None:
    """
    Валідує параметри висоти
    
    Args:
        start_height: Висота пуску (м)
        work_height: Висота польоту (м)
    
    Raises:
        ValidationError: Якщо параметри висоти некоректні
    """
    if start_height < 0:
        raise ValidationError("Висота пуску не може бути від'ємною")
    
    if work_height < 0:
        raise ValidationError("Висота польоту не може бути від'ємною")
    
    total_height = start_height + work_height
    if total_height > 50000:  # Максимальна висота стратосфери
        raise ValidationError("Загальна висота не може перевищувати 50 км")


def validate_all_inputs(
    gas_type: str,
    gas_volume: str,
    material: str,
    thickness: str,
    start_height: str,
    work_height: str,
    ground_temp: str = "15",
    inside_temp: str = "100",
    duration: str = "24",
    mode: str = "payload"
) -> Tuple[dict, dict]:
    """
    Валідує всі введені дані
    
    Args:
        gas_type: Тип газу
        gas_volume: Об'єм газу або навантаження
        material: Матеріал оболонки
        thickness: Товщина оболонки (мкм)
        start_height: Висота пуску (м)
        work_height: Висота польоту (м)
        ground_temp: Температура на землі (°C)
        inside_temp: Температура всередині (°C)
        duration: Тривалість польоту (год)
        mode: Режим розрахунку
    
    Returns:
        Tuple[валідовані_числа, валідовані_рядки]
    
    Raises:
        ValidationError: Якщо дані некоректні
    """
    # Валідація рядків
    validated_strings = {
        'gas_type': validate_gas_type(gas_type),
        'material': validate_material(material),
        'mode': mode
    }
    
    # Валідація чисел
    validated_numbers = {
        'gas_volume': validate_float(gas_volume, "Об'єм газу/навантаження", min_value=0.001),
        'thickness': validate_float(thickness, "Товщина оболонки", min_value=1, max_value=1000),
        'start_height': validate_float(start_height, "Висота пуску", min_value=0),
        'work_height': validate_float(work_height, "Висота польоту", min_value=0),
        'ground_temp': validate_float(ground_temp, "Температура на землі", min_value=-50, max_value=50),
        'inside_temp': validate_float(inside_temp, "Температура всередині", min_value=0, max_value=500),
        'duration': validate_float(duration, "Тривалість польоту (год)", min_value=0.01, max_value=10000)
    }
    
    # Додаткові перевірки
    validate_height_parameters(validated_numbers['start_height'], validated_numbers['work_height'])
    
    if gas_type == "Гаряче повітря":
        validate_temperature_difference(validated_numbers['inside_temp'], validated_numbers['ground_temp'])
    
    return validated_numbers, validated_strings 