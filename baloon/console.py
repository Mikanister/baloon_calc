"""
Модуль для консольного виводу через Rich
"""

from typing import Dict, Any, Optional, List

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def print_results_table(results: Dict[str, Any], title: str = "Результати розрахунку") -> None:
    """
    Виводить результати розрахунку у вигляді красивої таблиці
    
    Args:
        results: Словник з результатами
        title: Заголовок таблиці
    """
    if not RICH_AVAILABLE:
        # Fallback на простий вивід
        print(f"\n{title}")
        print("=" * 60)
        for key, value in results.items():
            print(f"{key}: {value}")
        return
    
    console = Console()
    
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Параметр", style="cyan", no_wrap=True)
    table.add_column("Значення", style="green")
    table.add_column("Одиниця", style="yellow")
    
    # Основні параметри
    if 'required_volume' in results:
        table.add_row("Об'єм кулі", f"{results['required_volume']:.4f}", "м³")
    if 'surface_area' in results:
        table.add_row("Площа поверхні", f"{results['surface_area']:.4f}", "м²")
    if 'envelope_mass' in results:
        table.add_row("Маса оболонки", f"{results['envelope_mass']:.4f}", "кг")
    if 'total_mass' in results:
        table.add_row("Загальна маса", f"{results['total_mass']:.4f}", "кг")
    if 'lift' in results:
        table.add_row("Підйомна сила (початок)", f"{results['lift']:.4f}", "Н")
    if 'lift_end' in results:
        table.add_row("Підйомна сила (кінець)", f"{results['lift_end']:.4f}", "Н")
    if 'payload' in results:
        table.add_row("Корисне навантаження", f"{results['payload']:.4f}", "кг")
    
    console.print(table)


def print_material_comparison(comparison: List[Dict[str, Any]]) -> None:
    """
    Виводить порівняння матеріалів у вигляді таблиці
    
    Args:
        comparison: Список словників з даними про матеріали
    """
    if not RICH_AVAILABLE:
        print("\nПорівняння матеріалів:")
        for item in comparison:
            print(f"{item.get('material', 'N/A')}: {item.get('payload', 0):.2f} кг")
        return
    
    console = Console()
    
    table = Table(title="Порівняння матеріалів", show_header=True, header_style="bold blue")
    table.add_column("Матеріал", style="cyan")
    table.add_column("Навантаження", style="green", justify="right")
    table.add_column("Маса оболонки", style="yellow", justify="right")
    table.add_column("Площа", style="magenta", justify="right")
    
    for item in comparison:
        material = item.get('material', 'N/A')
        payload = item.get('payload', 0)
        mass = item.get('envelope_mass', 0)
        area = item.get('surface_area', 0)
        
        table.add_row(
            material,
            f"{payload:.4f} кг",
            f"{mass:.4f} кг",
            f"{area:.4f} м²"
        )
    
    console.print(table)


def print_progress(message: str, total: Optional[int] = None):
    """
    Створює контекстний менеджер для відображення прогресу
    
    Args:
        message: Повідомлення про прогрес
        total: Загальна кількість кроків (опціонально)
    
    Returns:
        Progress контекстний менеджер
    """
    if not RICH_AVAILABLE:
        # Простий fallback
        class SimpleProgress:
            def __enter__(self):
                print(message)
                return self
            
            def __exit__(self, *args):
                pass
            
            def update(self, *args, **kwargs):
                pass
        
        return SimpleProgress()
    
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=Console()
    )
    
    task = progress.add_task(message, total=total)
    progress.start()
    
    return progress


def print_info_panel(title: str, content: str, style: str = "blue") -> None:
    """
    Виводить інформаційну панель
    
    Args:
        title: Заголовок панелі
        content: Вміст панелі
        style: Стиль панелі
    """
    if not RICH_AVAILABLE:
        print(f"\n{title}")
        print("=" * len(title))
        print(content)
        return
    
    console = Console()
    panel = Panel(content, title=title, border_style=style)
    console.print(panel)


def is_rich_available() -> bool:
    """Перевіряє, чи доступний Rich"""
    return RICH_AVAILABLE

