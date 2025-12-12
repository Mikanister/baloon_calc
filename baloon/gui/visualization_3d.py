"""
Модуль для 3D візуалізації форм
"""

import tkinter as tk
from tkinter import messagebox

try:
    from baloon.gui.matplotlib_utils import get_plt
except ImportError:
    from gui.matplotlib_utils import get_plt


class Visualization3D:
    """Клас для 3D візуалізації форм"""
    
    def __init__(self, gui_instance):
        """Ініціалізація з посиланням на головний клас GUI"""
        self.gui = gui_instance
    
    def create_3d_visualization(self, shape_code: str, shape_params: dict):
        """Створює 3D візуалізацію кулі"""
        try:
            import numpy as np
            from mpl_toolkits.mplot3d import Axes3D
            
            plt = get_plt()
            fig = plt.figure(figsize=(12, 10))
            ax = fig.add_subplot(111, projection='3d')
            
            # Налаштування темної теми
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
            
            if shape_code == 'sphere':
                self._draw_sphere_3d(ax, shape_params)
            elif shape_code == 'pillow':
                self._draw_pillow_3d(ax, shape_params)
            elif shape_code == 'pear':
                self._draw_pear_3d(ax, shape_params)
            elif shape_code == 'cigar':
                self._draw_cigar_3d(ax, shape_params)
            
            # Налаштування осей
            ax.set_xlabel('X (м)', fontsize=10)
            ax.set_ylabel('Y (м)', fontsize=10)
            ax.set_zlabel('Z (м)', fontsize=10)
            
            # Встановлюємо однаковий масштаб для всіх осей
            max_range = self._calculate_max_range(shape_code, shape_params)
            if max_range > 0:
                ax.set_xlim([-max_range, max_range])
                ax.set_ylim([-max_range, max_range])
                ax.set_zlim([-max_range, max_range])
            
            # Додаємо інформацію про об'єм та площу
            if hasattr(self.gui, 'last_calculation_results'):
                results = self.gui.last_calculation_results
                volume = results.get('required_volume', 0)
                surface = results.get('surface_area', 0)
                info_text = f"Об'єм: {volume:.2f} м³\nПлоща поверхні: {surface:.2f} м²"
                ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes, 
                         fontsize=10, verticalalignment='top',
                         bbox=dict(boxstyle='round', facecolor='#2b2b2b', alpha=0.8, edgecolor='#4a90e2'),
                         color='#ffffff')
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            messagebox.showerror("Помилка", "Для 3D візуалізації потрібна бібліотека numpy")
        except Exception as e:
            import logging
            logging.error(f"Помилка 3D візуалізації: {e}", exc_info=True)
            messagebox.showerror("Помилка", f"Не вдалося створити 3D модель: {e}")
    
    def _draw_sphere_3d(self, ax, shape_params):
        """Малює 3D сферу"""
        import numpy as np
        radius = shape_params.get('radius', 1.0)
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        x = radius * np.outer(np.cos(u), np.sin(v))
        y = radius * np.outer(np.sin(u), np.sin(v))
        z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(x, y, z, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
        ax.set_title(f'Сферична куля\nРадіус: {radius:.2f} м', color='#ffffff', fontsize=14, fontweight='bold')
    
    def _draw_pillow_3d(self, ax, shape_params):
        """Малює 3D подушку"""
        import numpy as np
        length = shape_params.get('pillow_len', 3.0)
        width = shape_params.get('pillow_wid', 2.0)
        # Товщина розраховується з об'єму (якщо є)
        if hasattr(self.gui, 'last_calculation_results'):
            volume = self.gui.last_calculation_results.get('required_volume', 0)
            if volume > 0:
                thickness = volume / (length * width)
            else:
                thickness = shape_params.get('thickness', width * 0.3)
        else:
            thickness = shape_params.get('thickness', width * 0.3)
        
        # Подушка - прямокутна форма
        x_coords = np.linspace(0, length, 30)
        y_coords = np.linspace(0, width, 30)
        z_coords = np.linspace(0, thickness, 20)
        
        # Верхня та нижня поверхні
        X, Y = np.meshgrid(x_coords, y_coords)
        Z_top = np.full_like(X, thickness)
        Z_bottom = np.full_like(X, 0)
        ax.plot_surface(X, Y, Z_top, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
        ax.plot_surface(X, Y, Z_bottom, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
        
        # Бічні поверхні
        Y_side, Z_side = np.meshgrid(y_coords, z_coords)
        X_front = np.full_like(Y_side, 0)
        X_back = np.full_like(Y_side, length)
        ax.plot_surface(X_front, Y_side, Z_side, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
        ax.plot_surface(X_back, Y_side, Z_side, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
        
        X_side, Z_side = np.meshgrid(x_coords, z_coords)
        Y_left = np.full_like(X_side, 0)
        Y_right = np.full_like(X_side, width)
        ax.plot_surface(X_side, Y_left, Z_side, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
        ax.plot_surface(X_side, Y_right, Z_side, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
        
        ax.set_title(f'Подушкоподібна куля (надута)\nДовжина: {length:.2f} м, Ширина: {width:.2f} м, Товщина: {thickness:.2f} м', 
                   color='#ffffff', fontsize=14, fontweight='bold')
    
    def _draw_pear_3d(self, ax, shape_params):
        """Малює 3D грушу"""
        import numpy as np
        height = shape_params.get('pear_height', 3.0)
        top_radius = shape_params.get('pear_top_radius', 1.2)
        bottom_radius = shape_params.get('pear_bottom_radius', 0.6)
        
        # Параметризація груші через обертання кривої
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, 1, 50)  # Від верху (0) до низу (1)
        u_grid, v_grid = np.meshgrid(u, v)
        
        # Радіус на кожній висоті - лінійна інтерполяція
        r_at_height = top_radius * (1 - v_grid) + bottom_radius * v_grid
        
        # Координати груші (обертання навколо осі Z)
        x = r_at_height * np.cos(u_grid)
        y = r_at_height * np.sin(u_grid)
        z = height * v_grid  # Від низу (0) до верху (height)
        
        # Малюємо поверхню
        ax.plot_surface(x, y, z, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
        
        ax.set_title(f'Грушоподібна куля\nВисота: {height:.2f} м, Верхній радіус: {top_radius:.2f} м, Нижній радіус: {bottom_radius:.2f} м', 
                   color='#ffffff', fontsize=14, fontweight='bold')
    
    def _draw_cigar_3d(self, ax, shape_params):
        """Малює 3D сигару"""
        import numpy as np
        length = shape_params.get('cigar_length', 5.0)
        radius = shape_params.get('cigar_radius', 1.0)
        
        # Сигара = циліндр + дві півсфери
        cylinder_length = max(0, length - 2 * radius)
        
        # Параметризація для циліндричної частини (якщо вона є)
        if cylinder_length > 0:
            u_cyl = np.linspace(0, 2 * np.pi, 50)
            z_cyl = np.linspace(radius, length - radius, 50)
            u_grid_cyl, z_grid_cyl = np.meshgrid(u_cyl, z_cyl)
            
            x_cyl = radius * np.cos(u_grid_cyl)
            y_cyl = radius * np.sin(u_grid_cyl)
            z_cyl = z_grid_cyl
            
            # Малюємо циліндричну частину
            ax.plot_surface(x_cyl, y_cyl, z_cyl, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
        
        # Параметризація для півсферичних кінців
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi / 2, 25)  # Тільки верхня півсфера
        u_grid, v_grid = np.meshgrid(u, v)
        
        # Перший півсферичний кінець (знизу)
        x1 = radius * np.cos(u_grid) * np.sin(v_grid)
        y1 = radius * np.sin(u_grid) * np.sin(v_grid)
        z1 = radius * (1 - np.cos(v_grid))  # Від 0 до radius
        ax.plot_surface(x1, y1, z1, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
        
        # Другий півсферичний кінець (зверху)
        x2 = radius * np.cos(u_grid) * np.sin(v_grid)
        y2 = radius * np.sin(u_grid) * np.sin(v_grid)
        z2 = (length - radius) + radius * np.cos(v_grid)  # Від (length-radius) до length
        ax.plot_surface(x2, y2, z2, color='#4a90e2', alpha=0.7, edgecolor='#2a5a9a', linewidth=0.5)
        
        ax.set_title(f'Сигароподібна куля\nДовжина: {length:.2f} м, Радіус: {radius:.2f} м', 
                   color='#ffffff', fontsize=14, fontweight='bold')
    
    def _calculate_max_range(self, shape_code: str, shape_params: dict) -> float:
        """Розраховує максимальний діапазон для осей"""
        max_range = 0
        if shape_code == 'sphere':
            max_range = max(max_range, shape_params.get('radius', 1.0) * 1.2)
        elif shape_code == 'pillow':
            max_range = max(max_range,
                          max(shape_params.get('pillow_len', 3.0) * 1.2,
                              shape_params.get('pillow_wid', 2.0) * 1.2))
        elif shape_code == 'pear':
            max_range = max(max_range,
                          max(shape_params.get('pear_height', 3.0) * 1.2,
                              shape_params.get('pear_top_radius', 1.2) * 1.2,
                              shape_params.get('pear_bottom_radius', 0.6) * 1.2))
        elif shape_code == 'cigar':
            max_range = max(max_range,
                          max(shape_params.get('cigar_length', 5.0) * 1.2,
                              shape_params.get('cigar_radius', 1.0) * 1.2))
        return max_range
    
    def show_3d_model(self):
        """Показує 3D модель кулі"""
        try:
            # Отримуємо параметри з останнього розрахунку або з поточного патерну
            shape_code = None
            shape_params = {}
            
            if hasattr(self.gui, 'current_pattern'):
                pattern = self.gui.current_pattern
                pattern_type = pattern.get('pattern_type')
                
                if pattern_type == 'sphere_gore':
                    shape_code = 'sphere'
                    radius = pattern.get('radius', 1.0)
                    shape_params = {'radius': radius}
                elif pattern_type == 'pillow':
                    shape_code = 'pillow'
                    shape_params = {
                        'pillow_len': pattern.get('length', 3.0),
                        'pillow_wid': pattern.get('width', 2.0)
                    }
                elif pattern_type == 'pear_gore':
                    shape_code = 'pear'
                    shape_params = {
                        'pear_height': pattern.get('height', 3.0),
                        'pear_top_radius': pattern.get('top_radius', 1.2),
                        'pear_bottom_radius': pattern.get('bottom_radius', 0.6)
                    }
                elif pattern_type == 'cigar_gore':
                    shape_code = 'cigar'
                    shape_params = {
                        'cigar_length': pattern.get('length', 5.0),
                        'cigar_radius': pattern.get('radius', 1.0)
                    }
            
            # Якщо немає патерну, спробуємо отримати з останнього розрахунку
            if not shape_code and hasattr(self.gui, 'last_calculation_results'):
                results = self.gui.last_calculation_results
                shape_code = results.get('shape_type', 'sphere')
                shape_params = results.get('shape_params', {})
                if shape_code == 'sphere' and 'radius' in results:
                    shape_params = {'radius': results['radius']}
            
            # Якщо все ще немає, спробуємо з полів
            if not shape_code:
                shape_display = self.gui.pattern_shape_var.get()
                shape_code = self.gui.shape_display_to_code.get(shape_display, 'sphere')
                if shape_code == 'sphere':
                    try:
                        if hasattr(self.gui, 'last_calculation_results') and 'radius' in self.gui.last_calculation_results:
                            radius = self.gui.last_calculation_results['radius']
                        else:
                            gas_volume = float(self.gui.entries['gas_volume'].get() or "1.0")
                            try:
                                from baloon.shapes import sphere_radius_from_volume
                            except ImportError:
                                from shapes import sphere_radius_from_volume
                            radius = sphere_radius_from_volume(gas_volume)
                        shape_params = {'radius': radius}
                    except:
                        shape_params = {'radius': 1.0}
                elif shape_code == 'pillow':
                    try:
                        shape_params = {
                            'pillow_len': float(self.gui.entries.get('pillow_len', tk.StringVar(value="3.0")).get() or "3.0"),
                            'pillow_wid': float(self.gui.entries.get('pillow_wid', tk.StringVar(value="2.0")).get() or "2.0")
                        }
                    except:
                        shape_params = {'pillow_len': 3.0, 'pillow_wid': 2.0}
                elif shape_code == 'pear':
                    try:
                        shape_params = {
                            'pear_height': float(self.gui.entries.get('pear_height', tk.StringVar(value="3.0")).get() or "3.0"),
                            'pear_top_radius': float(self.gui.entries.get('pear_top_radius', tk.StringVar(value="1.2")).get() or "1.2"),
                            'pear_bottom_radius': float(self.gui.entries.get('pear_bottom_radius', tk.StringVar(value="0.6")).get() or "0.6")
                        }
                    except:
                        shape_params = {'pear_height': 3.0, 'pear_top_radius': 1.2, 'pear_bottom_radius': 0.6}
                elif shape_code == 'cigar':
                    try:
                        shape_params = {
                            'cigar_length': float(self.gui.entries.get('cigar_length', tk.StringVar(value="5.0")).get() or "5.0"),
                            'cigar_radius': float(self.gui.entries.get('cigar_radius', tk.StringVar(value="1.0")).get() or "1.0")
                        }
                    except:
                        shape_params = {'cigar_length': 5.0, 'cigar_radius': 1.0}
            
            if not shape_code:
                messagebox.showwarning("Попередження", "Спочатку згенеруйте викрійку або виконайте розрахунок")
                return
            
            # Створюємо 3D візуалізацію
            self.create_3d_visualization(shape_code, shape_params)
            
        except Exception as e:
            import logging
            logging.error(f"Помилка 3D візуалізації: {e}", exc_info=True)
            messagebox.showerror("Помилка", f"Не вдалося створити 3D модель: {e}")

