"""
Допоміжний модуль для matplotlib 3D fallback візуалізації
"""

import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple


def create_matplotlib_3d_fallback(
    shape_code: str,
    shape_params: Dict[str, float],
    last_calculation_results: Optional[Dict[str, Any]] = None
) -> Optional[Tuple[Any, Any]]:
    """
    Створює matplotlib 3D візуалізацію як fallback, якщо Plotly недоступний
    
    Args:
        shape_code: Код форми
        shape_params: Параметри форми
        last_calculation_results: Результати останнього розрахунку (для об'єму/площі)
    
    Returns:
        Tuple (fig, ax) matplotlib об'єкти або None, None якщо не вдалося
    """
    try:
        from balloon.gui.matplotlib_utils import get_plt
        
        plt = get_plt()
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Налаштування темної теми
        _setup_dark_theme_3d(fig, ax)
        
        # Створюємо mesh для форми
        if shape_code == 'sphere':
            _create_sphere_mesh_matplotlib(ax, shape_params)
        elif shape_code == 'pillow':
            _create_pillow_mesh_matplotlib(ax, shape_params, last_calculation_results)
        elif shape_code == 'pear':
            _create_pear_mesh_matplotlib(ax, shape_params)
        elif shape_code == 'cigar':
            _create_cigar_mesh_matplotlib(ax, shape_params)
        else:
            logging.warning(f"Невідома форма для matplotlib fallback: {shape_code}")
            return None, None
        
        # Налаштування осей та масштабу
        _setup_axes_and_scale(ax, shape_code, shape_params, last_calculation_results)
        
        # Додаємо інформацію про об'єм та площу
        _add_volume_surface_info(ax, last_calculation_results)
        
        plt.tight_layout()
        plt.show()
        
        return fig, ax
    except Exception as e:
        logging.error(f"Помилка створення matplotlib 3D fallback: {e}", exc_info=True)
        return None, None


def _setup_dark_theme_3d(fig, ax):
    """Налаштовує темну тему для matplotlib 3D"""
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#1e1e1e')
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('#333333')
    ax.yaxis.pane.set_edgecolor('#333333')
    ax.zaxis.pane.set_edgecolor('#333333')
    ax.xaxis.label.set_color('#ffffff')
    ax.yaxis.label.set_color('#ffffff')
    ax.zaxis.label.set_color('#ffffff')
    ax.tick_params(colors='#ffffff')
    ax.grid(True, color='#444444', linestyle='--', alpha=0.3)


def _create_sphere_mesh_matplotlib(ax, shape_params: Dict[str, float]):
    """Створює mesh сфери для matplotlib"""
    try:
        from balloon.shapes.profile import get_shape_profile
        profile = get_shape_profile('sphere', shape_params)
        if profile:
            x, y, z = profile.generate_mesh(num_theta=50, num_z=50, center_at_origin=False)
            ax.plot_surface(x, y, z, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
            radius = shape_params.get('radius', 1.0)
            ax.set_title(f'Сферична куля\nРадіус: {radius:.2f} м', color='#ffffff', fontsize=14, fontweight='bold')
            return
    except Exception as e:
        logging.warning(f"Не вдалося використати profile-based mesh для сфери: {e}, використовуємо просту апроксимацію")
    
    # Fallback на просту апроксимацію
    radius = shape_params.get('radius', 1.0)
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
    ax.set_title(f'Сферична куля (апроксимація)\nРадіус: {radius:.2f} м', color='#ffffff', fontsize=14, fontweight='bold')


def _create_pillow_mesh_matplotlib(ax, shape_params: Dict[str, float], last_results: Optional[Dict[str, Any]]):
    """Створює mesh подушки для matplotlib"""
    length = shape_params.get('pillow_len', 3.0)
    width = shape_params.get('pillow_wid', 2.0)
    
    # Товщина розраховується з об'єму
    if last_results:
        volume = last_results.get('required_volume', 0)
        if volume > 0:
            thickness = volume / (length * width)
        else:
            thickness = shape_params.get('thickness', width * 0.3)
    else:
        thickness = shape_params.get('thickness', width * 0.3)
    
    # Еліпсоїдна форма
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    u_grid, v_grid = np.meshgrid(u, v)
    
    a = length / 2
    b = width / 2
    c = thickness / 2
    
    x = a * np.cos(u_grid) * np.sin(v_grid)
    y = b * np.sin(u_grid) * np.sin(v_grid)
    z = c * np.cos(v_grid)
    
    x = x - a + length / 2
    y = y - b + width / 2
    z = z - c + thickness / 2
    
    ax.plot_surface(x, y, z, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
    ax.set_title(
        f'Подушкоподібна куля (надута)\nДовжина: {length:.2f} м, Ширина: {width:.2f} м, Товщина: {thickness:.2f} м',
        color='#ffffff', fontsize=14, fontweight='bold'
    )


def _create_pear_mesh_matplotlib(ax, shape_params: Dict[str, float]):
    """Створює mesh груші для matplotlib"""
    try:
        from balloon.shapes.profile import get_shape_profile
        profile = get_shape_profile('pear', shape_params)
        if profile:
            x, y, z = profile.generate_mesh(num_theta=50, num_z=50, center_at_origin=False)
            ax.plot_surface(x, y, z, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
            height = shape_params.get('pear_height', 3.0)
            top_radius = shape_params.get('pear_top_radius', 1.2)
            bottom_radius = shape_params.get('pear_bottom_radius', 0.6)
            ax.set_title(
                f'Грушоподібна куля\nВисота: {height:.2f} м, Верхній радіус: {top_radius:.2f} м, Нижній радіус: {bottom_radius:.2f} м',
                color='#ffffff', fontsize=14, fontweight='bold'
            )
            return
    except Exception as e:
        logging.warning(f"Не вдалося використати profile-based mesh для груші: {e}, використовуємо просту апроксимацію")
    
    # Fallback на просту апроксимацію
    height = shape_params.get('pear_height', 3.0)
    top_radius = shape_params.get('pear_top_radius', 1.2)
    bottom_radius = shape_params.get('pear_bottom_radius', 0.6)
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, 1, 50)
    u_grid, v_grid = np.meshgrid(u, v)
    r_at_height = top_radius * (1 - v_grid) + bottom_radius * v_grid
    x = r_at_height * np.cos(u_grid)
    y = r_at_height * np.sin(u_grid)
    z = height * v_grid
    ax.plot_surface(x, y, z, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
    ax.set_title(f'Грушоподібна куля (апроксимація)\nВисота: {height:.2f} м', color='#ffffff', fontsize=14, fontweight='bold')


def _create_cigar_mesh_matplotlib(ax, shape_params: Dict[str, float]):
    """Створює mesh сигари для matplotlib"""
    try:
        from balloon.shapes.profile import get_shape_profile
        profile = get_shape_profile('cigar', shape_params)
        if profile:
            x, y, z = profile.generate_mesh(num_theta=50, num_z=50, center_at_origin=False)
            ax.plot_surface(x, y, z, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
            length = shape_params.get('cigar_length', 5.0)
            radius = shape_params.get('cigar_radius', 1.0)
            ax.set_title(f'Сигароподібна куля\nДовжина: {length:.2f} м, Радіус: {radius:.2f} м', color='#ffffff', fontsize=14, fontweight='bold')
            return
    except Exception as e:
        logging.warning(f"Не вдалося використати profile-based mesh для сигари: {e}, використовуємо просту апроксимацію")
    
    # Fallback на просту апроксимацію
    length = shape_params.get('cigar_length', 5.0)
    radius = shape_params.get('cigar_radius', 1.0)
    cylinder_length = max(0, length - 2 * radius)
    if cylinder_length > 0:
        u_cyl = np.linspace(0, 2 * np.pi, 50)
        z_cyl = np.linspace(radius, length - radius, 50)
        u_grid_cyl, z_grid_cyl = np.meshgrid(u_cyl, z_cyl)
        x_cyl = radius * np.cos(u_grid_cyl)
        y_cyl = radius * np.sin(u_grid_cyl)
        z_cyl = z_grid_cyl
        ax.plot_surface(x_cyl, y_cyl, z_cyl, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi / 2, 25)
    u_grid, v_grid = np.meshgrid(u, v)
    x1 = radius * np.cos(u_grid) * np.sin(v_grid)
    y1 = radius * np.sin(u_grid) * np.sin(v_grid)
    z1 = radius * (1 - np.cos(v_grid))
    ax.plot_surface(x1, y1, z1, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
    x2 = radius * np.cos(u_grid) * np.sin(v_grid)
    y2 = radius * np.sin(u_grid) * np.sin(v_grid)
    z2 = (length - radius) + radius * np.cos(v_grid)
    ax.plot_surface(x2, y2, z2, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
    ax.set_title(f'Сигароподібна куля (апроксимація)\nДовжина: {length:.2f} м', color='#ffffff', fontsize=14, fontweight='bold')


def _setup_axes_and_scale(ax, shape_code: str, shape_params: Dict[str, float], last_results: Optional[Dict[str, Any]]):
    """Налаштовує осі та масштаб для matplotlib 3D"""
    ax.set_xlabel('X (м)', fontsize=10)
    ax.set_ylabel('Y (м)', fontsize=10)
    ax.set_zlabel('Z (м)', fontsize=10)
    
    if shape_code == 'sphere':
        max_range = shape_params.get('radius', 1.0) * 1.2
        ax.set_xlim([-max_range, max_range])
        ax.set_ylim([-max_range, max_range])
        ax.set_zlim([-max_range, max_range])
    elif shape_code == 'pillow':
        length = shape_params.get('pillow_len', 3.0)
        width = shape_params.get('pillow_wid', 2.0)
        if last_results:
            volume = last_results.get('required_volume', 0)
            if volume > 0:
                thickness = volume / (length * width)
            else:
                thickness = shape_params.get('thickness', width * 0.3)
        else:
            thickness = shape_params.get('thickness', width * 0.3)
        ax.set_xlim([0, length * 1.1])
        ax.set_ylim([0, width * 1.1])
        ax.set_zlim([0, thickness * 1.1])
    elif shape_code == 'pear':
        height = shape_params.get('pear_height', 3.0)
        max_radius = max(shape_params.get('pear_top_radius', 1.2), shape_params.get('pear_bottom_radius', 0.6))
        max_range = max(height, max_radius * 2) * 1.2
        ax.set_xlim([-max_range, max_range])
        ax.set_ylim([-max_range, max_range])
        ax.set_zlim([0, height * 1.1])
    elif shape_code == 'cigar':
        length = shape_params.get('cigar_length', 5.0)
        radius = shape_params.get('cigar_radius', 1.0)
        max_range = max(length, radius * 2) * 1.2
        ax.set_xlim([-max_range, max_range])
        ax.set_ylim([-max_range, max_range])
        ax.set_zlim([0, length * 1.1])


def _add_volume_surface_info(ax, last_results: Optional[Dict[str, Any]]):
    """Додає інформацію про об'єм та площу до графіка"""
    if last_results:
        volume = last_results.get('required_volume', 0)
        surface = last_results.get('surface_area', 0)
        if volume > 0 or surface > 0:
            info_text = f"Об'єм: {volume:.2f} м³\nПлоща поверхні: {surface:.2f} м²"
            ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes,
                     fontsize=10, verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='#2a2a2a', alpha=0.8),
                     color='#ffffff')

