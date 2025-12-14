"""
Валідація введених даних
"""

from typing import Union, Tuple, Optional

from balloon.constants import MATERIALS, GAS_DENSITY
from balloon.models import BalloonInputs, ShapeParams


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


def validate_shape_params(shape_type: str, params: dict) -> dict:
    """
    Валідує параметри форми та повертає float-значення через Shape Registry.
    Параметри опціональні - якщо не задані, розраховуються на основі об'єму.
    """
    from balloon.shapes.registry import validate_shape_params as registry_validate, get_shape_entry
    
    # Перевіряємо, чи форма підтримується
    entry = get_shape_entry(shape_type)
    if entry is None:
        raise ValidationError(f"Непідтримувана форма: {shape_type}")
    
    # Використовуємо реєстр для валідації через Pydantic
    try:
        validated = registry_validate(shape_type, params)
        return validated
    except Exception as e:
        # Якщо валідація через реєстр не вдалася (наприклад, некоректні типи),
        # використовуємо простий спосіб валідації як fallback
        def optional(key: str, label: str, min_value: float = 0.0001) -> Optional[float]:
            """Валідує опціональне поле форми"""
            if key not in params or params[key] is None or str(params[key]).strip() == "":
                return None
            return validate_float(str(params[key]), label, min_value=min_value)

        out = {}
        if shape_type == "sphere":
            return out
        elif shape_type == "pillow":
            L = optional("pillow_len", "Довжина подушки")
            W = optional("pillow_wid", "Ширина подушки")
            if L is not None:
                out["pillow_len"] = L
            if W is not None:
                out["pillow_wid"] = W
        elif shape_type == "pear":
            H = optional("pear_height", "Висота груші")
            R_top = optional("pear_top_radius", "Радіус верхньої частини груші")
            R_bottom = optional("pear_bottom_radius", "Радіус нижньої частини груші")
            if H is not None:
                out["pear_height"] = H
            if R_top is not None:
                out["pear_top_radius"] = R_top
            if R_bottom is not None:
                out["pear_bottom_radius"] = R_bottom
        elif shape_type == "cigar":
            L = optional("cigar_length", "Довжина сигари")
            R = optional("cigar_radius", "Радіус сигари")
            if L is not None:
                out["cigar_length"] = L
            if R is not None:
                out["cigar_radius"] = R
        return out


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
    mode: str = "payload",
    shape_type: str = "sphere",
    shape_params: dict = None,
    extra_mass: str = "0",
    seam_factor: str = "1.0",
) -> Tuple[dict, dict]:
    """
    Валідує всі введені дані
    
    Використовує Pydantic моделі для валідації, якщо доступні.
    Інакше використовує просту реалізацію валідації.
    
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
        shape_type: Форма кулі
        shape_params: Параметри форми
        extra_mass: Додаткова маса обладнання
        seam_factor: Коефіцієнт втрат через шви
    
    Returns:
        Tuple[валідовані_числа, валідовані_рядки]
    
    Raises:
        ValidationError: Якщо дані некоректні
    """
    # Спробуємо використати Pydantic моделі
    if BalloonInputs is not None:
        try:
            # Підготовка параметрів форми
            shape_params_dict = shape_params or {}
            shape_params_obj = None
            if shape_params_dict:
                shape_params_obj = ShapeParams(**shape_params_dict)
            
            # Створюємо модель
            inputs = BalloonInputs(
                gas_type=gas_type,
                gas_volume=gas_volume,
                material=material,
                thickness=thickness,
                start_height=start_height,
                work_height=work_height,
                ground_temp=ground_temp,
                inside_temp=inside_temp,
                duration=duration,
                mode=mode,
                shape_type=shape_type,
                shape_params=shape_params_obj,
                extra_mass=extra_mass,
                seam_factor=seam_factor,
            )
            
            # Повертаємо валідовані дані
            return inputs.get_validated_numbers(), inputs.get_validated_strings()
            
        except Exception as e:
            # Якщо Pydantic валідація не вдалася, конвертуємо помилку
            from pydantic import ValidationError as PydanticValidationError
            if isinstance(e, PydanticValidationError):
                # Беремо першу помилку
                error_msg = str(e.errors()[0]['msg']) if e.errors() else str(e)
                raise ValidationError(error_msg)
            raise ValidationError(f"Помилка валідації: {e}")
    
    # Fallback на стару реалізацію
    # Валідація рядків
    validated_strings = {
        'gas_type': validate_gas_type(gas_type),
        'material': validate_material(material),
        'mode': mode,
        'shape_type': shape_type,
    }
    
    # Валідація чисел
    validated_numbers = {
        'gas_volume': validate_float(gas_volume, "Об'єм газу/навантаження", min_value=0.001),
        'thickness': validate_float(thickness, "Товщина оболонки", min_value=1, max_value=1000),
        'start_height': validate_float(start_height, "Висота пуску", min_value=0),
        'work_height': validate_float(work_height, "Висота польоту", min_value=0),
        'ground_temp': validate_float(ground_temp, "Температура на землі", min_value=-50, max_value=50),
        'inside_temp': validate_float(inside_temp, "Температура всередині", min_value=0, max_value=500),
        'duration': validate_float(duration, "Тривалість польоту (год)", min_value=0.01, max_value=10000),
        'extra_mass': validate_float(extra_mass, "Додаткова маса обладнання", min_value=0, max_value=1000),
        'seam_factor': validate_float(seam_factor, "Коефіцієнт втрат через шви", min_value=1.0, max_value=2.0)
    }
    
    # Додаткові перевірки
    validate_height_parameters(validated_numbers['start_height'], validated_numbers['work_height'])
    
    if gas_type == "Гаряче повітря":
        validate_temperature_difference(validated_numbers['inside_temp'], validated_numbers['ground_temp'])

    # Форми
    shape_params = shape_params or {}
    validated_numbers.update(validate_shape_params(shape_type, shape_params))
    
    return validated_numbers, validated_strings 