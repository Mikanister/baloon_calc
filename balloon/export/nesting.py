"""
Розкладка викрійок по тканині (nesting)

Оцінка необхідної кількості тканини та відходів
"""

import math
from typing import Dict, Any, List, Tuple, Optional


def estimate_fabric_requirements(
    pattern: Dict[str, Any],
    fabric_width_mm: float = 1500.0,  # Ширина рулону тканини (мм)
    min_gap_mm: float = 10.0,  # Мінімальний зазор між панелями (мм)
    num_panels: Optional[int] = None  # Кількість панелей (якщо None, береться з pattern)
) -> Dict[str, Any]:
    """
    Оцінює необхідну кількість тканини для викрійки
    
    Args:
        pattern: Патерн викрійки
        fabric_width_mm: Ширина рулону тканини (мм)
        min_gap_mm: Мінімальний зазор між панелями (мм)
        num_panels: Кількість панелей (якщо None, береться з pattern)
    
    Returns:
        Словник з оцінкою тканини
    """
    pattern_type = pattern.get('pattern_type', '')
    
    if 'gore' in pattern_type:
        # Для gores
        num_gores = num_panels or pattern.get('num_gores', 12)
        max_width = pattern.get('max_width', 0.0) * 1000  # Конвертуємо в мм
        # Використовуємо meridian_length (довжина по меридіану)
        meridian_length = pattern.get('meridian_length', 0.0)
        total_height = meridian_length * 1000  # Конвертуємо в мм
        
        # Оцінюємо, скільки gores влазить в ширину
        gore_width = max_width * 2  # Повна ширина gore (з дзеркальною стороною)
        gore_with_gap = gore_width + min_gap_mm
        
        gores_per_row = max(1, int((fabric_width_mm - min_gap_mm) / gore_with_gap))
        num_rows = math.ceil(num_gores / gores_per_row)
        
        # Довжина рулону
        fabric_length_mm = num_rows * (total_height + min_gap_mm) + min_gap_mm
        
        # Площа тканини
        fabric_area_m2 = (fabric_width_mm * fabric_length_mm) / 1e6
        
        # Площа панелей
        total_area_m2 = pattern.get('total_area', 0.0)
        
        # Відходи
        waste_m2 = fabric_area_m2 - total_area_m2
        waste_percent = (waste_m2 / fabric_area_m2 * 100) if fabric_area_m2 > 0 else 0.0
        
        return {
            'fabric_width_mm': fabric_width_mm,
            'fabric_length_mm': fabric_length_mm,
            'fabric_length_m': fabric_length_mm / 1000.0,
            'fabric_area_m2': fabric_area_m2,
            'panels_area_m2': total_area_m2,
            'waste_m2': waste_m2,
            'waste_percent': waste_percent,
            'gores_per_row': gores_per_row,
            'num_rows': num_rows,
            'num_panels': num_gores
        }
    
    elif pattern_type == 'pillow':
        # Для подушки
        num_panels_needed = 2  # Дві панелі
        length = pattern.get('length', 0.0) * 1000  # мм
        width = pattern.get('width', 0.0) * 1000  # мм
        
        # Оцінюємо розкладку
        panel_width = width + 2 * min_gap_mm
        panel_height = length + 2 * min_gap_mm
        
        panels_per_row = max(1, int((fabric_width_mm - min_gap_mm) / (panel_width + min_gap_mm)))
        num_rows = math.ceil(num_panels_needed / panels_per_row)
        
        fabric_length_mm = num_rows * panel_height + min_gap_mm
        
        fabric_area_m2 = (fabric_width_mm * fabric_length_mm) / 1e6
        total_area_m2 = pattern.get('total_area', 0.0)
        waste_m2 = fabric_area_m2 - total_area_m2
        waste_percent = (waste_m2 / fabric_area_m2 * 100) if fabric_area_m2 > 0 else 0.0
        
        return {
            'fabric_width_mm': fabric_width_mm,
            'fabric_length_mm': fabric_length_mm,
            'fabric_length_m': fabric_length_mm / 1000.0,
            'fabric_area_m2': fabric_area_m2,
            'panels_area_m2': total_area_m2,
            'waste_m2': waste_m2,
            'waste_percent': waste_percent,
            'panels_per_row': panels_per_row,
            'num_rows': num_rows,
            'num_panels': num_panels_needed
        }
    
    # Fallback
    return {
        'fabric_width_mm': fabric_width_mm,
        'fabric_length_mm': 0.0,
        'fabric_length_m': 0.0,
        'fabric_area_m2': 0.0,
        'panels_area_m2': pattern.get('total_area', 0.0),
        'waste_m2': 0.0,
        'waste_percent': 0.0,
        'num_panels': num_panels or 1
    }

