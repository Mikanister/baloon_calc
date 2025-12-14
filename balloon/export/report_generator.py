"""
Генерація звітів про розрахунки (PDF та HTML)

Створює детальні звіти з:
- Вхідними параметрами
- Припущеннями моделі
- Mass & lift budget
- Safety margins
- Згенерованими файлами викрійок
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import black, darkblue, darkgreen, darkred
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_pdf_report(
    results: Dict[str, Any],
    inputs: Dict[str, Any],
    assumptions: Optional[List[Dict[str, Any]]] = None,
    pattern_files: Optional[List[str]] = None,
    filename: Optional[str] = None
) -> str:
    """
    Генерує PDF звіт з результатами розрахунку
    
    Args:
        results: Результати розрахунків
        inputs: Вхідні параметри
        assumptions: Список припущень (опціонально)
        pattern_files: Список шляхів до згенерованих файлів викрійок (опціонально)
        filename: Ім'я файлу (якщо None, генерується автоматично)
    
    Returns:
        Шлях до збереженого PDF файлу
    
    Raises:
        ImportError: Якщо reportlab не встановлено
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError(
            "Для генерації PDF звітів потрібна бібліотека reportlab. "
            "Встановіть: pip install reportlab"
        )
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"balloon_report_{timestamp}.pdf"
    
    # Створюємо PDF документ
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Стилі
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=darkblue,
        spaceAfter=12,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=darkblue,
        spaceAfter=6,
        spaceBefore=12
    )
    
    # Заголовок
    story.append(Paragraph("ЗВІТ ПО РОЗРАХУНКУ АЕРОСТАТА", title_style))
    story.append(Paragraph(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # 1. Вхідні параметри
    story.append(Paragraph("1. ВХІДНІ ПАРАМЕТРИ", heading_style))
    
    input_data = [
        ['Параметр', 'Значення', 'Одиниця'],
        ['Режим розрахунку', inputs.get('mode', 'N/A'), ''],
        ['Тип газу', inputs.get('gas_type', 'N/A'), ''],
        ['Матеріал оболонки', inputs.get('material', 'N/A'), ''],
        ['Товщина оболонки', f"{inputs.get('thickness', 0):.1f}", 'мкм'],
        ['Висота пуску', f"{inputs.get('start_height', 0):.1f}", 'м'],
        ['Висота польоту', f"{inputs.get('work_height', 0):.1f}", 'м'],
    ]
    
    if inputs.get('gas_type') == "Гаряче повітря":
        input_data.append(['Температура на землі', f"{inputs.get('ground_temp', 0):.1f}", '°C'])
        input_data.append(['Температура всередині', f"{inputs.get('inside_temp', 0):.1f}", '°C'])
    
    if 'shape_type' in inputs:
        input_data.append(['Форма', inputs.get('shape_type', 'N/A'), ''])
        shape_params = inputs.get('shape_params', {})
        for key, value in shape_params.items():
            input_data.append([f"  - {key}", f"{value:.3f}", 'м'])
    
    input_table = Table(input_data, colWidths=[80*mm, 60*mm, 30*mm])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    story.append(input_table)
    story.append(Spacer(1, 12))
    
    # 2. Результати розрахунків
    story.append(Paragraph("2. РЕЗУЛЬТАТИ РОЗРАХУНКІВ", heading_style))
    
    results_data = [
        ['Параметр', 'Значення', 'Одиниця'],
        ['Об\'єм кулі', f"{results.get('required_volume', 0):.4f}", 'м³'],
        ['Площа поверхні', f"{results.get('surface_area', 0):.4f}", 'м²'],
        ['Корисне навантаження', f"{results.get('payload', 0):.4f}", 'кг'],
        ['Маса оболонки', f"{results.get('mass_shell', 0):.4f}", 'кг'],
        ['Підйомна сила', f"{results.get('lift', 0):.4f}", 'кг'],
    ]
    
    if 'radius' in results:
        results_data.append(['Радіус кулі', f"{results.get('radius', 0):.4f}", 'м'])
    
    if 'stress' in results and results.get('stress', 0) > 0:
        safety_factor = results.get('stress_limit', 0) / results.get('stress', 1) if results.get('stress', 0) > 0 else 0
        results_data.append(['Максимальна напруга', f"{results.get('stress', 0) / 1e6:.2f}", 'МПа'])
        results_data.append(['Допустима напруга', f"{results.get('stress_limit', 0) / 1e6:.1f}", 'МПа'])
        results_data.append(['Коефіцієнт безпеки', f"{safety_factor:.2f}", ''])
    
    results_table = Table(results_data, colWidths=[80*mm, 60*mm, 30*mm])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    story.append(results_table)
    story.append(Spacer(1, 12))
    
    # 3. Mass & Lift Budget
    if 'mass_budget' in results and 'lift_budget' in results:
        story.append(Paragraph("3. БЮДЖЕТ МАСИ ТА ПІДЙОМНОЇ СИЛИ", heading_style))
        
        mass_budget = results.get('mass_budget', {})
        lift_budget = results.get('lift_budget', {})
        
        budget_data = [
            ['Компонент', 'Маса (кг)', 'Підйомна сила (кг)'],
            ['Валова підйомна сила', '-', f"{lift_budget.get('gross_lift', 0):.4f}"],
            ['Маса газу', f"{mass_budget.get('gas_mass', 0):.4f}", f"-{mass_budget.get('gas_mass', 0):.4f}"],
            ['Чиста підйомна сила', '-', f"{lift_budget.get('net_lift', 0):.4f}"],
            ['Маса оболонки', f"{mass_budget.get('envelope_mass', 0):.4f}", '-'],
            ['Маса швів', f"{mass_budget.get('seams_mass', 0):.4f}", '-'],
            ['Додаткова маса', f"{mass_budget.get('extra_mass', 0):.4f}", '-'],
            ['Структурна маса', f"{mass_budget.get('structural_mass', 0):.4f}", '-'],
            ['Корисне навантаження', f"{mass_budget.get('payload_mass', 0):.4f}", '-'],
            ['Запас безпеки', f"{mass_budget.get('safety_margin_mass', 0):.4f}", '-'],
            ['Використана підйомна сила', '-', f"{lift_budget.get('used_lift', 0):.4f}"],
            ['Залишкова підйомна сила', '-', f"{lift_budget.get('remaining_lift', 0):.4f}"],
            ['Загальна маса', f"{mass_budget.get('total_mass', 0):.4f}", '-'],
        ]
        
        budget_table = Table(budget_data, colWidths=[80*mm, 50*mm, 50*mm])
        budget_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(budget_table)
        story.append(Spacer(1, 12))
    
    # 4. Припущення моделі
    if assumptions:
        story.append(PageBreak())
        story.append(Paragraph("4. ФІЗИЧНІ ПРИПУЩЕННЯ МОДЕЛІ", heading_style))
        story.append(Paragraph(
            "Цей розрахунок базується на наступних припущеннях та моделях:",
            styles['Normal']
        ))
        story.append(Spacer(1, 6))
        
        for i, assumption in enumerate(assumptions, 1):
            category = assumption.get('category', '')
            name = assumption.get('name', '')
            description = assumption.get('description', '')
            
            story.append(Paragraph(
                f"<b>{i}. {name}</b> ({category})",
                styles['Heading3']
            ))
            story.append(Paragraph(description, styles['Normal']))
            story.append(Spacer(1, 6))
    
    # 5. Згенеровані файли
    if pattern_files:
        story.append(PageBreak())
        story.append(Paragraph("5. ЗГЕНЕРОВАНІ ФАЙЛИ ВИКРІЙОК", heading_style))
        
        files_data = [['№', 'Файл', 'Тип']]
        for i, filepath in enumerate(pattern_files, 1):
            filename_only = os.path.basename(filepath)
            file_ext = os.path.splitext(filename_only)[1].upper()
            files_data.append([str(i), filename_only, file_ext])
        
        files_table = Table(files_data, colWidths=[20*mm, 100*mm, 50*mm])
        files_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(files_table)
    
    # Зберігаємо PDF
    doc.build(story)
    return os.path.abspath(filename)


def generate_html_report(
    results: Dict[str, Any],
    inputs: Dict[str, Any],
    assumptions: Optional[List[Dict[str, Any]]] = None,
    pattern_files: Optional[List[str]] = None,
    filename: Optional[str] = None
) -> str:
    """
    Генерує HTML звіт з результатами розрахунку
    
    Args:
        results: Результати розрахунків
        inputs: Вхідні параметри
        assumptions: Список припущень (опціонально)
        pattern_files: Список шляхів до згенерованих файлів викрійок (опціонально)
        filename: Ім'я файлу (якщо None, генерується автоматично)
    
    Returns:
        Шлях до збереженого HTML файлу
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"balloon_report_{timestamp}.html"
    
    html_lines = [
        '<!DOCTYPE html>',
        '<html lang="uk">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '    <title>Звіт по розрахунку аеростата</title>',
        '    <style>',
        '        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }',
        '        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }',
        '        h1 { color: #1a5490; text-align: center; border-bottom: 3px solid #1a5490; padding-bottom: 10px; }',
        '        h2 { color: #2c5f8d; margin-top: 30px; border-left: 4px solid #2c5f8d; padding-left: 10px; }',
        '        h3 { color: #4a7ba7; margin-top: 20px; }',
        '        table { width: 100%; border-collapse: collapse; margin: 15px 0; }',
        '        th { background: #2c5f8d; color: white; padding: 10px; text-align: left; }',
        '        td { padding: 8px; border: 1px solid #ddd; }',
        '        tr:nth-child(even) { background: #f9f9f9; }',
        '        .budget-table th { background: #2d8659; }',
        '        .budget-table tr:nth-child(even) { background: #e8f5e9; }',
        '        .results-table th { background: #4a7ba7; }',
        '        .results-table tr:nth-child(even) { background: #e3f2fd; }',
        '        .assumption { margin: 15px 0; padding: 10px; background: #fff9e6; border-left: 3px solid #ffc107; }',
        '        .footer { margin-top: 40px; text-align: center; color: #666; font-size: 0.9em; }',
        '    </style>',
        '</head>',
        '<body>',
        '    <div class="container">',
        f'        <h1>ЗВІТ ПО РОЗРАХУНКУ АЕРОСТАТА</h1>',
        f'        <p style="text-align: center; color: #666;">Дата: {datetime.now().strftime("%d.%m.%Y %H:%M")}</p>',
    ]
    
    # 1. Вхідні параметри
    html_lines.extend([
        '        <h2>1. Вхідні параметри</h2>',
        '        <table>',
        '            <tr><th>Параметр</th><th>Значення</th><th>Одиниця</th></tr>',
        f'            <tr><td>Режим розрахунку</td><td>{inputs.get("mode", "N/A")}</td><td></td></tr>',
        f'            <tr><td>Тип газу</td><td>{inputs.get("gas_type", "N/A")}</td><td></td></tr>',
        f'            <tr><td>Матеріал оболонки</td><td>{inputs.get("material", "N/A")}</td><td></td></tr>',
        f'            <tr><td>Товщина оболонки</td><td>{inputs.get("thickness", 0):.1f}</td><td>мкм</td></tr>',
        f'            <tr><td>Висота пуску</td><td>{inputs.get("start_height", 0):.1f}</td><td>м</td></tr>',
        f'            <tr><td>Висота польоту</td><td>{inputs.get("work_height", 0):.1f}</td><td>м</td></tr>',
    ])
    
    if inputs.get('gas_type') == "Гаряче повітря":
        html_lines.extend([
            f'            <tr><td>Температура на землі</td><td>{inputs.get("ground_temp", 0):.1f}</td><td>°C</td></tr>',
            f'            <tr><td>Температура всередині</td><td>{inputs.get("inside_temp", 0):.1f}</td><td>°C</td></tr>',
        ])
    
    html_lines.append('        </table>')
    
    # 2. Результати
    html_lines.extend([
        '        <h2>2. Результати розрахунків</h2>',
        '        <table class="results-table">',
        '            <tr><th>Параметр</th><th>Значення</th><th>Одиниця</th></tr>',
        f'            <tr><td>Об\'єм кулі</td><td>{results.get("required_volume", 0):.4f}</td><td>м³</td></tr>',
        f'            <tr><td>Площа поверхні</td><td>{results.get("surface_area", 0):.4f}</td><td>м²</td></tr>',
        f'            <tr><td>Корисне навантаження</td><td>{results.get("payload", 0):.4f}</td><td>кг</td></tr>',
        f'            <tr><td>Маса оболонки</td><td>{results.get("mass_shell", 0):.4f}</td><td>кг</td></tr>',
        f'            <tr><td>Підйомна сила</td><td>{results.get("lift", 0):.4f}</td><td>кг</td></tr>',
    ])
    
    if 'radius' in results:
        html_lines.append(f'            <tr><td>Радіус кулі</td><td>{results.get("radius", 0):.4f}</td><td>м</td></tr>')
    
    html_lines.append('        </table>')
    
    # 3. Mass & Lift Budget
    if 'mass_budget' in results and 'lift_budget' in results:
        mass_budget = results.get('mass_budget', {})
        lift_budget = results.get('lift_budget', {})
        
        html_lines.extend([
            '        <h2>3. Бюджет маси та підйомної сили</h2>',
            '        <table class="budget-table">',
            '            <tr><th>Компонент</th><th>Маса (кг)</th><th>Підйомна сила (кг)</th></tr>',
            f'            <tr><td>Валова підйомна сила</td><td>-</td><td>{lift_budget.get("gross_lift", 0):.4f}</td></tr>',
            f'            <tr><td>Маса газу</td><td>{mass_budget.get("gas_mass", 0):.4f}</td><td>-{mass_budget.get("gas_mass", 0):.4f}</td></tr>',
            f'            <tr><td>Чиста підйомна сила</td><td>-</td><td>{lift_budget.get("net_lift", 0):.4f}</td></tr>',
            f'            <tr><td>Маса оболонки</td><td>{mass_budget.get("envelope_mass", 0):.4f}</td><td>-</td></tr>',
            f'            <tr><td>Маса швів</td><td>{mass_budget.get("seams_mass", 0):.4f}</td><td>-</td></tr>',
            f'            <tr><td>Додаткова маса</td><td>{mass_budget.get("extra_mass", 0):.4f}</td><td>-</td></tr>',
            f'            <tr><td>Структурна маса</td><td>{mass_budget.get("structural_mass", 0):.4f}</td><td>-</td></tr>',
            f'            <tr><td>Корисне навантаження</td><td>{mass_budget.get("payload_mass", 0):.4f}</td><td>-</td></tr>',
            f'            <tr><td>Запас безпеки</td><td>{mass_budget.get("safety_margin_mass", 0):.4f}</td><td>-</td></tr>',
            f'            <tr><td>Використана підйомна сила</td><td>-</td><td>{lift_budget.get("used_lift", 0):.4f}</td></tr>',
            f'            <tr><td>Залишкова підйомна сила</td><td>-</td><td>{lift_budget.get("remaining_lift", 0):.4f}</td></tr>',
            f'            <tr><td>Загальна маса</td><td>{mass_budget.get("total_mass", 0):.4f}</td><td>-</td></tr>',
            '        </table>',
        ])
    
    # 4. Припущення
    if assumptions:
        html_lines.append('        <h2>4. Фізичні припущення моделі</h2>')
        html_lines.append('        <p>Цей розрахунок базується на наступних припущеннях та моделях:</p>')
        
        for i, assumption in enumerate(assumptions, 1):
            category = assumption.get('category', '')
            name = assumption.get('name', '')
            description = assumption.get('description', '')
            
            html_lines.extend([
                f'        <div class="assumption">',
                f'            <h3>{i}. {name} ({category})</h3>',
                f'            <p>{description}</p>',
                '        </div>',
            ])
    
    # 5. Файли
    if pattern_files:
        html_lines.extend([
            '        <h2>5. Згенеровані файли викрійок</h2>',
            '        <table>',
            '            <tr><th>№</th><th>Файл</th><th>Тип</th></tr>',
        ])
        
        for i, filepath in enumerate(pattern_files, 1):
            filename_only = os.path.basename(filepath)
            file_ext = os.path.splitext(filename_only)[1].upper()
            html_lines.append(f'            <tr><td>{i}</td><td>{filename_only}</td><td>{file_ext}</td></tr>')
        
        html_lines.append('        </table>')
    
    html_lines.extend([
        '        <div class="footer">',
        f'            <p>Згенеровано: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}</p>',
        '        </div>',
        '    </div>',
        '</body>',
        '</html>',
    ])
    
    # Зберігаємо HTML
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_lines))
    
    return os.path.abspath(filename)

