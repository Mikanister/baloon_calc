"""
Модуль для експорту результатів розрахунку
"""

import os
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
    
    # Параметри форми
    shape_type = results.get('shape_type', 'sphere')
    shape_params = results.get('shape_params', {})
    
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
            ['Кількість сегментів', pattern.get('num_segments', 0)],
            ['Загальна площа', f"{pattern.get('total_area', 0):.4f} м²"],
            ['Довжина швів', f"{pattern.get('seam_length', 0):.4f} м"],
        ]
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

