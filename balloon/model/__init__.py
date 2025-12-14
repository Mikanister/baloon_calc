"""
Ядро моделі калькулятора аеростатів - чиста логіка без GUI
"""

from balloon.model.atmosphere import air_density_at_height
from balloon.model.gas import (
    calculate_gas_density_at_altitude,
    calculate_hot_air_density
)
from balloon.model.materials import (
    get_material_density,
    get_material_stress_limit,
    get_material_permeability,
    calc_stress
)
from balloon.model.shapes import (
    ShapeGeometry,
    get_shape_volume,
    get_shape_surface_area,
    get_shape_dimensions_from_volume
)
from balloon.model.solve import (
    solve_volume_to_payload,
    solve_payload_to_volume,
    calculate_balloon_state
)
from balloon.model.assumptions import (
    get_all_assumptions,
    get_assumptions_by_category,
    get_assumptions_dict,
    get_assumptions_table_data,
    AssumptionCategory,
    PhysicalAssumption
)
from balloon.model.mass_budget import (
    MassBudget,
    LiftBudget,
    calculate_mass_budget,
    calculate_lift_budget
)

__all__ = [
    'air_density_at_height',
    'calculate_gas_density_at_altitude',
    'calculate_hot_air_density',
    'get_material_density',
    'get_material_stress_limit',
    'get_material_permeability',
    'calc_stress',
    'ShapeGeometry',
    'get_shape_volume',
    'get_shape_surface_area',
    'get_shape_dimensions_from_volume',
    'solve_volume_to_payload',
    'solve_payload_to_volume',
    'calculate_balloon_state',
    # Assumptions
    'get_all_assumptions',
    'get_assumptions_by_category',
    'get_assumptions_dict',
    'get_assumptions_table_data',
    'AssumptionCategory',
    'PhysicalAssumption',
    # Mass & Lift Budget
    'MassBudget',
    'LiftBudget',
    'calculate_mass_budget',
    'calculate_lift_budget',
]

