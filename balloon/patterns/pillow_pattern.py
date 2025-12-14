"""
Патерн для подушкоподібної форми
"""

from typing import Dict, Any

from balloon.shapes import pillow_surface_area


def calculate_pillow_pattern(length: float, width: float, thickness: float = None) -> Dict[str, Any]:
    """
    Розраховує патерн для подушкоподібної оболонки
    
    Подушка складається з двох прямокутних сегментів однакового розміру,
    з'єднаних по кромці, з отвором на одній зі сторін для заповнення.
    
    Args:
        length: Довжина подушки (м)
        width: Ширина подушки (м)
        thickness: Товщина подушки (м) - не використовується для викрійки, лише для опису
    
    Returns:
        Словник з координатами для прямокутних панелей
    """
    # Подушка складається з 2 прямокутних панелей однакового розміру
    panel_area = length * width
    
    # Довжина швів: периметр прямокутника мінус одна сторона (отвір - незакрита ділянка кромки)
    # Зазвичай отвір роблять на коротшій стороні для зручності заповнення
    if width <= length:
        # Отвір на коротшій стороні (ширина) - ця сторона не зшивається
        seam_length = 2 * length + width  # Дві довгі сторони + одна коротка
        opening_side = 'width'
        opening_size = width
    else:
        # Отвір на коротшій стороні (довжина) - ця сторона не зшивається
        seam_length = 2 * width + length  # Дві широкі сторони + одна коротка
        opening_side = 'length'
        opening_size = length
    
    # Загальна площа поверхні
    total_area = pillow_surface_area(length, width, thickness)
    
    # Створюємо опис панелей
    panels = [
        {
            'width': length,
            'height': width,
            'area': panel_area
        },
        {
            'width': length,
            'height': width,
            'area': panel_area
        }
    ]
    
    return {
        'pattern_type': 'pillow',
        'panels': panels,
        'length': length,
        'width': width,
        'thickness': thickness,
        'total_area': total_area,
        'seam_length': seam_length,
        'opening_side': opening_side,
        'opening_size': opening_size,
        'description': f'Подушкоподібна оболонка: {length:.2f} × {width:.2f} м, 2 панелі'
    }

