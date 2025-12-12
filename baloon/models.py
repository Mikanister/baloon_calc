"""
Pydantic моделі для валідації даних
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator

try:
    from baloon.constants import MATERIALS, GAS_DENSITY
except ImportError:
    from constants import MATERIALS, GAS_DENSITY


class ShapeParams(BaseModel):
    """Параметри форми кулі"""
    
    # Подушка
    pillow_len: Optional[float] = Field(None, gt=0.0001, description="Довжина подушки (м)")
    pillow_wid: Optional[float] = Field(None, gt=0.0001, description="Ширина подушки (м)")
    
    # Груша
    pear_height: Optional[float] = Field(None, gt=0.0001, description="Висота груші (м)")
    pear_top_radius: Optional[float] = Field(None, gt=0.0001, description="Радіус верхньої частини груші (м)")
    pear_bottom_radius: Optional[float] = Field(None, gt=0.0001, description="Радіус нижньої частини груші (м)")
    
    # Сигара
    cigar_length: Optional[float] = Field(None, gt=0.0001, description="Довжина сигари (м)")
    cigar_radius: Optional[float] = Field(None, gt=0.0001, description="Радіус сигари (м)")
    
    @field_validator('*', mode='before')
    @classmethod
    def parse_strings(cls, v):
        """Конвертує рядки в числа"""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            try:
                return float(v)
            except ValueError:
                return None
        return v
    
    def to_dict(self) -> dict:
        """Повертає тільки задані параметри як словник"""
        result = {}
        for key, value in self.model_dump().items():
            if value is not None:
                result[key] = value
        return result


class BalloonInputs(BaseModel):
    """Модель для валідації вхідних даних калькулятора"""
    
    # Обов'язкові поля
    gas_type: str = Field(..., description="Тип газу")
    material: str = Field(..., description="Матеріал оболонки")
    thickness: float = Field(..., gt=1, le=1000, description="Товщина оболонки (мкм)")
    start_height: float = Field(..., ge=0, description="Висота пуску (м)")
    work_height: float = Field(..., ge=0, description="Висота польоту (м)")
    
    # Опціональні поля
    gas_volume: Optional[float] = Field(None, gt=0.001, description="Об'єм газу (потрібен тільки в режимі 'payload')")
    ground_temp: float = Field(15, ge=-50, le=50, description="Температура на землі (°C)")
    inside_temp: float = Field(100, ge=0, le=500, description="Температура всередині (°C)")
    duration: float = Field(24, gt=0.01, le=10000, description="Тривалість польоту (год)")
    mode: Literal["payload", "volume"] = Field("payload", description="Режим розрахунку")
    shape_type: Literal["sphere", "pillow", "pear", "cigar"] = Field("sphere", description="Форма кулі")
    extra_mass: float = Field(0, ge=0, le=1000, description="Додаткова маса обладнання (кг)")
    seam_factor: float = Field(1.0, ge=1.0, le=2.0, description="Коефіцієнт втрат через шви")
    
    # Параметри форми
    shape_params: Optional[ShapeParams] = Field(None, description="Параметри форми")
    
    @field_validator('gas_type')
    @classmethod
    def validate_gas_type(cls, v):
        """Валідує тип газу"""
        if v not in GAS_DENSITY:
            raise ValueError(f"Непідтримуваний тип газу: {v}. Доступні: {list(GAS_DENSITY.keys())}")
        return v
    
    @field_validator('material')
    @classmethod
    def validate_material(cls, v):
        """Валідує матеріал"""
        if v not in MATERIALS:
            raise ValueError(f"Непідтримуваний матеріал: {v}. Доступні: {list(MATERIALS.keys())}")
        return v
    
    @field_validator('*', mode='before')
    @classmethod
    def parse_strings(cls, v, info):
        """Конвертує рядки в числа для числових полів"""
        if info.field_name in ['gas_type', 'material', 'mode', 'shape_type']:
            return v  # Рядкові поля не конвертуємо
        
        if v is None or v == "":
            # Повертаємо значення за замовчуванням для опціональних полів
            if info.field_name in ['ground_temp', 'inside_temp', 'duration', 'extra_mass', 'seam_factor']:
                return None
            return v
        
        if isinstance(v, str):
            v = v.strip()
            if not v:
                if info.field_name in ['ground_temp', 'inside_temp', 'duration', 'extra_mass', 'seam_factor']:
                    return None
                return v
            try:
                return float(v)
            except ValueError:
                raise ValueError(f"Поле '{info.field_name}' має містити число")
        
        return v
    
    @model_validator(mode='after')
    def validate_mode_and_volume(self):
        """Валідує залежність між режимом та об'ємом/навантаженням"""
        # В режимі "payload" gas_volume обов'язковий
        if self.mode == 'payload' and (self.gas_volume is None or self.gas_volume <= 0):
            raise ValueError("В режимі 'Об'єм -> навантаження' потрібно вказати об'єм газу")
        
        # В режимі "volume" gas_volume не потрібен (об'єм розраховується з навантаження)
        # Але якщо він переданий, він ігнорується
        return self
    
    @model_validator(mode='after')
    def validate_temperature_difference(self):
        """Валідує різницю температур для гарячого повітря"""
        if self.gas_type == "Гаряче повітря":
            if self.inside_temp <= self.ground_temp:
                raise ValueError(
                    f"Температура всередині ({self.inside_temp}°C) має бути більшою за "
                    f"температуру на землі ({self.ground_temp}°C)"
                )
        return self
    
    @model_validator(mode='after')
    def validate_height_parameters(self):
        """Валідує параметри висоти"""
        total_height = self.start_height + self.work_height
        if total_height > 50000:  # Максимальна висота стратосфери
            raise ValueError("Загальна висота не може перевищувати 50 км")
        return self
    
    def get_validated_numbers(self) -> dict:
        """Повертає валідовані числові значення"""
        result = {
            'gas_volume': self.gas_volume,
            'thickness': self.thickness,
            'start_height': self.start_height,
            'work_height': self.work_height,
            'ground_temp': self.ground_temp,
            'inside_temp': self.inside_temp,
            'duration': self.duration,
            'extra_mass': self.extra_mass,
            'seam_factor': self.seam_factor,
        }
        
        # Додаємо параметри форми, якщо вони є
        if self.shape_params:
            result.update(self.shape_params.to_dict())
        
        return result
    
    def get_validated_strings(self) -> dict:
        """Повертає валідовані рядкові значення"""
        return {
            'gas_type': self.gas_type,
            'material': self.material,
            'mode': self.mode,
            'shape_type': self.shape_type,
        }

