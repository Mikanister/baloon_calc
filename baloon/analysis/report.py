"""
Генерація звітів
"""

from typing import Dict, Any


def generate_report(results: Dict[str, Any], mode: str, inputs: Dict[str, Any]) -> str:
    """
    Генерує текстовий звіт з результатами
    
    Args:
        results: Результати розрахунків
        mode: Режим розрахунку
        inputs: Вхідні параметри
    
    Returns:
        Текстовий звіт
    """
    report = []
    report.append("=" * 60)
    report.append("ЗВІТ ПО РОЗРАХУНКУ АЕРОСТАТА")
    report.append("=" * 60)
    report.append("")
    
    # Вхідні параметри
    report.append("ВХІДНІ ПАРАМЕТРИ:")
    report.append("-" * 30)
    report.append(f"Режим розрахунку: {'Обʼєм ➜ навантаження' if mode == 'payload' else 'Навантаження ➜ обʼєм'}")
    report.append(f"Тип газу: {inputs['gas_type']}")
    report.append(f"Матеріал оболонки: {inputs['material']}")
    report.append(f"Товщина оболонки: {inputs['thickness']} мкм")
    report.append(f"Висота пуску: {inputs['start_height']} м")
    report.append(f"Висота польоту: {inputs['work_height']} м")
    
    if inputs['gas_type'] == "Гаряче повітря":
        report.append(f"Температура на землі: {inputs['ground_temp']} °C")
        report.append(f"Температура всередині: {inputs['inside_temp']} °C")
    
    report.append("")
    
    # Результати
    report.append("РЕЗУЛЬТАТИ РОЗРАХУНКІВ:")
    report.append("-" * 30)
    
    if mode == "volume":
        report.append(f"Потрібний обʼєм газу: {results['gas_volume']:.2f} м³")
    
    report.extend([
        f"Необхідний обʼєм кулі: {results['required_volume']:.2f} м³",
        f"Корисне навантаження: {results['payload']:.2f} кг",
        f"Маса оболонки: {results['mass_shell']:.2f} кг",
        f"Підйомна сила: {results['lift']:.2f} кг",
        f"Радіус кулі: {results['radius']:.2f} м",
        f"Площа поверхні: {results['surface_area']:.2f} м²",
        f"Щільність повітря: {results['rho_air']:.4f} кг/м³",
        f"Підйомна сила на м³: {results['net_lift_per_m3']:.4f} кг/м³"
    ])
    
    if inputs['gas_type'] == "Гаряче повітря":
        if results['stress'] > 0:
            safety_factor = results['stress_limit'] / results['stress']
        else:
            safety_factor = float('inf')
        report.extend([
            f"Температура зовні: {results['T_outside_C']:.1f} °C",
            f"Максимальна напруга: {results['stress'] / 1e6:.2f} МПа",
            f"Допустима напруга: {results['stress_limit'] / 1e6:.1f} МПа",
            f"Коефіцієнт безпеки: {'∞' if safety_factor == float('inf') else f'{safety_factor:.1f}'}"
        ])
        if safety_factor < 2:
            report.append("⚠️  УВАГА: Низький коефіцієнт безпеки!")
    
    report.append("")
    report.append("=" * 60)
    
    return '\n'.join(report)

