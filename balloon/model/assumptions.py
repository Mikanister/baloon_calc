"""
Explicit Physical Assumptions

Цей модуль документує всі фізичні припущення, моделі та ігноровані ефекти,
що використовуються в розрахунках аеростатів.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


class AssumptionCategory(Enum):
    """Категорії припущень"""
    ATMOSPHERIC = "atmospheric"
    GAS = "gas"
    MATERIAL = "material"
    GEOMETRIC = "geometric"
    THERMAL = "thermal"
    MECHANICAL = "mechanical"
    IGNORED = "ignored"


@dataclass
class PhysicalAssumption:
    """
    Фізичне припущення або модель
    
    Attributes:
        category: Категорія припущення
        name: Назва припущення
        description: Детальний опис
        model: Використовувана модель/формула
        limitations: Обмеження та умови застосування
        references: Посилання на джерела (опціонально)
    """
    category: AssumptionCategory
    name: str
    description: str
    model: str
    limitations: str = ""
    references: List[str] = field(default_factory=list)


# ============================================================================
# АТМОСФЕРНА МОДЕЛЬ
# ============================================================================

ATMOSPHERIC_ASSUMPTIONS = [
    PhysicalAssumption(
        category=AssumptionCategory.ATMOSPHERIC,
        name="International Standard Atmosphere (ISA)",
        description=(
            "Використовується стандартна атмосферна модель ISA з лінійним градієнтом температури. "
            "Температура знижується лінійно з висотою: T(h) = T_sea - LAPSE_RATE × h, "
            "де LAPSE_RATE = 0.0065 K/m."
        ),
        model=(
            "T(h) = T_sea - LAPSE_RATE × h\n"
            "P(h) = P_sea × (T(h)/T_sea)^(g/(R×LAPSE_RATE))\n"
            "ρ(h) = P(h) / (R × T(h))"
        ),
        limitations=(
            "Модель справедлива до висоти ~11 км (тропосфера). "
            "Вище цієї висоти температура стає постійною (стратосфера). "
            "Не враховує місцеві кліматичні умови, сезонні зміни, погодні умови."
        ),
        references=[
            "International Standard Atmosphere (ISO 2533:1975)",
            "US Standard Atmosphere (1976)"
        ]
    ),
    PhysicalAssumption(
        category=AssumptionCategory.ATMOSPHERIC,
        name="Постійний градієнт температури",
        description=(
            "Припускається лінійний градієнт температури 0.0065 K/m на всій висоті. "
            "Це справедливо для тропосфери, але не для стратосфери."
        ),
        model="LAPSE_RATE = 0.0065 K/m (постійний)",
        limitations="Не враховує зміну градієнта в стратосфері та інверсії температури."
    ),
]

# ============================================================================
# МОДЕЛЬ ГАЗУ
# ============================================================================

GAS_ASSUMPTIONS = [
    PhysicalAssumption(
        category=AssumptionCategory.GAS,
        name="Ідеальний газовий закон",
        description=(
            "Всі гази (гелій, водень, повітря) моделюються як ідеальні гази. "
            "Використовується рівняння стану: PV = nRT або ρ = P/(R_specific × T)."
        ),
        model="ρ = P / (R_specific × T)",
        limitations=(
            "Ідеальний газовий закон справедливий при низьких тисках та високих температурах. "
            "Може давати помилки при високих тисках (>10 атм) або низьких температурах. "
            "Не враховує міжмолекулярні взаємодії."
        ),
        references=["Ideal Gas Law (Clapeyron equation)"]
    ),
    PhysicalAssumption(
        category=AssumptionCategory.GAS,
        name="Постійна температура газу",
        description=(
            "Температура газу всередині аеростата вважається постійною та рівною заданій "
            "inside_temp. Не враховуються температурні градієнти всередині оболонки."
        ),
        model="T_gas = inside_temp (постійна)",
        limitations=(
            "В реальності температура газу може змінюватися через: "
            "сонячне нагрівання, радіаційне охолодження, конвекцію, контакт з оболонкою. "
            "Температурні градієнти можуть впливати на розподіл тиску та форму."
        )
    ),
    PhysicalAssumption(
        category=AssumptionCategory.GAS,
        name="Рівновага тисків",
        description=(
            "Припускається, що тиск газу всередині дорівнює зовнішньому тиску (нульова "
            "різниця тисків для підйомної сили). Для розрахунку напруги використовується "
            "невелика різниця тисків."
        ),
        model="P_inside ≈ P_outside (для підйомної сили)",
        limitations=(
            "В реальності може бути невелика різниця тисків через: "
            "деформацію оболонки, швидкість підйому, вітрові навантаження."
        )
    ),
]

# ============================================================================
# МОДЕЛЬ МАТЕРІАЛІВ
# ============================================================================

MATERIAL_ASSUMPTIONS = [
    PhysicalAssumption(
        category=AssumptionCategory.MATERIAL,
        name="Модель проникності газу",
        description=(
            "Втрати газу через оболонку моделюються через закон Фіка дифузії: "
            "Q = permeability × A × ΔP × t / thickness. "
            "Проникність залежить від матеріалу та типу газу."
        ),
        model="Q = (permeability × A × ΔP × t) / thickness",
        limitations=(
            "Модель спрощена та не враховує: "
            "залежність проникності від температури, "
            "неоднорідність матеріалу, "
            "мікротріщини та дефекти, "
            "старіння матеріалу."
        ),
        references=["Fick's law of diffusion"]
    ),
    PhysicalAssumption(
        category=AssumptionCategory.MATERIAL,
        name="Однорідність матеріалу",
        description=(
            "Матеріал оболонки вважається однорідним з постійною щільністю, "
            "товщиною та проникністю по всій поверхні."
        ),
        model="ρ, t, permeability = const (по всій поверхні)",
        limitations=(
            "Не враховує: місцеві зміни товщини, шви та з'єднання, "
            "підсилення в критичних місцях, зношування."
        )
    ),
]

# ============================================================================
# ГЕОМЕТРИЧНІ ПРИПУЩЕННЯ
# ============================================================================

GEOMETRIC_ASSUMPTIONS = [
    PhysicalAssumption(
        category=AssumptionCategory.GEOMETRIC,
        name="Ідеальна форма",
        description=(
            "Аеростат має ідеальну геометричну форму (сфера, груша, сигара, подушка) "
            "без деформацій. Форма не змінюється під дією тиску або навантаження."
        ),
        model="Форма = математична модель (без деформацій)",
        limitations=(
            "В реальності форма може деформуватися через: "
            "тиск газу, вітрові навантаження, навантаження, "
            "неоднорідність матеріалу, температурні ефекти."
        )
    ),
    PhysicalAssumption(
        category=AssumptionCategory.GEOMETRIC,
        name="Поверхня обертання",
        description=(
            "Для сфери, груші та сигари використовується модель поверхні обертання "
            "з профілем r(z). Це спрощує розрахунки об'єму, площі та викрійок."
        ),
        model="r = f(z) - профіль поверхні обертання",
        limitations=(
            "Припускає симетричність форми. Не враховує асиметрію, "
            "яка може виникати через навантаження або вітер."
        )
    ),
]

# ============================================================================
# ТЕРМІЧНІ ПРИПУЩЕННЯ
# ============================================================================

THERMAL_ASSUMPTIONS = [
    PhysicalAssumption(
        category=AssumptionCategory.THERMAL,
        name="Постійна температура всередині",
        description=(
            "Температура газу всередині аеростата вважається постійною та рівною "
            "заданій inside_temp протягом усього польоту."
        ),
        model="T_inside = inside_temp (постійна)",
        limitations=(
            "Не враховує: сонячне нагрівання протягом дня, "
            "радіаційне охолодження вночі, "
            "конвекційні потоки, "
            "теплообмін з оболонкою та навколишнім середовищем."
        )
    ),
    PhysicalAssumption(
        category=AssumptionCategory.THERMAL,
        name="Відсутність теплового розширення",
        description=(
            "Не враховується теплове розширення матеріалу оболонки та газу "
            "через зміни температури."
        ),
        model="Теплове розширення = 0",
        limitations=(
            "Теплове розширення може впливати на об'єм та форму, "
            "особливо при значних температурних змінах."
        )
    ),
]

# ============================================================================
# МЕХАНІЧНІ ПРИПУЩЕННЯ
# ============================================================================

MECHANICAL_ASSUMPTIONS = [
    PhysicalAssumption(
        category=AssumptionCategory.MECHANICAL,
        name="Рівномірний розподіл напруги",
        description=(
            "Напруга в оболонці розраховується за формулою тонкостінної сфери: "
            "σ = (P_inside - P_outside) × R / (2 × thickness). "
            "Припускається рівномірний розподіл напруги по всій поверхні."
        ),
        model="σ = (ΔP × R) / (2 × t) (тонкостінна сфера)",
        limitations=(
            "Формула справедлива для сферичних форм. "
            "Для інших форм (груша, сигара) це наближення. "
            "Не враховує концентрацію напруги біля швів, підсилень, "
            "місць кріплення навантаження."
        ),
        references=["Thin-walled pressure vessel theory"]
    ),
    PhysicalAssumption(
        category=AssumptionCategory.MECHANICAL,
        name="Пружна деформація",
        description=(
            "Матеріал оболонки вважається пружним (лінійна залежність напруга-деформація) "
            "до межі текучості. Не враховується пластична деформація та повзучість."
        ),
        model="σ = E × ε (пружна деформація)",
        limitations=(
            "При тривалих навантаженнях може виникати повзучість. "
            "При високих напругах може бути пластична деформація."
        )
    ),
]

# ============================================================================
# ІГНОРОВАНІ ЕФЕКТИ
# ============================================================================

IGNORED_EFFECTS = [
    PhysicalAssumption(
        category=AssumptionCategory.IGNORED,
        name="Вітрові навантаження",
        description=(
            "Вітрові навантаження та аеродинамічний опір не враховуються. "
            "Не розраховується сила опору, нестабільність форми під дією вітру."
        ),
        model="F_drag = 0",
        limitations=(
            "Вітер може значно впливати на: "
            "форму аеростата, підйомну силу, стабільність, "
            "напругу в оболонці, швидкість підйому/спуску."
        )
    ),
    PhysicalAssumption(
        category=AssumptionCategory.IGNORED,
        name="Динамічні ефекти",
        description=(
            "Всі розрахунки статичні. Не враховуються: "
            "інерція при підйомі/спуску, коливання, резонанс, "
            "динамічні навантаження."
        ),
        model="Динаміка = 0 (статичний розрахунок)",
        limitations=(
            "Динамічні ефекти можуть бути важливими при: "
            "швидких змінах висоти, сильних вітрах, "
            "коливаннях навантаження."
        )
    ),
    PhysicalAssumption(
        category=AssumptionCategory.IGNORED,
        name="Радіаційні ефекти",
        description=(
            "Не враховується сонячна радіація, інфрачервоне випромінювання, "
            "теплообмін через випромінювання."
        ),
        model="Радіація = 0",
        limitations=(
            "Сонячна радіація може значно нагрівати оболонку та газ, "
            "особливо в денний час. Це впливає на підйомну силу та форму."
        )
    ),
    PhysicalAssumption(
        category=AssumptionCategory.IGNORED,
        name="Вологість та конденсація",
        description=(
            "Не враховується вміст вологи в повітрі, конденсація води на оболонці, "
            "вплив вологи на масу та теплопровідність."
        ),
        model="Вологість = 0",
        limitations=(
            "Конденсація води може додавати масу, "
            "впливати на теплопровідність оболонки."
        )
    ),
    PhysicalAssumption(
        category=AssumptionCategory.IGNORED,
        name="Неідеальність газу",
        description=(
            "Гази моделюються як ідеальні. Не враховуються: "
            "відхилення від ідеального газу, "
            "взаємодія між молекулами, "
            "ван-дер-Ваальсові сили."
        ),
        model="Газ = ідеальний",
        limitations=(
            "При високих тисках (>10 атм) або низьких температурах "
            "відхилення від ідеального газу можуть бути значними."
        )
    ),
]

# ============================================================================
# ЗБІРКА ВСІХ ПРИПУЩЕНЬ
# ============================================================================

ALL_ASSUMPTIONS = (
    ATMOSPHERIC_ASSUMPTIONS +
    GAS_ASSUMPTIONS +
    MATERIAL_ASSUMPTIONS +
    GEOMETRIC_ASSUMPTIONS +
    THERMAL_ASSUMPTIONS +
    MECHANICAL_ASSUMPTIONS +
    IGNORED_EFFECTS
)


def get_assumptions_by_category(category: AssumptionCategory) -> List[PhysicalAssumption]:
    """Повертає всі припущення заданої категорії"""
    return [a for a in ALL_ASSUMPTIONS if a.category == category]


def get_all_assumptions() -> List[PhysicalAssumption]:
    """Повертає всі припущення"""
    return list(ALL_ASSUMPTIONS)


def get_assumptions_dict() -> Dict[str, List[Dict[str, Any]]]:
    """
    Повертає словник з усіма припущеннями, згрупованими за категоріями
    
    Returns:
        Словник {category_name: [assumption_dict, ...]}
    """
    result = {}
    for category in AssumptionCategory:
        assumptions = get_assumptions_by_category(category)
        result[category.value] = [
            {
                'name': a.name,
                'description': a.description,
                'model': a.model,
                'limitations': a.limitations,
                'references': a.references
            }
            for a in assumptions
        ]
    return result


def get_assumptions_table_data() -> List[Dict[str, Any]]:
    """
    Повертає дані для таблиці відображення припущень
    
    Returns:
        Список словників з даними для таблиці
    """
    table_data = []
    for assumption in ALL_ASSUMPTIONS:
        table_data.append({
            'Категорія': assumption.category.value,
            'Назва': assumption.name,
            'Опис': assumption.description,
            'Модель': assumption.model,
            'Обмеження': assumption.limitations,
            'Джерела': ', '.join(assumption.references) if assumption.references else ''
        })
    return table_data

