"""
Модуль для експорту результатів розрахунку та викрійок
"""

import os
import math
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def export_results_to_excel(results: Dict[str, Any], filename: Optional[str] = None) -> str:
    """
    Експортує результати розрахунку в Excel файл
    
    Args:
        results: Словник з результатами розрахунку
        filename: Ім'я файлу (якщо None, генерується автоматично)
    
    Returns:
        Шлях до збереженого файлу
    
    Raises:
        ImportError: Якщо pandas не встановлено
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("Для експорту в Excel потрібна бібліотека pandas. Встановіть: pip install pandas openpyxl")
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"balloon_results_{timestamp}.xlsx"
    
    # Підготовка даних для експорту
    data = []
    
    # Основні параметри
    data.append({
        'Параметр': 'Об\'єм кулі',
        'Значення': f"{results.get('required_volume', 0):.4f}",
        'Одиниця': 'м³'
    })
    data.append({
        'Параметр': 'Площа поверхні',
        'Значення': f"{results.get('surface_area', 0):.4f}",
        'Одиниця': 'м²'
    })
    data.append({
        'Параметр': 'Маса оболонки',
        'Значення': f"{results.get('envelope_mass', 0):.4f}",
        'Одиниця': 'кг'
    })
    data.append({
        'Параметр': 'Загальна маса',
        'Значення': f"{results.get('total_mass', 0):.4f}",
        'Одиниця': 'кг'
    })
    data.append({
        'Параметр': 'Підйомна сила (початок)',
        'Значення': f"{results.get('lift', 0):.4f}",
        'Одиниця': 'Н'
    })
    data.append({
        'Параметр': 'Підйомна сила (кінець)',
        'Значення': f"{results.get('lift_end', 0):.4f}",
        'Одиниця': 'Н'
    })
    
    if 'payload' in results:
        data.append({
            'Параметр': 'Корисне навантаження',
            'Значення': f"{results.get('payload', 0):.4f}",
            'Одиниця': 'кг'
        })
    
    if 'stress' in results:
        data.append({
            'Параметр': 'Напруга в оболонці',
            'Значення': f"{results.get('stress', 0):.2e}",
            'Одиниця': 'Па'
        })
        data.append({
            'Параметр': 'Гранична напруга',
            'Значення': f"{results.get('stress_limit', 0):.2e}",
            'Одиниця': 'Па'
        })
    
    # Параметри форми - використовуємо реєстр для отримання інформації про параметри
    from balloon.shapes.registry import get_shape_entry
    
    shape_type = results.get('shape_type', 'sphere')
    shape_params = results.get('shape_params', {})
    
    # Отримуємо інформацію про форму з реєстру
    entry = get_shape_entry(shape_type)
    if entry:
        # Використовуємо Pydantic модель для отримання назв полів
        param_model = entry.param_model
        param_fields = param_model.model_fields
        
        # Додаємо параметри форми до експорту
        for param_name, field_info in param_fields.items():
            if param_name in shape_params:
                # Отримуємо опис з field_info або використовуємо param_name
                description = field_info.description or param_name.replace('_', ' ').title()
                data.append({
                    'Параметр': description,
                    'Значення': f"{shape_params[param_name]:.4f}",
                    'Одиниця': 'м'
                })
        
        # Для сфери також перевіряємо results на наявність radius
        if shape_type == 'sphere' and 'radius' in results and 'radius' not in shape_params:
            data.append({
                'Параметр': 'Радіус сфери',
                'Значення': f"{results.get('radius', 0):.4f}",
                'Одиниця': 'м'
            })
    else:
        # Fallback на старий спосіб, якщо форма не знайдена в реєстрі
        if shape_type == 'sphere' and 'radius' in results:
            data.append({
                'Параметр': 'Радіус сфери',
                'Значення': f"{results.get('radius', 0):.4f}",
                'Одиниця': 'м'
            })
        elif shape_type == 'pillow':
            data.append({
                'Параметр': 'Довжина подушки',
                'Значення': f"{shape_params.get('pillow_len', 0):.4f}",
                'Одиниця': 'м'
            })
            data.append({
                'Параметр': 'Ширина подушки',
                'Значення': f"{shape_params.get('pillow_wid', 0):.4f}",
                'Одиниця': 'м'
            })
        elif shape_type == 'pear':
            data.append({
                'Параметр': 'Висота груші',
                'Значення': f"{shape_params.get('pear_height', 0):.4f}",
                'Одиниця': 'м'
            })
            data.append({
                'Параметр': 'Радіус верхньої частини',
                'Значення': f"{shape_params.get('pear_top_radius', 0):.4f}",
                'Одиниця': 'м'
            })
            data.append({
                'Параметр': 'Радіус нижньої частини',
                'Значення': f"{shape_params.get('pear_bottom_radius', 0):.4f}",
                'Одиниця': 'м'
            })
        elif shape_type == 'cigar':
            data.append({
                'Параметр': 'Довжина сигари',
                'Значення': f"{shape_params.get('cigar_length', 0):.4f}",
                'Одиниця': 'м'
            })
            data.append({
                'Параметр': 'Радіус сигари',
                'Значення': f"{shape_params.get('cigar_radius', 0):.4f}",
                'Одиниця': 'м'
            })
    
    # Створюємо DataFrame
    df = pd.DataFrame(data)
    
    # Створюємо Excel writer
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Основні результати
        df.to_excel(writer, sheet_name='Результати', index=False)
        
        # Додаємо інформацію про розрахунок
        info_data = [
            ['Дата розрахунку', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ['Тип газу', results.get('gas_type', 'Невідомо')],
            ['Матеріал', results.get('material', 'Невідомо')],
            ['Форма', shape_type],
            ['Режим', results.get('mode', 'Невідомо')],
        ]
        info_df = pd.DataFrame(info_data, columns=['Параметр', 'Значення'])
        info_df.to_excel(writer, sheet_name='Інформація', index=False)
        
        # Якщо є профіль висоти
        if 'height_profile' in results:
            profile = results['height_profile']
            if isinstance(profile, list) and len(profile) > 0:
                profile_data = []
                for item in profile:
                    if isinstance(item, dict):
                        profile_data.append({
                            'Висота (м)': item.get('height', 0),
                            'Підйомна сила (Н)': item.get('lift', 0),
                            'Тиск (Па)': item.get('pressure', 0),
                        })
                if profile_data:
                    profile_df = pd.DataFrame(profile_data)
                    profile_df.to_excel(writer, sheet_name='Профіль висоти', index=False)
    
    return os.path.abspath(filename)


def export_pattern_to_excel(pattern: Dict[str, Any], filename: Optional[str] = None) -> str:
    """
    Експортує викрійку в Excel файл
    
    Args:
        pattern: Словник з даними викрійки
        filename: Ім'я файлу (якщо None, генерується автоматично)
    
    Returns:
        Шлях до збереженого файлу
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("Для експорту в Excel потрібна бібліотека pandas. Встановіть: pip install pandas openpyxl")
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pattern_type = pattern.get('pattern_type', 'unknown')
        filename = f"balloon_pattern_{pattern_type}_{timestamp}.xlsx"
    
    pattern_type = pattern.get('pattern_type', 'unknown')
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Інформація про викрійку
        info_data = [
            ['Тип викрійки', pattern_type],
            ['Кількість сегментів', pattern.get('num_gores', pattern.get('num_segments', 0))],
            ['Загальна площа', f"{pattern.get('total_area', 0):.4f} м²"],
            ['Довжина швів', f"{pattern.get('seam_length', 0):.4f} м"],
        ]
        if 'seam_allowance_m' in pattern:
            info_data.append(['Припуск на шов', f"{pattern['seam_allowance_m'] * 1000:.1f} мм"])
        info_df = pd.DataFrame(info_data, columns=['Параметр', 'Значення'])
        info_df.to_excel(writer, sheet_name='Інформація', index=False)
        
        # Координати точок
        if 'points' in pattern:
            points = pattern['points']
            if isinstance(points, list) and len(points) > 0:
                points_data = []
                for i, point in enumerate(points):
                    if isinstance(point, (list, tuple)) and len(point) >= 2:
                        points_data.append({
                            'Точка': i + 1,
                            'X (м)': point[0],
                            'Y (м)': point[1],
                        })
                    elif isinstance(point, dict):
                        points_data.append({
                            'Точка': i + 1,
                            'X (м)': point.get('x', point.get('X', 0)),
                            'Y (м)': point.get('y', point.get('Y', 0)),
                        })
                
                if points_data:
                    points_df = pd.DataFrame(points_data)
                    points_df.to_excel(writer, sheet_name='Координати', index=False)
    
    return os.path.abspath(filename)


def export_pattern_to_svg(pattern: Dict[str, Any], filename: str, scale_mm_per_m: float = 1000.0, 
                          seam_allowance_mm: float = 10.0, add_notches: bool = True, 
                          add_centerline: bool = True) -> str:
    """
    Експортує викрійку в SVG файл (масштаб 1:1)
    
    Args:
        pattern: Словник з даними викрійки
        filename: Ім'я файлу для збереження
        scale_mm_per_m: Масштаб (мм на метр) - для 1:1 використовувати 1000
        seam_allowance_mm: Припуск на шов (мм) - вже додано в pattern, але може бути корисним для відображення
    
    Returns:
        Шлях до збереженого файлу
    """
    pattern_type = pattern.get('pattern_type', 'unknown')
    points = pattern.get('points', [])
    
    if not points:
        raise ValueError("Патерн не містить координат для експорту")
    
    # Знаходимо розміри для viewBox
    max_x = max(x for x, y in points) if points else 0
    max_y = max(y for x, y in points) if points else 0
    
    # Конвертуємо в мм
    width_mm = max_x * scale_mm_per_m
    height_mm = max_y * scale_mm_per_m
    
    # Додаємо відступи для припуску та міток
    padding_mm = 20
    total_width = width_mm + 2 * padding_mm
    total_height = height_mm + 2 * padding_mm
    
    # Створюємо SVG
    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width:.2f}mm" height="{total_height:.2f}mm"',
        f'     viewBox="0 0 {total_width:.2f} {total_height:.2f}">',
        '  <defs>',
        '    <style>',
        '      .pattern-line { stroke: #000; stroke-width: 0.5; fill: none; }',
        '      .seam-line { stroke: #f00; stroke-width: 0.3; stroke-dasharray: 2,2; fill: none; }',
        '      .cut-line { stroke: #00f; stroke-width: 0.5; fill: none; }',
        '      .center-line { stroke: #0a0; stroke-width: 0.2; stroke-dasharray: 5,5; fill: none; }',
        '      .notch { stroke: #f00; stroke-width: 0.3; fill: none; }',
        '      .text { font-family: Arial; font-size: 3mm; fill: #000; }',
        '    </style>',
        '  </defs>',
        '  <g transform="translate(20, 20)">',  # Відступ для міток
    ]
    
    # Малюємо викрійку
    if len(points) > 1:
        # Для gores: малюємо повний контур (одна половина + дзеркальна)
        # Лінія викрійки (з припуском) - від центру вправо, потім вниз, потім дзеркально вліво
        path_data = f'M 0,{points[0][1] * scale_mm_per_m:.2f}'  # Початок від центру
        # Права сторона (з припуском)
        for x, y in points:
            path_data += f' L {x * scale_mm_per_m:.2f},{y * scale_mm_per_m:.2f}'
        # Нижня точка (якщо потрібно)
        if points[-1][0] > 0:
            path_data += f' L {points[-1][0] * scale_mm_per_m:.2f},{points[-1][1] * scale_mm_per_m:.2f}'
        # Ліва сторона (дзеркально, з припуском)
        for x, y in reversed(points):
            path_data += f' L {-x * scale_mm_per_m:.2f},{y * scale_mm_per_m:.2f}'
        path_data += ' Z'
        
        svg_lines.append(f'    <path class="cut-line" d="{path_data}"/>')
        
        # Осьова лінія (центральна лінія gore) - якщо потрібно
        if add_centerline:
            y_start = points[0][1] * scale_mm_per_m
            y_end = points[-1][1] * scale_mm_per_m
            svg_lines.append(f'    <line x1="0" y1="{y_start:.2f}" x2="0" y2="{y_end:.2f}" class="center-line"/>')
        
        # Мітки суміщення (notches) - якщо потрібно
        if add_notches and len(points) > 4:
            # Використовуємо notches з pattern, якщо вони є, інакше обчислюємо
            notch_y_positions = pattern.get('notches', [])
            if not notch_y_positions:
                # Fallback: обчислюємо позиції по довжині меридіану
                meridian_length = pattern.get('meridian_length', 0)
                if meridian_length > 0:
                    notch_positions = [0.1, 0.3, 0.5, 0.7, 0.9]
                    notch_y_positions = [pos * meridian_length for pos in notch_positions]
            
            # Знаходимо точки на контурі, найближчі до позицій notches
            for notch_y in notch_y_positions:
                # Знаходимо найближчу точку по Y
                closest_idx = min(range(len(points)), key=lambda i: abs(points[i][1] - notch_y))
                if 0 <= closest_idx < len(points):
                    x, y = points[closest_idx]
                    y_mm = y * scale_mm_per_m
                    # Мітка: коротка лінія перпендикулярна до контуру (назовні)
                    notch_length = 5.0  # 5 мм
                    # Права сторона
                    svg_lines.append(f'    <line x1="{x * scale_mm_per_m:.2f}" y1="{y_mm:.2f}" '
                                   f'x2="{(x + notch_length) * scale_mm_per_m:.2f}" y2="{y_mm:.2f}" class="notch"/>')
                    # Ліва сторона (дзеркально)
                    svg_lines.append(f'    <line x1="{-x * scale_mm_per_m:.2f}" y1="{y_mm:.2f}" '
                                   f'x2="{(-x - notch_length) * scale_mm_per_m:.2f}" y2="{y_mm:.2f}" class="notch"/>')
        
        # Лінія шва (без припуску) - якщо є seam_allowance
        if 'seam_allowance_m' in pattern and pattern['seam_allowance_m'] > 0:
            allowance_m = pattern['seam_allowance_m']
            seam_path_data = f'M 0,{points[0][1] * scale_mm_per_m:.2f}'  # Початок від центру
            # Права сторона (без припуску)
            for x, y in points:
                seam_path_data += f' L {(x - allowance_m) * scale_mm_per_m:.2f},{y * scale_mm_per_m:.2f}'
            # Ліва сторона (дзеркально, без припуску)
            for x, y in reversed(points):
                seam_path_data += f' L {(-x + allowance_m) * scale_mm_per_m:.2f},{y * scale_mm_per_m:.2f}'
            seam_path_data += ' Z'
            svg_lines.append(f'    <path class="seam-line" d="{seam_path_data}"/>')
    
    # Додаємо мітки та інформацію
    svg_lines.extend([
        f'    <text x="0" y="-5" class="text">{pattern_type}</text>',
        f'    <text x="0" y="{height_mm + 10:.2f}" class="text">Масштаб 1:1 ({scale_mm_per_m} мм/м)</text>',
    ])
    
    if 'seam_allowance_m' in pattern:
        svg_lines.append(f'    <text x="0" y="{height_mm + 15:.2f}" class="text">Припуск на шов: {pattern["seam_allowance_m"] * 1000:.1f} мм</text>')
    
    svg_lines.extend([
        '  </g>',
        '</svg>',
    ])
    
    # Зберігаємо файл
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg_lines))
    
    return os.path.abspath(filename)
