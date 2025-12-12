"""
Додаткові функції аналізу та візуалізації для аеростатів
"""

import math
from typing import List, Tuple, Dict, Any

from .constants import *
from .calculations import (
    air_density_at_height,
    calculate_hot_air_density,
    calculate_gas_density_at_altitude,
    sphere_surface_area,
    calculate_gas_loss,
)


def calculate_optimal_height(gas_type: str, material: str, thickness_mm: float, 
                           gas_volume: float, ground_temp: float = 15, 
                           inside_temp: float = 100) -> Dict[str, Any]:
    """
    Розраховує оптимальну висоту польоту для максимального навантаження
    
    Args:
        gas_type: Тип газу
        material: Матеріал оболонки
        thickness_mm: Товщина оболонки (мкм)
        gas_volume: Об'єм газу (м³)
        ground_temp: Температура на землі (°C)
        inside_temp: Температура всередині (°C)
    
    Returns:
        Словник з оптимальними параметрами
    """
    max_payload = 0
    optimal_params = {}
    
    # Перевіряємо висоти від 0 до 50 км
    for height in range(0, 50001, 100):
        try:
            state = _compute_lift_state(
                gas_type=gas_type,
                material=material,
                thickness_mm=thickness_mm,
                gas_volume=gas_volume,
                height=height,
                ground_temp=ground_temp,
                inside_temp=inside_temp,
            )
            if state['net_lift_per_m3'] > 0 and state['payload'] > max_payload:
                max_payload = state['payload']
                optimal_params = {
                    'height': height,
                    **state,
                }
                    
        except Exception:
            continue
    
    return optimal_params


def calculate_height_profile(gas_type: str, material: str, thickness_mm: float,
                           gas_volume: float, ground_temp: float = 15,
                           inside_temp: float = 100, max_height: int = 50000) -> List[Dict[str, Any]]:
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
            )
            profile.append({'height': height, **state})
            if state['net_lift_per_m3'] <= 0:
                profile[-1].update({'lift': 0, 'payload': 0, 'mass_shell': 0, 'required_volume': 0})
                
        except Exception:
            continue
    
    return profile


def calculate_material_comparison(gas_type: str, thickness_mm: float, gas_volume: float,
                                ground_temp: float = 15, inside_temp: float = 100,
                                height: float = 1000) -> Dict[str, Dict[str, float]]:
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


def calculate_cost_analysis(material: str, thickness_mm: float, gas_volume: float,
                          gas_type: str, ground_temp: float = 15, 
                          inside_temp: float = 100, height: float = 1000) -> Dict[str, float]:
    """
    Розраховує приблизну вартість матеріалів
    
    Args:
        material: Матеріал оболонки
        thickness_mm: Товщина оболонки (мкм)
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
            thickness_mm=thickness_mm,
            gas_volume=gas_volume,
            height=height,
            ground_temp=ground_temp,
            inside_temp=inside_temp,
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
            
    except Exception:
        pass
    
    return {
        'material_cost': 0,
        'gas_cost': 0,
        'total_cost': 0,
        'mass_shell': 0,
        'gas_volume': gas_volume,
        'cost_per_kg_payload': 0
    }


def _compute_lift_state(
    gas_type: str,
    material: str,
    thickness_mm: float,
    gas_volume: float,
    height: float,
    ground_temp: float,
    inside_temp: float,
) -> Dict[str, Any]:
    """Спільний розрахунок параметрів підйомної сили на заданій висоті."""
    thickness = thickness_mm / 1e6
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
        required_volume = gas_volume * SEA_LEVEL_PRESSURE / P_outside * T_outside / (ground_temp + T0)
        surface_area = sphere_surface_area(required_volume)
        mass_shell = surface_area * thickness * MATERIALS[material][0]
        payload = lift - mass_shell

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


def calculate_max_flight_time(
    gas_type: str,
    material: str,
    thickness_mm: float,
    gas_volume: float,
    start_height: float,
    work_height: float,
    ground_temp: float = 15,
    inside_temp: float = 100,
    perm_mult: float = 1.0,
    min_payload: float = 0.0
) -> Dict[str, Any]:
    """
    Розраховує максимальний час польоту до втрати мінімального навантаження
    
    Args:
        gas_type: Тип газу
        material: Матеріал оболонки
        thickness_mm: Товщина оболонки (мкм)
        gas_volume: Початковий об'єм газу (м³)
        start_height: Висота пуску (м)
        work_height: Висота польоту (м)
        ground_temp: Температура на землі (°C)
        inside_temp: Температура всередині (°C)
        perm_mult: Множник проникності
        min_payload: Мінімальне допустиме навантаження (кг)
    
    Returns:
        Словник з результатами: max_time_hours, time_to_zero_payload, etc.
    """
    from .calculations import (
        calculate_balloon_parameters,
        calculate_gas_density_at_altitude,
        sphere_surface_area,
        calculate_gas_loss
    )
    from .constants import PERMEABILITY, MATERIALS, T0
    
    if gas_type not in ("Гелій", "Водень"):
        # Для гарячого повітря або інших газів втрати не враховуються
        return {
            'max_time_hours': float('inf'),
            'time_to_zero_payload': float('inf'),
            'message': 'Втрати газу не враховуються для цього типу газу'
        }
    
    thickness = thickness_mm / 1e6
    total_height = start_height + work_height
    
    # Розрахунок початкових параметрів
    initial_results = calculate_balloon_parameters(
        gas_type=gas_type,
        gas_volume=gas_volume,
        material=material,
        thickness_mm=thickness_mm,
        start_height=start_height,
        work_height=work_height,
        ground_temp=ground_temp,
        inside_temp=inside_temp,
        mode="payload",
        duration=0,
        perm_mult=perm_mult
    )
    
    initial_payload = initial_results['payload']
    if initial_payload <= min_payload:
        return {
            'max_time_hours': 0.0,
            'time_to_zero_payload': 0.0,
            'message': 'Початкове навантаження вже менше мінімального'
        }
    
    # Параметри для розрахунку втрат
    surface_area = initial_results['surface_area']
    permeability = PERMEABILITY.get(material, {}).get(gas_type, 0) * perm_mult
    
    if permeability == 0:
        return {
            'max_time_hours': float('inf'),
            'time_to_zero_payload': float('inf'),
            'message': 'Проникність не задана для цього матеріалу/газу'
        }
    
    # Атмосферні умови на висоті
    T_outside_C, rho_air, P_outside = air_density_at_height(total_height, ground_temp)
    T_outside = T_outside_C + T0
    
    # Щільність газу на висоті
    rho_gas = calculate_gas_density_at_altitude(gas_type, P_outside, T_outside)
    net_lift_per_m3 = rho_air - rho_gas
    
    # Різниця тисків (мінімальна для оболонки)
    delta_p = max(100, abs(initial_results.get('P_outside', P_outside) - P_outside))
    
    # Ітеративний пошук максимального часу
    # Використовуємо бінарний пошук для швидкості
    max_time = 0.0
    time_low = 0.0
    time_high = 10000.0  # Максимум 10000 годин
    
    for _ in range(50):  # 50 ітерацій для точності
        test_time = (time_low + time_high) / 2
        
        # Розрахунок втрат газу
        gas_loss = calculate_gas_loss(
            permeability, surface_area, delta_p, test_time, thickness
        )
        
        final_gas_volume = max(0, gas_volume - gas_loss)
        lift = net_lift_per_m3 * final_gas_volume
        payload = lift - initial_results['mass_shell']
        
        if payload >= min_payload:
            max_time = test_time
            time_low = test_time
        else:
            time_high = test_time
        
        if time_high - time_low < 0.01:  # Точність 0.01 години
            break
    
    # Розрахунок часу до нульового навантаження
    time_to_zero = max_time
    if initial_payload > 0:
        # Лінійна апроксимація для швидкості
        gas_loss_rate = calculate_gas_loss(
            permeability, surface_area, delta_p, 1.0, thickness
        )  # Втрати за годину
        if gas_loss_rate > 0:
            lift_loss_rate = net_lift_per_m3 * gas_loss_rate
            if lift_loss_rate > 0:
                time_to_zero = initial_payload / lift_loss_rate
    
    return {
        'max_time_hours': max_time,
        'time_to_zero_payload': time_to_zero,
        'initial_payload': initial_payload,
        'final_payload_at_max_time': min_payload,
        'gas_loss_rate_per_hour': calculate_gas_loss(
            permeability, surface_area, delta_p, 1.0, thickness
        ),
        'message': f'Максимальний час польоту: {max_time:.2f} год ({max_time/24:.2f} днів)'
    }


def generate_report(results: Dict[str, Any], mode: str, inputs: Dict[str, Any]) -> str:
    """
    Генерує текстовий звіт з результатами
    
    Args:
        results: Результати розрахунків
        mode: Режим розрахунку
        inputs: Вхідні параметри
    
    Returns:
        Текстовий звіт
    """
    report = []
    report.append("=" * 60)
    report.append("ЗВІТ ПО РОЗРАХУНКУ АЕРОСТАТА")
    report.append("=" * 60)
    report.append("")
    
    # Вхідні параметри
    report.append("ВХІДНІ ПАРАМЕТРИ:")
    report.append("-" * 30)
    report.append(f"Режим розрахунку: {'Обʼєм ➜ навантаження' if mode == 'payload' else 'Навантаження ➜ обʼєм'}")
    report.append(f"Тип газу: {inputs['gas_type']}")
    report.append(f"Матеріал оболонки: {inputs['material']}")
    report.append(f"Товщина оболонки: {inputs['thickness']} мкм")
    report.append(f"Висота пуску: {inputs['start_height']} м")
    report.append(f"Висота польоту: {inputs['work_height']} м")
    
    if inputs['gas_type'] == "Гаряче повітря":
        report.append(f"Температура на землі: {inputs['ground_temp']} °C")
        report.append(f"Температура всередині: {inputs['inside_temp']} °C")
    
    report.append("")
    
    # Результати
    report.append("РЕЗУЛЬТАТИ РОЗРАХУНКІВ:")
    report.append("-" * 30)
    
    if mode == "volume":
        report.append(f"Потрібний обʼєм газу: {results['gas_volume']:.2f} м³")
    
    report.extend([
        f"Необхідний обʼєм кулі: {results['required_volume']:.2f} м³",
        f"Корисне навантаження: {results['payload']:.2f} кг",
        f"Маса оболонки: {results['mass_shell']:.2f} кг",
        f"Підйомна сила: {results['lift']:.2f} кг",
        f"Радіус кулі: {results['radius']:.2f} м",
        f"Площа поверхні: {results['surface_area']:.2f} м²",
        f"Щільність повітря: {results['rho_air']:.4f} кг/м³",
        f"Підйомна сила на м³: {results['net_lift_per_m3']:.4f} кг/м³"
    ])
    
    if inputs['gas_type'] == "Гаряче повітря":
        if results['stress'] > 0:
            safety_factor = results['stress_limit'] / results['stress']
        else:
            safety_factor = float('inf')
        report.extend([
            f"Температура зовні: {results['T_outside_C']:.1f} °C",
            f"Максимальна напруга: {results['stress'] / 1e6:.2f} МПа",
            f"Допустима напруга: {results['stress_limit'] / 1e6:.1f} МПа",
            f"Коефіцієнт безпеки: {'∞' if safety_factor == float('inf') else f'{safety_factor:.1f}'}"
        ])
        if safety_factor < 2:
            report.append("⚠️  УВАГА: Низький коефіцієнт безпеки!")
    
    report.append("")
    report.append("=" * 60)
    
    return '\n'.join(report) 