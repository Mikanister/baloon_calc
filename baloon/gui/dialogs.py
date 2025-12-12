"""
Модуль для діалогових вікон
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging

try:
    from baloon.analysis import (
        calculate_height_profile,
        calculate_material_comparison,
        calculate_optimal_height,
        calculate_max_flight_time
    )
    from baloon.calculations import calculate_balloon_parameters
    from baloon.validators import validate_all_inputs
    from baloon.constants import FIELD_DEFAULTS
    from baloon.labels import BUTTON_LABELS
    from baloon.help_texts import (
        HELP_FORMULAS, HELP_PARAMETERS, HELP_SAFETY,
        HELP_EXAMPLES, HELP_FAQ, ABOUT_TEXT_EXTENDED
    )
    from baloon.gui.matplotlib_utils import get_plt
except ImportError:
    from analysis import (
        calculate_height_profile,
        calculate_material_comparison,
        calculate_optimal_height,
        calculate_max_flight_time
    )
    from calculations import calculate_balloon_parameters
    from validators import validate_all_inputs
    from constants import FIELD_DEFAULTS
    from labels import BUTTON_LABELS
    from help_texts import (
        HELP_FORMULAS, HELP_PARAMETERS, HELP_SAFETY,
        HELP_EXAMPLES, HELP_FAQ, ABOUT_TEXT_EXTENDED
    )
    from gui.matplotlib_utils import get_plt


class Dialogs:
    """Клас для діалогових вікон"""
    
    def __init__(self, gui_instance):
        """Ініціалізація з посиланням на головний клас GUI"""
        self.gui = gui_instance
    
    def show_graph(self):
        """Показати покращений графік залежності параметрів від висоти"""
        try:
            # Валідація перед побудовою графіка
            inputs = {
                'gas_type': self.gui.gas_var.get(),
                'gas_volume': self.gui.entries['gas_volume' if self.gui.mode_var.get() == "payload" else 'payload'].get(),
                'material': self.gui.material_var.get(),
                'thickness': self.gui.entries['thickness'].get(),
                'start_height': self.gui.entries['start_height'].get(),
                'work_height': self.gui.entries['work_height'].get(),
                'ground_temp': self.gui.entries['ground_temp'].get() if self.gui.gas_var.get() == "Гаряче повітря" else "15",
                'inside_temp': self.gui.entries['inside_temp'].get() if self.gui.gas_var.get() == "Гаряче повітря" else "100",
                'mode': self.gui.mode_var.get(),
                'shape_type': self.gui.shape_display_to_code.get(self.gui.entries['shape_type'].get(), 'sphere'),
                'shape_params': {
                    'pillow_len': self.gui.entries.get('pillow_len').get() if 'pillow_len' in self.gui.entries else None,
                    'pillow_wid': self.gui.entries.get('pillow_wid').get() if 'pillow_wid' in self.gui.entries else None,
                }
            }
            # Валідація вхідних даних
            validated_numbers, validated_strings = validate_all_inputs(**inputs)
            
            # Збір даних для графіка
            graph_inputs = {
                'gas_type': validated_strings['gas_type'],
                'material': validated_strings['material'],
                'thickness_mm': validated_numbers['thickness'],
                'gas_volume': validated_numbers['gas_volume'],
                'ground_temp': validated_numbers['ground_temp'],
                'inside_temp': validated_numbers['inside_temp'],
                'max_height': 10000,  # Збільшено до 10 км
                'shape_type': validated_strings.get('shape_type', 'sphere'),
                'shape_params': {k: validated_numbers[k] for k in validated_numbers if k.startswith('pillow_') and k != 'pillow_height'},
                'extra_mass': validated_numbers.get('extra_mass', 0.0),
                'seam_factor': validated_numbers.get('seam_factor', 1.0),
            }
            profile = calculate_height_profile(**graph_inputs)
            heights = [p['height'] for p in profile]
            payloads = [p['payload'] for p in profile]
            lifts = [p['lift'] for p in profile]
            net_lifts = [p['net_lift_per_m3'] for p in profile]
            volumes = [p.get('required_volume', 0) for p in profile]
            # Пошук ключових точок
            zero_payload_height = next((h for h, p in zip(heights, payloads) if p <= 0), None)
            payload_max = max(payloads) if payloads else None
            payload_max_h = heights[payloads.index(payload_max)] if payload_max is not None else None

            # Створюємо subplots для кращої візуалізації
            plt = get_plt()
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle('Залежність параметрів аеростата від висоти', fontsize=14, fontweight='bold')
            
            # Графік 1: Навантаження та підйомна сила
            ax1 = axes[0, 0]
            ax1.plot(heights, payloads, 'b-', label='Корисне навантаження (кг)', linewidth=2)
            ax1.plot(heights, lifts, 'g-', label='Підйомна сила (кг)', linewidth=2)
            ax1.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Нульове навантаження')
            # Маркери ключових точок
            if payload_max is not None:
                ax1.plot(payload_max_h, payload_max, 'bo')
                ax1.annotate(f"max {payload_max:.1f} кг", xy=(payload_max_h, payload_max),
                             xytext=(payload_max_h, payload_max + 1),
                             arrowprops=dict(arrowstyle="->", color='blue'), color='blue')
            if zero_payload_height is not None:
                ax1.plot(zero_payload_height, 0, 'ro')
                ax1.annotate(f"0 кг @ {zero_payload_height} м", xy=(zero_payload_height, 0),
                             xytext=(zero_payload_height, max(payloads)*0.1 if payloads else 1),
                             arrowprops=dict(arrowstyle="->", color='red'), color='red')
            ax1.set_xlabel('Висота, м')
            ax1.set_ylabel('Маса, кг')
            ax1.set_title('Навантаження та підйомна сила')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Графік 2: Підйомна сила на м³
            ax2 = axes[0, 1]
            ax2.plot(heights, net_lifts, 'm-', label='Підйомна сила на м³', linewidth=2)
            target_net = 0.5
            ax2.axhline(y=target_net, color='orange', linestyle='--', alpha=0.6, label='Орієнтир 0.5 кг/м³')
            ax2.set_xlabel('Висота, м')
            ax2.set_ylabel('Підйомна сила, кг/м³')
            ax2.set_title('Підйомна сила на одиницю об\'єму')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Графік 3: Об'єм кулі
            ax3 = axes[1, 0]
            ax3.plot(heights, volumes, 'c-', label='Об\'єм кулі', linewidth=2)
            ax3.set_xlabel('Висота, м')
            ax3.set_ylabel('Об\'єм, м³')
            ax3.set_title('Зміна об\'єму кулі з висотою')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # Графік 4: Комбінований
            ax4 = axes[1, 1]
            ax4_twin = ax4.twinx()
            line1 = ax4.plot(heights, payloads, 'b-', label='Навантаження (кг)', linewidth=2)
            line2 = ax4_twin.plot(heights, volumes, 'r-', label='Об\'єм (м³)', linewidth=2)
            ax4.set_xlabel('Висота, м')
            ax4.set_ylabel('Навантаження, кг', color='b')
            ax4_twin.set_ylabel('Об\'єм, м³', color='r')
            ax4.set_title('Навантаження та об\'єм')
            ax4.tick_params(axis='y', labelcolor='b')
            ax4_twin.tick_params(axis='y', labelcolor='r')
            ax4.spines['left'].set_color('b')
            ax4.spines['right'].set_color('r')
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax4.legend(lines, labels, loc='upper left', framealpha=0.9)
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Помилка графіка", str(e))
    
    def show_material_comparison(self):
        """Показати порівняння матеріалів"""
        try:
            # Завжди читаємо актуальні дані з полів
            logging.info("Порівняння матеріалів: читання даних з полів")
            
            # Отримуємо gas_volume залежно від режиму
            mode = self.gui.mode_var.get()
            if mode == "payload":
                gas_volume_val = self.gui.entries['gas_volume'].get()
            else:
                # Якщо режим "volume", то gas_volume розраховується з payload
                payload_val = self.gui.entries['payload'].get()
                if not payload_val or float(payload_val) <= 0:
                    messagebox.showerror("Помилка", "Введіть коректне навантаження для розрахунку об'єму")
                    return
                
                try:
                    temp_inputs = {
                        'gas_type': self.gui.gas_var.get(),
                        'gas_volume': payload_val,
                        'material': self.gui.material_var.get(),
                        'thickness': self.gui.entries['thickness'].get(),
                        'start_height': self.gui.entries['start_height'].get(),
                        'work_height': self.gui.entries['work_height'].get(),
                        'ground_temp': FIELD_DEFAULTS['ground_temp'] if self.gui.gas_var.get() != "Гаряче повітря" else self.gui.entries['ground_temp'].get(),
                        'inside_temp': FIELD_DEFAULTS['ground_temp'] if self.gui.gas_var.get() != "Гаряче повітря" else self.gui.entries['inside_temp'].get(),
                        'mode': 'volume'
                    }
                    temp_validated, _ = validate_all_inputs(**temp_inputs)
                    
                    temp_result = calculate_balloon_parameters(
                        gas_type=temp_inputs['gas_type'],
                        gas_volume=temp_validated['gas_volume'],
                        material=temp_inputs['material'],
                        thickness_mm=temp_validated['thickness'],
                        start_height=temp_validated['start_height'],
                        work_height=temp_validated['work_height'],
                        ground_temp=temp_validated['ground_temp'],
                        inside_temp=temp_validated['inside_temp'],
                        mode='volume'
                    )
                    gas_volume_val = str(temp_result.get('gas_volume', payload_val))
                    logging.info(f"Порівняння матеріалів: розраховано об'єм {gas_volume_val} м³ з навантаження {payload_val} кг")
                except Exception as e:
                    logging.error(f"Помилка розрахунку об'єму з навантаження: {e}")
                    messagebox.showerror("Помилка", f"Не вдалося розрахувати об'єм з навантаження: {e}")
                    return
            
            # Для не-гарячого повітря використовуємо значення за замовчуванням
            gas_type = self.gui.gas_var.get()
            if gas_type == "Гаряче повітря":
                ground_temp_val = self.gui.entries['ground_temp'].get()
                inside_temp_val = self.gui.entries['inside_temp'].get()
            else:
                ground_temp_val = FIELD_DEFAULTS['ground_temp']
                inside_temp_val = FIELD_DEFAULTS['ground_temp']
            
            inputs = {
                'gas_type': gas_type,
                'gas_volume': gas_volume_val,
                'material': self.gui.material_var.get(),
                'thickness': self.gui.entries['thickness'].get(),
                'start_height': self.gui.entries['start_height'].get(),
                'work_height': self.gui.entries['work_height'].get(),
                'ground_temp': ground_temp_val,
                'inside_temp': inside_temp_val,
            }
            
            validated_numbers, validated_strings = validate_all_inputs(**inputs)
            
            total_height = validated_numbers['start_height'] + validated_numbers['work_height']
            
            comparison = calculate_material_comparison(
                gas_type=validated_strings['gas_type'],
                thickness_mm=validated_numbers['thickness'],
                gas_volume=validated_numbers['gas_volume'],
                ground_temp=validated_numbers['ground_temp'],
                inside_temp=validated_numbers['inside_temp'],
                height=total_height,
                extra_mass=validated_numbers.get('extra_mass', 0.0),
                seam_factor=validated_numbers.get('seam_factor', 1.0),
            )
            
            # Закриваємо попереднє вікно, якщо воно існує
            if hasattr(self.gui, '_material_comparison_window') and self.gui._material_comparison_window.winfo_exists():
                self.gui._material_comparison_window.destroy()
            
            # Створюємо нове вікно з результатами
            comp_window = tk.Toplevel(self.gui.root)
            self.gui._material_comparison_window = comp_window
            comp_window.title("Порівняння матеріалів")
            comp_window.geometry("800x600")
            
            # Створюємо Treeview для таблиці
            tree = ttk.Treeview(comp_window, columns=('Матеріал', 'Навантаження', 'Маса оболонки', 'Підйомна сила', 'Коеф. безпеки'), show='headings')
            tree.heading('Матеріал', text='Матеріал')
            tree.heading('Навантаження', text='Навантаження (кг)')
            tree.heading('Маса оболонки', text='Маса оболонки (кг)')
            tree.heading('Підйомна сила', text='Підйомна сила (кг)')
            tree.heading('Коеф. безпеки', text='Коеф. безпеки')
            
            tree.column('Матеріал', width=120)
            tree.column('Навантаження', width=120)
            tree.column('Маса оболонки', width=120)
            tree.column('Підйомна сила', width=120)
            tree.column('Коеф. безпеки', width=120)
            
            # Сортуємо за навантаженням
            sorted_materials = sorted(comparison.items(), key=lambda x: x[1]['payload'], reverse=True)
            
            for material, data in sorted_materials:
                safety = f"{data['safety_factor']:.1f}" if data['safety_factor'] != float('inf') else "∞"
                tree.insert('', 'end', values=(
                    material,
                    f"{data['payload']:.2f}",
                    f"{data['mass_shell']:.3f}",
                    f"{data['lift']:.2f}",
                    safety
                ))
            
            tree.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Додаємо графік
            plt = get_plt()
            fig, ax = plt.subplots(figsize=(10, 6))
            materials = [m[0] for m in sorted_materials]
            payloads = [m[1]['payload'] for m in sorted_materials]
            colors = plt.cm.viridis(range(len(materials)))
            
            bars = ax.bar(materials, payloads, color=colors)
            ax.set_xlabel('Матеріал')
            ax.set_ylabel('Корисне навантаження (кг)')
            ax.set_title('Порівняння матеріалів за навантаженням')
            ax.grid(True, alpha=0.3, axis='y')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Помилка порівняння", str(e))
    
    def show_optimal_height(self):
        """Показати оптимальну висоту польоту"""
        try:
            mode = self.gui.mode_var.get()
            if mode == "payload":
                gas_volume_val = self.gui.entries['gas_volume'].get()
            else:
                payload_val = self.gui.entries['payload'].get()
                if not payload_val or float(payload_val) <= 0:
                    messagebox.showerror("Помилка", "Введіть коректне навантаження для розрахунку об'єму")
                    return
                try:
                    temp_inputs = {
                        'gas_type': self.gui.gas_var.get(),
                        'gas_volume': payload_val,
                        'material': self.gui.material_var.get(),
                        'thickness': self.gui.entries['thickness'].get(),
                        'start_height': self.gui.entries['start_height'].get(),
                        'work_height': self.gui.entries['work_height'].get(),
                        'ground_temp': FIELD_DEFAULTS['ground_temp'] if self.gui.gas_var.get() != "Гаряче повітря" else self.gui.entries['ground_temp'].get(),
                        'inside_temp': FIELD_DEFAULTS['ground_temp'] if self.gui.gas_var.get() != "Гаряче повітря" else self.gui.entries['inside_temp'].get(),
                        'mode': 'volume'
                    }
                    temp_validated, _ = validate_all_inputs(**temp_inputs)
                    temp_result = calculate_balloon_parameters(
                        gas_type=temp_inputs['gas_type'],
                        gas_volume=temp_validated['gas_volume'],
                        material=temp_inputs['material'],
                        thickness_mm=temp_validated['thickness'],
                        start_height=temp_validated['start_height'],
                        work_height=temp_validated['work_height'],
                        ground_temp=temp_validated['ground_temp'],
                        inside_temp=temp_validated['inside_temp'],
                        mode='volume'
                    )
                    gas_volume_val = str(temp_result.get('gas_volume', payload_val))
                except Exception as e:
                    messagebox.showerror("Помилка", f"Не вдалося розрахувати об'єм з навантаження: {e}")
                    return
            
            gas_type = self.gui.gas_var.get()
            if gas_type == "Гаряче повітря":
                ground_temp_val = self.gui.entries['ground_temp'].get()
                inside_temp_val = self.gui.entries['inside_temp'].get()
            else:
                ground_temp_val = FIELD_DEFAULTS['ground_temp']
                inside_temp_val = FIELD_DEFAULTS['ground_temp']
            
            inputs = {
                'gas_type': gas_type,
                'gas_volume': gas_volume_val,
                'material': self.gui.material_var.get(),
                'thickness': self.gui.entries['thickness'].get(),
                'start_height': self.gui.entries['start_height'].get(),
                'work_height': self.gui.entries['work_height'].get(),
                'ground_temp': ground_temp_val,
                'inside_temp': inside_temp_val,
            }
            validated_numbers, validated_strings = validate_all_inputs(**inputs)
            
            optimal = calculate_optimal_height(
                gas_type=validated_strings['gas_type'],
                material=validated_strings['material'],
                thickness_mm=validated_numbers['thickness'],
                gas_volume=validated_numbers['gas_volume'],
                ground_temp=validated_numbers['ground_temp'],
                inside_temp=validated_numbers['inside_temp'],
                extra_mass=validated_numbers.get('extra_mass', 0.0),
                seam_factor=validated_numbers.get('seam_factor', 1.0),
            )
            
            result_text = (
                f"Оптимальна висота: {optimal['optimal_height']:.0f} м\n\n"
                f"На цій висоті:\n"
                f"• Корисне навантаження: {optimal['payload']:.2f} кг\n"
                f"• Підйомна сила: {optimal['lift']:.2f} кг\n"
                f"• Підйомна сила на м³: {optimal['net_lift_per_m3']:.3f} кг/м³"
            )
            
            messagebox.showinfo("Оптимальна висота", result_text)
            
        except Exception as e:
            messagebox.showerror("Помилка розрахунку", str(e))
    
    def show_flight_time(self):
        """Показати максимальний час польоту"""
        try:
            if self.gui.mode_var.get() == "payload":
                gas_volume_val = self.gui.entries['gas_volume'].get()
            else:
                gas_volume_val = self.gui.entries['gas_volume'].get() or self.gui.entries['payload'].get()
            
            gas_type = self.gui.gas_var.get()
            if gas_type == "Гаряче повітря":
                ground_temp_val = self.gui.entries['ground_temp'].get()
                inside_temp_val = self.gui.entries['inside_temp'].get()
            else:
                ground_temp_val = FIELD_DEFAULTS['ground_temp']
                inside_temp_val = FIELD_DEFAULTS['ground_temp']
            
            inputs = {
                'gas_type': gas_type,
                'gas_volume': gas_volume_val,
                'material': self.gui.material_var.get(),
                'thickness': self.gui.entries['thickness'].get(),
                'start_height': self.gui.entries['start_height'].get(),
                'work_height': self.gui.entries['work_height'].get(),
                'ground_temp': ground_temp_val,
                'inside_temp': inside_temp_val,
            }
            validated_numbers, validated_strings = validate_all_inputs(**inputs)
            
            perm_mult_str = self.gui.entries['perm_mult'].get()
            try:
                perm_mult = float(perm_mult_str)
            except:
                perm_mult = 1.0
            
            flight_time = calculate_max_flight_time(
                gas_type=validated_strings['gas_type'],
                material=validated_strings['material'],
                thickness_mm=validated_numbers['thickness'],
                gas_volume=validated_numbers['gas_volume'],
                start_height=validated_numbers['start_height'],
                work_height=validated_numbers['work_height'],
                ground_temp=validated_numbers['ground_temp'],
                inside_temp=validated_numbers['inside_temp'],
                perm_mult=perm_mult
            )
            
            if flight_time['max_time_hours'] == float('inf'):
                result_text = flight_time.get('message', 'Час польоту не обмежений')
            else:
                result_text = (
                    f"{flight_time.get('message', '')}\n\n"
                    f"Деталі:\n"
                    f"• Початкове навантаження: {flight_time.get('initial_payload', 0):.2f} кг\n"
                    f"• Втрати газу за годину: {flight_time.get('gas_loss_rate_per_hour', 0):.6f} м³/год\n"
                    f"• Час до нульового навантаження: {flight_time.get('time_to_zero_payload', 0):.2f} год ({flight_time.get('time_to_zero_payload', 0)/24:.2f} днів)"
                )
            
            messagebox.showinfo("Час польоту", result_text)
            
        except Exception as e:
            messagebox.showerror("Помилка розрахунку", str(e))
    
    def show_help(self):
        """Показати довідку"""
        help_window = tk.Toplevel(self.gui.root)
        help_window.title("Довідка")
        help_window.geometry("800x600")
        help_window.configure(bg="#2b2b2b")
        
        # Notebook для вкладок
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Вкладка "Формули"
        formulas_frame = tk.Frame(notebook, bg="#2b2b2b")
        formulas_text = tk.Text(
            formulas_frame, 
            wrap="word", 
            bg="#1e1e1e", 
            fg="#ffffff",
            font=("Courier New", 10),
            padx=10,
            pady=10
        )
        formulas_text.insert(1.0, HELP_FORMULAS)
        formulas_text.config(state="disabled")
        formulas_text.pack(fill="both", expand=True)
        notebook.add(formulas_frame, text="Формули")
        
        # Вкладка "Параметри"
        params_frame = tk.Frame(notebook, bg="#2b2b2b")
        params_text = tk.Text(
            params_frame, 
            wrap="word", 
            bg="#1e1e1e", 
            fg="#ffffff",
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        params_text.insert(1.0, HELP_PARAMETERS)
        params_text.config(state="disabled")
        params_text.pack(fill="both", expand=True)
        notebook.add(params_frame, text="Параметри")
        
        # Вкладка "Безпека"
        safety_frame = tk.Frame(notebook, bg="#2b2b2b")
        safety_text = tk.Text(
            safety_frame, 
            wrap="word", 
            bg="#1e1e1e", 
            fg="#ffffff",
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        safety_text.insert(1.0, HELP_SAFETY)
        safety_text.config(state="disabled")
        safety_text.pack(fill="both", expand=True)
        notebook.add(safety_frame, text="Безпека")
        
        # Вкладка "Приклади"
        examples_frame = tk.Frame(notebook, bg="#2b2b2b")
        examples_text = tk.Text(
            examples_frame, 
            wrap="word", 
            bg="#1e1e1e", 
            fg="#ffffff",
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        examples_text.insert(1.0, HELP_EXAMPLES)
        examples_text.config(state="disabled")
        examples_text.pack(fill="both", expand=True)
        notebook.add(examples_frame, text="Приклади")
        
        # Вкладка "FAQ"
        faq_frame = tk.Frame(notebook, bg="#2b2b2b")
        faq_text = tk.Text(
            faq_frame, 
            wrap="word", 
            bg="#1e1e1e", 
            fg="#ffffff",
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        faq_text.insert(1.0, HELP_FAQ)
        faq_text.config(state="disabled")
        faq_text.pack(fill="both", expand=True)
        notebook.add(faq_frame, text="FAQ")
    
    def show_about(self):
        """Показати інформацію про програму"""
        messagebox.showinfo(BUTTON_LABELS['about'], ABOUT_TEXT_EXTENDED)

