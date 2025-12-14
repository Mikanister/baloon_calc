"""
DXF Export для CAD систем

Експортує викрійки в DXF формат для використання в CAD системах.
"""

import os
from typing import Dict, Any, Optional

try:
    import ezdxf
    from ezdxf import colors
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False


def export_pattern_to_dxf(
    pattern: Dict[str, Any],
    filename: str,
    scale_mm_per_m: float = 1000.0,
    add_notches: bool = True,
    add_centerline: bool = True
) -> str:
    """
    Експортує викрійку в DXF файл
    
    Args:
        pattern: Словник з даними викрійки
        filename: Ім'я файлу для збереження
        scale_mm_per_m: Масштаб (мм на метр) - для 1:1 використовувати 1000
        add_notches: Чи додавати мітки суміщення
        add_centerline: Чи додавати центральну лінію
    
    Returns:
        Шлях до збереженого файлу
    
    Raises:
        ImportError: Якщо ezdxf не встановлено
        ValueError: Якщо pattern не містить координат
    """
    if not EZDXF_AVAILABLE:
        raise ImportError(
            "Для експорту в DXF потрібна бібліотека ezdxf. "
            "Встановіть: pip install ezdxf"
        )
    
    pattern_type = pattern.get('pattern_type', 'unknown')
    points = pattern.get('points', [])
    
    if not points:
        raise ValueError("Патерн не містить координат для експорту")
    
    # Створюємо DXF документ
    doc = ezdxf.new('R2010')  # AutoCAD 2010 формат
    msp = doc.modelspace()
    
    # Знаходимо розміри для масштабування
    min_x = min(x for x, y in points) if points else 0
    max_x = max(x for x, y in points) if points else 0
    min_y = min(y for x, y in points) if points else 0
    max_y = max(y for x, y in points) if points else 0
    
    # Конвертуємо координати в мм
    def to_mm_x(x: float) -> float:
        return (x - min_x) * scale_mm_per_m
    
    def to_mm_y(y: float) -> float:
        return (y - min_y) * scale_mm_per_m
    
    # Малюємо контур викрійки
    contour_points = []
    for x, y in points:
        contour_points.append((to_mm_x(x), to_mm_y(y)))
    
    if len(contour_points) > 1:
        # Створюємо полілінію для контуру
        msp.add_lwpolyline(
            contour_points,
            close=True,
            dxfattribs={'color': colors.BLACK, 'lineweight': 50}  # 0.5mm line
        )
    
    # Малюємо дзеркальну сторону (для gores)
    mirror_points = []
    for x, y in points:
        mirror_points.append((to_mm_x(-x), to_mm_y(y)))
    
    if len(mirror_points) > 1:
        msp.add_lwpolyline(
            mirror_points,
            close=True,
            dxfattribs={'color': colors.BLACK, 'lineweight': 50}
        )
    
    # Малюємо мітки суміщення (notches)
    if add_notches and 'notch_positions' in pattern and pattern['notch_positions']:
        notch_length = 5.0  # 5 мм
        for y_pos_m in pattern['notch_positions']:
            y_mm = to_mm_y(y_pos_m)
            
            # Знаходимо X координату на контурі
            x_at_y = 0.0
            for i in range(len(points) - 1):
                (x1, y1), (x2, y2) = points[i], points[i+1]
                if (y1 <= y_pos_m < y2) or (y2 <= y_pos_m < y1):
                    if y2 != y1:
                        x_at_y = x1 + (x2 - x1) * (y_pos_m - y1) / (y2 - y1)
                    else:
                        x_at_y = x1
                    break
            
            x_mm = to_mm_x(x_at_y)
            
            # Малюємо мітку (лінія)
            msp.add_line(
                (x_mm, y_mm),
                (x_mm + notch_length, y_mm),
                dxfattribs={'color': colors.RED, 'lineweight': 30}
            )
            msp.add_line(
                (-x_mm, y_mm),
                (-x_mm - notch_length, y_mm),
                dxfattribs={'color': colors.RED, 'lineweight': 30}
            )
    
    # Малюємо центральну лінію
    if add_centerline:
        y_start_mm = 0.0
        y_end_mm = to_mm_y(max_y)
        x_center = 0.0
        
        msp.add_line(
            (x_center, y_start_mm),
            (x_center, y_end_mm),
            dxfattribs={
                'color': colors.GREEN,
                'lineweight': 20,
                'linetype': 'DASHED'
            }
        )
    
    # Додаємо текст з інформацією
    msp.add_text(
        f"Pattern: {pattern_type}",
        height=5.0,  # 5 мм висота тексту
        dxfattribs={'color': colors.BLACK}
    ).set_placement((10, 10))
    
    # Зберігаємо файл
    doc.saveas(filename)
    return os.path.abspath(filename)

