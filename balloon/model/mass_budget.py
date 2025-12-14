"""
Mass & Lift Budget Breakdown

Структурований розрахунок бюджету маси та підйомної сили аеростата.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class MassComponent(Enum):
    """Компоненти маси"""
    GAS = "gas_mass"
    ENVELOPE = "envelope_mass"
    SEAMS = "seams_mass"
    REINFORCEMENTS = "reinforcements_mass"
    PAYLOAD = "payload_mass"
    SAFETY_MARGIN = "safety_margin_mass"
    EXTRA = "extra_mass"


@dataclass
class MassBudget:
    """
    Бюджет маси аеростата
    
    Attributes:
        gas_mass: Маса газу (кг)
        envelope_mass: Маса оболонки (кг)
        seams_mass: Маса швів (кг) - додаткова маса через шви
        reinforcements_mass: Маса підсилень (кг) - додаткові елементи міцності
        payload_mass: Маса навантаження (кг)
        safety_margin_mass: Запас безпеки (кг)
        extra_mass: Додаткова маса (кг) - інше обладнання
        total_mass: Загальна маса (кг)
    """
    gas_mass: float = 0.0
    envelope_mass: float = 0.0
    seams_mass: float = 0.0
    reinforcements_mass: float = 0.0
    payload_mass: float = 0.0
    safety_margin_mass: float = 0.0
    extra_mass: float = 0.0
    
    @property
    def total_mass(self) -> float:
        """Загальна маса (кг)"""
        return (
            self.gas_mass +
            self.envelope_mass +
            self.seams_mass +
            self.reinforcements_mass +
            self.payload_mass +
            self.safety_margin_mass +
            self.extra_mass
        )
    
    @property
    def structural_mass(self) -> float:
        """Структурна маса (оболонка + шви + підсилення)"""
        return self.envelope_mass + self.seams_mass + self.reinforcements_mass
    
    def to_dict(self) -> Dict[str, float]:
        """Повертає словник з усіма компонентами"""
        return {
            'gas_mass': self.gas_mass,
            'envelope_mass': self.envelope_mass,
            'seams_mass': self.seams_mass,
            'reinforcements_mass': self.reinforcements_mass,
            'payload_mass': self.payload_mass,
            'safety_margin_mass': self.safety_margin_mass,
            'extra_mass': self.extra_mass,
            'structural_mass': self.structural_mass,
            'total_mass': self.total_mass,
        }
    
    def to_table_data(self) -> list[Dict[str, Any]]:
        """Повертає дані для таблиці відображення"""
        return [
            {
                'Компонент': 'Газ',
                'Маса (кг)': f"{self.gas_mass:.4f}",
                'Відсоток': f"{(self.gas_mass / self.total_mass * 100) if self.total_mass > 0 else 0:.1f}%",
                'Опис': 'Маса газу всередині аеростата'
            },
            {
                'Компонент': 'Оболонка',
                'Маса (кг)': f"{self.envelope_mass:.4f}",
                'Відсоток': f"{(self.envelope_mass / self.total_mass * 100) if self.total_mass > 0 else 0:.1f}%",
                'Опис': 'Маса матеріалу оболонки'
            },
            {
                'Компонент': 'Шви',
                'Маса (кг)': f"{self.seams_mass:.4f}",
                'Відсоток': f"{(self.seams_mass / self.total_mass * 100) if self.total_mass > 0 else 0:.1f}%",
                'Опис': 'Додаткова маса через шви (seam_factor)'
            },
            {
                'Компонент': 'Підсилення',
                'Маса (кг)': f"{self.reinforcements_mass:.4f}",
                'Відсоток': f"{(self.reinforcements_mass / self.total_mass * 100) if self.total_mass > 0 else 0:.1f}%",
                'Опис': 'Маса додаткових елементів міцності'
            },
            {
                'Компонент': 'Навантаження',
                'Маса (кг)': f"{self.payload_mass:.4f}",
                'Відсоток': f"{(self.payload_mass / self.total_mass * 100) if self.total_mass > 0 else 0:.1f}%",
                'Опис': 'Корисне навантаження'
            },
            {
                'Компонент': 'Запас безпеки',
                'Маса (кг)': f"{self.safety_margin_mass:.4f}",
                'Відсоток': f"{(self.safety_margin_mass / self.total_mass * 100) if self.total_mass > 0 else 0:.1f}%",
                'Опис': 'Запас для компенсації невизначеностей'
            },
            {
                'Компонент': 'Інше обладнання',
                'Маса (кг)': f"{self.extra_mass:.4f}",
                'Відсоток': f"{(self.extra_mass / self.total_mass * 100) if self.total_mass > 0 else 0:.1f}%",
                'Опис': 'Додаткове обладнання (клапани, датчики тощо)'
            },
            {
                'Компонент': 'РАЗОМ',
                'Маса (кг)': f"{self.total_mass:.4f}",
                'Відсоток': '100.0%',
                'Опис': 'Загальна маса аеростата'
            },
        ]


@dataclass
class LiftBudget:
    """
    Бюджет підйомної сили
    
    Attributes:
        gross_lift: Валовий підйом (кг) - підйомна сила газу
        gas_mass: Маса газу (кг)
        net_lift: Чистий підйом (кг) - підйомна сила мінус маса газу
        available_lift: Доступний підйом (кг) - для навантаження та структури
        used_lift: Використаний підйом (кг) - для структури та навантаження
        remaining_lift: Залишковий підйом (кг) - доступний для додаткового навантаження
    """
    gross_lift: float = 0.0
    gas_mass: float = 0.0
    net_lift: float = 0.0
    available_lift: float = 0.0
    used_lift: float = 0.0
    remaining_lift: float = 0.0
    
    @property
    def lift_efficiency(self) -> float:
        """Ефективність використання підйомної сили (0..1)"""
        if self.available_lift <= 0:
            return 0.0
        return self.used_lift / self.available_lift
    
    def to_dict(self) -> Dict[str, float]:
        """Повертає словник з усіма компонентами"""
        return {
            'gross_lift': self.gross_lift,
            'gas_mass': self.gas_mass,
            'net_lift': self.net_lift,
            'available_lift': self.available_lift,
            'used_lift': self.used_lift,
            'remaining_lift': self.remaining_lift,
            'lift_efficiency': self.lift_efficiency,
        }
    
    def to_table_data(self) -> list[Dict[str, Any]]:
        """Повертає дані для таблиці відображення"""
        return [
            {
                'Компонент': 'Валовий підйом',
                'Значення (кг)': f"{self.gross_lift:.4f}",
                'Опис': 'Підйомна сила газу (ρ_air - ρ_gas) × V'
            },
            {
                'Компонент': 'Маса газу',
                'Значення (кг)': f"{self.gas_mass:.4f}",
                'Опис': 'Маса газу всередині аеростата'
            },
            {
                'Компонент': 'Чистий підйом',
                'Значення (кг)': f"{self.net_lift:.4f}",
                'Опис': 'Валовий підйом мінус маса газу'
            },
            {
                'Компонент': 'Доступний підйом',
                'Значення (кг)': f"{self.available_lift:.4f}",
                'Опис': 'Підйомна сила для структури та навантаження'
            },
            {
                'Компонент': 'Використаний підйом',
                'Значення (кг)': f"{self.used_lift:.4f}",
                'Опис': 'Використано для структури та навантаження'
            },
            {
                'Компонент': 'Залишковий підйом',
                'Значення (кг)': f"{self.remaining_lift:.4f}",
                'Опис': 'Доступний для додаткового навантаження'
            },
            {
                'Компонент': 'Ефективність',
                'Значення (%)': f"{self.lift_efficiency * 100:.1f}%",
                'Опис': 'Відсоток використання доступного підйому'
            },
        ]


def calculate_mass_budget(
    gas_volume: float,
    gas_density: float,
    surface_area: float,
    thickness_m: float,
    material_density: float,
    seam_factor: float = 1.0,
    reinforcements_mass: float = 0.0,
    payload_mass: float = 0.0,
    safety_margin_percent: float = 0.0,
    extra_mass: float = 0.0
) -> MassBudget:
    """
    Розраховує бюджет маси аеростата
    
    Args:
        gas_volume: Об'єм газу (м³)
        gas_density: Щільність газу (кг/м³)
        surface_area: Площа поверхні (м²)
        thickness_m: Товщина оболонки (м)
        material_density: Щільність матеріалу (кг/м³)
        seam_factor: Коефіцієнт швів (множник площі)
        reinforcements_mass: Маса підсилень (кг)
        payload_mass: Маса навантаження (кг)
        safety_margin_percent: Запас безпеки (% від загальної маси)
        extra_mass: Додаткова маса (кг)
    
    Returns:
        MassBudget з розбиттям маси
    """
    # Маса газу
    gas_mass = gas_volume * gas_density
    
    # Маса оболонки (базова)
    envelope_mass = surface_area * thickness_m * material_density
    
    # Маса швів (додаткова маса через seam_factor)
    # seam_factor > 1.0 означає додаткову площу через шви
    seams_mass = envelope_mass * (seam_factor - 1.0) if seam_factor > 1.0 else 0.0
    
    # Загальна структурна маса
    structural_mass = envelope_mass + seams_mass + reinforcements_mass
    
    # Запас безпеки (відсоток від загальної маси)
    # Спочатку розраховуємо без запасу, потім додаємо
    total_without_safety = gas_mass + structural_mass + payload_mass + extra_mass
    safety_margin_mass = total_without_safety * (safety_margin_percent / 100.0)
    
    budget = MassBudget(
        gas_mass=gas_mass,
        envelope_mass=envelope_mass,
        seams_mass=seams_mass,
        reinforcements_mass=reinforcements_mass,
        payload_mass=payload_mass,
        safety_margin_mass=safety_margin_mass,
        extra_mass=extra_mass
    )
    
    return budget


def calculate_lift_budget(
    gas_volume: float,
    air_density: float,
    gas_density: float,
    mass_budget: MassBudget
) -> LiftBudget:
    """
    Розраховує бюджет підйомної сили
    
    Args:
        gas_volume: Об'єм газу (м³)
        air_density: Щільність повітря (кг/м³)
        gas_density: Щільність газу (кг/м³)
        mass_budget: Бюджет маси
    
    Returns:
        LiftBudget з розбиттям підйомної сили
    """
    # Валовий підйом (підйомна сила газу)
    gross_lift = (air_density - gas_density) * gas_volume
    
    # Маса газу
    gas_mass = mass_budget.gas_mass
    
    # Чистий підйом (мінус маса газу)
    net_lift = gross_lift - gas_mass
    
    # Доступний підйом (для структури та навантаження)
    available_lift = net_lift
    
    # Використаний підйом (структура + навантаження + інше)
    used_lift = (
        mass_budget.structural_mass +
        mass_budget.payload_mass +
        mass_budget.extra_mass +
        mass_budget.safety_margin_mass
    )
    
    # Залишковий підйом
    remaining_lift = available_lift - used_lift
    
    return LiftBudget(
        gross_lift=gross_lift,
        gas_mass=gas_mass,
        net_lift=net_lift,
        available_lift=available_lift,
        used_lift=used_lift,
        remaining_lift=remaining_lift
    )

