"""
Модуль для інтерактивної 3D візуалізації через Plotly
"""

import numpy as np
from typing import Optional

try:
    import plotly.graph_objects as go
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


def create_3d_plotly(shape_code: str, shape_params: dict, results: dict = None, num_segments: int = 50) -> Optional[str]:
    """
    Створює інтерактивну 3D візуалізацію через Plotly
    
    Args:
        shape_code: Код форми ('sphere', 'pillow', 'pear', 'cigar')
        shape_params: Параметри форми
        results: Результати розрахунку (опціонально)
        num_segments: Параметр дискретизації (той самий що використовується в patterns)
    
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
    
    # Отримуємо підтримувані форми з реєстру
    from balloon.shapes.registry import get_all_shape_codes
    SUPPORTED_SHAPES = get_all_shape_codes()
    
    # Використовуємо реєстр для перевірки підтримки форми
    from balloon.shapes.registry import get_shape_entry
    entry = get_shape_entry(shape_code)
    
    if entry is None:
        # Форма не підтримується - показуємо повідомлення замість "лівої" моделі
        logging.warning(f"Форма '{shape_code}' не підтримується в 3D візуалізації")
        fig = _create_unsupported_shape_message(shape_code, SUPPORTED_SHAPES)
        # Для непідтримуваних форм не додаємо стандартний макет
        return fig
    
    # Викликаємо відповідну функцію створення 3D моделі
    # Примітка: тут залишаємо if/elif, оскільки це специфічна логіка візуалізації
    # Але форма вже перевірена через реєстр
    # Всі rotational shapes використовують profile-based mesh з однаковим параметром дискретизації
    try:
        if shape_code == 'sphere':
            fig = _create_sphere_plotly(shape_params, results, num_segments)
        elif shape_code == 'pillow':
            # Pillow не є rotational shape, тому не використовує profile
            fig = _create_pillow_plotly(shape_params, results)
        elif shape_code == 'pear':
            fig = _create_pear_plotly(shape_params, results, num_segments)
        elif shape_code == 'cigar':
            fig = _create_cigar_plotly(shape_params, results, num_segments)
        else:
            # Це не повинно статися, якщо реєстр працює правильно
            logging.error(f"Форма '{shape_code}' є в реєстрі, але не має 3D візуалізації")
            fig = _create_unsupported_shape_message(shape_code, SUPPORTED_SHAPES)
            return fig
    except ValueError as e:
        # Якщо не вдалося створити профіль, показуємо повідомлення
        logging.error(f"Помилка створення 3D моделі: {e}")
        fig = _create_unsupported_shape_message(shape_code, SUPPORTED_SHAPES)
        return fig
    
    if fig is None:
        logging.error("Не вдалося створити фігуру")
        fig = _create_unsupported_shape_message(shape_code or 'unknown', SUPPORTED_SHAPES)
        return fig
    
    # Налаштування макету
    title_text = f'3D Модель: {shape_code}'
    
    fig.update_layout(
        title={
            'text': title_text,
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


def _create_sphere_plotly(shape_params: dict, results: dict = None, num_segments: int = 50):
    """Створює 3D сферу через Plotly з profile-based mesh (центр у 0)"""
    from balloon.shapes.profile import get_shape_profile
    
    # Отримуємо профіль через реєстр
    profile = get_shape_profile('sphere', shape_params)
    if profile is None:
        import logging
        logging.error("Не вдалося створити профіль для сфери")
        raise ValueError("Не вдалося створити профіль для форми 'sphere'")
    
    # Покращена якість mesh: більше точок для кращої візуалізації
    enhanced_num_segments = max(num_segments, 60)  # Мінімум 60 для кращої якості
    x, y, z = profile.generate_mesh(num_theta=enhanced_num_segments, num_z=enhanced_num_segments, center_at_origin=True)
    
    fig = go.Figure(data=[go.Surface(
        x=x, y=y, z=z,
        colorscale='Blues',
        showscale=False,
        opacity=0.85,
        lighting=dict(
            ambient=0.5,
            diffuse=0.9,
            specular=0.3,
            roughness=0.4,
            fresnel=0.5
        ),
        lightposition=dict(x=100, y=100, z=100)
    )])
    
    radius = shape_params.get('radius', 1.0)
    fig.update_layout(
        title=f'Сферична куля<br>Радіус: {radius:.2f} м'
    )
    
    return fig


def _create_pillow_plotly(shape_params: dict, results: dict = None):
    """Створює 3D подушку (паралелепіпед/box) через Plotly - відповідає V=L*W*H"""
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
    
    # Створюємо паралелепіпед (box) з центром у (0,0,0)
    # Координати вершин
    l2 = length / 2
    w2 = width / 2
    t2 = thickness / 2
    
    # Вершини паралелепіпеда
    vertices = np.array([
        [-l2, -w2, -t2], [l2, -w2, -t2], [l2, w2, -t2], [-l2, w2, -t2],  # Нижня грань
        [-l2, -w2, t2], [l2, -w2, t2], [l2, w2, t2], [-l2, w2, t2]        # Верхня грань
    ])
    
    # Створюємо поверхню через mesh для кожної грані
    fig = go.Figure()
    
    # Нижня грань (z = -t2)
    x_bottom = np.array([[-l2, l2], [-l2, l2]])
    y_bottom = np.array([[-w2, -w2], [w2, w2]])
    z_bottom = np.array([[-t2, -t2], [-t2, -t2]])
    fig.add_trace(go.Surface(x=x_bottom, y=y_bottom, z=z_bottom, 
                            colorscale='Blues', showscale=False, opacity=0.8))
    
    # Верхня грань (z = t2)
    x_top = np.array([[-l2, l2], [-l2, l2]])
    y_top = np.array([[-w2, -w2], [w2, w2]])
    z_top = np.array([[t2, t2], [t2, t2]])
    fig.add_trace(go.Surface(x=x_top, y=y_top, z=z_top, 
                            colorscale='Blues', showscale=False, opacity=0.8))
    
    # Бічні грані
    # Передня (y = w2)
    x_front = np.array([[-l2, l2], [-l2, l2]])
    y_front = np.array([[w2, w2], [w2, w2]])
    z_front = np.array([[-t2, -t2], [t2, t2]])
    fig.add_trace(go.Surface(x=x_front, y=y_front, z=z_front, 
                            colorscale='Blues', showscale=False, opacity=0.8))
    
    # Задня (y = -w2)
    x_back = np.array([[-l2, l2], [-l2, l2]])
    y_back = np.array([[-w2, -w2], [-w2, -w2]])
    z_back = np.array([[-t2, -t2], [t2, t2]])
    fig.add_trace(go.Surface(x=x_back, y=y_back, z=z_back, 
                            colorscale='Blues', showscale=False, opacity=0.8))
    
    # Ліва (x = -l2)
    x_left = np.array([[-l2, -l2], [-l2, -l2]])
    y_left = np.array([[-w2, w2], [-w2, w2]])
    z_left = np.array([[-t2, -t2], [t2, t2]])
    fig.add_trace(go.Surface(x=x_left, y=y_left, z=z_left, 
                            colorscale='Blues', showscale=False, opacity=0.8))
    
    # Права (x = l2)
    x_right = np.array([[l2, l2], [l2, l2]])
    y_right = np.array([[-w2, w2], [-w2, w2]])
    z_right = np.array([[-t2, -t2], [t2, t2]])
    fig.add_trace(go.Surface(x=x_right, y=y_right, z=z_right, 
                            colorscale='Blues', showscale=False, opacity=0.8))
    
    fig.update_layout(
        title=f'Подушкоподібна куля (паралелепіпед)<br>Довжина: {length:.2f} м, Ширина: {width:.2f} м, Товщина: {thickness:.2f} м'
    )
    
    return fig


def _create_pear_plotly(shape_params: dict, results: dict = None, num_segments: int = 50):
    """Створює 3D грушу через Plotly з profile-based mesh"""
    from balloon.shapes.profile import get_shape_profile
    
    # Отримуємо профіль через реєстр
    profile = get_shape_profile('pear', shape_params)
    if profile is None:
        import logging
        logging.error("Не вдалося створити профіль для груші")
        raise ValueError("Не вдалося створити профіль для форми 'pear'")
    
    # Покращена якість mesh: більше точок для кращої візуалізації
    enhanced_num_segments = max(num_segments, 60)  # Мінімум 60 для кращої якості
    x, y, z = profile.generate_mesh(num_theta=enhanced_num_segments, num_z=enhanced_num_segments, center_at_origin=True)
    
    fig = go.Figure(data=[go.Surface(
        x=x, y=y, z=z,
        colorscale='Blues',
        showscale=False,
        opacity=0.85,
        lighting=dict(
            ambient=0.5,
            diffuse=0.9,
            specular=0.3,
            roughness=0.4,
            fresnel=0.5
        ),
        lightposition=dict(x=100, y=100, z=100)
    )])
    
    # Додаємо gore overlay (межі сегментів) якщо є інформація про кількість сегментів
    # Це допомагає візуалізувати, як викрійка відповідає 3D моделі
    num_gores = shape_params.get('num_gores', 12)
    if num_gores > 0:
        _add_gore_overlay_to_fig(fig, x, y, z, num_gores)
    
    height = shape_params.get('pear_height', 3.0)
    top_radius = shape_params.get('pear_top_radius', 1.2)
    bottom_radius = shape_params.get('pear_bottom_radius', 0.6)
    fig.update_layout(
        title=f'Грушоподібна куля<br>Висота: {height:.2f} м, Верхній радіус: {top_radius:.2f} м, Нижній радіус: {bottom_radius:.2f} м'
    )
    
    return fig


def _create_cigar_plotly(shape_params: dict, results: dict = None, num_segments: int = 50):
    """Створює 3D сигару через Plotly з profile-based mesh"""
    from balloon.shapes.profile import get_shape_profile
    
    # Отримуємо профіль через реєстр
    profile = get_shape_profile('cigar', shape_params)
    if profile is None:
        import logging
        logging.error("Не вдалося створити профіль для сигари")
        raise ValueError("Не вдалося створити профіль для форми 'cigar'")
    
    # Покращена якість mesh: більше точок для кращої візуалізації
    enhanced_num_segments = max(num_segments, 60)  # Мінімум 60 для кращої якості
    x, y, z = profile.generate_mesh(num_theta=enhanced_num_segments, num_z=enhanced_num_segments, center_at_origin=True)
    
    fig = go.Figure(data=[go.Surface(
        x=x, y=y, z=z,
        colorscale='Blues',
        showscale=False,
        opacity=0.85,
        lighting=dict(
            ambient=0.5,
            diffuse=0.9,
            specular=0.3,
            roughness=0.4,
            fresnel=0.5
        ),
        lightposition=dict(x=100, y=100, z=100)
    )])
    
    # Додаємо gore overlay (межі сегментів)
    num_gores = shape_params.get('num_gores', 12)
    if num_gores > 0:
        _add_gore_overlay_to_fig(fig, x, y, z, num_gores)
    
    length = shape_params.get('cigar_length', 5.0)
    radius = shape_params.get('cigar_radius', 1.0)
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


def _create_unsupported_shape_message(shape_code: str, supported_shapes: list):
    """Створює повідомлення про непідтримувану форму"""
    fig = go.Figure()
    
    # Додаємо текст повідомлення
    fig.add_annotation(
        text=f"3D візуалізація недоступна для форми '{shape_code}'<br><br>"
             f"Підтримувані форми: {', '.join(supported_shapes)}",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        xanchor="center", yanchor="middle",
        font=dict(size=16, color='white'),
        bgcolor="rgba(40, 40, 40, 0.9)",
        bordercolor="rgb(200, 50, 50)",
        borderwidth=2,
        showarrow=False
    )
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor='rgb(20, 20, 20)',
        ),
        paper_bgcolor='rgb(30, 30, 30)',
        plot_bgcolor='rgb(20, 20, 20)',
    )
    
    return fig


def is_plotly_available():
    """Перевіряє, чи доступний Plotly"""
    return PLOTLY_AVAILABLE


def _add_gore_overlay_to_fig(fig, x, y, z, num_gores):
    """
    Додає overlay з межами сегментів (gores) на 3D модель
    
    Це допомагає візуалізувати, як викрійка відповідає 3D моделі
    """
    if not PLOTLY_AVAILABLE:
        return
    
    # Обчислюємо кути для меж сегментів
    theta_step = 2 * np.pi / num_gores
    
    # Для кожної межі сегмента малюємо лінію від низу до верху
    num_z_points = z.shape[1]
    
    for i in range(num_gores):
        theta = i * theta_step
        
        # Знаходимо найближчі точки по theta
        theta_idx = int(theta / (2 * np.pi) * x.shape[0])
        if theta_idx >= x.shape[0]:
            theta_idx = x.shape[0] - 1
        
        # Створюємо лінію вздовж меридіану
        x_line = []
        y_line = []
        z_line = []
        
        for j in range(num_z_points):
            x_line.append(x[theta_idx, j])
            y_line.append(y[theta_idx, j])
            z_line.append(z[theta_idx, j])
        
        # Додаємо лінію до фігури
        fig.add_trace(go.Scatter3d(
            x=x_line,
            y=y_line,
            z=z_line,
            mode='lines',
            line=dict(color='rgba(255, 100, 100, 0.6)', width=2),
            showlegend=False,
            hoverinfo='skip'
        ))

