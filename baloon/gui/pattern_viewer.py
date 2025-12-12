"""
Модуль для роботи з викрійками (генерація, експорт, інформація)
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import csv

try:
    from baloon.patterns import generate_pattern_from_shape, calculate_seam_length
    from baloon.gui.matplotlib_utils import get_plt
except ImportError:
    from patterns import generate_pattern_from_shape, calculate_seam_length
    from gui.matplotlib_utils import get_plt


class PatternViewer:
    """Клас для роботи з викрійками"""
    
    def __init__(self, gui_instance):
        """Ініціалізація з посиланням на головний клас GUI"""
        self.gui = gui_instance
    
    def generate_pattern(self):
        """Генерує викрійку на основі параметрів"""
        try:
            # Отримуємо параметри з полів
            shape_display = self.gui.pattern_shape_var.get()
            shape_code = self.gui.shape_code_map.get(shape_display, "sphere")
            
            # Отримуємо параметри форми з останнього розрахунку або з полів
            shape_params = {}
            
            if hasattr(self.gui, 'last_calculation_results'):
                results = self.gui.last_calculation_results
                shape_params_from_results = results.get('shape_params', {})
                shape_params.update(shape_params_from_results)
            
            # Якщо параметрів немає, використовуємо значення з полів
            if shape_code == 'sphere':
                if 'radius' not in shape_params:
                    # Спробуємо отримати з останнього розрахунку
                    if hasattr(self.gui, 'last_calculation_results'):
                        radius = self.gui.last_calculation_results.get('shape_params', {}).get('radius', 1.0)
                    else:
                        radius = 1.0
                    shape_params['radius'] = radius
            elif shape_code == 'pillow':
                if 'pillow_len' not in shape_params:
                    shape_params['pillow_len'] = float(self.gui.entries.get('pillow_len', tk.StringVar(value="3.0")).get() or "3.0")
                if 'pillow_wid' not in shape_params:
                    shape_params['pillow_wid'] = float(self.gui.entries.get('pillow_wid', tk.StringVar(value="2.0")).get() or "2.0")
            elif shape_code == 'pear':
                if 'pear_height' not in shape_params:
                    shape_params['pear_height'] = float(self.gui.entries.get('pear_height', tk.StringVar(value="3.0")).get() or "3.0")
                if 'pear_top_radius' not in shape_params:
                    shape_params['pear_top_radius'] = float(self.gui.entries.get('pear_top_radius', tk.StringVar(value="1.2")).get() or "1.2")
                if 'pear_bottom_radius' not in shape_params:
                    shape_params['pear_bottom_radius'] = float(self.gui.entries.get('pear_bottom_radius', tk.StringVar(value="0.6")).get() or "0.6")
            elif shape_code == 'cigar':
                if 'cigar_length' not in shape_params:
                    shape_params['cigar_length'] = float(self.gui.entries.get('cigar_length', tk.StringVar(value="5.0")).get() or "5.0")
                if 'cigar_radius' not in shape_params:
                    shape_params['cigar_radius'] = float(self.gui.entries.get('cigar_radius', tk.StringVar(value="1.0")).get() or "1.0")
            
            # Кількість сегментів
            num_segments = int(self.gui.pattern_segments_var.get() or "12")
            
            # Генеруємо патерн
            pattern = generate_pattern_from_shape(shape_code, shape_params, num_segments)
            
            # Зберігаємо поточний патерн
            self.gui.current_pattern = pattern
            
            # Візуалізуємо
            self.gui.visualize_pattern(pattern)
            
            # Показуємо інформацію
            self.gui.show_pattern_info(pattern)
            
        except Exception as e:
            import logging
            logging.error(f"Помилка генерації викрійки: {e}", exc_info=True)
            messagebox.showerror("Помилка", f"Не вдалося згенерувати викрійку: {e}")
    
    def show_pattern_info(self, pattern):
        """Показує інформацію про патерн"""
        self.gui.pattern_info_text.config(state="normal")
        self.gui.pattern_info_text.delete(1.0, tk.END)
        
        info = []
        info.append("=" * 50)
        info.append("ІНФОРМАЦІЯ ПРО ВИКРІЙКУ")
        info.append("=" * 50)
        info.append("")
        info.append(f"Тип: {pattern.get('description', '')}")
        info.append("")
        
        pattern_type = pattern.get('pattern_type')
        
        if pattern_type == 'sphere_gore':
            info.append(f"Кількість сегментів: {pattern.get('num_gores', 12)}")
            info.append(f"Радіус сфери: {pattern.get('radius', 0):.2f} м")
            info.append(f"Максимальна ширина сегмента: {pattern.get('max_width', 0):.2f} м")
            info.append(f"Висота сегмента: {pattern.get('total_height', 0):.2f} м")
            info.append(f"Площа одного сегмента: {pattern.get('gore_area', 0):.2f} м²")
            info.append(f"Загальна площа: {pattern.get('total_area', 0):.2f} м²")
        
        elif pattern_type == 'pillow':
            panels = pattern.get('panels', [])
            info.append(f"Довжина: {pattern.get('length', 0):.2f} м")
            info.append(f"Ширина: {pattern.get('width', 0):.2f} м")
            info.append(f"Товщина: {pattern.get('thickness', 0):.2f} м")
            info.append("")
            info.append("Панелі (2 шт, однакові):")
            if panels:
                panel = panels[0]
                info.append(f"  Розмір: {panel.get('width', 0):.2f} × {panel.get('height', 0):.2f} м")
                info.append(f"  Площа однієї панелі: {panel.get('area', 0):.2f} м²")
            info.append(f"Загальна площа: {pattern.get('total_area', 0):.2f} м²")
            info.append("")
            opening_side = pattern.get('opening_side', 'width')
            opening_size = pattern.get('opening_size', 0)
            side_name = "ширина" if opening_side == 'width' else "довжина"
            info.append(f"Незакрита кромка (отвір): на стороні '{side_name}', довжина: {opening_size:.2f} м")
            info.append("(ця ділянка кромки не зшивається, для заповнення газу)")
        
        elif pattern_type == 'pear_gore':
            info.append(f"Кількість сегментів: {pattern.get('num_gores', 12)}")
            info.append(f"Висота груші: {pattern.get('height', 0):.2f} м")
            info.append(f"Верхній радіус: {pattern.get('top_radius', 0):.2f} м")
            info.append(f"Нижній радіус: {pattern.get('bottom_radius', 0):.2f} м")
            info.append(f"Максимальна ширина сегмента: {pattern.get('max_width', 0):.2f} м")
            info.append(f"Висота сегмента: {pattern.get('total_height', 0):.2f} м")
            info.append(f"Площа одного сегмента: {pattern.get('gore_area', 0):.2f} м²")
            info.append(f"Загальна площа: {pattern.get('total_area', 0):.2f} м²")
        
        elif pattern_type == 'cigar_gore':
            info.append(f"Кількість сегментів: {pattern.get('num_gores', 12)}")
            info.append(f"Довжина сигари: {pattern.get('length', 0):.2f} м")
            info.append(f"Радіус сигари: {pattern.get('radius', 0):.2f} м")
            info.append(f"Максимальна ширина сегмента: {pattern.get('max_width', 0):.2f} м")
            info.append(f"Висота сегмента: {pattern.get('total_height', 0):.2f} м")
            info.append(f"Площа одного сегмента: {pattern.get('gore_area', 0):.2f} м²")
            info.append(f"Загальна площа: {pattern.get('total_area', 0):.2f} м²")
        
        seam_length = calculate_seam_length(pattern)
        info.append("")
        info.append(f"Загальна довжина швів: {seam_length:.2f} м")
        
        self.gui.pattern_info_text.insert(1.0, "\n".join(info))
        self.gui.pattern_info_text.config(state="disabled")
    
    def export_pattern(self):
        """Експортує викрійку як PNG"""
        if not hasattr(self.gui, 'current_pattern'):
            messagebox.showwarning("Попередження", "Спочатку згенеруйте викрійку")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            if filename:
                plt = get_plt()
                fig, ax = plt.subplots(figsize=(10, 12))
                ax.set_aspect('equal')
                ax.axis('off')
                ax.set_facecolor('#1e1e1e')
                fig.patch.set_facecolor('#1e1e1e')
                
                pattern = self.gui.current_pattern
                pattern_type = pattern.get('pattern_type')
                
                if pattern_type == 'sphere_gore':
                    points = pattern.get('points', [])
                    if points:
                        xs = [x for x, y in points]
                        ys = [y for x, y in points]
                        ax.plot(xs, ys, 'b-', linewidth=2)
                        ax.plot([-x for x in xs], ys, 'b-', linewidth=2)
                        ax.axvline(0, color='white', linestyle='--', alpha=0.5)
                
                plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='#1e1e1e')
                plt.close()
                messagebox.showinfo("Успіх", f"Викрійку збережено: {filename}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося експортувати: {e}")
    
    def export_pattern_data(self):
        """Експортує дані викрійки як CSV"""
        if not hasattr(self.gui, 'current_pattern'):
            messagebox.showwarning("Попередження", "Спочатку згенеруйте викрійку")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if filename:
                pattern = self.gui.current_pattern
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Параметр', 'Значення'])
                    writer.writerow(['Тип', pattern.get('description', '')])
                    
                    if pattern.get('pattern_type') == 'sphere_gore':
                        points = pattern.get('points', [])
                        writer.writerow(['', ''])
                        writer.writerow(['Координати сегмента', ''])
                        writer.writerow(['X (м)', 'Y (м)'])
                        for x, y in points:
                            writer.writerow([f"{x:.4f}", f"{y:.4f}"])
                
                messagebox.showinfo("Успіх", f"Дані збережено: {filename}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося експортувати: {e}")

