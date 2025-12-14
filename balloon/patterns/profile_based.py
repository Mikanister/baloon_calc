"""
Генерація розкрою на основі профілів форм

Використовує ShapeProfile для узгодженості з 3D та розрахунками
"""

import math
import numpy as np
from typing import Dict, Any, List, Tuple
from balloon.shapes.profile import get_shape_profile, ShapeProfile

# Використовуємо scipy для покращення якості розкрою
try:
    from scipy import integrate
    from scipy.interpolate import UnivariateSpline, interp1d
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


def _adaptive_z_discretization(profile: ShapeProfile, z_min: float, z_max: float, num_points: int) -> List[float]:
    """
    Адаптивна дискретизація по Z: більше точок там, де похідна dr/dz велика
    
    Це забезпечує плавніший контур для всіх форм:
    - Груша: півсфера зверху
    - Сигара: півсфери зверху та знизу
    - Сфера: полюси (де радіус швидко змінюється)
    """
    # Спочатку створюємо рівномірну сітку для оцінки похідної
    uniform_z = [z_min + (z_max - z_min) * i / (num_points * 3) for i in range(num_points * 3 + 1)]
    
    # Обчислюємо похідну dr/dz для кожної точки
    derivatives = []
    for i in range(len(uniform_z) - 1):
        z1 = uniform_z[i]
        z2 = uniform_z[i + 1]
        r1 = profile.get_radius(z1)
        r2 = profile.get_radius(z2)
        dr_dz = abs((r2 - r1) / (z2 - z1)) if z2 != z1 else 0.0
        derivatives.append(dr_dz)
    
    # Нормалізуємо похідні (0..1)
    max_deriv = max(derivatives) if derivatives else 1.0
    if max_deriv == 0:
        # Якщо похідна всюди 0, використовуємо рівномірну дискретизацію
        return [z_min + (z_max - z_min) * i / num_points for i in range(num_points + 1)]
    
    normalized_derivs = [d / max_deriv for d in derivatives]
    
    # Розподіляємо точки пропорційно до похідної
    # Більше точок там, де похідна велика (особливо в півсфері)
    z_points = [z_min]
    total_weight = sum(1 + norm_deriv * 3 for norm_deriv in normalized_derivs)  # Збільшуємо вагу похідної
    
    points_remaining = num_points - 1  # Вже додали z_min
    
    for i in range(len(normalized_derivs)):
        if points_remaining <= 0:
            break
            
        z1 = uniform_z[i]
        z2 = uniform_z[i + 1]
        norm_deriv = normalized_derivs[i]
        
        # Кількість точок на цьому інтервалі пропорційна до похідної
        weight = 1 + norm_deriv * 3
        points_for_interval = max(1, min(points_remaining, int(num_points * weight / total_weight)))
        
        # Додаємо точки на цьому інтервалі
        for j in range(1, points_for_interval + 1):
            if points_remaining <= 0:
                break
            t = j / (points_for_interval + 1)
            z = z1 + (z2 - z1) * t
            if z > z_points[-1] and z < z_max:
                z_points.append(z)
                points_remaining -= 1
    
    # Додаємо останню точку
    if z_points[-1] < z_max:
        z_points.append(z_max)
    
    # Сортуємо та видаляємо дублікати
    z_points = sorted(set(z_points))
    
    # Якщо точок менше ніж потрібно, додаємо рівномірно
    if len(z_points) < num_points + 1:
        additional = num_points + 1 - len(z_points)
        for _ in range(additional):
            # Додаємо точки в проміжки з найбільшою відстанню
            max_gap = 0
            max_gap_idx = 0
            for j in range(len(z_points) - 1):
                gap = z_points[j + 1] - z_points[j]
                if gap > max_gap:
                    max_gap = gap
                    max_gap_idx = j
            if max_gap > 0:
                new_z = (z_points[max_gap_idx] + z_points[max_gap_idx + 1]) / 2
                z_points.append(new_z)
        z_points = sorted(set(z_points))
    
    return z_points


def _smooth_gore_contour(raw_points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Згладжує контур gores за допомогою scipy.interpolate
    
    Використовує UnivariateSpline для згладжування, зберігаючи початкові та кінцеві точки.
    Застосовується до всіх форм (sphere, pear, cigar) для покращення якості розкрою.
    """
    if not SCIPY_AVAILABLE or len(raw_points) < 4:
        return raw_points
    
    # Розділяємо на X та Y координати
    x_coords = np.array([p[0] for p in raw_points])
    y_coords = np.array([p[1] for p in raw_points])
    
    # Використовуємо UnivariateSpline для згладжування
    # s - параметр згладжування (менше = точніше, але менш згладжено)
    # k - степінь сплайну (3 = cubic)
    try:
        # Для X координат (ширина) - згладжування
        # Використовуємо y як параметр, оскільки він монотонно зростає
        if len(set(y_coords)) == len(y_coords):  # Перевіряємо, чи Y унікальні
            # Використовуємо адаптивний параметр s залежно від похідної
            # Більше згладжування там, де похідна велика (біля вершини)
            # Обчислюємо середню похідну для налаштування параметра
            dx_dy = np.abs(np.diff(x_coords) / np.diff(y_coords))
            avg_deriv = np.mean(dx_dy) if len(dx_dy) > 0 else 1.0
            
            # Параметр згладжування: менший для більш точного згладжування
            # Але адаптуємо до похідної
            s_param = len(raw_points) * 0.03 * (1 + avg_deriv * 0.5)
            spline_x = UnivariateSpline(y_coords, x_coords, s=s_param, k=3)
            x_smooth = spline_x(y_coords)
        else:
            # Якщо Y не унікальні, використовуємо індекс як параметр
            indices = np.array(range(len(raw_points)))
            s_param = len(raw_points) * 0.05
            spline_x = UnivariateSpline(indices, x_coords, s=s_param, k=3)
            x_smooth = spline_x(indices)
        
        # Переконуємося, що X не стає негативним
        x_smooth = np.maximum(x_smooth, 0.0)
        
        # Зберігаємо початкову та кінцеву точки точно
        x_smooth[0] = x_coords[0]
        x_smooth[-1] = x_coords[-1]
        
        # Об'єднуємо назад
        smoothed_points = [(float(x_smooth[i]), float(y_coords[i])) for i in range(len(raw_points))]
        
        return smoothed_points
    except Exception as e:
        # Якщо щось пішло не так, повертаємо оригінальні точки
        import logging
        logging.debug(f"Помилка згладжування контуру: {e}")
        return raw_points


def generate_gore_pattern_from_profile(
    profile: ShapeProfile,
    num_gores: int = 12,
    num_points: int = 50
) -> Dict[str, Any]:
    """
    Генерує патерн gores на основі профілю форми
    
    Використовує покращення для всіх форм:
    - Адаптивна дискретизація (більше точок там, де похідна велика)
    - scipy.integrate для точнішого обчислення меридіанної довжини
    - scipy.interpolate для згладжування контуру
    
    Args:
        profile: ShapeProfile об'єкт (для будь-якої форми: sphere, pear, cigar)
        num_gores: Кількість сегментів
        num_points: Кількість точок для апроксимації
    
    Returns:
        Словник з координатами точок та параметрами
    """
    if num_gores < 4:
        num_gores = 4
    if num_gores > 32:
        num_gores = 32
    
    z_min, z_max = profile.z_range
    
    # Адаптивна дискретизація: більше точок там, де похідна dr/dz велика
    # Це важливо для всіх форм, особливо:
    # - Півсфери в груші (швидка зміна радіуса)
    # - Півсфери в сигарі (верхня та нижня частини)
    # - Полюси сфери (де радіус швидко зменшується)
    z_points = _adaptive_z_discretization(profile, z_min, z_max, num_points)
    
    # Додаємо додаткові точки для плавності контуру, особливо біля вершини
    # де радіус швидко зменшується до 0
    if len(z_points) > 2:
        max_r = max(profile.get_radius(z) for z in z_points)
        threshold = max_r * 0.3  # Збільшуємо поріг
        
        # Проходимо всі точки з кінця до початку
        i = len(z_points) - 2
        while i >= 0:
            z = z_points[i]
            z_next = z_points[i + 1]
            gap = z_next - z
            r = profile.get_radius(z)
            r_next = profile.get_radius(z_next)
            
            # Додаємо проміжні точки якщо:
            # 1. Проміжок великий, АБО
            # 2. Радіус швидко зменшується (велика похідна), АБО
            # 3. Біля вершини (z близько до z_max)
            should_add = False
            if gap > (z_max - z_min) / num_points * 0.4:
                should_add = True
            elif r > 0 and r_next >= 0:
                dr_dz = abs((r_next - r) / gap) if gap > 0 else 0
                if dr_dz > max_r / (z_max - z_min) * 2:  # Велика похідна
                    should_add = True
            elif z_next > z_max * 0.9:  # Біля вершини
                should_add = True
            
            if should_add:
                # Додаємо більше проміжних точок для великих проміжків або біля вершини
                # Особливо багато точок біля вершини, де радіус швидко зменшується
                if z_next > z_max * 0.9:
                    # Біля вершини - додаємо більше точок
                    num_intermediate = min(10, max(6, int(gap / ((z_max - z_min) / num_points * 0.15))))
                else:
                    num_intermediate = min(6, max(4, int(gap / ((z_max - z_min) / num_points * 0.2))))
                
                for j in range(1, num_intermediate + 1):
                    new_z = z + gap * j / (num_intermediate + 1)
                    if new_z not in z_points and new_z < z_max:
                        z_points.append(new_z)
            i -= 1
        
        z_points = sorted(set(z_points))
    
    gore_points = []
    total_meridian_length = profile.get_total_meridian_length(num_points * 2)
    
    # Кут між сегментами
    theta_step = 2 * math.pi / num_gores
    
    for z in z_points:
        # Y-координата = довжина меридіану від початку
        y = profile.get_meridian_length(z, num_points * 2)
        
        # Радіус на цій висоті
        r = profile.get_radius(z)
        
        # Ширина сегмента на цій висоті = півдуга паралелі між меридіанами
        # Для кола радіуса r: half_width = r * (theta_step / 2)
        half_width = r * (theta_step / 2) if r > 0 else 0.0
        
        # Координата X (горизонтальна, від центру до краю) = півширина сегмента
        x = half_width
        
        gore_points.append((x, y))
    
    # Розраховуємо розміри
    max_width = max(x for x, y in gore_points) if gore_points else 0.0
    meridian_length = total_meridian_length
    # Геометрична висота форми (осьова координата)
    axis_height = z_max - z_min
    
    # Площа одного сегмента (приблизно через інтеграцію)
    # Площа gores = загальна площа поверхні / num_gores
    # Примітка: get_surface_area() вже враховує обертання, тому ділимо на num_gores
    total_surface_area = profile.get_surface_area(num_points * 2)
    gore_area = total_surface_area / num_gores
    
    return {
        'pattern_type': 'gore',
        'num_gores': num_gores,
        'points': gore_points,
        'max_width': max_width,
        'meridian_length': meridian_length,  # Довжина по меридіану (по шву)
        'axis_height': axis_height,  # Геометрична висота форми
        'gore_area': gore_area,
        'total_area': total_surface_area,
        'description': f'Викрійка: {num_gores} сегментів'
    }


def generate_pattern_from_shape_profile(
    shape_type: str,
    shape_params: dict,
    num_segments: int = 12,
    seam_allowance_mm: float = 10.0
) -> Dict[str, Any]:
    """
    Генерує патерн на основі профілю форми
    
    Args:
        shape_type: Тип форми ('sphere', 'pillow', 'pear', 'cigar')
        shape_params: Параметри форми
        num_segments: Кількість сегментів (для gores)
        seam_allowance_mm: Припуск на шов (мм)
    
    Returns:
        Словник з патерном
    """
    profile = get_shape_profile(shape_type, shape_params)
    
    if profile is None:
        raise ValueError(f"Форма '{shape_type}' не підтримується")
    
    # Для подушки - окрема логіка (не gores)
    if shape_type == 'pillow':
        # Подушка не використовує gores, повертаємо базовий патерн
        from balloon.patterns.pillow_pattern import calculate_pillow_pattern
        length = shape_params.get('pillow_len', 3.0)
        width = shape_params.get('pillow_wid', 2.0)
        thickness = shape_params.get('thickness', 1.0)
        pattern = calculate_pillow_pattern(length, width, thickness)
        if seam_allowance_mm > 0:
            from balloon.patterns.base import _add_seam_allowance_pillow
            # Unit conversion: GUI provides seam_allowance in millimeters (mm), model uses SI (meters)
            # Conversion: 1 mm = 0.001 m
            pattern = _add_seam_allowance_pillow(pattern, seam_allowance_mm / 1000.0)
        return pattern
    
    # Для інших форм - gores на основі профілю
    pattern = generate_gore_pattern_from_profile(profile, num_segments)
    
    # Додаємо припуск на шов (offset по нормалі до контуру)
    if seam_allowance_mm > 0:
        from balloon.patterns.base import _add_seam_allowance
        # Unit conversion: GUI provides seam_allowance in millimeters (mm), model uses SI (meters)
        # Conversion: 1 mm = 0.001 m
        pattern = _add_seam_allowance(pattern, seam_allowance_mm / 1000.0)
    
    # Додаємо notches (мітки суміщення) - позиції для міток
    pattern['notches'] = _calculate_notch_positions(pattern)
    
    # Додаємо специфічні параметри форми
    if shape_type == 'sphere':
        pattern['pattern_type'] = 'sphere_gore'
        pattern['radius'] = shape_params.get('radius', 1.0)
    elif shape_type == 'pear':
        pattern['pattern_type'] = 'pear_gore'
        pattern['height'] = shape_params.get('pear_height', 3.0)
        pattern['top_radius'] = shape_params.get('pear_top_radius', 1.2)
        pattern['bottom_radius'] = shape_params.get('pear_bottom_radius', 0.6)
    elif shape_type == 'cigar':
        pattern['pattern_type'] = 'cigar_gore'
        pattern['length'] = shape_params.get('cigar_length', 5.0)
        pattern['radius'] = shape_params.get('cigar_radius', 1.0)
    
    return pattern


def _calculate_notch_positions(pattern: Dict[str, Any]) -> List[float]:
    """
    Обчислює позиції для міток суміщення (notches) на панелі
    
    Args:
        pattern: Патерн викрійки
    
    Returns:
        Список позицій по Y (від 0 до meridian_length) для міток
    """
    meridian_length = pattern.get('meridian_length', 0.0)
    if meridian_length <= 0:
        return []
    
    # 4 мітки: на 10%, 30%, 50% (екватор), 70%, 90% висоти
    notch_positions = [0.1, 0.3, 0.5, 0.7, 0.9]
    return [pos * meridian_length for pos in notch_positions]

