"""
Розв'язання задач: об'єм→навантаження, навантаження→об'єм
"""

from typing import Dict, Any, Literal, Optional
import math

from balloon.model.atmosphere import air_density_at_height
from balloon.model.gas import (
    calculate_gas_density_at_altitude,
    calculate_hot_air_density
)
from balloon.model.materials import (
    get_material_density,
    get_material_stress_limit,
    get_material_permeability,
    calc_stress
)
from balloon.model.shapes import get_shape_dimensions_from_volume
from balloon.constants import (
    T0, GAS_CONSTANT, GRAVITY
)


def required_balloon_volume(
    gas_volume_ground: float,
    ground_temp_C: float,
    P: float,
    T: float
) -> float:
    """
    Розраховує необхідний об'єм кулі на висоті з урахуванням розширення газу
    
    Args:
        gas_volume_ground: Об'єм газу на землі (м³)
        ground_temp_C: Температура на землі (°C)
        P: Тиск на висоті (Па)
        T: Температура на висоті (К)
    
    Returns:
        Необхідний об'єм кулі на висоті (м³)
    """
    T_ground = ground_temp_C + T0
    P_ground = 101325  # Стандартний тиск на рівні моря
    # Використовуємо ідеальний газовий закон: PV/T = const
    return gas_volume_ground * (P_ground / P) * (T / T_ground)


def calculate_gas_loss(
    permeability: float,
    surface_area: float,
    delta_p: float,
    duration_h: float,
    thickness_m: float
) -> float:
    """
    Розраховує втрати газу через оболонку за час польоту
    
    Args:
        permeability: Коефіцієнт проникності (м²/(с·Па))
        surface_area: Площа поверхні (м²)
        delta_p: Різниця тисків (Па)
        duration_h: Тривалість польоту (год)
        thickness_m: Товщина оболонки (м)
    
    Returns:
        Втрачений об'єм газу (м³)
    """
    # Unit conversion: GUI provides duration in hours (h), model uses SI (seconds)
    # Conversion: 1 hour = 3600 seconds
    t_sec = duration_h * 3600
    Q = permeability * surface_area * delta_p * t_sec / thickness_m
    return Q


def calculate_balloon_state(
    gas_type: Literal["Гелій", "Водень", "Гаряче повітря"],
    gas_volume: float,
    material: str,
    thickness_m: float,
    total_height: float,
    ground_temp: float,
    inside_temp: float,
    shape_type: Literal["sphere", "pillow", "pear", "cigar"],
    shape_params: Optional[Dict[str, float]] = None,
    extra_mass: float = 0.0,
    seam_factor: float = 1.0
) -> Dict[str, Any]:
    """
    Розраховує стан аеростата на заданій висоті
    
    Args:
        gas_type: Тип газу
        gas_volume: Об'єм газу (м³)
        material: Матеріал оболонки
        thickness_m: Товщина оболонки (м)
        total_height: Загальна висота (м)
        ground_temp: Температура на землі (°C)
        inside_temp: Температура всередині (°C)
        shape_type: Тип форми
        shape_params: Параметри форми
        extra_mass: Додаткова маса (кг)
        seam_factor: Коефіцієнт швів
    
    Returns:
        Словник з параметрами стану
    """
    shape_params = shape_params or {}
    
    # Атмосферні умови на висоті
    T_outside_C, rho_air, P_outside = air_density_at_height(total_height, ground_temp)
    T_outside = T_outside_C + T0
    
    # Щільність газу на висоті
    if gas_type == "Гаряче повітря":
        rho_gas = calculate_hot_air_density(inside_temp)
        P_inside = rho_gas * GAS_CONSTANT * (inside_temp + T0)
    else:
        rho_gas = calculate_gas_density_at_altitude(gas_type, P_outside, T_outside)
        P_inside = P_outside
    
    net_lift_per_m3 = rho_air - rho_gas
    if net_lift_per_m3 <= 0:
        raise ValueError("Газ не має підйомної сили на обраній висоті.")
    
    # Необхідний об'єм на висоті
    required_volume = required_balloon_volume(gas_volume, ground_temp, P_outside, T_outside)
    
    # Геометрія форми
    volume, surface_area, radius, calculated_shape_params = get_shape_dimensions_from_volume(
        shape_type, required_volume, shape_params
    )
    shape_params.update(calculated_shape_params)
    
    # Ефективна площа з урахуванням швів
    effective_surface_area = surface_area * seam_factor
    
    # Маса оболонки
    material_density = get_material_density(material)
    mass_shell = effective_surface_area * thickness_m * material_density
    
    # Підйомна сила та навантаження
    lift = net_lift_per_m3 * gas_volume
    payload = lift - mass_shell - extra_mass
    
    # Розраховуємо детальний бюджет маси та підйомної сили
    from balloon.model.mass_budget import calculate_mass_budget, calculate_lift_budget
    
    mass_budget = calculate_mass_budget(
        gas_volume=gas_volume,
        gas_density=rho_gas,
        surface_area=surface_area,
        thickness_m=thickness_m,
        material_density=material_density,
        seam_factor=seam_factor,
        reinforcements_mass=0.0,  # За замовчуванням немає підсилень
        payload_mass=payload,
        safety_margin_percent=0.0,  # За замовчуванням немає запасу
        extra_mass=extra_mass
    )
    
    lift_budget = calculate_lift_budget(
        gas_volume=gas_volume,
        air_density=rho_air,
        gas_density=rho_gas,
        mass_budget=mass_budget
    )
    
    # Напруга
    stress = calc_stress(P_inside, P_outside, radius, thickness_m)
    stress_limit = get_material_stress_limit(material)
    
    return {
        'gas_volume': gas_volume,
        'required_volume': required_volume,
        'payload': payload,
        'mass_shell': mass_shell,
        'extra_mass': extra_mass,
        'lift': lift,
        'radius': radius,
        'surface_area': surface_area,
        'effective_surface_area': effective_surface_area,
        'mass_budget': mass_budget.to_dict(),
        'lift_budget': lift_budget.to_dict(),
        'stress': stress,
        'stress_limit': stress_limit,
        'T_outside_C': T_outside_C,
        'P_outside': P_outside,
        'rho_air': rho_air,
        'net_lift_per_m3': net_lift_per_m3,
        'shape_type': shape_type,
        'shape_params': shape_params,
    }


def solve_volume_to_payload(
    gas_type: Literal["Гелій", "Водень", "Гаряче повітря"],
    gas_volume: float,
    material: str,
    thickness_um: float,
    start_height: float,
    work_height: float,
    ground_temp: float = 15,
    inside_temp: float = 100,
    duration: float = 0,
    perm_mult: float = 1.0,
    shape_type: Literal["sphere", "pillow", "pear", "cigar"] = "sphere",
    shape_params: Optional[Dict[str, float]] = None,
    extra_mass: float = 0.0,
    seam_factor: float = 1.0,
) -> Dict[str, Any]:
    """
    Розв'язує задачу: об'єм → навантаження
    
    Args:
        gas_type: Тип газу
        gas_volume: Об'єм газу (м³)
        material: Матеріал оболонки
        thickness_um: Товщина оболонки (мкм)
        start_height: Висота пуску (м)
        work_height: Висота польоту (м)
        ground_temp: Температура на землі (°C)
        inside_temp: Температура всередині (°C)
        duration: Тривалість польоту (год)
        perm_mult: Множник проникності
        shape_type: Тип форми
        shape_params: Параметри форми
        extra_mass: Додаткова маса (кг)
        seam_factor: Коефіцієнт швів
    
    Returns:
        Словник з результатами
    """
    if gas_volume <= 0:
        raise ValueError("Об'єм газу має бути додатнім.")
    
    # Unit conversion: GUI provides thickness in micrometers (µm), model uses SI (meters)
    # Conversion: 1 µm = 1e-6 m
    thickness_m = thickness_um / 1e6
    total_height = start_height + work_height
    
    # Базовий стан
    state = calculate_balloon_state(
        gas_type=gas_type,
        gas_volume=gas_volume,
        material=material,
        thickness_m=thickness_m,
        total_height=total_height,
        ground_temp=ground_temp,
        inside_temp=inside_temp,
        shape_type=shape_type,
        shape_params=shape_params,
        extra_mass=extra_mass,
        seam_factor=seam_factor
    )
    
    # Втрати газу
    gas_loss = 0
    final_gas_volume = gas_volume
    lift_end = state['lift']
    payload_end = state['payload']
    
    if gas_type in ("Гелій", "Водень") and duration > 0:
        permeability_base = get_material_permeability(material, gas_type)
        if permeability_base is not None:
            permeability = permeability_base * perm_mult
            delta_p = abs(state.get('P_inside', state['P_outside']) - state['P_outside'])
            if delta_p < 100:
                delta_p = 100  # Мінімальна різниця тисків
            
            gas_loss = calculate_gas_loss(
                permeability,
                state['effective_surface_area'],
                delta_p,
                duration,
                thickness_m
            )
            final_gas_volume = max(0, gas_volume - gas_loss)
            lift_end = state['net_lift_per_m3'] * final_gas_volume
            payload_end = lift_end - state['mass_shell'] - extra_mass
    
    state.update({
        'gas_loss': gas_loss,
        'final_gas_volume': final_gas_volume,
        'lift_end': lift_end,
        'payload_end': payload_end,
    })
    
    return state


def solve_payload_to_volume(
    gas_type: Literal["Гелій", "Водень", "Гаряче повітря"],
    target_payload: float,
    material: str,
    thickness_um: float,
    start_height: float,
    work_height: float,
    ground_temp: float = 15,
    inside_temp: float = 100,
    duration: float = 0,
    perm_mult: float = 1.0,
    shape_type: Literal["sphere", "pillow", "pear", "cigar"] = "sphere",
    shape_params: Optional[Dict[str, float]] = None,
    extra_mass: float = 0.0,
    seam_factor: float = 1.0,
) -> Dict[str, Any]:
    """
    Розв'язує задачу: навантаження → об'єм
    
    Args:
        gas_type: Тип газу
        target_payload: Бажане навантаження (кг)
        material: Матеріал оболонки
        thickness_um: Товщина оболонки (мкм)
        start_height: Висота пуску (м)
        work_height: Висота польоту (м)
        ground_temp: Температура на землі (°C)
        inside_temp: Температура всередині (°C)
        duration: Тривалість польоту (год)
        perm_mult: Множник проникності
        shape_type: Тип форми
        shape_params: Параметри форми
        extra_mass: Додаткова маса (кг)
        seam_factor: Коефіцієнт швів
    
    Returns:
        Словник з результатами
    """
    if target_payload <= 0:
        raise ValueError("Навантаження має бути додатнім.")
    
    # Unit conversion: GUI provides thickness in micrometers (µm), model uses SI (meters)
    # Conversion: 1 µm = 1e-6 m
    thickness_m = thickness_um / 1e6
    total_height = start_height + work_height
    
    # Спочатку отримуємо атмосферні умови
    T_outside_C, rho_air, P_outside = air_density_at_height(total_height, ground_temp)
    T_outside = T_outside_C + T0
    
    # Щільність газу
    if gas_type == "Гаряче повітря":
        rho_gas = calculate_hot_air_density(inside_temp)
    else:
        rho_gas = calculate_gas_density_at_altitude(gas_type, P_outside, T_outside)
    
    net_lift_per_m3 = rho_air - rho_gas
    if net_lift_per_m3 <= 0:
        raise ValueError("Газ не має підйомної сили на обраній висоті.")
    
    # Ітеративний розрахунок об'єму
    # Початкове наближення: об'єм = навантаження / підйомна_сила_на_м³
    volume_guess = target_payload / net_lift_per_m3
    
    for iteration in range(20):  # Максимум 20 ітерацій
        # Розраховуємо геометрію для поточного об'єму
        required_volume = required_balloon_volume(volume_guess, ground_temp, P_outside, T_outside)
        _, surface_area, _, _ = get_shape_dimensions_from_volume(
            shape_type, required_volume, shape_params
        )
        
        # Маса оболонки
        effective_surface = surface_area * seam_factor
        material_density = get_material_density(material)
        mass_shell_guess = effective_surface * thickness_m * material_density
        total_mass_guess = mass_shell_guess + extra_mass
        
        # Новий об'єм з урахуванням маси оболонки
        new_volume_guess = (target_payload + total_mass_guess) / net_lift_per_m3
        
        # Перевірка збіжності
        if abs(new_volume_guess - volume_guess) < 0.001:
            volume_guess = new_volume_guess
            break
        
        volume_guess = new_volume_guess
    
    # Фінальний розрахунок стану
    state = calculate_balloon_state(
        gas_type=gas_type,
        gas_volume=volume_guess,
        material=material,
        thickness_m=thickness_m,
        total_height=total_height,
        ground_temp=ground_temp,
        inside_temp=inside_temp,
        shape_type=shape_type,
        shape_params=shape_params,
        extra_mass=extra_mass,
        seam_factor=seam_factor
    )
    
    # Втрати газу (якщо потрібно)
    gas_loss = 0
    final_gas_volume = volume_guess
    lift_end = state['lift']
    payload_end = state['payload']
    
    if gas_type in ("Гелій", "Водень") and duration > 0:
        permeability_base = get_material_permeability(material, gas_type)
        if permeability_base is not None:
            permeability = permeability_base * perm_mult
            delta_p = abs(state.get('P_inside', state['P_outside']) - state['P_outside'])
            if delta_p < 100:
                delta_p = 100
            
            gas_loss = calculate_gas_loss(
                permeability,
                state['effective_surface_area'],
                delta_p,
                duration,
                thickness_m
            )
            final_gas_volume = max(0, volume_guess - gas_loss)
            lift_end = state['net_lift_per_m3'] * final_gas_volume
            payload_end = lift_end - state['mass_shell'] - extra_mass
    
    state.update({
        'gas_loss': gas_loss,
        'final_gas_volume': final_gas_volume,
        'lift_end': lift_end,
        'payload_end': payload_end,
    })
    
    return state

