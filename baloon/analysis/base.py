"""
Базові функції для аналізу
"""

from typing import Dict, Any

try:
    from baloon.constants import *
    from baloon.calculations import (
        air_density_at_height,
        calculate_hot_air_density,
        calculate_gas_density_at_altitude,
        _shape_base_geometry,
    )
except ImportError:
    from constants import *
    from calculations import (
        air_density_at_height,
        calculate_hot_air_density,
        calculate_gas_density_at_altitude,
        _shape_base_geometry,
    )


def _compute_lift_state(
    gas_type: str,
    material: str,
    thickness_mm: float,
    gas_volume: float,
    height: float,
    ground_temp: float,
    inside_temp: float,
    shape_type: str = "sphere",
    shape_params: dict = None,
    extra_mass: float = 0.0,
    seam_factor: float = 1.0,
) -> Dict[str, Any]:
    """Спільний розрахунок параметрів підйомної сили на заданій висоті."""
    thickness = thickness_mm / 1e6
    shape_params = shape_params or {}

    T_outside_C, rho_air, P_outside = air_density_at_height(height, ground_temp)
    T_outside = T_outside_C + T0

    if gas_type == "Гаряче повітря":
        rho_gas = calculate_hot_air_density(inside_temp)
    else:
        rho_gas = calculate_gas_density_at_altitude(gas_type, P_outside, T_outside)

    net_lift_per_m3 = rho_air - rho_gas
    required_volume = 0
    surface_area = 0
    mass_shell = 0
    lift = net_lift_per_m3 * gas_volume
    payload = lift

    if net_lift_per_m3 > 0:
        # Розраховуємо required_volume на висоті
        T0_K = ground_temp + T0
        required_volume = gas_volume * SEA_LEVEL_PRESSURE / P_outside * T_outside / T0_K
        
        # Розраховуємо геометрію на основі required_volume
        volume, surface_area, radius, calculated_shape_params = _shape_base_geometry(
            shape_type, shape_params, target_volume=required_volume
        )
        
        # Враховуємо коефіцієнт швів
        effective_surface_area = surface_area * seam_factor
        mass_shell = effective_surface_area * thickness * MATERIALS[material][0]
        # Враховуємо додаткову масу
        payload = lift - mass_shell - extra_mass

    return {
        'rho_air': rho_air,
        'rho_gas': rho_gas,
        'net_lift_per_m3': net_lift_per_m3,
        'required_volume': required_volume,
        'surface_area': surface_area,
        'mass_shell': mass_shell,
        'lift': lift,
        'payload': payload,
        'T_outside_C': T_outside_C,
        'P_outside': P_outside,
    }

