"""
Утиліти для роботи з консоллю та логуванням
"""

from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def get_console() -> Optional['Console']:
    """Повертає Rich Console, якщо доступний"""
    if RICH_AVAILABLE:
        return Console()
    return None


def print_results_table(results: dict, title: str = "Результати розрахунку"):
    """
    Виводить результати розрахунку у вигляді красивої таблиці через Rich
    
    Args:
        results: Словник з результатами
        title: Заголовок таблиці
    """
    if not RICH_AVAILABLE:
        # Fallback на звичайний print
        print(f"\n{title}:")
        for key, value in results.items():
            print(f"  {key}: {value}")
        return
    
    console = Console()
    table = Table(title=title, box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Параметр", style="cyan", no_wrap=True)
    table.add_column("Значення", style="green")
    table.add_column("Одиниця", style="yellow")
    
    # Додаємо основні параметри
    if 'required_volume' in results:
        table.add_row("Об'єм кулі", f"{results['required_volume']:.4f}", "м³")
    if 'surface_area' in results:
        table.add_row("Площа поверхні", f"{results['surface_area']:.4f}", "м²")
    if 'envelope_mass' in results:
        table.add_row("Маса оболонки", f"{results['envelope_mass']:.4f}", "кг")
    if 'total_mass' in results:
        table.add_row("Загальна маса", f"{results['total_mass']:.4f}", "кг")
    if 'lift' in results:
        table.add_row("Підйомна сила", f"{results['lift']:.4f}", "Н")
    if 'payload' in results:
        table.add_row("Корисне навантаження", f"{results['payload']:.4f}", "кг")
    
    console.print(table)


def print_error(message: str, details: Optional[str] = None):
    """
    Виводить помилку через Rich
    
    Args:
        message: Повідомлення про помилку
        details: Деталі помилки (опціонально)
    """
    if not RICH_AVAILABLE:
        print(f"Помилка: {message}")
        if details:
            print(f"Деталі: {details}")
        return
    
    console = Console()
    error_text = f"[bold red]Помилка:[/bold red] {message}"
    if details:
        error_text += f"\n[dim]{details}[/dim]"
    console.print(Panel(error_text, title="Помилка", border_style="red"))


def print_success(message: str):
    """
    Виводить успішне повідомлення через Rich
    
    Args:
        message: Повідомлення
    """
    if not RICH_AVAILABLE:
        print(f"[OK] {message}")
        return
    
    console = Console()
    console.print(f"[bold green][OK][/bold green] {message}")


def print_warning(message: str):
    """
    Виводить попередження через Rich
    
    Args:
        message: Повідомлення
    """
    if not RICH_AVAILABLE:
        print(f"[WARNING] {message}")
        return
    
    console = Console()
    console.print(f"[bold yellow][WARNING][/bold yellow] {message}")


def create_progress() -> Optional['Progress']:
    """
    Створює Rich Progress об'єкт для відображення прогресу
    
    Returns:
        Progress об'єкт або None, якщо Rich недоступний
    """
    if not RICH_AVAILABLE:
        return None
    
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=Console()
    )

