"""
PDF Export з tiling (розбиття на сторінки A4/A3)

Експортує викрійки в PDF з автоматичним розбиттям на сторінки
та мітками для склейки.
"""

import os
import math
from typing import Dict, Any, Optional, Tuple, List

try:
    from reportlab.lib.pagesizes import A4, A3
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import black, red, blue, green
    REPORTLAB_AVAILABLE = True
except ImportError:
    # Placeholders для type hints коли reportlab недоступний
    A4 = (595.27, 841.89)  # A4 в points
    A3 = (841.89, 1190.55)  # A3 в points
    REPORTLAB_AVAILABLE = False


def _calculate_tiles(
    width_mm: float,
    height_mm: float,
    page_size: Optional[Tuple[float, float]] = None,
    overlap_mm: float = 10.0
) -> List[Dict[str, Any]]:
    """
    Розраховує розбиття викрійки на сторінки (tiles)
    
    Args:
        width_mm: Ширина викрійки (мм)
        height_mm: Висота викрійки (мм)
        page_size: Розмір сторінки (ширина, висота в точках)
        overlap_mm: Перекриття між сторінками (мм)
    
    Returns:
        Список словників з координатами та розмірами кожного tile
    """
    if page_size is None:
        page_size = A4
    
    # Конвертуємо page_size в мм (1 point = 1/72 inch = 25.4/72 mm)
    page_width_mm = page_size[0] * 25.4 / 72
    page_height_mm = page_size[1] * 25.4 / 72
    
    # Враховуємо перекриття
    usable_width = page_width_mm - 2 * overlap_mm
    usable_height = page_height_mm - 2 * overlap_mm
    
    # Кількість сторінок
    num_cols = math.ceil(width_mm / usable_width)
    num_rows = math.ceil(height_mm / usable_height)
    
    tiles = []
    for row in range(num_rows):
        for col in range(num_cols):
            # Координати початку tile в мм (відносно викрійки)
            x_start = col * usable_width
            y_start = row * usable_height
            
            # Розміри tile
            tile_width = min(usable_width, width_mm - x_start)
            tile_height = min(usable_height, height_mm - y_start)
            
            tiles.append({
                'row': row,
                'col': col,
                'x_start_mm': x_start,
                'y_start_mm': y_start,
                'width_mm': tile_width,
                'height_mm': tile_height,
                'page_x_mm': overlap_mm,  # Позиція на сторінці
                'page_y_mm': overlap_mm,
            })
    
    return tiles


def export_pattern_to_pdf(
    pattern: Dict[str, Any],
    filename: str,
    scale_mm_per_m: float = 1000.0,
    page_size: str = 'A4',
    overlap_mm: float = 10.0,
    add_notches: bool = True,
    add_centerline: bool = True,
    add_grid: bool = True
) -> str:
    """
    Експортує викрійку в PDF з автоматичним розбиттям на сторінки
    
    Args:
        pattern: Словник з даними викрійки
        filename: Ім'я файлу для збереження
        scale_mm_per_m: Масштаб (мм на метр) - для 1:1 використовувати 1000
        page_size: Розмір сторінки ('A4' або 'A3')
        overlap_mm: Перекриття між сторінками (мм) - для склейки
        add_notches: Чи додавати мітки суміщення
        add_centerline: Чи додавати центральну лінію
        add_grid: Чи додавати сітку координат
    
    Returns:
        Шлях до збереженого файлу
    
    Raises:
        ImportError: Якщо reportlab не встановлено
        ValueError: Якщо pattern не містить координат
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError(
            "Для експорту в PDF потрібна бібліотека reportlab. "
            "Встановіть: pip install reportlab"
        )
    
    pattern_type = pattern.get('pattern_type', 'unknown')
    points = pattern.get('points', [])
    
    if not points:
        raise ValueError("Патерн не містить координат для експорту")
    
    # Знаходимо розміри викрійки
    min_x = min(x for x, y in points) if points else 0
    max_x = max(x for x, y in points) if points else 0
    min_y = min(y for x, y in points) if points else 0
    max_y = max(y for x, y in points) if points else 0
    
    # Конвертуємо в мм
    width_mm = (max_x - min_x) * scale_mm_per_m
    height_mm = (max_y - min_y) * scale_mm_per_m
    
    # Вибір розміру сторінки
    if page_size.upper() == 'A3':
        page_size_pt = A3
    else:
        page_size_pt = A4
    
    # Розраховуємо tiles
    tiles = _calculate_tiles(width_mm, height_mm, page_size_pt, overlap_mm)
    
    # Створюємо PDF
    c = canvas.Canvas(filename, pagesize=page_size_pt)
    
    for tile_idx, tile in enumerate(tiles):
        # Нова сторінка
        if tile_idx > 0:
            c.showPage()
        
        # Відступ для міток
        margin_mm = overlap_mm
        c.translate(margin_mm * mm, margin_mm * mm)
        
        # Масштаб для відображення
        scale = 1.0  # 1 mm = 1 point (через mm unit)
        
        # Малюємо сітку координат (опціонально)
        if add_grid:
            _draw_grid(c, tile['width_mm'], tile['height_mm'], scale)
        
        # Малюємо контур викрійки
        _draw_pattern_contour(
            c, points, min_x, min_y, tile, scale_mm_per_m, scale
        )
        
        # Малюємо мітки суміщення (notches)
        if add_notches:
            _draw_notches(c, pattern, min_x, min_y, tile, scale_mm_per_m, scale)
        
        # Малюємо центральну лінію
        if add_centerline:
            _draw_centerline(c, points, min_x, min_y, tile, scale_mm_per_m, scale)
        
        # Малюємо мітки для склейки (overlap markers)
        _draw_overlap_markers(c, tile, tiles, page_size_pt, overlap_mm)
        
        # Додаємо інформацію про сторінку
        max_cols = max(t['col'] for t in tiles) + 1
        _draw_page_info(c, tile, len(tiles), max_cols, pattern_type, page_size_pt, margin_mm)
    
    c.save()
    return os.path.abspath(filename)


def _draw_grid(canvas_obj, width_mm: float, height_mm: float, scale: float):
    """Малює сітку координат"""
    canvas_obj.setStrokeColor(black)
    canvas_obj.setLineWidth(0.1)
    
    # Горизонтальні лінії (кожні 50 мм)
    step_mm = 50
    for y in range(0, int(height_mm) + step_mm, step_mm):
        canvas_obj.line(0, y * mm * scale, width_mm * mm * scale, y * mm * scale)
    
    # Вертикальні лінії
    for x in range(0, int(width_mm) + step_mm, step_mm):
        canvas_obj.line(x * mm * scale, 0, x * mm * scale, height_mm * mm * scale)


def _draw_pattern_contour(
    canvas_obj,
    points: List[Tuple[float, float]],
    min_x: float,
    min_y: float,
    tile: Dict[str, Any],
    scale_mm_per_m: float,
    scale: float
):
    """Малює контур викрійки"""
    canvas_obj.setStrokeColor(black)
    canvas_obj.setLineWidth(0.5)
    
    path = canvas_obj.beginPath()
    first_point = True
    
    for x, y in points:
        # Конвертуємо координати в мм відносно min_x, min_y
        x_mm = (x - min_x) * scale_mm_per_m
        y_mm = (y - min_y) * scale_mm_per_m
        
        # Перевіряємо, чи точка в межах tile
        if (tile['x_start_mm'] <= x_mm < tile['x_start_mm'] + tile['width_mm'] and
            tile['y_start_mm'] <= y_mm < tile['y_start_mm'] + tile['height_mm']):
            
            # Відносні координати на сторінці
            page_x = (x_mm - tile['x_start_mm'] + tile['page_x_mm']) * mm * scale
            page_y = (y_mm - tile['y_start_mm'] + tile['page_y_mm']) * mm * scale
            
            if first_point:
                path.moveTo(page_x, page_y)
                first_point = False
            else:
                path.lineTo(page_x, page_y)
    
    # Закриваємо контур
    if not first_point:
        path.close()
        canvas_obj.drawPath(path, stroke=1, fill=0)
    
    # Малюємо дзеркальну сторону (для gores)
    path_mirror = canvas_obj.beginPath()
    first_point = True
    
    for x, y in points:
        x_mm = (x - min_x) * scale_mm_per_m
        y_mm = (y - min_y) * scale_mm_per_m
        
        # Дзеркальна координата X
        x_mm_mirror = -x_mm
        
        if (tile['x_start_mm'] <= abs(x_mm_mirror) < tile['x_start_mm'] + tile['width_mm'] and
            tile['y_start_mm'] <= y_mm < tile['y_start_mm'] + tile['height_mm']):
            
            page_x = (abs(x_mm_mirror) - tile['x_start_mm'] + tile['page_x_mm']) * mm * scale
            page_y = (y_mm - tile['y_start_mm'] + tile['page_y_mm']) * mm * scale
            
            if first_point:
                path_mirror.moveTo(page_x, page_y)
                first_point = False
            else:
                path_mirror.lineTo(page_x, page_y)
    
    if not first_point:
        path_mirror.close()
        canvas_obj.drawPath(path_mirror, stroke=1, fill=0)


def _draw_notches(
    canvas_obj,
    pattern: Dict[str, Any],
    min_x: float,
    min_y: float,
    tile: Dict[str, Any],
    scale_mm_per_m: float,
    scale: float
):
    """Малює мітки суміщення (notches)"""
    if 'notch_positions' not in pattern or not pattern['notch_positions']:
        return
    
    canvas_obj.setStrokeColor(red)
    canvas_obj.setLineWidth(0.3)
    
    notch_length = 5.0  # 5 мм
    
    for y_pos_m in pattern['notch_positions']:
        y_mm = (y_pos_m - min_y) * scale_mm_per_m
        
        # Перевіряємо, чи notch в межах tile
        if tile['y_start_mm'] <= y_mm < tile['y_start_mm'] + tile['height_mm']:
            page_y = (y_mm - tile['y_start_mm'] + tile['page_y_mm']) * mm * scale
            
            # Знаходимо X координату на контурі (спрощено)
            # В ідеалі потрібно інтерполювати
            points = pattern.get('points', [])
            if points:
                # Беремо середнє значення X для цього Y
                x_at_y = 0.0
                for i in range(len(points) - 1):
                    (x1, y1), (x2, y2) = points[i], points[i+1]
                    if (y1 <= y_pos_m < y2) or (y2 <= y_pos_m < y1):
                        if y2 != y1:
                            x_at_y = x1 + (x2 - x1) * (y_pos_m - y1) / (y2 - y1)
                        else:
                            x_at_y = x1
                        break
                
                x_mm = (x_at_y - min_x) * scale_mm_per_m
                if tile['x_start_mm'] <= x_mm < tile['x_start_mm'] + tile['width_mm']:
                    page_x = (x_mm - tile['x_start_mm'] + tile['page_x_mm']) * mm * scale
                    canvas_obj.line(
                        page_x, page_y,
                        page_x + notch_length * mm * scale, page_y
                    )
                    canvas_obj.line(
                        -page_x, page_y,
                        -page_x - notch_length * mm * scale, page_y
                    )


def _draw_centerline(
    canvas_obj,
    points: List[Tuple[float, float]],
    min_x: float,
    min_y: float,
    tile: Dict[str, Any],
    scale_mm_per_m: float,
    scale: float
):
    """Малює центральну лінію"""
    canvas_obj.setStrokeColor(green)
    canvas_obj.setLineWidth(0.2)
    canvas_obj.setDash([5, 5])
    
    # Центральна лінія: x = 0
    x_mm = 0.0
    y_start_mm = 0.0
    y_end_mm = (max(y for x, y in points) - min_y) * scale_mm_per_m
    
    if tile['x_start_mm'] <= x_mm < tile['x_start_mm'] + tile['width_mm']:
        page_x = (x_mm - tile['x_start_mm'] + tile['page_x_mm']) * mm * scale
        page_y_start = max(0, (y_start_mm - tile['y_start_mm'] + tile['page_y_mm']) * mm * scale)
        page_y_end = min(
            tile['height_mm'] * mm * scale,
            (y_end_mm - tile['y_start_mm'] + tile['page_y_mm']) * mm * scale
        )
        canvas_obj.line(page_x, page_y_start, page_x, page_y_end)
    
    canvas_obj.setDash()


def _draw_overlap_markers(
    canvas_obj,
    tile: Dict[str, Any],
    tiles: List[Dict[str, Any]],
    page_size: Tuple[float, float],
    overlap_mm: float
):
    """Малює мітки для склейки сторінок (overlap markers)"""
    canvas_obj.setStrokeColor(blue)
    canvas_obj.setLineWidth(0.5)
    
    page_width_mm = page_size[0] * 25.4 / 72
    page_height_mm = page_size[1] * 25.4 / 72
    
    # Знаходимо максимальні індекси
    max_row = max(t['row'] for t in tiles)
    max_col = max(t['col'] for t in tiles)
    
    # Мітки на краях сторінки
    marker_length = 5.0  # мм
    
    # Верхній край
    if tile['row'] > 0:
        for x in [overlap_mm, page_width_mm / 2, page_width_mm - overlap_mm]:
            canvas_obj.line(
                x * mm, (page_height_mm - overlap_mm) * mm,
                x * mm, (page_height_mm - overlap_mm + marker_length) * mm
            )
    
    # Нижній край
    if tile['row'] < max_row:
        for x in [overlap_mm, page_width_mm / 2, page_width_mm - overlap_mm]:
            canvas_obj.line(
                x * mm, overlap_mm * mm,
                x * mm, (overlap_mm - marker_length) * mm
            )
    
    # Лівий край
    if tile['col'] > 0:
        for y in [overlap_mm, page_height_mm / 2, page_height_mm - overlap_mm]:
            canvas_obj.line(
                overlap_mm * mm, y * mm,
                (overlap_mm - marker_length) * mm, y * mm
            )
    
    # Правий край
    if tile['col'] < max_col:
        for y in [overlap_mm, page_height_mm / 2, page_height_mm - overlap_mm]:
            canvas_obj.line(
                (page_width_mm - overlap_mm) * mm, y * mm,
                (page_width_mm - overlap_mm + marker_length) * mm, y * mm
            )


def _draw_page_info(
    canvas_obj,
    tile: Dict[str, Any],
    total_pages: int,
    max_cols: int,
    pattern_type: str,
    page_size: Tuple[float, float],
    margin_mm: float
):
    """Додає інформацію про сторінку"""
    canvas_obj.setFillColor(black)
    canvas_obj.setFont("Helvetica", 8)
    
    page_width_mm = page_size[0] * 25.4 / 72
    page_height_mm = page_size[1] * 25.4 / 72
    
    page_num = tile['row'] * max_cols + tile['col'] + 1
    
    # Номер сторінки
    text = f"Сторінка {page_num}/{total_pages} | {pattern_type}"
    canvas_obj.drawString(
        margin_mm * mm,
        (page_height_mm - margin_mm - 5) * mm,
        text
    )
    
    # Координати tile
    coord_text = f"Tile: R{tile['row']} C{tile['col']}"
    canvas_obj.drawString(
        margin_mm * mm,
        margin_mm * mm,
        coord_text
    )

