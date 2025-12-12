"""
Математичні розрахунки для аеростатів
"""

import math
from typing import Tuple, Optional, Dict, Any, Literal

try:
    from baloon.constants import *
    from baloon.shapes import (
        sphere_surface_area as geom_sphere_surface_area,
        pillow_volume,
        pillow_surface_area,
        sphere_radius_from_volume,
        pillow_dimensions_from_volume,
        pear_volume,
        pear_surface_area,
        pear_dimensions_from_volume,
        cigar_volume,
        cigar_surface_area,
        cigar_dimensions_from_volume,
    )
except ImportError:
    # Для сумісності з локальними запусками
    from constants import *
    from shapes import (
        sphere_surface_area as geom_sphere_surface_area,
        pillow_volume,
        pillow_surface_area,
        sphere_radius_from_volume,
        pillow_dimensions_from_volume,
        pear_volume,
        pear_surface_area,
        pear_dimensions_from_volume,
        cigar_volume,
        cigar_surface_area,
        cigar_dimensions_from_volume,
    )


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
    try:
        from .constants import GAS_SPECIFIC_CONSTANT
    except ImportError:
        from baloon.constants import GAS_SPECIFIC_CONSTANT
    
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


def _shape_base_geometry(
    shape_type: Literal["sphere", "pillow", "pear", "cigar"], 
    params: Dict[str, Any], 
    target_volume: Optional[float] = None
) -> Tuple[float, float, float, Dict[str, float]]:
    """
    Розраховує геометрію форми на основі об'єму та параметрів
    
    Args:
        shape_type: Тип форми
        params: Параметри форми (можуть бути частковими)
        target_volume: Цільовий об'єм (м³). Якщо не задано, використовуються значення з params
    
    Returns:
        (об'єм, площа поверхні, характерний радіус, словник з розрахованими розмірами)
    """
    shape_type = shape_type or "sphere"
    params = params or {}
    
    if shape_type == "sphere":
        if target_volume is not None and target_volume > 0:
            r = sphere_radius_from_volume(target_volume)
            volume = target_volume
        else:
            # Fallback до одиничної сфери
            volume = 1.0
            r = (3 * volume / (4 * math.pi)) ** (1 / 3)
        base_surface = geom_sphere_surface_area(r)
        return volume, base_surface, r, {'radius': r}
    
    if shape_type == "pillow":
        L_param = params.get("pillow_len")
        W_param = params.get("pillow_wid")
        if target_volume is not None and target_volume > 0:
            # Розраховуємо розміри на основі об'єму
            L, W, H = pillow_dimensions_from_volume(target_volume,
                                                      length=float(L_param) if L_param else None,
                                                      width=float(W_param) if W_param else None)
            volume = target_volume
        else:
            # Використовуємо значення з params або дефолти
            L = float(L_param) if L_param else 3.0
            W = float(W_param) if W_param else 2.0
            # Якщо об'єм не задано, використовуємо дефолтну товщину для розрахунку об'єму
            # Але для викрійки товщина не потрібна
            H = 1.0  # Дефолтна товщина для розрахунку об'єму (не використовується для викрійки)
            volume = pillow_volume(L, W, H)
        # Площа поверхні = 2 прямокутники однакового розміру
        base_surface = pillow_surface_area(L, W)
        char_r = min(L, W) / 2
        return volume, base_surface, char_r, {'pillow_len': L, 'pillow_wid': W}
    
    if shape_type == "pear":
        H_param = params.get("pear_height")
        R_top_param = params.get("pear_top_radius")
        R_bottom_param = params.get("pear_bottom_radius")
        if target_volume is not None and target_volume > 0:
            # Розраховуємо розміри на основі об'єму
            H, R_top, R_bottom = pear_dimensions_from_volume(target_volume,
                                                              height=float(H_param) if H_param else None,
                                                              top_radius=float(R_top_param) if R_top_param else None,
                                                              bottom_radius=float(R_bottom_param) if R_bottom_param else None)
            volume = target_volume
        else:
            # Використовуємо значення з params або дефолти
            H = float(H_param) if H_param else 3.0
            R_top = float(R_top_param) if R_top_param else 1.2
            R_bottom = float(R_bottom_param) if R_bottom_param else 0.6
            volume = pear_volume(H, R_top, R_bottom)
        base_surface = pear_surface_area(H, R_top, R_bottom)
        char_r = (R_top + R_bottom) / 2
        return volume, base_surface, char_r, {'pear_height': H, 'pear_top_radius': R_top, 'pear_bottom_radius': R_bottom}
    
    if shape_type == "cigar":
        L_param = params.get("cigar_length")
        R_param = params.get("cigar_radius")
        if target_volume is not None and target_volume > 0:
            # Розраховуємо розміри на основі об'єму
            L, R = cigar_dimensions_from_volume(target_volume,
                                                length=float(L_param) if L_param else None,
                                                radius=float(R_param) if R_param else None)
            volume = target_volume
        else:
            # Використовуємо значення з params або дефолти
            L = float(L_param) if L_param else 5.0
            R = float(R_param) if R_param else 1.0
            volume = cigar_volume(L, R)
        base_surface = cigar_surface_area(L, R)
        char_r = R
        return volume, base_surface, char_r, {'cigar_length': L, 'cigar_radius': R}
    
    # fallback до сфери
    volume = 1.0
    r = (3 * volume / (4 * math.pi)) ** (1 / 3)
    base_surface = geom_sphere_surface_area(r)
    return volume, base_surface, r, {'radius': r}


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
    gas_type: Literal["Гелій", "Водень", "Гаряче повітря"],
    gas_volume: float,
    material: str,
    thickness_mm: float,
    start_height: float,
    work_height: float,
    ground_temp: float = 15,
    inside_temp: float = 100,
    mode: Literal["payload", "volume"] = "payload",
    duration: float = 0,
    perm_mult: float = 1.0,
    shape_type: Literal["sphere", "pillow", "pear", "cigar"] = "sphere",
    shape_params: Optional[Dict[str, float]] = None,
    extra_mass: float = 0.0,
    seam_factor: float = 1.0,
) -> Dict[str, Any]:
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
        extra_mass: Додаткова маса обладнання (кг) - кріплення, клапани, шнури
        seam_factor: Множник для площі поверхні через шви (1.0 = без втрат, 1.05 = +5%)
    
    Returns:
        Словник з результатами розрахунків
    """
    # Конвертація одиниць
    thickness = thickness_mm / 1e6  # мкм -> м
    total_height = start_height + work_height
    shape_params = shape_params or {}
    
    # Розрахунок умов на висоті
    T_outside_C, rho_air, P_outside = air_density_at_height(total_height, ground_temp)
    T_outside = T_outside_C + T0
    
    # Розрахунок щільності газу на висоті
    if gas_type == "Гаряче повітря":
        if inside_temp <= ground_temp:
            raise ValueError("Температура всередині має бути більшою за температуру на землі.")
        rho_gas = calculate_hot_air_density(inside_temp)
        P_inside = rho_gas * GAS_CONSTANT * (inside_temp + T0)
    else:
        rho_gas = calculate_gas_density_at_altitude(gas_type, P_outside, T_outside)
        P_inside = P_outside
    
    net_lift_per_m3 = rho_air - rho_gas
    if net_lift_per_m3 <= 0:
        raise ValueError("Газ не має підйомної сили на обраній висоті.")
    
    # Розрахунок об'єму в залежності від режиму
    if mode == "payload":
        if gas_volume <= 0:
            raise ValueError("Обʼєм газу має бути додатнім.")
        final_gas_volume = gas_volume
    else:
        if gas_volume <= 0:
            raise ValueError("Навантаження має бути додатнім.")
        # Ітеративний розрахунок об'єму з урахуванням маси оболонки та додаткової маси
        volume_guess = gas_volume / net_lift_per_m3
        for _ in range(10):
            # Розраховуємо геометрію для поточного об'єму
            _, base_surface, _, _ = _shape_base_geometry(shape_type, shape_params, target_volume=volume_guess)
            # Враховуємо коефіцієнт швів
            effective_surface = base_surface * seam_factor
            mass_shell_guess = effective_surface * thickness * MATERIALS[material][0]
            total_mass_guess = mass_shell_guess + extra_mass
            volume_guess = gas_volume / net_lift_per_m3 + total_mass_guess / net_lift_per_m3
        final_gas_volume = volume_guess
    
    # Розраховуємо required_volume на висоті
    required_volume = required_balloon_volume(final_gas_volume, ground_temp, P_outside, T_outside)
    
    # Розраховуємо геометрію на основі required_volume
    volume, surface_area, radius, calculated_shape_params = _shape_base_geometry(
        shape_type, shape_params, target_volume=required_volume
    )
    
    # Оновлюємо shape_params з розрахованими значеннями
    shape_params.update(calculated_shape_params)
    
    # Враховуємо коефіцієнт швів для площі поверхні
    effective_surface_area = surface_area * seam_factor
    
    mass_shell = effective_surface_area * thickness * MATERIALS[material][0]
    lift = net_lift_per_m3 * final_gas_volume
    # Враховуємо додаткову масу обладнання
    payload = lift - mass_shell - extra_mass
    stress = calc_stress(P_inside, P_outside, radius, thickness)
    stress_limit = MATERIALS[material][1]
    
    # Додаємо розрахунок втрат газу для гелію/водню
    gas_loss = 0
    final_gas_volume = gas_volume
    if gas_type in ("Гелій", "Водень") and duration > 0:
        permeability = PERMEABILITY.get(material, {}).get(gas_type, 0) * perm_mult
        delta_p = abs(P_inside - P_outside)
        if delta_p < 100:
            delta_p = 100  # Па
        # Враховуємо ефективну площу поверхні з урахуванням швів для втрат газу
        gas_loss = calculate_gas_loss(permeability, effective_surface_area, delta_p, duration, thickness)
        final_gas_volume = max(0, gas_volume - gas_loss)
        lift_end = net_lift_per_m3 * final_gas_volume
        payload_end = lift_end - mass_shell - extra_mass
    else:
        lift_end = lift
        payload_end = payload

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
        'stress': stress,
        'stress_limit': stress_limit,
        'T_outside_C': T_outside_C,
        'P_outside': P_outside,
        'rho_air': rho_air,
        'net_lift_per_m3': net_lift_per_m3,
        'gas_loss': gas_loss,
        'final_gas_volume': final_gas_volume,
        'lift_end': lift_end,
        'payload_end': payload_end,
        'shape_type': shape_type,
        'shape_params': shape_params,
    } 