"""
Модуль для оптимізації параметрів форми через SciPy
"""

from typing import Dict, Optional, Tuple, Literal
import numpy as np

try:
    from scipy.optimize import minimize, differential_evolution
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from baloon.shapes import (
        sphere_surface_area, pillow_surface_area,
        pear_surface_area, cigar_surface_area
    )
except ImportError:
    from shapes import (
        sphere_surface_area, pillow_surface_area,
        pear_surface_area, cigar_surface_area
    )


def optimize_shape_for_min_surface_area(
    shape_type: Literal["sphere", "pillow", "pear", "cigar"],
    target_volume: float,
    constraints: Optional[Dict] = None
) -> Dict[str, float]:
    """
    Оптимізує параметри форми для мінімальної площі поверхні при заданому об'ємі
    
    Args:
        shape_type: Тип форми
        target_volume: Цільовий об'єм (м³)
        constraints: Додаткові обмеження (наприклад, мінімальна/максимальна висота)
    
    Returns:
        Словник з оптимальними параметрами форми
    
    Raises:
        ImportError: Якщо SciPy не встановлено
        ValueError: Якщо форма не підтримується
    """
    if not SCIPY_AVAILABLE:
        raise ImportError("Для оптимізації потрібна бібліотека scipy. Встановіть: pip install scipy")
    
    if shape_type == "sphere":
        # Для сфери оптимальна форма - це сфера (мінімальна площа при заданому об'ємі)
        from baloon.shapes import sphere_radius_from_volume
        radius = sphere_radius_from_volume(target_volume)
        return {'radius': radius}
    
    elif shape_type == "pillow":
        return _optimize_pillow(target_volume, constraints)
    
    elif shape_type == "pear":
        return _optimize_pear(target_volume, constraints)
    
    elif shape_type == "cigar":
        return _optimize_cigar(target_volume, constraints)
    
    else:
        raise ValueError(f"Непідтримувана форма для оптимізації: {shape_type}")


def _optimize_pillow(target_volume: float, constraints: Optional[Dict] = None) -> Dict[str, float]:
    """Оптимізує параметри подушки для мінімальної площі поверхні"""
    constraints = constraints or {}
    
    # Обмеження
    min_length = constraints.get('min_length', 0.5)
    max_length = constraints.get('max_length', 20.0)
    min_width = constraints.get('min_width', 0.5)
    max_width = constraints.get('max_width', 20.0)
    aspect_ratio = constraints.get('aspect_ratio', None)  # length/width
    
    def objective(x):
        """Мінімізуємо площу поверхні"""
        length, width = x
        thickness = target_volume / (length * width)
        if thickness <= 0:
            return 1e10  # Велике значення для невалідних параметрів
        return pillow_surface_area(length, width, thickness)
    
    # Обмеження
    bounds = [(min_length, max_length), (min_width, max_width)]
    
    # Додаткові обмеження
    constraint_list = []
    
    # Обмеження на об'єм
    def volume_constraint(x):
        length, width = x
        thickness = target_volume / (length * width)
        return thickness - 0.01  # Мінімальна товщина
    
    constraint_list.append({'type': 'ineq', 'fun': volume_constraint})
    
    # Обмеження на співвідношення сторін
    if aspect_ratio:
        def aspect_constraint(x):
            length, width = x
            return aspect_ratio - (length / width) if width > 0 else 1e10
        
        constraint_list.append({'type': 'eq', 'fun': aspect_constraint})
    
    # Початкове наближення
    x0 = [np.sqrt(target_volume), np.sqrt(target_volume)]
    
    # Оптимізація
    result = minimize(
        objective,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraint_list,
        options={'maxiter': 1000}
    )
    
    if result.success:
        length, width = result.x
        thickness = target_volume / (length * width)
        return {
            'pillow_len': length,
            'pillow_wid': width,
            'thickness': thickness
        }
    else:
        # Fallback на квадратну форму
        side = np.cbrt(target_volume)
        return {
            'pillow_len': side,
            'pillow_wid': side,
            'thickness': side
        }


def _optimize_pear(target_volume: float, constraints: Optional[Dict] = None) -> Dict[str, float]:
    """Оптимізує параметри груші для мінімальної площі поверхні"""
    constraints = constraints or {}
    
    min_height = constraints.get('min_height', 0.5)
    max_height = constraints.get('max_height', 20.0)
    min_radius = constraints.get('min_radius', 0.1)
    max_radius = constraints.get('max_radius', 5.0)
    
    def objective(x):
        """Мінімізуємо площу поверхні"""
        height, top_radius, bottom_radius = x
        try:
            return pear_surface_area(height, top_radius, bottom_radius)
        except:
            return 1e10
    
    # Обмеження
    bounds = [
        (min_height, max_height),
        (min_radius, max_radius),
        (min_radius, max_radius)
    ]
    
    # Обмеження на об'єм
    def volume_constraint(x):
        height, top_radius, bottom_radius = x
        try:
            from baloon.shapes import pear_volume
            vol = pear_volume(height, top_radius, bottom_radius)
            return abs(vol - target_volume) / target_volume - 0.01  # Допустима похибка 1%
        except:
            return 1e10
    
    constraint_list = [{'type': 'ineq', 'fun': volume_constraint}]
    
    # Початкове наближення (сферична форма)
    from baloon.shapes import sphere_radius_from_volume
    radius = sphere_radius_from_volume(target_volume)
    x0 = [radius * 2, radius, radius * 0.5]
    
    # Оптимізація
    result = minimize(
        objective,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraint_list,
        options={'maxiter': 1000}
    )
    
    if result.success:
        height, top_radius, bottom_radius = result.x
        return {
            'pear_height': height,
            'pear_top_radius': top_radius,
            'pear_bottom_radius': bottom_radius
        }
    else:
        # Fallback
        return {
            'pear_height': radius * 2,
            'pear_top_radius': radius,
            'pear_bottom_radius': radius * 0.5
        }


def _optimize_cigar(target_volume: float, constraints: Optional[Dict] = None) -> Dict[str, float]:
    """Оптимізує параметри сигари для мінімальної площі поверхні"""
    constraints = constraints or {}
    
    min_length = constraints.get('min_length', 0.5)
    max_length = constraints.get('max_length', 30.0)
    min_radius = constraints.get('min_radius', 0.1)
    max_radius = constraints.get('max_radius', 5.0)
    
    def objective(x):
        """Мінімізуємо площу поверхні"""
        length, radius = x
        try:
            return cigar_surface_area(length, radius)
        except:
            return 1e10
    
    # Обмеження
    bounds = [
        (min_length, max_length),
        (min_radius, max_radius)
    ]
    
    # Обмеження на об'єм
    def volume_constraint(x):
        length, radius = x
        try:
            from baloon.shapes import cigar_volume
            vol = cigar_volume(length, radius)
            return abs(vol - target_volume) / target_volume - 0.01
        except:
            return 1e10
    
    constraint_list = [{'type': 'ineq', 'fun': volume_constraint}]
    
    # Початкове наближення
    from baloon.shapes import sphere_radius_from_volume
    radius_init = sphere_radius_from_volume(target_volume)
    x0 = [radius_init * 3, radius_init]
    
    # Оптимізація
    result = minimize(
        objective,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraint_list,
        options={'maxiter': 1000}
    )
    
    if result.success:
        length, radius = result.x
        return {
            'cigar_length': length,
            'cigar_radius': radius
        }
    else:
        # Fallback
        return {
            'cigar_length': radius_init * 3,
            'cigar_radius': radius_init
        }


def is_scipy_available() -> bool:
    """Перевіряє, чи доступний SciPy"""
    return SCIPY_AVAILABLE

