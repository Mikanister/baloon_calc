"""
Математичні розрахунки для аеростатів
"""

import math
from typing import Tuple, Optional

from .constants import *


def air_density_at_height(h: float, ground_temp_C: float) -> Tuple[float, float, float]:
    """
    Розраховує температуру, щільність та тиск повітря на висоті
    
    Args:
        h: Висота над рівнем моря (м)
        ground_temp_C: Температура на землі (°C)
    
    Returns:
        Tuple[температура_°C, щільність_кг/м³, тиск_Па]
    """
    T_sea = ground_temp_C + T0
    T = T_sea - LAPSE_RATE * h
    P = SEA_LEVEL_PRESSURE * (T / T_sea) ** (GRAVITY / (GAS_CONSTANT * LAPSE_RATE))
    rho = P / (GAS_CONSTANT * T)
    return T - T0, rho, P


def calc_stress(p_internal: float, p_external: float, r: float, t: float) -> float:
    """
    Розраховує напругу в оболонці кулі
    
    Args:
        p_internal: Внутрішній тиск (Па)
        p_external: Зовнішній тиск (Па)
        r: Радіус кулі (м)
        t: Товщина оболонки (м)
    
    Returns:
        Напруга (Па)
    """
    if t == 0:
        return 0.0
    delta_p = max(0, p_internal - p_external)
    return delta_p * r / (2 * t)


def calculate_gas_density_at_altitude(gas_type: str, pressure: float, temperature_K: float) -> float:
    """
    Розраховує щільність газу на висоті за ідеальним газовим законом
    
    Args:
        gas_type: Тип газу ("Гелій", "Водень", "Гаряче повітря")
        pressure: Тиск на висоті (Па)
        temperature_K: Температура на висоті (К)
    
    Returns:
        Щільність газу на висоті (кг/м³)
    """
    from constants import GAS_SPECIFIC_CONSTANT
    
    if gas_type == "Гаряче повітря":
        # Для гарячого повітря використовується GAS_CONSTANT
        return pressure / (GAS_CONSTANT * temperature_K)
    else:
        # Для гелію та водню використовуємо питому газову сталу
        R_specific = GAS_SPECIFIC_CONSTANT.get(gas_type)
        if R_specific is None:
            raise ValueError(f"Невідома питома газова стала для {gas_type}")
        return pressure / (R_specific * temperature_K)


def sphere_surface_area(volume: float) -> float:
    """
    Розраховує площу поверхні сфери за об'ємом
    
    Args:
        volume: Об'єм сфери (м³)
    
    Returns:
        Площа поверхні (м²)
    """
    # Для сфери: V = (4/3)πr³, тому r = (3V/(4π))^(1/3)
    # S = 4πr² = 4π * (3V/(4π))^(2/3) = (36πV²)^(1/3)
    if volume <= 0:
        return 0.0
    return (36 * math.pi * volume**2) ** (1/3)


def required_balloon_volume(gas_volume_ground: float, ground_temp_C: float, 
                          P: float, T: float) -> float:
    """
    Розраховує необхідний об'єм кулі на висоті
    
    Args:
        gas_volume_ground: Об'єм газу на землі (м³)
        ground_temp_C: Температура на землі (°C)
        P: Тиск на висоті (Па)
        T: Температура на висоті (К)
    
    Returns:
        Необхідний об'єм кулі (м³)
    """
    T0_K = ground_temp_C + T0
    return gas_volume_ground * SEA_LEVEL_PRESSURE / P * T / T0_K


def calculate_hot_air_density(inside_temp_C: float) -> float:
    """
    Розраховує щільність гарячого повітря
    
    Args:
        inside_temp_C: Температура всередині кулі (°C)
    
    Returns:
        Щільність гарячого повітря (кг/м³)
    """
    T_inside = inside_temp_C + T0
    return SEA_LEVEL_AIR_DENSITY * T0 / T_inside


def calculate_gas_loss(
    permeability: float, surface_area: float, delta_p: float, duration_h: float, thickness_m: float
) -> float:
    """
    Розраховує втрати газу через оболонку за час польоту
    Args:
        permeability: коефіцієнт проникності (м²/(с·Па))
        surface_area: площа поверхні (м²)
        delta_p: різниця тисків (Па)
        duration_h: тривалість польоту (год)
        thickness_m: товщина оболонки (м)
    Returns:
        Втрачений об'єм газу (м³)
    """
    t_sec = duration_h * 3600
    Q = permeability * surface_area * delta_p * t_sec / thickness_m  # м³
    return Q


def calculate_balloon_parameters(
    gas_type: str,
    gas_volume: float,
    material: str,
    thickness_mm: float,
    start_height: float,
    work_height: float,
    ground_temp: float = 15,
    inside_temp: float = 100,
    mode: str = "payload",
    duration: float = 0,
    perm_mult: float = 1.0
) -> dict:
    """
    Основний розрахунок параметрів аеростата
    
    Args:
        gas_type: Тип газу
        gas_volume: Об'єм газу (м³) або бажане навантаження (кг)
        material: Матеріал оболонки
        thickness_mm: Товщина оболонки (мкм, мікрометри)
        start_height: Висота пуску (м)
        work_height: Висота польоту (м)
        ground_temp: Температура на землі (°C)
        inside_temp: Температура всередині (°C)
        mode: Режим розрахунку ("payload" або "volume")
        duration: Тривалість польоту (год)
        perm_mult: Множник для коефіцієнта проникності
    
    Returns:
        Словник з результатами розрахунків
    """
    # Конвертація одиниць
    thickness = thickness_mm / 1e6  # мкм -> м
    total_height = start_height + work_height
    
    # Розрахунок умов на висоті
    T_outside_C, rho_air, P_outside = air_density_at_height(total_height, ground_temp)
    T_outside = T_outside_C + T0
    
    # Розрахунок щільності газу на висоті
    if gas_type == "Гаряче повітря":
        if inside_temp <= ground_temp:
            raise ValueError("Температура всередині має бути більшою за температуру на землі.")
        # Для гарячого повітря щільність розраховується від температури всередині
        rho_gas = calculate_hot_air_density(inside_temp)
        # Внутрішній тиск для гарячого повітря
        P_inside = rho_gas * GAS_CONSTANT * (inside_temp + T0)
    else:
        # Для гелію та водню щільність змінюється з висотою (тиск і температура)
        # Використовуємо ідеальний газовий закон: ρ = P/(R_specific * T)
        rho_gas = calculate_gas_density_at_altitude(gas_type, P_outside, T_outside)
        # Для гелію/водню внутрішній тиск зазвичай дорівнює зовнішньому
        # (але можна додати надлишковий тиск пізніше)
        P_inside = P_outside
    
    # Розрахунок підйомної сили
    net_lift_per_m3 = rho_air - rho_gas
    if net_lift_per_m3 <= 0:
        raise ValueError("Газ не має підйомної сили на обраній висоті.")
    
    # Розрахунок об'єму в залежності від режиму
    if mode == "payload":
        # Заданий об'єм газу -> розрахунок навантаження
        if gas_volume <= 0:
            raise ValueError("Обʼєм газу має бути додатнім.")
        required_volume = required_balloon_volume(gas_volume, ground_temp, P_outside, T_outside)
        final_gas_volume = gas_volume
    else:
        # Задане навантаження -> розрахунок об'єму
        if gas_volume <= 0:
            raise ValueError("Навантаження має бути додатнім.")
        
        # Ітеративний розрахунок об'єму
        volume_guess = gas_volume / net_lift_per_m3
        for _ in range(5):
            surface_area = sphere_surface_area(volume_guess)
            mass_shell = surface_area * thickness * MATERIALS[material][0]
            volume_guess = gas_volume / net_lift_per_m3 + mass_shell / net_lift_per_m3
        
        final_gas_volume = volume_guess
        required_volume = required_balloon_volume(final_gas_volume, ground_temp, P_outside, T_outside)
    
    # Фінальні розрахунки
    surface_area = sphere_surface_area(required_volume)
    mass_shell = surface_area * thickness * MATERIALS[material][0]
    lift = net_lift_per_m3 * final_gas_volume
    payload = lift - mass_shell
    radius = ((3 * required_volume) / (4 * math.pi)) ** (1 / 3)
    stress = calc_stress(P_inside, P_outside, radius, thickness)
    stress_limit = MATERIALS[material][1]
    
    # Додаємо розрахунок втрат газу для гелію/водню
    gas_loss = 0
    final_gas_volume = gas_volume
    if gas_type in ("Гелій", "Водень") and duration > 0:
        permeability = PERMEABILITY.get(material, {}).get(gas_type, 0) * perm_mult
        delta_p = abs(P_inside - P_outside)
        # Мінімальний надлишковий тиск для оболонки (щоб втрати не були нульовими)
        if delta_p < 100:
            delta_p = 100  # Па
        gas_loss = calculate_gas_loss(permeability, surface_area, delta_p, duration, thickness)
        final_gas_volume = max(0, gas_volume - gas_loss)
        lift_end = net_lift_per_m3 * final_gas_volume
        payload_end = lift_end - mass_shell
    else:
        lift_end = lift
        payload_end = payload

    return {
        'gas_volume': gas_volume,
        'required_volume': required_volume,
        'payload': payload,
        'mass_shell': mass_shell,
        'lift': lift,
        'radius': radius,
        'surface_area': surface_area,
        'stress': stress,
        'stress_limit': stress_limit,
        'T_outside_C': T_outside_C,
        'P_outside': P_outside,
        'rho_air': rho_air,
        'net_lift_per_m3': net_lift_per_m3,
        'gas_loss': gas_loss,
        'final_gas_volume': final_gas_volume,
        'lift_end': lift_end,
        'payload_end': payload_end
    } 