"""
Розрахунки для неідеальних форм аеростатів
"""

import math
from typing import Dict, Any

try:
    from baloon.constants import *
except ImportError:
    from constants import *


def sphere_volume(radius: float) -> float:
    """Об'єм сфери"""
    return (4/3) * math.pi * radius**3


def sphere_surface_area(radius: float) -> float:
    """Площа поверхні сфери"""
    return 4 * math.pi * radius**2


def torus_volume(major_radius: float, minor_radius: float) -> float:
    """
    Об'єм тороїда
    
    Args:
        major_radius: Великий радіус (від центру до центру труби)
        minor_radius: Малий радіус (радіус перерізу труби)
    
    Returns:
        Об'єм тороїда (м³)
    """
    return 2 * math.pi**2 * major_radius * minor_radius**2


def torus_surface_area(major_radius: float, minor_radius: float) -> float:
    """Площа поверхні тороїда"""
    return 4 * math.pi**2 * major_radius * minor_radius


def cylinder_volume(radius: float, height: float) -> float:
    """Об'єм циліндра"""
    return math.pi * radius**2 * height


def cylinder_surface_area(radius: float, height: float, include_ends: bool = True) -> float:
    """Площа поверхні циліндра"""
    lateral = 2 * math.pi * radius * height
    if include_ends:
        ends = 2 * math.pi * radius**2
        return lateral + ends
    return lateral


def calculate_toroidal_balloon(
    major_radius: float,
    minor_radius: float,
    material: str,
    thickness_mm: float,
    gas_type: str,
    start_height: float,
    work_height: float,
    ground_temp: float = 15,
    inside_temp: float = 100
) -> Dict[str, Any]:
    """
    Розрахунок параметрів тороїдального аеростата
    
    Args:
        major_radius: Великий радіус тороїда (м)
        minor_radius: Малий радіус тороїда (м)
        material: Матеріал оболонки
        thickness_mm: Товщина оболонки (мкм)
        gas_type: Тип газу
        start_height: Висота пуску (м)
        work_height: Висота польоту (м)
        ground_temp: Температура на землі (°C)
        inside_temp: Температура всередині (°C)
    
    Returns:
        Словник з результатами розрахунків
    """
    try:
        from baloon.calculations import (
            air_density_at_height,
            calculate_gas_density_at_altitude,
            calculate_hot_air_density,
            calc_stress
        )
    except ImportError:
        from calculations import (
            air_density_at_height,
            calculate_gas_density_at_altitude,
            calculate_hot_air_density,
            calc_stress
        )
    
    thickness = thickness_mm / 1e6
    total_height = start_height + work_height
    
    # Атмосферні умови на висоті
    T_outside_C, rho_air, P_outside = air_density_at_height(total_height, ground_temp)
    T_outside = T_outside_C + T0
    
    # Щільність газу
    if gas_type == "Гаряче повітря":
        rho_gas = calculate_hot_air_density(inside_temp)
        P_inside = rho_gas * GAS_CONSTANT * (inside_temp + T0)
    else:
        rho_gas = calculate_gas_density_at_altitude(gas_type, P_outside, T_outside)
        P_inside = P_outside
    
    # Об'єм та площа поверхні
    volume = torus_volume(major_radius, minor_radius)
    surface_area = torus_surface_area(major_radius, minor_radius)
    
    # Маса оболонки
    mass_shell = surface_area * thickness * MATERIALS[material][0]
    
    # Підйомна сила
    net_lift_per_m3 = rho_air - rho_gas
    lift = net_lift_per_m3 * volume
    payload = lift - mass_shell
    
    # Напруга (приблизно, для тороїда складніше)
    # Використовуємо середній радіус для спрощення
    avg_radius = (major_radius + minor_radius) / 2
    stress = calc_stress(P_inside, P_outside, avg_radius, thickness)
    stress_limit = MATERIALS[material][1]
    
    return {
        'volume': volume,
        'surface_area': surface_area,
        'payload': payload,
        'mass_shell': mass_shell,
        'lift': lift,
        'major_radius': major_radius,
        'minor_radius': minor_radius,
        'stress': stress,
        'stress_limit': stress_limit,
        'T_outside_C': T_outside_C,
        'P_outside': P_outside,
        'rho_air': rho_air,
        'net_lift_per_m3': net_lift_per_m3
    }


def calculate_cylindrical_balloon(
    radius: float,
    height: float,
    material: str,
    thickness_mm: float,
    gas_type: str,
    start_height: float,
    work_height: float,
    ground_temp: float = 15,
    inside_temp: float = 100,
    closed_ends: bool = True
) -> Dict[str, Any]:
    """
    Розрахунок параметрів циліндричного аеростата
    
    Args:
        radius: Радіус циліндра (м)
        height: Висота циліндра (м)
        material: Матеріал оболонки
        thickness_mm: Товщина оболонки (мкм)
        gas_type: Тип газу
        start_height: Висота пуску (м)
        work_height: Висота польоту (м)
        ground_temp: Температура на землі (°C)
        inside_temp: Температура всередині (°C)
        closed_ends: Чи закриті торці циліндра
    
    Returns:
        Словник з результатами розрахунків
    """
    try:
        from baloon.calculations import (
            air_density_at_height,
            calculate_gas_density_at_altitude,
            calculate_hot_air_density,
            calc_stress
        )
    except ImportError:
        from calculations import (
            air_density_at_height,
            calculate_gas_density_at_altitude,
            calculate_hot_air_density,
            calc_stress
        )
    
    thickness = thickness_mm / 1e6
    total_height = start_height + work_height
    
    # Атмосферні умови на висоті
    T_outside_C, rho_air, P_outside = air_density_at_height(total_height, ground_temp)
    T_outside = T_outside_C + T0
    
    # Щільність газу
    if gas_type == "Гаряче повітря":
        rho_gas = calculate_hot_air_density(inside_temp)
        P_inside = rho_gas * GAS_CONSTANT * (inside_temp + T0)
    else:
        rho_gas = calculate_gas_density_at_altitude(gas_type, P_outside, T_outside)
        P_inside = P_outside
    
    # Об'єм та площа поверхні
    volume = cylinder_volume(radius, height)
    surface_area = cylinder_surface_area(radius, height, include_ends=closed_ends)
    
    # Маса оболонки
    mass_shell = surface_area * thickness * MATERIALS[material][0]
    
    # Підйомна сила
    net_lift_per_m3 = rho_air - rho_gas
    lift = net_lift_per_m3 * volume
    payload = lift - mass_shell
    
    # Напруга (для циліндра)
    # Радіальна напруга
    radial_stress = calc_stress(P_inside, P_outside, radius, thickness)
    # Аксіальна напруга (для закритих торців)
    if closed_ends:
        axial_stress = P_inside * radius / (2 * thickness) if thickness > 0 else 0
        stress = max(radial_stress, axial_stress)
    else:
        stress = radial_stress
    
    stress_limit = MATERIALS[material][1]
    
    return {
        'volume': volume,
        'surface_area': surface_area,
        'payload': payload,
        'mass_shell': mass_shell,
        'lift': lift,
        'radius': radius,
        'height': height,
        'stress': stress,
        'stress_limit': stress_limit,
        'T_outside_C': T_outside_C,
        'P_outside': P_outside,
        'rho_air': rho_air,
        'net_lift_per_m3': net_lift_per_m3
    }

