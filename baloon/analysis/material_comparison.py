"""
Порівняння матеріалів оболонки
"""

import math
from typing import Dict

try:
    from baloon.constants import MATERIALS, GAS_CONSTANT, T0
    from baloon.analysis.base import _compute_lift_state
except ImportError:
    from constants import MATERIALS, GAS_CONSTANT, T0
    from analysis.base import _compute_lift_state


def calculate_material_comparison(gas_type: str, thickness_mm: float, gas_volume: float,
                                ground_temp: float = 15, inside_temp: float = 100,
                                height: float = 1000,
                                shape_type: str = "sphere", shape_params: dict = None,
                                extra_mass: float = 0.0,
                                seam_factor: float = 1.0) -> Dict[str, Dict[str, float]]:
    """
    Порівнює різні матеріали оболонки
    
    Args:
        gas_type: Тип газу
        thickness_mm: Товщина оболонки (мкм)
        gas_volume: Об'єм газу (м³)
        ground_temp: Температура на землі (°C)
        inside_temp: Температура всередині (°C)
        height: Висота польоту (м)
    
    Returns:
        Словник з результатами для кожного матеріалу
    """
    results = {}
    
    for material in MATERIALS.keys():
        try:
            state = _compute_lift_state(
                gas_type=gas_type,
                material=material,
                thickness_mm=thickness_mm,
                gas_volume=gas_volume,
                height=height,
                ground_temp=ground_temp,
                inside_temp=inside_temp,
                shape_type=shape_type,
                shape_params=shape_params,
                extra_mass=extra_mass,
                seam_factor=seam_factor,
            )
            if state['net_lift_per_m3'] > 0:
                radius = ((3 * state['required_volume']) / (4 * math.pi)) ** (1 / 3) if state['required_volume'] > 0 else 0
                stress = 0
                if gas_type == "Гаряче повітря":
                    P_inside = state['rho_gas'] * GAS_CONSTANT * (inside_temp + T0)
                    stress = max(0, P_inside - state['P_outside']) * radius / (2 * (thickness_mm / 1e6))
                
                stress_limit = MATERIALS[material][1]
                safety_factor = stress_limit / stress if stress > 0 else float('inf')
                
                results[material] = {
                    'payload': state['payload'],
                    'mass_shell': state['mass_shell'],
                    'lift': state['lift'],
                    'stress': stress,
                    'stress_limit': stress_limit,
                    'safety_factor': safety_factor,
                    'density': MATERIALS[material][0]
                }
                
        except Exception:
            results[material] = {
                'payload': 0,
                'mass_shell': 0,
                'lift': 0,
                'stress': 0,
                'stress_limit': MATERIALS[material][1],
                'safety_factor': 0,
                'density': MATERIALS[material][0]
            }
    
    return results

