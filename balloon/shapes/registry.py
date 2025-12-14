"""
Shape Registry - Single Source of Truth для всіх форм

Кожна форма реєструється з:
- shape_code: внутрішній код
- parameter schema: Pydantic модель для валідації
- profile(z) → r: функція профілю
- volume(): функція об'єму
- area(): функція площі
- pattern_generator: функція генерації розкрою
- mesh_generator: функція генерації 3D mesh

Це усуває всі `if shape == ...` логіки поза реєстром.
"""

from typing import Dict, Any, Callable, Optional, Type
from dataclasses import dataclass
from pydantic import BaseModel, Field

from balloon.shapes.profile import ShapeProfile, get_shape_profile
from balloon.shapes.sphere import sphere_volume, sphere_surface_area, sphere_radius_from_volume
from balloon.shapes.pillow import pillow_volume, pillow_surface_area, pillow_dimensions_from_volume
from balloon.shapes.pear import pear_volume, pear_surface_area, pear_dimensions_from_volume
from balloon.shapes.cigar import cigar_volume, cigar_surface_area, cigar_dimensions_from_volume


# ============================================================================
# Pydantic моделі для параметрів форм
# ============================================================================

class SphereParams(BaseModel):
    """Параметри сфери"""
    radius: float = Field(gt=0, description="Радіус сфери (м)")


class PillowParams(BaseModel):
    """Параметри подушки"""
    pillow_len: float = Field(gt=0, description="Довжина (м)")
    pillow_wid: float = Field(gt=0, description="Ширина (м)")
    thickness: Optional[float] = Field(None, gt=0, description="Товщина (м)")


class PearParams(BaseModel):
    """Параметри груші"""
    pear_height: float = Field(gt=0, description="Висота (м)")
    pear_top_radius: float = Field(gt=0, description="Верхній радіус (м)")
    pear_bottom_radius: float = Field(gt=0, description="Нижній радіус (м)")


class CigarParams(BaseModel):
    """Параметри сигари"""
    cigar_length: float = Field(gt=0, description="Довжина (м)")
    cigar_radius: float = Field(gt=0, description="Радіус (м)")


# ============================================================================
# Shape Registry Entry
# ============================================================================

@dataclass
class ShapeRegistryEntry:
    """Запис у реєстрі форми"""
    shape_code: str
    display_name: str
    param_model: Type[BaseModel]
    profile_func: Callable[[Dict[str, Any]], Optional[ShapeProfile]]
    volume_func: Callable[[Dict[str, Any]], float]
    area_func: Callable[[Dict[str, Any]], float]
    dimensions_from_volume_func: Optional[Callable[[float, Dict[str, Any]], Dict[str, Any]]] = None
    description: str = ""


# ============================================================================
# Profile Functions
# ============================================================================

def _get_sphere_profile(params: Dict[str, Any]) -> Optional[ShapeProfile]:
    """Створює профіль сфери"""
    from balloon.shapes.profile import create_sphere_profile
    radius = params.get('radius', 1.0)
    return create_sphere_profile(radius)


def _get_pillow_profile(params: Dict[str, Any]) -> Optional[ShapeProfile]:
    """Створює профіль подушки"""
    from balloon.shapes.profile import create_pillow_profile
    length = params.get('pillow_len', 3.0)
    width = params.get('pillow_wid', 2.0)
    thickness = params.get('thickness', 1.0)
    return create_pillow_profile(length, width, thickness)


def _get_pear_profile(params: Dict[str, Any]) -> Optional[ShapeProfile]:
    """Створює профіль груші"""
    from balloon.shapes.profile import create_pear_profile
    height = params.get('pear_height', 3.0)
    top_radius = params.get('pear_top_radius', 1.2)
    bottom_radius = params.get('pear_bottom_radius', 0.6)
    return create_pear_profile(height, top_radius, bottom_radius)


def _get_cigar_profile(params: Dict[str, Any]) -> Optional[ShapeProfile]:
    """Створює профіль сигари"""
    from balloon.shapes.profile import create_cigar_profile
    length = params.get('cigar_length', 5.0)
    radius = params.get('cigar_radius', 1.0)
    return create_cigar_profile(length, radius)


# ============================================================================
# Wrapper Functions для volume/area з параметрами
# ============================================================================

def _sphere_volume_wrapper(params: Dict[str, Any]) -> float:
    """Обгортка для sphere_volume"""
    radius = params.get('radius', 1.0)
    return sphere_volume(radius)


def _sphere_area_wrapper(params: Dict[str, Any]) -> float:
    """Обгортка для sphere_surface_area"""
    radius = params.get('radius', 1.0)
    return sphere_surface_area(radius)


def _pillow_volume_wrapper(params: Dict[str, Any]) -> float:
    """Обгортка для pillow_volume"""
    length = params.get('pillow_len', 3.0)
    width = params.get('pillow_wid', 2.0)
    thickness = params.get('thickness', 1.0)
    return pillow_volume(length, width, thickness)


def _pillow_area_wrapper(params: Dict[str, Any]) -> float:
    """Обгортка для pillow_surface_area"""
    length = params.get('pillow_len', 3.0)
    width = params.get('pillow_wid', 2.0)
    thickness = params.get('thickness', 1.0)
    return pillow_surface_area(length, width, thickness)


def _pear_volume_wrapper(params: Dict[str, Any]) -> float:
    """Обгортка для pear_volume"""
    height = params.get('pear_height', 3.0)
    top_radius = params.get('pear_top_radius', 1.2)
    bottom_radius = params.get('pear_bottom_radius', 0.6)
    return pear_volume(height, top_radius, bottom_radius)


def _pear_area_wrapper(params: Dict[str, Any]) -> float:
    """Обгортка для pear_surface_area"""
    height = params.get('pear_height', 3.0)
    top_radius = params.get('pear_top_radius', 1.2)
    bottom_radius = params.get('pear_bottom_radius', 0.6)
    return pear_surface_area(height, top_radius, bottom_radius)


def _cigar_volume_wrapper(params: Dict[str, Any]) -> float:
    """Обгортка для cigar_volume"""
    length = params.get('cigar_length', 5.0)
    radius = params.get('cigar_radius', 1.0)
    return cigar_volume(length, radius)


def _cigar_area_wrapper(params: Dict[str, Any]) -> float:
    """Обгортка для cigar_surface_area"""
    length = params.get('cigar_length', 5.0)
    radius = params.get('cigar_radius', 1.0)
    return cigar_surface_area(length, radius)


# ============================================================================
# Shape Registry
# ============================================================================

SHAPE_REGISTRY: Dict[str, ShapeRegistryEntry] = {
    "sphere": ShapeRegistryEntry(
        shape_code="sphere",
        display_name="Сфера",
        param_model=SphereParams,
        profile_func=_get_sphere_profile,
        volume_func=_sphere_volume_wrapper,
        area_func=_sphere_area_wrapper,
        dimensions_from_volume_func=lambda vol, params: {"radius": sphere_radius_from_volume(vol)},
        description="Класична сферична форма"
    ),
    "pillow": ShapeRegistryEntry(
        shape_code="pillow",
        display_name="Подушка/мішок",
        param_model=PillowParams,
        profile_func=_get_pillow_profile,
        volume_func=_pillow_volume_wrapper,
        area_func=_pillow_area_wrapper,
        dimensions_from_volume_func=lambda vol, params: dict(zip(
            ['pillow_len', 'pillow_wid', 'thickness'],
            pillow_dimensions_from_volume(
                vol,
                length=params.get('pillow_len'),
                width=params.get('pillow_wid')
            )
        )),
        description="Еліпсоїдна форма з параметрами довжини та ширини"
    ),
    "pear": ShapeRegistryEntry(
        shape_code="pear",
        display_name="Груша",
        param_model=PearParams,
        profile_func=_get_pear_profile,
        volume_func=_pear_volume_wrapper,
        area_func=_pear_area_wrapper,
        dimensions_from_volume_func=lambda vol, params: dict(zip(
            ['pear_height', 'pear_top_radius', 'pear_bottom_radius'],
            pear_dimensions_from_volume(
                vol,
                height=params.get('pear_height'),
                top_radius=params.get('pear_top_radius'),
                bottom_radius=params.get('pear_bottom_radius')
            )
        )),
        description="Конічна форма з різними радіусами верхньої та нижньої частини"
    ),
    "cigar": ShapeRegistryEntry(
        shape_code="cigar",
        display_name="Сигара",
        param_model=CigarParams,
        profile_func=_get_cigar_profile,
        volume_func=_cigar_volume_wrapper,
        area_func=_cigar_area_wrapper,
        dimensions_from_volume_func=lambda vol, params: dict(zip(
            ['cigar_length', 'cigar_radius'],
            cigar_dimensions_from_volume(
                vol,
                length=params.get('cigar_length'),
                radius=params.get('cigar_radius')
            )
        )),
        description="Циліндрична форма з параметрами довжини та радіуса"
    ),
}


# ============================================================================
# Public API
# ============================================================================

def get_shape_entry(shape_code: str) -> Optional[ShapeRegistryEntry]:
    """Отримує запис форми з реєстру"""
    return SHAPE_REGISTRY.get(shape_code)


def get_all_shape_codes() -> list[str]:
    """Повертає список всіх кодів форм"""
    return list(SHAPE_REGISTRY.keys())


def get_all_display_names() -> list[str]:
    """Повертає список всіх назв для відображення"""
    return [entry.display_name for entry in SHAPE_REGISTRY.values()]


def get_shape_code_from_display(display_name: str) -> Optional[str]:
    """Отримує код форми за назвою для відображення"""
    for code, entry in SHAPE_REGISTRY.items():
        if entry.display_name == display_name:
            return code
    return None


def validate_shape_params(shape_code: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Валідує параметри форми через Pydantic
    
    Returns:
        Валідовані параметри як словник
    """
    entry = get_shape_entry(shape_code)
    if entry is None:
        raise ValueError(f"Невідома форма: {shape_code}")
    
    # Створюємо Pydantic модель з параметрів
    validated = entry.param_model(**params)
    return validated.model_dump()


def get_shape_profile_from_registry(shape_code: str, params: Dict[str, Any]) -> Optional[ShapeProfile]:
    """Отримує профіль форми через реєстр"""
    entry = get_shape_entry(shape_code)
    if entry is None:
        return None
    return entry.profile_func(params)


def get_shape_volume(shape_code: str, params: Dict[str, Any]) -> float:
    """Отримує об'єм форми через реєстр"""
    entry = get_shape_entry(shape_code)
    if entry is None:
        raise ValueError(f"Невідома форма: {shape_code}")
    return entry.volume_func(params)


def get_shape_area(shape_code: str, params: Dict[str, Any]) -> float:
    """Отримує площу форми через реєстр"""
    entry = get_shape_entry(shape_code)
    if entry is None:
        raise ValueError(f"Невідома форма: {shape_code}")
    return entry.area_func(params)


def get_shape_dimensions_from_volume(shape_code: str, volume: float, params: Dict[str, Any]) -> Dict[str, Any]:
    """Отримує розміри форми з об'єму через реєстр"""
    entry = get_shape_entry(shape_code)
    if entry is None:
        raise ValueError(f"Невідома форма: {shape_code}")
    
    if entry.dimensions_from_volume_func is None:
        raise ValueError(f"Форма {shape_code} не підтримує розрахунок розмірів з об'єму")
    
    return entry.dimensions_from_volume_func(volume, params)

