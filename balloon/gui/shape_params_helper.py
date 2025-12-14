"""
Допоміжний модуль для отримання параметрів форм з різних джерел
"""

import logging
from typing import Dict, Any, Optional


def get_shape_params_from_sources(
    shape_code: str,
    entries: Dict[str, Any],
    last_calculation_results: Optional[Dict[str, Any]] = None,
    current_pattern: Optional[Dict[str, Any]] = None,
    default_values: Optional[Dict[str, Dict[str, float]]] = None
) -> Dict[str, float]:
    """
    Отримує параметри форми з різних джерел у порядку пріоритету:
    1. Поточний патерн (якщо є)
    2. Останній розрахунок (якщо є)
    3. Поля вводу GUI
    4. Значення за замовчуванням
    
    Args:
        shape_code: Код форми ('sphere', 'pear', 'cigar', 'pillow')
        entries: Словник з віджетами GUI (self.entries)
        last_calculation_results: Результати останнього розрахунку
        current_pattern: Поточний патерн (якщо є)
        default_values: Значення за замовчуванням для кожної форми
    
    Returns:
        Словник з параметрами форми
    """
    if default_values is None:
        default_values = {
            'sphere': {'radius': 1.0},
            'pear': {'pear_height': 3.0, 'pear_top_radius': 1.2, 'pear_bottom_radius': 0.6},
            'cigar': {'cigar_length': 5.0, 'cigar_radius': 1.0},
            'pillow': {'pillow_len': 3.0, 'pillow_wid': 2.0}
        }
    
    shape_params = {}
    
    # 1. Спробуємо отримати з поточного патерну
    if current_pattern:
        pattern_type = current_pattern.get('pattern_type', '')
        if pattern_type == 'sphere_gore' and shape_code == 'sphere':
            shape_params = {'radius': current_pattern.get('radius', default_values['sphere']['radius'])}
        elif pattern_type == 'pear_gore' and shape_code == 'pear':
            shape_params = {
                'pear_height': current_pattern.get('height', default_values['pear']['pear_height']),
                'pear_top_radius': current_pattern.get('top_radius', default_values['pear']['pear_top_radius']),
                'pear_bottom_radius': current_pattern.get('bottom_radius', default_values['pear']['pear_bottom_radius'])
            }
        elif pattern_type == 'cigar_gore' and shape_code == 'cigar':
            shape_params = {
                'cigar_length': current_pattern.get('length', default_values['cigar']['cigar_length']),
                'cigar_radius': current_pattern.get('radius', default_values['cigar']['cigar_radius'])
            }
    
    # 2. Спробуємо отримати з останнього розрахунку
    if not shape_params and last_calculation_results:
        calc_shape_code = last_calculation_results.get('shape_type', '')
        if calc_shape_code == shape_code:
            shape_params = last_calculation_results.get('shape_params', {}) or {}
            
            # Якщо shape_params порожній, спробуємо отримати з results напряму
            if not shape_params:
                if shape_code == 'sphere' and 'radius' in last_calculation_results:
                    shape_params = {'radius': last_calculation_results['radius']}
                elif shape_code == 'pear':
                    shape_params = {
                        'pear_height': last_calculation_results.get('pear_height', default_values['pear']['pear_height']),
                        'pear_top_radius': last_calculation_results.get('pear_top_radius', default_values['pear']['pear_top_radius']),
                        'pear_bottom_radius': last_calculation_results.get('pear_bottom_radius', default_values['pear']['pear_bottom_radius'])
                    }
                elif shape_code == 'cigar':
                    shape_params = {
                        'cigar_length': last_calculation_results.get('cigar_length', default_values['cigar']['cigar_length']),
                        'cigar_radius': last_calculation_results.get('cigar_radius', default_values['cigar']['cigar_radius'])
                    }
                elif shape_code == 'pillow':
                    shape_params = {
                        'pillow_len': last_calculation_results.get('pillow_len', default_values['pillow']['pillow_len']),
                        'pillow_wid': last_calculation_results.get('pillow_wid', default_values['pillow']['pillow_wid'])
                    }
    
    # 3. Спробуємо отримати з полів GUI
    if not shape_params:
        try:
            if shape_code == 'sphere':
                # Для сфери спробуємо обчислити радіус з об'єму
                if last_calculation_results and 'radius' in last_calculation_results:
                    shape_params = {'radius': last_calculation_results['radius']}
                elif 'gas_volume' in entries:
                    try:
                        gas_volume = float(entries['gas_volume'].get() or "1.0")
                        from balloon.shapes import sphere_radius_from_volume
                        radius = sphere_radius_from_volume(gas_volume)
                        shape_params = {'radius': radius}
                    except (ValueError, TypeError, AttributeError):
                        shape_params = default_values['sphere'].copy()
                else:
                    shape_params = default_values['sphere'].copy()
                    
            elif shape_code == 'pear':
                shape_params = {
                    'pear_height': _get_float_from_entry(entries, 'pear_height', default_values['pear']['pear_height']),
                    'pear_top_radius': _get_float_from_entry(entries, 'pear_top_radius', default_values['pear']['pear_top_radius']),
                    'pear_bottom_radius': _get_float_from_entry(entries, 'pear_bottom_radius', default_values['pear']['pear_bottom_radius'])
                }
            elif shape_code == 'cigar':
                shape_params = {
                    'cigar_length': _get_float_from_entry(entries, 'cigar_length', default_values['cigar']['cigar_length']),
                    'cigar_radius': _get_float_from_entry(entries, 'cigar_radius', default_values['cigar']['cigar_radius'])
                }
            elif shape_code == 'pillow':
                shape_params = {
                    'pillow_len': _get_float_from_entry(entries, 'pillow_len', default_values['pillow']['pillow_len']),
                    'pillow_wid': _get_float_from_entry(entries, 'pillow_wid', default_values['pillow']['pillow_wid'])
                }
        except Exception as e:
            logging.debug(f"Не вдалося отримати параметри форми {shape_code}: {e}, використовуємо значення за замовчуванням")
            shape_params = default_values.get(shape_code, {}).copy()
    
    # 4. Fallback на значення за замовчуванням
    if not shape_params:
        shape_params = default_values.get(shape_code, {}).copy()
    
    return shape_params


def _get_float_from_entry(entries: Dict[str, Any], key: str, default: float) -> float:
    """
    Отримує float значення з GUI entry з обробкою помилок
    
    Args:
        entries: Словник з віджетами GUI
        key: Ключ поля
        default: Значення за замовчуванням
    
    Returns:
        Float значення або default
    """
    try:
        entry = entries.get(key)
        if entry is None:
            return default
        value = entry.get() if hasattr(entry, 'get') else str(entry)
        return float(value or str(default))
    except (ValueError, TypeError, AttributeError):
        return default


def get_shape_code_from_sources(
    entries: Dict[str, Any],
    pattern_shape_var: Optional[Any] = None,
    last_calculation_results: Optional[Dict[str, Any]] = None,
    current_pattern: Optional[Dict[str, Any]] = None,
    shape_display_to_code: Optional[Dict[str, str]] = None
) -> str:
    """
    Отримує shape_code з різних джерел у порядку пріоритету
    
    Args:
        entries: Словник з віджетами GUI
        pattern_shape_var: Змінна форми для патерну
        last_calculation_results: Результати останнього розрахунку
        current_pattern: Поточний патерн
        shape_display_to_code: Мапінг display_name -> shape_code
    
    Returns:
        Код форми або 'sphere' за замовчуванням
    """
    if shape_display_to_code is None:
        shape_display_to_code = {
            "Сфера": "sphere",
            "Подушка/мішок": "pillow",
            "Груша": "pear",
            "Сигара": "cigar",
        }
    
    # 1. Спробуємо отримати з поточного патерну
    if current_pattern:
        pattern_type = current_pattern.get('pattern_type', '')
        if pattern_type == 'sphere_gore':
            return 'sphere'
        elif pattern_type == 'pear_gore':
            return 'pear'
        elif pattern_type == 'cigar_gore':
            return 'cigar'
        elif pattern_type == 'pillow':
            return 'pillow'
    
    # 2. Спробуємо отримати з останнього розрахунку
    if last_calculation_results:
        shape_code = last_calculation_results.get('shape_type')
        if shape_code:
            return shape_code
    
    # 3. Спробуємо отримати з pattern_shape_var
    if pattern_shape_var:
        try:
            shape_display = pattern_shape_var.get() if hasattr(pattern_shape_var, 'get') else str(pattern_shape_var)
            return shape_display_to_code.get(shape_display, 'sphere')
        except (AttributeError, TypeError):
            pass
    
    # 4. Спробуємо отримати з entries['shape_type']
    if 'shape_type' in entries:
        try:
            shape_display = entries['shape_type'].get() if hasattr(entries['shape_type'], 'get') else str(entries['shape_type'])
            return shape_display_to_code.get(shape_display, 'sphere')
        except (AttributeError, TypeError, KeyError):
            pass
    
    # 5. Fallback
    return 'sphere'

