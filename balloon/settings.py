"""
Pydantic Settings для управління налаштуваннями
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    from balloon.constants import (
        DEFAULT_THICKNESS, DEFAULT_START_HEIGHT, DEFAULT_WORK_HEIGHT,
        DEFAULT_GROUND_TEMP, DEFAULT_INSIDE_TEMP, DEFAULT_PAYLOAD,
        DEFAULT_GAS_VOLUME, DEFAULT_SHAPE_TYPE, DEFAULT_PILLOW_LEN,
        DEFAULT_PILLOW_WID, DEFAULT_PEAR_HEIGHT, DEFAULT_PEAR_TOP_RADIUS,
        DEFAULT_PEAR_BOTTOM_RADIUS, DEFAULT_CIGAR_LENGTH, DEFAULT_CIGAR_RADIUS,
        DEFAULT_EXTRA_MASS, DEFAULT_SEAM_FACTOR
    )
except ImportError:
    from constants import (
        DEFAULT_THICKNESS, DEFAULT_START_HEIGHT, DEFAULT_WORK_HEIGHT,
        DEFAULT_GROUND_TEMP, DEFAULT_INSIDE_TEMP, DEFAULT_PAYLOAD,
        DEFAULT_GAS_VOLUME, DEFAULT_SHAPE_TYPE, DEFAULT_PILLOW_LEN,
        DEFAULT_PILLOW_WID, DEFAULT_PEAR_HEIGHT, DEFAULT_PEAR_TOP_RADIUS,
        DEFAULT_PEAR_BOTTOM_RADIUS, DEFAULT_CIGAR_LENGTH, DEFAULT_CIGAR_RADIUS,
        DEFAULT_EXTRA_MASS, DEFAULT_SEAM_FACTOR
    )


class BalloonSettings(BaseSettings):
    """Налаштування калькулятора аеростатів"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # json_file та json_file_encoding видалено, бо використовуємо власні методи save_to_file/load_from_file
        case_sensitive=False,
        extra="ignore"
    )
    
    # Основні налаштування
    mode: str = Field("payload", description="Режим розрахунку")
    material: str = Field("TPU", description="Матеріал оболонки")
    gas: str = Field("Гелій", description="Тип газу")
    shape_type: str = Field(DEFAULT_SHAPE_TYPE, description="Форма оболонки")
    
    # Параметри
    thickness: str = Field(str(DEFAULT_THICKNESS), description="Товщина оболонки (мкм)")
    start_height: str = Field(str(DEFAULT_START_HEIGHT), description="Висота пуску (м)")
    work_height: str = Field(str(DEFAULT_WORK_HEIGHT), description="Висота польоту (м)")
    ground_temp: str = Field(str(DEFAULT_GROUND_TEMP), description="Температура на землі (°C)")
    inside_temp: str = Field(str(DEFAULT_INSIDE_TEMP), description="Температура всередині (°C)")
    payload: str = Field(str(DEFAULT_PAYLOAD), description="Корисне навантаження (кг)")
    gas_volume: str = Field(str(DEFAULT_GAS_VOLUME), description="Об'єм газу (м³)")
    perm_mult: str = Field("1", description="Множник проникності")
    extra_mass: str = Field(str(DEFAULT_EXTRA_MASS), description="Додаткова маса (кг)")
    seam_factor: str = Field(str(DEFAULT_SEAM_FACTOR), description="Коефіцієнт втрат через шви")
    
    # Параметри форм
    pillow_len: str = Field("", description="Довжина подушки (м)")
    pillow_wid: str = Field("", description="Ширина подушки (м)")
    pear_height: str = Field("", description="Висота груші (м)")
    pear_top_radius: str = Field("", description="Радіус верхньої частини груші (м)")
    pear_bottom_radius: str = Field("", description="Радіус нижньої частини груші (м)")
    cigar_length: str = Field("", description="Довжина сигари (м)")
    cigar_radius: str = Field("", description="Радіус сигари (м)")
    
    def to_dict(self) -> dict:
        """Повертає налаштування як словник"""
        return self.model_dump(exclude_none=True)
    
    def save_to_file(self, filename: str = "balloon_settings.json"):
        """Зберігає налаштування у файл"""
        import json
        import sys
        import os
        
        # Визначаємо шлях для налаштувань (в exe режимі використовуємо папку з exe)
        if getattr(sys, 'frozen', False):
            settings_path = os.path.join(os.path.dirname(sys.executable), filename)
        else:
            settings_path = filename
            
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str = "balloon_settings.json") -> "BalloonSettings":
        """Завантажує налаштування з файлу"""
        import os
        import sys
        import json
        
        # Визначаємо шлях для налаштувань (в exe режимі використовуємо папку з exe)
        if getattr(sys, 'frozen', False):
            settings_path = os.path.join(os.path.dirname(sys.executable), filename)
        else:
            settings_path = filename
            
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return cls(**data)
            except Exception:
                return cls()
        return cls()

