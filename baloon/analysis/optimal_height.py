"""
Розрахунок оптимальної висоти польоту
"""

from typing import Dict, Any

try:
    from baloon.analysis.base import _compute_lift_state
except ImportError:
    from analysis.base import _compute_lift_state


def calculate_optimal_height(gas_type: str, material: str, thickness_mm: float, 
                           gas_volume: float, ground_temp: float = 15, 
                           inside_temp: float = 100,
                           shape_type: str = "sphere",
                           shape_params: dict = None,
                           extra_mass: float = 0.0,
                           seam_factor: float = 1.0) -> Dict[str, Any]:
    """
    Розраховує оптимальну висоту польоту для максимального навантаження
    
    Використовує SciPy для оптимізації, якщо доступний, інакше - простий перебір.
    
    Args:
        gas_type: Тип газу
        material: Матеріал оболонки
        thickness_mm: Товщина оболонки (мкм)
        gas_volume: Об'єм газу (м³)
        ground_temp: Температура на землі (°C)
        inside_temp: Температура всередині (°C)
        shape_type: Форма кулі
        shape_params: Параметри форми
        extra_mass: Додаткова маса
        seam_factor: Коефіцієнт втрат через шви
    
    Returns:
        Словник з оптимальними параметрами
    """
    # Спробуємо використати SciPy для оптимізації
    try:
        from scipy.optimize import minimize_scalar
        SCIPY_AVAILABLE = True
    except ImportError:
        SCIPY_AVAILABLE = False
    
    if SCIPY_AVAILABLE:
        # Використовуємо SciPy для швидшої оптимізації
        def negative_payload(height):
            """Мінімізуємо негативне навантаження (максимізуємо навантаження)"""
            try:
                state = _compute_lift_state(
                    gas_type=gas_type,
                    material=material,
                    thickness_mm=thickness_mm,
                    gas_volume=gas_volume,
                    height=float(height),
                    ground_temp=ground_temp,
                    inside_temp=inside_temp,
                    shape_type=shape_type,
                    shape_params=shape_params,
                    extra_mass=extra_mass,
                    seam_factor=seam_factor,
                )
                # Повертаємо негативне значення для максимізації
                return -state.get('payload', 0)
            except Exception:
                return 1e10  # Велике значення для невалідних висот
        
        # Оптимізація в діапазоні 0-50 км
        result = minimize_scalar(
            negative_payload,
            bounds=(0, 50000),
            method='bounded',
            options={'maxiter': 1000}
        )
        
        if result.success:
            optimal_height = int(result.x)
            state = _compute_lift_state(
                gas_type=gas_type,
                material=material,
                thickness_mm=thickness_mm,
                gas_volume=gas_volume,
                height=optimal_height,
                ground_temp=ground_temp,
                inside_temp=inside_temp,
                shape_type=shape_type,
                shape_params=shape_params,
                extra_mass=extra_mass,
                seam_factor=seam_factor,
            )
            return {
                'optimal_height': optimal_height,
                'height': optimal_height,  # Для сумісності з тестами
                **state,
            }
    
    # Fallback на простий перебір
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
                shape_type=shape_type,
                shape_params=shape_params,
                extra_mass=extra_mass,
                seam_factor=seam_factor,
            )
            if state['net_lift_per_m3'] > 0 and state['payload'] > max_payload:
                max_payload = state['payload']
                optimal_params = {
                    'optimal_height': height,
                    'height': height,  # Для сумісності з тестами
                    **state,
                }
                    
        except Exception:
            continue
    
    return optimal_params

