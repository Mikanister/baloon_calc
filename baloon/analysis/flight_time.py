"""
Розрахунок максимального часу польоту
"""

from typing import Dict, Any

try:
    from baloon.constants import PERMEABILITY, MATERIALS, T0
    from baloon.calculations import (
        calculate_balloon_parameters,
        air_density_at_height,
        calculate_gas_density_at_altitude,
        calculate_gas_loss,
    )
except ImportError:
    from constants import PERMEABILITY, MATERIALS, T0
    from calculations import (
        calculate_balloon_parameters,
        air_density_at_height,
        calculate_gas_density_at_altitude,
        calculate_gas_loss,
    )


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
    min_payload: float = 0.0,
    shape_type: str = "sphere",
    shape_params: dict = None,
    extra_mass: float = 0.0,
    seam_factor: float = 1.0
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
        perm_mult=perm_mult,
        shape_type=shape_type,
        shape_params=shape_params,
        extra_mass=extra_mass,
        seam_factor=seam_factor,
    )
    
    initial_payload = initial_results['payload']
    if initial_payload <= min_payload:
        return {
            'max_time_hours': 0.0,
            'time_to_zero_payload': 0.0,
            'message': 'Початкове навантаження вже менше мінімального'
        }
    
    # Параметри для розрахунку втрат (використовуємо ефективну площу з урахуванням швів)
    surface_area = initial_results.get('effective_surface_area', initial_results['surface_area'])
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
        payload = lift - initial_results['mass_shell'] - extra_mass
        
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

