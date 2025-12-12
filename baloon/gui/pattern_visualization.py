"""
Модуль для візуалізації викрійок/патернів
"""

import tkinter as tk


class PatternVisualizer:
    """Клас для візуалізації викрійок на canvas"""
    
    def __init__(self, gui_instance):
        """Ініціалізація з посиланням на головний клас GUI"""
        self.gui = gui_instance
    
    def visualize_pattern(self, pattern):
        """Візуалізує патерн на canvas"""
        self.gui.pattern_canvas.delete("all")
        
        canvas_width = self.gui.pattern_canvas.winfo_width()
        canvas_height = self.gui.pattern_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 400
            canvas_height = 500
        
        pattern_type = pattern.get('pattern_type')
        
        if pattern_type == 'sphere_gore':
            self._draw_sphere_gore(pattern, canvas_width, canvas_height)
        elif pattern_type == 'pillow':
            self._draw_pillow_pattern(pattern, canvas_width, canvas_height)
        elif pattern_type == 'pear_gore':
            self._draw_pear_pattern(pattern, canvas_width, canvas_height)
        elif pattern_type == 'cigar_gore':
            self._draw_cigar_pattern(pattern, canvas_width, canvas_height)
    
    def _draw_sphere_gore(self, pattern, width, height):
        """Малює гобеновий сегмент для сфери"""
        points = pattern.get('points', [])
        if not points:
            return
        
        max_y = max(abs(y) for x, y in points)
        max_x = max(abs(x) for x, y in points)
        
        scale_x = (width * 0.8) / (2 * max_x) if max_x > 0 else 1
        scale_y = (height * 0.8) / (2 * max_y) if max_y > 0 else 1
        scale = min(scale_x, scale_y)
        
        center_x = width / 2
        center_y = height / 2
        
        path = []
        for x, y in points:
            px = center_x + x * scale
            py = center_y - y * scale
            path.append((px, py))
        
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            self.gui.pattern_canvas.create_line(x1, y1, x2, y2, fill="#4a90e2", width=2)
        
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            self.gui.pattern_canvas.create_line(
                center_x - (x1 - center_x), y1,
                center_x - (x2 - center_x), y2,
                fill="#4a90e2", width=2
            )
        
        if path:
            first_x, first_y = path[0]
            last_x, last_y = path[-1]
            self.gui.pattern_canvas.create_line(
                center_x, first_y, center_x, last_y,
                fill="#ffffff", width=1, dash=(5, 5)
            )
        
        # Додаємо розміри та анотації
        radius = pattern.get('radius', 0)
        max_width = pattern.get('max_width', 0)
        total_height = pattern.get('total_height', 0)
        
        self.gui.pattern_canvas.create_text(
            center_x, 20, text=f"Сегмент (1 з {pattern.get('num_gores', 12)})",
            fill="#ffffff", font=("Arial", 11, "bold")
        )
        
        # Показуємо розміри
        if max_width > 0:
            # Максимальна ширина
            max_width_x = center_x + max_width * scale / 2
            self.gui.pattern_canvas.create_line(
                center_x, center_y - max_width * scale / 2,
                max_width_x, center_y - max_width * scale / 2,
                fill="#66d17c", width=1, dash=(3, 3)
            )
            self.gui.pattern_canvas.create_text(
                (center_x + max_width_x) / 2, center_y - max_width * scale / 2 - 10,
                text=f"Макс. ширина: {max_width:.2f} м",
                fill="#66d17c", font=("Arial", 8)
            )
        
        if total_height > 0:
            # Висота
            self.gui.pattern_canvas.create_line(
                center_x + max_x * scale + 10, center_y - total_height * scale / 2,
                center_x + max_x * scale + 10, center_y + total_height * scale / 2,
                fill="#66d17c", width=1, dash=(3, 3)
            )
            self.gui.pattern_canvas.create_text(
                center_x + max_x * scale + 15, center_y,
                text=f"Висота: {total_height:.2f} м",
                fill="#66d17c", font=("Arial", 8), anchor="w"
            )
        
        if radius > 0:
            self.gui.pattern_canvas.create_text(
                center_x, height - 30,
                text=f"Радіус сфери: {radius:.2f} м",
                fill="#888888", font=("Arial", 9)
            )
    
    def _draw_pillow_pattern(self, pattern, width, height):
        """Малює патерн для подушки - два прямокутники з позначенням отвору"""
        panels = pattern.get('panels', [])
        if not panels:
            return
        
        # Малюємо два прямокутники однакового розміру
        panel_w = panels[0].get('width', 0) if panels else 0
        panel_h = panels[0].get('height', 0) if panels else 0
        
        if panel_w <= 0 or panel_h <= 0:
            return
        
        # Масштабування для обох панелей
        max_dim = max(panel_w, panel_h)
        scale_w = (width * 0.7) / max_dim if max_dim > 0 else 1
        scale_h = (height * 0.35) / max_dim if max_dim > 0 else 1
        scale = min(scale_w, scale_h)
        
        w = panel_w * scale
        h = panel_h * scale
        
        # Центруємо
        center_x = width / 2
        spacing = 20  # Відстань між панелями
        
        # Перша панель (верхня)
        x1_1 = center_x - w / 2
        y1_1 = height * 0.15
        x2_1 = x1_1 + w
        y2_1 = y1_1 + h
        
        self.gui.pattern_canvas.create_rectangle(x1_1, y1_1, x2_1, y2_1, outline="#4a90e2", width=2)
        self.gui.pattern_canvas.create_text(
            center_x, y1_1 - 15, text="Панель 1",
            fill="#ffffff", font=("Arial", 10, "bold")
        )
        
        # Друга панель (нижня)
        x1_2 = center_x - w / 2
        y1_2 = y2_1 + spacing
        x2_2 = x1_2 + w
        y2_2 = y1_2 + h
        
        self.gui.pattern_canvas.create_rectangle(x1_2, y1_2, x2_2, y2_2, outline="#4a90e2", width=2)
        self.gui.pattern_canvas.create_text(
            center_x, y1_2 - 15, text="Панель 2",
            fill="#ffffff", font=("Arial", 10, "bold")
        )
        
        # Позначаємо отвір (незакрита ділянка кромки)
        opening_side = pattern.get('opening_side', 'width')
        opening_size = pattern.get('opening_size', 0)
        
        # Позначаємо лінії з'єднання (шви) - зеленою пунктирною лінією
        seam_color = "#66d17c"
        
        if opening_side == 'width':
            # Отвір на коротшій стороні (ширина) - ліва сторона не зшивається
            # Шви: верх, низ, права сторона
            self.gui.pattern_canvas.create_line(x1_2, y1_2, x2_2, y1_2, fill=seam_color, width=2, dash=(5, 3))  # Верх
            self.gui.pattern_canvas.create_line(x1_2, y2_2, x2_2, y2_2, fill=seam_color, width=2, dash=(5, 3))  # Низ
            self.gui.pattern_canvas.create_line(x2_2, y1_2, x2_2, y2_2, fill=seam_color, width=2, dash=(5, 3))  # Права
            
            # Позначаємо незакриту кромку (отвір) - ліва сторона
            opening_y = y1_2 + h / 2
            self.gui.pattern_canvas.create_line(
                x1_2, y1_2,
                x1_2, y2_2,
                fill="#ff6b6b", width=3, dash=(10, 5)
            )
            self.gui.pattern_canvas.create_text(
                x1_2 - 15, opening_y, text="НЕ ЗШИВАТИ\n(отвір)",
                fill="#ff6b6b", font=("Arial", 9, "bold"), anchor="e", justify="center"
            )
        else:
            # Отвір на довгій стороні (довжина) - верхня сторона не зшивається
            # Шви: ліва, права, низ
            self.gui.pattern_canvas.create_line(x1_2, y1_2, x1_2, y2_2, fill=seam_color, width=2, dash=(5, 3))  # Ліва
            self.gui.pattern_canvas.create_line(x2_2, y1_2, x2_2, y2_2, fill=seam_color, width=2, dash=(5, 3))  # Права
            self.gui.pattern_canvas.create_line(x1_2, y2_2, x2_2, y2_2, fill=seam_color, width=2, dash=(5, 3))  # Низ
            
            # Позначаємо незакриту кромку (отвір) - верхня сторона
            opening_x = center_x
            self.gui.pattern_canvas.create_line(
                x1_2, y1_2,
                x2_2, y1_2,
                fill="#ff6b6b", width=3, dash=(10, 5)
            )
            self.gui.pattern_canvas.create_text(
                opening_x, y1_2 - 20, text="НЕ ЗШИВАТИ (отвір)",
                fill="#ff6b6b", font=("Arial", 9, "bold"), anchor="s"
            )
    
    def _draw_pear_pattern(self, pattern, width, height):
        """Малює гобеновий сегмент для груші"""
        points = pattern.get('points', [])
        if not points:
            return
        
        max_y = max(y for x, y in points) if points else 1
        max_x = max(x for x, y in points) if points else 1
        
        scale_x = (width * 0.8) / (2 * max_x) if max_x > 0 else 1
        scale_y = (height * 0.8) / max_y if max_y > 0 else 1
        scale = min(scale_x, scale_y)
        
        center_x = width / 2
        center_y = height / 2
        
        # Малюємо сегмент
        coords = []
        for x, y in points:
            # Для груші y йде від низу (0) до верху (height)
            # Перетворюємо координати
            screen_x = center_x + x * scale
            screen_y = center_y + (y - max_y / 2) * scale  # Y від низу до верху
            coords.append((screen_x, screen_y))
        
        # Малюємо ліву половину сегмента
        if len(coords) > 1:
            for i in range(len(coords) - 1):
                x1, y1 = coords[i]
                x2, y2 = coords[i + 1]
                self.gui.pattern_canvas.create_line(x1, y1, x2, y2, fill="#4a90e2", width=2)
        
        # Малюємо праву половину (дзеркально)
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            # Дзеркалюємо відносно центру
            x1_mirror = center_x - (x1 - center_x)
            x2_mirror = center_x - (x2 - center_x)
            self.gui.pattern_canvas.create_line(x1_mirror, y1, x2_mirror, y2, fill="#4a90e2", width=2)
        
        # Додаємо підписи
        num_gores = pattern.get('num_gores', 12)
        pear_height = pattern.get('height', 3.0)
        top_radius = pattern.get('top_radius', 1.2)
        bottom_radius = pattern.get('bottom_radius', 0.6)
        
        self.gui.pattern_canvas.create_text(
            center_x, 20, text=f"Сегмент груші ({num_gores} сегментів)",
            fill="#ffffff", font=("Arial", 12, "bold")
        )
        self.gui.pattern_canvas.create_text(
            center_x, height - 40, 
            text=f"Висота: {pear_height:.2f} м\nВерхній радіус: {top_radius:.2f} м\nНижній радіус: {bottom_radius:.2f} м",
            fill="#cccccc", font=("Arial", 9), justify="center"
        )
    
    def _draw_cigar_pattern(self, pattern, width, height):
        """Малює гобеновий сегмент для сигари"""
        points = pattern.get('points', [])
        if not points:
            return
        
        max_y = max(y for x, y in points) if points else 1
        max_x = max(x for x, y in points) if points else 1
        
        scale_x = (width * 0.8) / (2 * max_x) if max_x > 0 else 1
        scale_y = (height * 0.8) / max_y if max_y > 0 else 1
        scale = min(scale_x, scale_y)
        
        center_x = width / 2
        center_y = height / 2
        
        # Малюємо сегмент
        coords = []
        for x, y in points:
            # Для сигари y йде вздовж осі (від 0 до length)
            screen_x = center_x + x * scale
            screen_y = center_y + (y - max_y / 2) * scale  # Y від низу до верху
            coords.append((screen_x, screen_y))
        
        # Малюємо ліву половину сегмента
        if len(coords) > 1:
            for i in range(len(coords) - 1):
                x1, y1 = coords[i]
                x2, y2 = coords[i + 1]
                self.gui.pattern_canvas.create_line(x1, y1, x2, y2, fill="#4a90e2", width=2)
        
        # Малюємо праву половину (дзеркально)
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            # Дзеркалюємо відносно центру
            x1_mirror = center_x - (x1 - center_x)
            x2_mirror = center_x - (x2 - center_x)
            self.gui.pattern_canvas.create_line(x1_mirror, y1, x2_mirror, y2, fill="#4a90e2", width=2)
        
        # Додаємо підписи
        num_gores = pattern.get('num_gores', 12)
        cigar_length = pattern.get('length', 5.0)
        radius = pattern.get('radius', 1.0)
        
        self.gui.pattern_canvas.create_text(
            center_x, 20, text=f"Сегмент сигари ({num_gores} сегментів)",
            fill="#ffffff", font=("Arial", 12, "bold")
        )
        self.gui.pattern_canvas.create_text(
            center_x, height - 40, 
            text=f"Довжина: {cigar_length:.2f} м\nРадіус: {radius:.2f} м",
            fill="#cccccc", font=("Arial", 9), justify="center"
        )

