"""
Модуль для аналізу аеростатів
"""

# Експортуємо функції з окремих модулів
try:
    from baloon.analysis.optimal_height import calculate_optimal_height
    from baloon.analysis.height_profile import calculate_height_profile
    from baloon.analysis.material_comparison import calculate_material_comparison
    from baloon.analysis.cost_analysis import calculate_cost_analysis
    from baloon.analysis.flight_time import calculate_max_flight_time
    from baloon.analysis.report import generate_report
    from baloon.analysis.base import _compute_lift_state
except ImportError:
    from analysis.optimal_height import calculate_optimal_height
    from analysis.height_profile import calculate_height_profile
    from analysis.material_comparison import calculate_material_comparison
    from analysis.cost_analysis import calculate_cost_analysis
    from analysis.flight_time import calculate_max_flight_time
    from analysis.report import generate_report
    from analysis.base import _compute_lift_state

__all__ = [
    'calculate_optimal_height',
    'calculate_height_profile',
    'calculate_material_comparison',
    'calculate_cost_analysis',
    'calculate_max_flight_time',
    'generate_report',
    '_compute_lift_state',
]

