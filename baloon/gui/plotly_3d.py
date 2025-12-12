"""
Модуль для інтерактивної 3D візуалізації через Plotly
"""

import numpy as np

try:
    import plotly.graph_objects as go
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


def create_3d_plotly(shape_code: str, shape_params: dict, results: dict = None):
    """
    Створює інтерактивну 3D візуалізацію через Plotly
    
    Args:
        shape_code: Код форми ('sphere', 'pillow', 'pear', 'cigar')
        shape_params: Параметри форми
        results: Результати розрахунку (опціонально)
    
    Returns:
        HTML рядок або None, якщо Plotly недоступний
    """
    if not PLOTLY_AVAILABLE:
        return None
    
    # Нормалізуємо shape_code
    if shape_code is None:
        shape_code = 'sphere'
    shape_code = str(shape_code).lower().strip()
    
    # Логування для діагностики
    import logging
    logging.info(f"create_3d_plotly: shape_code={shape_code}, shape_params={shape_params}")
    
    fig = None
    
    if shape_code == 'sphere':
        fig = _create_sphere_plotly(shape_params, results)
    elif shape_code == 'pillow':
        fig = _create_pillow_plotly(shape_params, results)
    elif shape_code == 'pear':
        fig = _create_pear_plotly(shape_params, results)
    elif shape_code == 'cigar':
        fig = _create_cigar_plotly(shape_params, results)
    else:
        # Fallback на сферу, якщо форма не розпізнана
        logging.warning(f"Невідома форма: {shape_code}, використовуємо сферу")
        fig = _create_sphere_plotly(shape_params, results)
    
    if fig is None:
        logging.error("Не вдалося створити фігуру, використовуємо сферу за замовчуванням")
        fig = _create_sphere_plotly({'radius': 1.0}, results)
    
    # Налаштування макету
    fig.update_layout(
        title={
            'text': f'3D Модель: {shape_code}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'white'}
        },
        scene=dict(
            xaxis=dict(
                title='X (м)',
                backgroundcolor='rgb(20, 20, 20)',
                gridcolor='rgb(100, 100, 100)',
                showbackground=True,
            ),
            yaxis=dict(
                title='Y (м)',
                backgroundcolor='rgb(20, 20, 20)',
                gridcolor='rgb(100, 100, 100)',
                showbackground=True,
            ),
            zaxis=dict(
                title='Z (м)',
                backgroundcolor='rgb(20, 20, 20)',
                gridcolor='rgb(100, 100, 100)',
                showbackground=True,
            ),
            bgcolor='rgb(20, 20, 20)',
            aspectmode='data'
        ),
        paper_bgcolor='rgb(30, 30, 30)',
        plot_bgcolor='rgb(20, 20, 20)',
        font=dict(color='white', size=12),
        width=900,
        height=700,
    )
    
    # Додаємо інформацію про об'єм та площу, якщо є
    if results:
        volume = results.get('required_volume', 0)
        surface = results.get('surface_area', 0)
        info_text = f"Об'єм: {volume:.2f} м³<br>Площа поверхні: {surface:.2f} м²"
        fig.add_annotation(
            text=info_text,
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            xanchor="left", yanchor="top",
            bgcolor="rgba(40, 40, 40, 0.8)",
            bordercolor="rgb(74, 144, 226)",
            borderwidth=2,
            font=dict(color='white', size=11),
            showarrow=False
        )
    
    return fig


def _create_sphere_plotly(shape_params: dict, results: dict = None):
    """Створює 3D сферу через Plotly"""
    radius = shape_params.get('radius', 1.0)
    
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
    
    fig = go.Figure(data=[go.Surface(
        x=x, y=y, z=z,
        colorscale='Blues',
        showscale=False,
        opacity=0.8,
        lighting=dict(
            ambient=0.4,
            diffuse=0.8,
            specular=0.2,
            roughness=0.5
        )
    )])
    
    fig.update_layout(
        title=f'Сферична куля<br>Радіус: {radius:.2f} м'
    )
    
    return fig


def _create_pillow_plotly(shape_params: dict, results: dict = None):
    """Створює 3D подушку (еліпсоїд) через Plotly"""
    length = shape_params.get('pillow_len', 3.0)
    width = shape_params.get('pillow_wid', 2.0)
    
    # Товщина розраховується з об'єму, якщо є
    if results:
        volume = results.get('required_volume', 0)
        if volume > 0:
            thickness = volume / (length * width)
        else:
            thickness = shape_params.get('thickness', width * 0.3)
    else:
        thickness = shape_params.get('thickness', width * 0.3)
    
    # Півосі еліпсоїда
    a = length / 2
    b = width / 2
    c = thickness / 2
    
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    u_grid, v_grid = np.meshgrid(u, v)
    
    x = a * np.cos(u_grid) * np.sin(v_grid)
    y = b * np.sin(u_grid) * np.sin(v_grid)
    z = c * np.cos(v_grid)
    
    # Зсуваємо центр
    x = x - a + length / 2
    y = y - b + width / 2
    z = z - c + thickness / 2
    
    fig = go.Figure(data=[go.Surface(
        x=x, y=y, z=z,
        colorscale='Blues',
        showscale=False,
        opacity=0.8,
        lighting=dict(
            ambient=0.4,
            diffuse=0.8,
            specular=0.2,
            roughness=0.5
        )
    )])
    
    fig.update_layout(
        title=f'Подушкоподібна куля<br>Довжина: {length:.2f} м, Ширина: {width:.2f} м, Товщина: {thickness:.2f} м'
    )
    
    return fig


def _create_pear_plotly(shape_params: dict, results: dict = None):
    """Створює 3D грушу через Plotly"""
    height = shape_params.get('pear_height', 3.0)
    top_radius = shape_params.get('pear_top_radius', 1.2)
    bottom_radius = shape_params.get('pear_bottom_radius', 0.6)
    
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, 1, 50)
    u_grid, v_grid = np.meshgrid(u, v)
    
    # Радіус на кожній висоті - лінійна інтерполяція
    r_at_height = top_radius * (1 - v_grid) + bottom_radius * v_grid
    
    # Координати груші
    x = r_at_height * np.cos(u_grid)
    y = r_at_height * np.sin(u_grid)
    z = height * v_grid
    
    fig = go.Figure(data=[go.Surface(
        x=x, y=y, z=z,
        colorscale='Blues',
        showscale=False,
        opacity=0.8,
        lighting=dict(
            ambient=0.4,
            diffuse=0.8,
            specular=0.2,
            roughness=0.5
        )
    )])
    
    fig.update_layout(
        title=f'Грушоподібна куля<br>Висота: {height:.2f} м, Верхній радіус: {top_radius:.2f} м, Нижній радіус: {bottom_radius:.2f} м'
    )
    
    return fig


def _create_cigar_plotly(shape_params: dict, results: dict = None):
    """Створює 3D сигару через Plotly"""
    length = shape_params.get('cigar_length', 5.0)
    radius = shape_params.get('cigar_radius', 1.0)
    
    fig = go.Figure()
    
    # Циліндрична частина
    cylinder_length = max(0, length - 2 * radius)
    if cylinder_length > 0:
        u_cyl = np.linspace(0, 2 * np.pi, 50)
        z_cyl = np.linspace(radius, length - radius, 50)
        u_grid_cyl, z_grid_cyl = np.meshgrid(u_cyl, z_cyl)
        
        x_cyl = radius * np.cos(u_grid_cyl)
        y_cyl = radius * np.sin(u_grid_cyl)
        z_cyl = z_grid_cyl
        
        fig.add_trace(go.Surface(
            x=x_cyl, y=y_cyl, z=z_cyl,
            colorscale='Blues',
            showscale=False,
            opacity=0.8,
            lighting=dict(
                ambient=0.4,
                diffuse=0.8,
                specular=0.2,
                roughness=0.5
            )
        ))
    
    # Півсферичні кінці
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi / 2, 25)
    u_grid, v_grid = np.meshgrid(u, v)
    
    # Нижній кінець
    x1 = radius * np.cos(u_grid) * np.sin(v_grid)
    y1 = radius * np.sin(u_grid) * np.sin(v_grid)
    z1 = radius * (1 - np.cos(v_grid))
    
    fig.add_trace(go.Surface(
        x=x1, y=y1, z=z1,
        colorscale='Blues',
        showscale=False,
        opacity=0.8,
        lighting=dict(
            ambient=0.4,
            diffuse=0.8,
            specular=0.2,
            roughness=0.5
        )
    ))
    
    # Верхній кінець
    x2 = radius * np.cos(u_grid) * np.sin(v_grid)
    y2 = radius * np.sin(u_grid) * np.sin(v_grid)
    z2 = (length - radius) + radius * np.cos(v_grid)
    
    fig.add_trace(go.Surface(
        x=x2, y=y2, z=z2,
        colorscale='Blues',
        showscale=False,
        opacity=0.8,
        lighting=dict(
            ambient=0.4,
            diffuse=0.8,
            specular=0.2,
            roughness=0.5
        )
    ))
    
    fig.update_layout(
        title=f'Сигароподібна куля<br>Довжина: {length:.2f} м, Радіус: {radius:.2f} м'
    )
    
    return fig


def show_plotly_3d(fig, save_html: bool = False, filename: str = None):
    """
    Показує або зберігає Plotly фігуру
    
    Args:
        fig: Plotly Figure об'єкт
        save_html: Чи зберігати як HTML файл
        filename: Ім'я файлу для збереження
    """
    if not PLOTLY_AVAILABLE:
        return
    
    if save_html and filename:
        fig.write_html(filename)
    else:
        # Відкриваємо в браузері
        fig.show()


def is_plotly_available():
    """Перевіряє, чи доступний Plotly"""
    return PLOTLY_AVAILABLE

