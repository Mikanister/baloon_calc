"""
Аналіз вартості матеріалів
"""

import logging
from typing import Dict

try:
    from balloon.analysis.base import _compute_lift_state
except ImportError:
    from balloon.analysis.base import _compute_lift_state

logger = logging.getLogger(__name__)


def calculate_cost_analysis(material: str, thickness_um: float, gas_volume: float,
                          gas_type: str, ground_temp: float = 15, 
                          inside_temp: float = 100, height: float = 1000,
                          shape_type: str = "sphere", shape_params: dict = None,
                          extra_mass: float = 0.0,
                          seam_factor: float = 1.0) -> Dict[str, float]:
    """
    Розраховує приблизну вартість матеріалів
    
    Args:
        material: Матеріал оболонки
        thickness_um: Товщина оболонки (мкм)
        gas_volume: Об'єм газу (м³)
        gas_type: Тип газу
        ground_temp: Температура на землі (°C)
        inside_temp: Температура всередині (°C)
        height: Висота польоту (м)
    
    Returns:
        Словник з вартісними показниками
    """
    # Приблизні ціни на матеріали (грн/кг)
    material_prices = {
        "HDPE": 25,
        "TPU": 80,
        "Mylar": 120,
        "Nylon": 60,
        "PET": 35
    }
    
    # Ціни на гази (грн/м³)
    gas_prices = {
        "Гелій": 150,
        "Водень": 5,
        "Гаряче повітря": 0.1  # вартість нагріву
    }
    
    try:
        state = _compute_lift_state(
            gas_type=gas_type,
            material=material,
            thickness_um=thickness_um,
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
            material_cost = state['mass_shell'] * material_prices.get(material, 50)
            gas_cost = gas_volume * gas_prices.get(gas_type, 0)
            total_cost = material_cost + gas_cost
            
            return {
                'material_cost': material_cost,
                'gas_cost': gas_cost,
                'total_cost': total_cost,
                'mass_shell': state['mass_shell'],
                'gas_volume': gas_volume,
                'cost_per_kg_payload': total_cost / max(0.001, state['lift'] - state['mass_shell'])
            }
            
    except Exception as e:
        logger.warning(f"Помилка розрахунку вартості: {e}", exc_info=True)
        # Повертаємо значення за замовчуванням при помилці
    
    return {
        'material_cost': 0,
        'gas_cost': 0,
        'total_cost': 0,
        'mass_shell': 0,
        'gas_volume': gas_volume,
        'cost_per_kg_payload': 0
    }

