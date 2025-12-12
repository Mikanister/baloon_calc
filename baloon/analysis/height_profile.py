"""
Розрахунок профілю параметрів по висоті
"""

from typing import List, Dict, Any

try:
    from baloon.analysis.base import _compute_lift_state
except ImportError:
    from analysis.base import _compute_lift_state


def calculate_height_profile(gas_type: str, material: str, thickness_mm: float,
                           gas_volume: float, ground_temp: float = 15,
                           inside_temp: float = 100, max_height: int = 50000,
                           shape_type: str = "sphere", shape_params: dict = None,
                           extra_mass: float = 0.0,
                           seam_factor: float = 1.0) -> List[Dict[str, Any]]:
    """
    Розраховує профіль параметрів по висоті
    
    Args:
        gas_type: Тип газу
        material: Матеріал оболонки
        thickness_mm: Товщина оболонки (мкм)
        gas_volume: Об'єм газу (м³)
        ground_temp: Температура на землі (°C)
        inside_temp: Температура всередині (°C)
        max_height: Максимальна висота для аналізу (м)
    
    Returns:
        Список словників з параметрами на різних висотах
    """
    profile = []
    
    for height in range(0, max_height + 1, 500):
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
            profile.append({'height': height, **state})
            if state['net_lift_per_m3'] <= 0:
                profile[-1].update({'lift': 0, 'payload': 0, 'mass_shell': 0, 'required_volume': 0})
                
        except Exception:
            continue
    
    return profile

