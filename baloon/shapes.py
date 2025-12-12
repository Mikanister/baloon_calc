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


def pillow_volume(length: float, width: float, thickness: float = 1.0) -> float:
    """
    Об'єм плоскої подушки/мішка
    
    Args:
        length: Довжина подушки (м)
        width: Ширина подушки (м)
        thickness: Товщина подушки (м), за замовчуванням 1.0
    """
    return length * width * thickness


def pillow_surface_area(length: float, width: float, thickness: float = None) -> float:
    """
    Площа поверхні плоскої подушки/мішка
    
    Подушка складається з двох прямокутних сегментів однакового розміру,
    з'єднаних по кромці. Площа = 2 × (length × width)
    
    Args:
        length: Довжина подушки (м)
        width: Ширина подушки (м)
        thickness: Товщина подушки (м) - не використовується для розрахунку площі, але може бути для сумісності
    """
    # Площа двох прямокутних панелей
    return 2 * length * width


# Функції для розрахунку розмірів на основі об'єму
def sphere_radius_from_volume(volume: float) -> float:
    """Розраховує радіус сфери за об'ємом"""
    if volume <= 0:
        return 0.0
    return (3 * volume / (4 * math.pi)) ** (1 / 3)


def cylinder_dimensions_from_volume(volume: float, radius: float = None, height: float = None) -> tuple:
    """
    Розраховує розміри циліндра за об'ємом
    
    Args:
        volume: Об'єм циліндра (м³)
        radius: Якщо задано, розраховується висота
        height: Якщо задано, розраховується радіус
    
    Returns:
        (radius, height) в метрах
    """
    if volume <= 0:
        return (0.0, 0.0)
    if radius is not None and radius > 0:
        height = volume / (math.pi * radius**2)
        return (radius, height)
    elif height is not None and height > 0:
        radius = (volume / (math.pi * height)) ** 0.5
        return (radius, height)
    else:
        # Якщо не задано жодного параметра, використовуємо співвідношення 2:1 (висота:радіус)
        # V = πr²h, якщо h = 2r, то V = 2πr³, r = (V/(2π))^(1/3)
        radius = (volume / (2 * math.pi)) ** (1 / 3)
        height = 2 * radius
        return (radius, height)


def torus_dimensions_from_volume(volume: float, major_radius: float = None, minor_radius: float = None) -> tuple:
    """
    Розраховує розміри тора за об'ємом
    
    Args:
        volume: Об'єм тора (м³)
        major_radius: Якщо задано, розраховується minor_radius
        minor_radius: Якщо задано, розраховується major_radius
    
    Returns:
        (major_radius, minor_radius) в метрах
    """
    if volume <= 0:
        return (0.0, 0.0)
    if major_radius is not None and major_radius > 0:
        # V = 2π²Rr², тому r = sqrt(V/(2π²R))
        minor_radius = (volume / (2 * math.pi**2 * major_radius)) ** 0.5
        return (major_radius, minor_radius)
    elif minor_radius is not None and minor_radius > 0:
        # V = 2π²Rr², тому R = V/(2π²r²)
        major_radius = volume / (2 * math.pi**2 * minor_radius**2)
        return (major_radius, minor_radius)
    else:
        # Якщо не задано жодного параметра, використовуємо співвідношення 4:1 (major:minor)
        # V = 2π²Rr², якщо R = 4r, то V = 8π²r³, r = (V/(8π²))^(1/3)
        minor_radius = (volume / (8 * math.pi**2)) ** (1 / 3)
        major_radius = 4 * minor_radius
        return (major_radius, minor_radius)


def pear_volume(height: float, top_radius: float, bottom_radius: float) -> float:
    """
    Об'єм грушоподібної форми
    
    Груша моделюється як обертання кривої навколо вертикальної осі.
    Використовуємо наближення через об'єм двох частин:
    - Верхня частина (сферична): полусфера з радіусом top_radius
    - Нижня частина (конусоподібна): зрізаний конус між top_radius та bottom_radius
    
    Args:
        height: Висота груші (м)
        top_radius: Радіус верхньої частини (ширша, м)
        bottom_radius: Радіус нижньої частини (вужча, м)
    
    Returns:
        Об'єм груші (м³)
    """
    # Розділяємо грушу на дві частини
    # Верхня частина - приблизно полусфера (40% висоти)
    h_top = height * 0.4
    V_top = (2/3) * math.pi * top_radius**3  # Об'єм полусфери
    
    # Нижня частина - зрізаний конус (60% висоти)
    h_bottom = height * 0.6
    # Об'єм зрізаного конуса: V = (πh/3) * (R² + Rr + r²)
    V_bottom = (math.pi * h_bottom / 3) * (top_radius**2 + top_radius * bottom_radius + bottom_radius**2)
    
    return V_top + V_bottom


def pear_surface_area(height: float, top_radius: float, bottom_radius: float) -> float:
    """
    Площа поверхні грушоподібної форми
    
    Args:
        height: Висота груші (м)
        top_radius: Радіус верхньої частини (ширша, м)
        bottom_radius: Радіус нижньої частини (вужча, м)
    
    Returns:
        Площа поверхні груші (м²)
    """
    # Розділяємо на дві частини
    h_top = height * 0.4
    h_bottom = height * 0.6
    
    # Верхня частина - полусфера
    S_top = 2 * math.pi * top_radius**2  # Площа поверхні полусфери
    
    # Нижня частина - бічна поверхня зрізаного конуса
    # S = π(R + r) * l, де l - твірна конуса
    l = math.sqrt(h_bottom**2 + (top_radius - bottom_radius)**2)
    S_bottom = math.pi * (top_radius + bottom_radius) * l
    
    return S_top + S_bottom


def pear_dimensions_from_volume(volume: float, height: float = None, top_radius: float = None, bottom_radius: float = None) -> tuple:
    """
    Розраховує розміри груші за об'ємом
    
    Args:
        volume: Об'єм груші (м³)
        height: Якщо задано, розраховуються радіуси
        top_radius: Якщо задано, розраховується bottom_radius або height
        bottom_radius: Якщо задано, розраховується top_radius або height
    
    Returns:
        (height, top_radius, bottom_radius) в метрах
    """
    if volume <= 0:
        return (0.0, 0.0, 0.0)
    
    # Підраховуємо скільки параметрів задано
    given = sum(1 for x in [height, top_radius, bottom_radius] if x is not None and x > 0)
    
    if given == 3:
        # Всі параметри задані
        return (height, top_radius, bottom_radius)
    elif given == 2:
        # Задано два параметри, розраховуємо третій
        if height is None:
            # Потрібно розрахувати height
            # Використовуємо ітераційний підхід або наближення
            # Для простоти, використаємо співвідношення height = 2 * top_radius
            height = 2 * top_radius
            # Перевіряємо об'єм та коригуємо
            test_volume = pear_volume(height, top_radius, bottom_radius)
            if test_volume > 0:
                scale = (volume / test_volume) ** (1/3)
                height = height * scale
        elif top_radius is None:
            # Потрібно розрахувати top_radius
            # Використовуємо співвідношення top_radius = 2 * bottom_radius
            top_radius = 2 * bottom_radius
            # Перевіряємо об'єм та коригуємо
            test_volume = pear_volume(height, top_radius, bottom_radius)
            if test_volume > 0:
                scale = (volume / test_volume) ** (1/3)
                top_radius = top_radius * scale
                bottom_radius = bottom_radius * scale
        elif bottom_radius is None:
            # Потрібно розрахувати bottom_radius
            # Використовуємо співвідношення bottom_radius = top_radius / 2
            bottom_radius = top_radius / 2
            # Перевіряємо об'єм та коригуємо
            test_volume = pear_volume(height, top_radius, bottom_radius)
            if test_volume > 0:
                scale = (volume / test_volume) ** (1/3)
                top_radius = top_radius * scale
                bottom_radius = bottom_radius * scale
        
        return (height, top_radius, bottom_radius)
    elif given == 1:
        # Задано один параметр
        if height is not None and height > 0:
            # Використовуємо співвідношення: top_radius = height / 2.5, bottom_radius = top_radius / 2
            top_radius = height / 2.5
            bottom_radius = top_radius / 2
        elif top_radius is not None and top_radius > 0:
            # Використовуємо співвідношення: height = 2.5 * top_radius, bottom_radius = top_radius / 2
            height = 2.5 * top_radius
            bottom_radius = top_radius / 2
        elif bottom_radius is not None and bottom_radius > 0:
            # Використовуємо співвідношення: top_radius = 2 * bottom_radius, height = 2.5 * top_radius
            top_radius = 2 * bottom_radius
            height = 2.5 * top_radius
        else:
            return (0.0, 0.0, 0.0)
        
        # Перевіряємо об'єм та коригуємо
        test_volume = pear_volume(height, top_radius, bottom_radius)
        if test_volume > 0:
            scale = (volume / test_volume) ** (1/3)
            height = height * scale
            top_radius = top_radius * scale
            bottom_radius = bottom_radius * scale
        
        return (height, top_radius, bottom_radius)
    else:
        # Не задано жодного параметра, використовуємо співвідношення
        # Для груші: height = 2.5 * top_radius, bottom_radius = top_radius / 2
        # Наближено: V ≈ 0.8 * π * top_radius^3 (для типової груші)
        top_radius = (volume / (0.8 * math.pi)) ** (1/3)
        height = 2.5 * top_radius
        bottom_radius = top_radius / 2
        
        return (height, top_radius, bottom_radius)


def cigar_volume(length: float, radius: float) -> float:
    """
    Об'єм сигароподібної форми
    
    Сигара моделюється як циліндр з двома півсферичними кінцями.
    
    Args:
        length: Загальна довжина сигари (м)
        radius: Радіус сигари (м)
    
    Returns:
        Об'єм сигари (м³)
    """
    if length <= 0 or radius <= 0:
        return 0.0
    
    # Довжина циліндричної частини
    cylinder_length = length - 2 * radius
    
    if cylinder_length < 0:
        # Якщо довжина менша за 2*радіус, то це просто сфера
        return (4/3) * math.pi * radius**3
    
    # Об'єм циліндричної частини
    V_cylinder = math.pi * radius**2 * cylinder_length
    
    # Об'єм двох півсфер (разом = одна сфера)
    V_spheres = (4/3) * math.pi * radius**3
    
    return V_cylinder + V_spheres


def cigar_surface_area(length: float, radius: float) -> float:
    """
    Площа поверхні сигароподібної форми
    
    Args:
        length: Загальна довжина сигари (м)
        radius: Радіус сигари (м)
    
    Returns:
        Площа поверхні сигари (м²)
    """
    if length <= 0 or radius <= 0:
        return 0.0
    
    # Довжина циліндричної частини
    cylinder_length = length - 2 * radius
    
    if cylinder_length < 0:
        # Якщо довжина менша за 2*радіус, то це просто сфера
        return 4 * math.pi * radius**2
    
    # Бічна поверхня циліндра
    S_cylinder = 2 * math.pi * radius * cylinder_length
    
    # Площа поверхні двох півсфер (разом = площа сфери)
    S_spheres = 4 * math.pi * radius**2
    
    return S_cylinder + S_spheres


def cigar_dimensions_from_volume(volume: float, length: float = None, radius: float = None) -> tuple:
    """
    Розраховує розміри сигари за об'ємом
    
    Args:
        volume: Об'єм сигари (м³)
        length: Якщо задано, розраховується radius
        radius: Якщо задано, розраховується length
    
    Returns:
        (length, radius) в метрах
    """
    if volume <= 0:
        return (0.0, 0.0)
    
    # Підраховуємо скільки параметрів задано
    given = sum(1 for x in [length, radius] if x is not None and x > 0)
    
    if given == 2:
        # Всі параметри задані
        return (length, radius)
    elif given == 1:
        # Задано один параметр
        if length is not None and length > 0:
            # Потрібно розрахувати radius
            # Використовуємо співвідношення: radius = length / 5 (типова сигара)
            radius = length / 5
            # Перевіряємо об'єм та коригуємо
            test_volume = cigar_volume(length, radius)
            if test_volume > 0:
                # Використовуємо ітераційний підхід для точного розрахунку
                # V = π*R²*(L - 2*R) + (4/3)*π*R³
                # Для заданого L, це кубічне рівняння відносно R
                # Для спрощення, використаємо наближення через масштабування
                scale = (volume / test_volume) ** (1/3)
                radius = radius * scale
        elif radius is not None and radius > 0:
            # Потрібно розрахувати length
            # Використовуємо співвідношення: length = 5 * radius (типова сигара)
            length = 5 * radius
            # Перевіряємо об'єм та коригуємо
            test_volume = cigar_volume(length, radius)
            if test_volume > 0:
                # V = π*R²*(L - 2*R) + (4/3)*π*R³
                # L = (V - (4/3)*π*R³) / (π*R²) + 2*R
                sphere_volume = (4/3) * math.pi * radius**3
                cylinder_volume = volume - sphere_volume
                if cylinder_volume > 0:
                    cylinder_length = cylinder_volume / (math.pi * radius**2)
                    length = cylinder_length + 2 * radius
                else:
                    # Якщо об'єм менший за об'єм сфери, то це просто сфера
                    length = 2 * radius
        else:
            return (0.0, 0.0)
        
        return (length, radius)
    else:
        # Не задано жодного параметра, використовуємо співвідношення
        # Для сигари: length = 5 * radius
        # V = π*R²*(5*R - 2*R) + (4/3)*π*R³ = π*R²*3*R + (4/3)*π*R³ = 3*π*R³ + (4/3)*π*R³ = (13/3)*π*R³
        radius = (3 * volume / (13 * math.pi)) ** (1/3)
        length = 5 * radius
        
        return (length, radius)


def pillow_dimensions_from_volume(volume: float, length: float = None, width: float = None) -> tuple:
    """
    Розраховує розміри подушки за об'ємом
    
    Подушка складається з двох прямокутних сегментів однакового розміру.
    Товщина (відстань між панелями) розраховується з об'єму: thickness = volume / (length × width)
    
    Args:
        volume: Об'єм подушки (м³)
        length: Якщо задано, розраховується width або використовується співвідношення
        width: Якщо задано, розраховується length або використовується співвідношення
    
    Returns:
        (length, width, thickness) в метрах, де thickness розраховується з об'єму
    """
    if volume <= 0:
        return (0.0, 0.0, 0.0)
    
    # Підраховуємо скільки параметрів задано
    given = sum(1 for x in [length, width] if x is not None and x > 0)
    
    if given == 2:
        # Якщо задано обидва параметри, розраховуємо товщину
        if length > 0 and width > 0:
            thickness = volume / (length * width)
            return (length, width, thickness)
        return (length or 0.0, width or 0.0, 0.0)
    elif given == 1:
        # Якщо задано один параметр, використовуємо співвідношення 3:2 (length:width)
        if length is not None and length > 0:
            width = length * 2 / 3
        elif width is not None and width > 0:
            length = width * 3 / 2
        else:
            return (0.0, 0.0, 0.0)
        
        # Розраховуємо товщину з об'єму
        if length > 0 and width > 0:
            thickness = volume / (length * width)
            return (length, width, thickness)
        return (length or 0.0, width or 0.0, 0.0)
    else:
        # Якщо не задано жодного параметра, використовуємо співвідношення 3:2
        # V = L*W*H, якщо L:W = 3:2, то L = 3W/2, V = (3W/2)*W*H = (3W²H)/2
        # Для зручності приймаємо H = W/2 (товщина = половині ширини)
        # Тоді V = (3W² * W/2)/2 = 3W³/4, W = (4V/3)^(1/3)
        width = (4 * volume / 3) ** (1 / 3)
        length = width * 3 / 2
        thickness = volume / (length * width)
        return (length, width, thickness)


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

