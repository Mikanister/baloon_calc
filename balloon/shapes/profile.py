"""
Єдине джерело геометрії через профіль поверхні обертання r(z)

Кожна форма визначається через профіль r(z), де:
- z: координата вздовж осі обертання (0..height)
- r(z): радіус на висоті z

Це забезпечує узгодженість між:
- 3D візуалізацією (обертання профілю)
- Розкроєм (меридіанна довжина s(z) = ∫sqrt(1+(dr/dz)^2)dz)
- Площею/об'ємом (чисельна інтеграція)
"""

import math
import numpy as np
import warnings
from typing import Callable, Tuple, Optional

# Використовуємо scipy для точнішого обчислення інтегралів
# Застосовується до всіх форм (sphere, pear, cigar) для покращення точності меридіанної довжини
try:
    from scipy import integrate
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
from dataclasses import dataclass


@dataclass
class ShapeProfile:
    """Профіль форми поверхні обертання"""
    r_func: Callable[[float], float]  # r(z) - радіус на висоті z
    z_range: Tuple[float, float]  # (z_min, z_max)
    has_cap_top: bool = False  # Чи є "кришка" зверху (півсфера/плоска)
    has_cap_bottom: bool = False  # Чи є "кришка" знизу
    cap_radius: Optional[float] = None  # Радіус кришки (якщо є)
    
    def get_radius(self, z: float) -> float:
        """Повертає радіус на висоті z"""
        z_min, z_max = self.z_range
        if z < z_min or z > z_max:
            return 0.0
        return self.r_func(z)
    
    def get_meridian_length(self, z: float, num_points: int = 100) -> float:
        """
        Обчислює довжину меридіану від z_min до z
        
        s(z) = ∫[z_min to z] sqrt(1 + (dr/dz)^2) dz
        
        Використовує scipy.integrate.quad для точнішого обчислення, якщо доступний
        """
        z_min, z_max = self.z_range
        if z <= z_min:
            return 0.0
        if z > z_max:
            z = z_max
        
        # Використовуємо scipy для точнішого обчислення, якщо доступний
        # Застосовується до всіх форм (sphere, pear, cigar)
        if SCIPY_AVAILABLE:
            try:
                # Функція для інтегрування
                def integrand(z_val):
                    r = self.r_func(z_val)
                    # Обчислюємо похідну чисельно
                    eps = 1e-6
                    r_plus = self.r_func(z_val + eps)
                    r_minus = self.r_func(z_val - eps) if z_val > z_min + eps else r
                    dr_dz = (r_plus - r_minus) / (2 * eps) if eps > 0 else 0.0
                    return math.sqrt(1 + dr_dz**2)
                
                # Використовуємо quad для адаптивної квадратури
                # Приглушуємо попередження про збіжність - fallback метод все одно точний
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', category=integrate.IntegrationWarning)
                    result, _ = integrate.quad(integrand, z_min, z, limit=100, epsabs=1e-6, epsrel=1e-6)
                return result
            except Exception:
                # Якщо scipy не працює, використовуємо старий метод
                pass
        
        # Чисельна інтеграція (fallback)
        z_points = np.linspace(z_min, z, num_points)
        s = 0.0
        
        for i in range(1, len(z_points)):
            z1 = z_points[i-1]
            z2 = z_points[i]
            r1 = self.r_func(z1)
            r2 = self.r_func(z2)
            
            # Приблизна похідна dr/dz
            dr_dz = (r2 - r1) / (z2 - z1) if z2 != z1 else 0.0
            
            # Довжина сегмента
            ds = math.sqrt(1 + dr_dz**2) * (z2 - z1)
            s += ds
        
        return s
    
    def get_total_meridian_length(self, num_points: int = 100) -> float:
        """Повна довжина меридіану"""
        _, z_max = self.z_range
        return self.get_meridian_length(z_max, num_points)
    
    def get_volume(self, num_points: int = 100) -> float:
        """
        Обчислює об'єм через обертання профілю
        
        V = π ∫[z_min to z_max] r(z)^2 dz
        """
        z_min, z_max = self.z_range
        z_points = np.linspace(z_min, z_max, num_points)
        
        volume = 0.0
        for i in range(1, len(z_points)):
            z1 = z_points[i-1]
            z2 = z_points[i]
            r1 = self.r_func(z1)
            r2 = self.r_func(z2)
            
            # Трапеційна інтеграція
            dz = z2 - z1
            volume += math.pi * (r1**2 + r2**2) / 2 * dz
        
        return volume
    
    def get_surface_area(self, num_points: int = 100) -> float:
        """
        Обчислює площу поверхні через обертання профілю
        
        S = 2π ∫[z_min to z_max] r(z) * sqrt(1 + (dr/dz)^2) dz
        """
        z_min, z_max = self.z_range
        z_points = np.linspace(z_min, z_max, num_points)
        
        area = 0.0
        for i in range(1, len(z_points)):
            z1 = z_points[i-1]
            z2 = z_points[i]
            r1 = self.r_func(z1)
            r2 = self.r_func(z2)
            
            # Приблизна похідна
            dr_dz = (r2 - r1) / (z2 - z1) if z2 != z1 else 0.0
            
            # Середній радіус
            r_avg = (r1 + r2) / 2
            
            # Довжина сегмента
            ds = math.sqrt(1 + dr_dz**2) * (z2 - z1)
            
            area += 2 * math.pi * r_avg * ds
        
        return area
    
    def generate_mesh(self, num_theta: int = 50, num_z: int = 50, center_at_origin: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Генерує 3D mesh з профілю через обертання r(z) навколо осі Z
        
        Використовує адаптивну дискретизацію по Z для кращої якості в зонах з великою кривизною
        (наприклад, півсфери в груші та сигарі, полюси сфери)
        
        Args:
            num_theta: Кількість точок по азимутальному куту (0..2π)
            num_z: Кількість точок по осі Z (базова, може бути збільшена адаптивно)
            center_at_origin: Чи центрувати mesh на (0,0,0)
        
        Returns:
            Tuple[x, y, z] - три масиви координат для 3D візуалізації
        """
        z_min, z_max = self.z_range
        
        # Адаптивна дискретизація по Z: більше точок там, де похідна dr/dz велика
        # Це покращує якість mesh для форм з великою кривизною
        z_points = self._adaptive_z_discretization_for_mesh(z_min, z_max, num_z)
        
        # Координати по theta (рівномірно, оскільки обертання симетричне)
        theta_points = np.linspace(0, 2 * np.pi, num_theta)
        
        # Створюємо сітку
        z_grid, theta_grid = np.meshgrid(z_points, theta_points)
        
        # Обчислюємо радіус для кожної точки Z
        r_grid = np.zeros_like(z_grid)
        for i in range(len(z_points)):
            z_val = z_points[i]
            r_val = self.r_func(z_val)
            r_grid[:, i] = r_val
        
        # Конвертуємо в декартові координати
        x = r_grid * np.cos(theta_grid)
        y = r_grid * np.sin(theta_grid)
        z = z_grid
        
        # Центруємо навколо (0,0,0), якщо потрібно
        if center_at_origin:
            z_center = (z_min + z_max) / 2
            z = z - z_center
        
        return x, y, z
    
    def _adaptive_z_discretization_for_mesh(self, z_min: float, z_max: float, num_points: int) -> np.ndarray:
        """
        Адаптивна дискретизація по Z для mesh: більше точок там, де похідна dr/dz велика
        
        Аналогічно до _adaptive_z_discretization в patterns/profile_based.py,
        але оптимізовано для mesh генерації
        """
        # Спочатку створюємо рівномірну сітку для оцінки похідної
        uniform_z = np.linspace(z_min, z_max, num_points * 2)
        
        # Обчислюємо похідну dr/dz для кожної точки
        derivatives = []
        for i in range(len(uniform_z) - 1):
            z1 = uniform_z[i]
            z2 = uniform_z[i + 1]
            r1 = self.r_func(z1)
            r2 = self.r_func(z2)
            dr_dz = abs((r2 - r1) / (z2 - z1)) if z2 != z1 else 0.0
            derivatives.append(dr_dz)
        
        # Нормалізуємо похідні
        max_deriv = max(derivatives) if derivatives else 1.0
        if max_deriv == 0:
            # Якщо похідна всюди 0, використовуємо рівномірну дискретизацію
            return np.linspace(z_min, z_max, num_points + 1)
        
        normalized_derivs = [d / max_deriv for d in derivatives]
        
        # Розподіляємо точки пропорційно до похідної
        z_points = [z_min]
        total_weight = sum(1 + norm_deriv * 2 for norm_deriv in normalized_derivs)
        
        points_remaining = num_points - 1
        
        for i in range(len(normalized_derivs)):
            if points_remaining <= 0:
                break
            
            z1 = uniform_z[i]
            z2 = uniform_z[i + 1]
            norm_deriv = normalized_derivs[i]
            
            # Кількість точок на цьому інтервалі пропорційна до похідної
            weight = 1 + norm_deriv * 2
            points_for_interval = max(1, min(points_remaining, int(num_points * weight / total_weight)))
            
            # Додаємо точки на цьому інтервалі
            for j in range(1, points_for_interval + 1):
                if points_remaining <= 0:
                    break
                t = j / (points_for_interval + 1)
                z = z1 + (z2 - z1) * t
                if z > z_points[-1] and z < z_max:
                    z_points.append(z)
                    points_remaining -= 1
        
        # Додаємо останню точку
        if z_points[-1] < z_max:
            z_points.append(z_max)
        
        # Додаємо додаткові точки біля вершин для плавності
        # (де радіус швидко зменшується до 0)
        apex_z = z_max
        if self.r_func(apex_z) < 1e-6:  # Якщо вершина є точкою
            # Додаємо 3-5 точок в останніх 5% висоти
            for i in range(1, 4):
                z_val = apex_z - (apex_z - z_min) * (0.05 / 3) * (3 - i)
                if z_val > z_points[-2] and z_val < z_max:
                    z_points.append(z_val)
        
        # Сортуємо та видаляємо дублікати
        z_points = sorted(set(z_points))
        
        return np.array(z_points)


def create_sphere_profile(radius: float) -> ShapeProfile:
    """Створює профіль сфери"""
    def r_func(z: float) -> float:
        # Для сфери радіуса R, центр на z = R
        # r(z) = sqrt(R^2 - (z - R)^2) для z в [0, 2R]
        if z < 0 or z > 2 * radius:
            return 0.0
        return math.sqrt(radius**2 - (z - radius)**2)
    
    return ShapeProfile(
        r_func=r_func,
        z_range=(0.0, 2 * radius),
        has_cap_top=False,
        has_cap_bottom=False
    )


def create_pillow_profile(length: float, width: float, thickness: float) -> ShapeProfile:
    """
    Створює профіль подушки (паралелепіпед)
    
    Для подушки профіль - це прямокутник з радіусом = width/2 (постійний)
    """
    def r_func(z: float) -> float:
        # Для подушки: радіус постійний = width/2
        if z < 0 or z > thickness:
            return 0.0
        return width / 2
    
    return ShapeProfile(
        r_func=r_func,
        z_range=(0.0, thickness),
        has_cap_top=False,
        has_cap_bottom=False
    )


def create_pear_profile(height: float, top_radius: float, bottom_radius: float) -> ShapeProfile:
    """
    Створює профіль груші: півсфера зверху + усічений конус
    
    Верхня частина (40% висоти): півсфера радіуса top_radius
    Нижня частина (60% висоти): усічений конус від top_radius до bottom_radius
    
    Відповідає аналітичній формулі pear_volume():
    - Півсфера: V = (2/3)π * top_radius^3
    - Конус: V = (πh/3) * (R² + Rr + r²)
    
    Виправлено: півсфера починається на z = h_bottom, де радіус = top_radius
    Центр півсфери на z = h_bottom (на межі), радіус top_radius
    Але обмежена зверху на z = height
    """
    h_top = height * 0.4
    h_bottom = height * 0.6
    z_sphere_start = h_bottom  # Початок півсфери (де конус досягає top_radius)
    z_sphere_center = h_bottom  # Центр півсфери на межі (де радіус = top_radius)
    
    def r_func(z: float) -> float:
        if z < 0 or z > height:
            return 0.0
        
        if z >= z_sphere_start:
            # Півсфера: центр на z = h_bottom, радіус top_radius
            # На z = h_bottom: r = top_radius (край півсфери)
            # На z > h_bottom: r зменшується за формулою півсфери
            dist_from_center = z - z_sphere_center  # Відстань від центру (завжди >= 0 для z >= h_bottom)
            
            # Перевіряємо, чи не на вершині (з невеликим допуском для числових помилок)
            if z >= height - 1e-6:
                return 0.0
            
            if dist_from_center >= top_radius:
                # За межами півсфери - між h_bottom + top_radius і height
                # Радіус зменшується лінійно до 0
                if z > h_bottom + top_radius:
                    # Лінійна інтерполяція від top_radius до 0
                    remaining_height = height - (h_bottom + top_radius)
                    if remaining_height > 1e-6:
                        t = (z - (h_bottom + top_radius)) / remaining_height
                        return top_radius * (1 - t)
                    return 0.0
                # Якщо dist_from_center == top_radius (на межі півсфери)
                return 0.0
            
            # В межах півсфери
            r_sq = top_radius**2 - dist_from_center**2
            if r_sq < 0:
                return 0.0
            return math.sqrt(r_sq)
        else:
            # Усічений конус: лінійна інтерполяція
            # z від 0 до h_bottom, r від bottom_radius до top_radius
            t = z / h_bottom if h_bottom > 0 else 0
            return bottom_radius * (1 - t) + top_radius * t
    
    return ShapeProfile(
        r_func=r_func,
        z_range=(0.0, height),
        has_cap_top=True,
        cap_radius=top_radius
    )


def create_cigar_profile(length: float, radius: float) -> ShapeProfile:
    """
    Створює профіль сигари: циліндр + дві півсфери
    
    Нижня півсфера: z від 0 до radius
    Циліндр: z від radius до length - radius
    Верхня півсфера: z від length - radius до length
    """
    def r_func(z: float) -> float:
        if z < 0 or z > length:
            return 0.0
        
        if z < radius:
            # Нижня півсфера
            r_sq = radius**2 - (z - radius)**2
            if r_sq < 0:
                return 0.0
            return math.sqrt(r_sq)
        elif z > length - radius:
            # Верхня півсфера
            z_from_top = length - z
            r_sq = radius**2 - (z_from_top - radius)**2
            if r_sq < 0:
                return 0.0
            return math.sqrt(r_sq)
        else:
            # Циліндрична частина
            return radius
    
    return ShapeProfile(
        r_func=r_func,
        z_range=(0.0, length),
        has_cap_top=True,
        has_cap_bottom=True,
        cap_radius=radius
    )


def get_shape_profile(shape_type: str, shape_params: dict) -> Optional[ShapeProfile]:
    """
    Створює профіль форми на основі типу та параметрів через Shape Registry
    
    Args:
        shape_type: Тип форми ('sphere', 'pillow', 'pear', 'cigar')
        shape_params: Параметри форми
    
    Returns:
        ShapeProfile або None, якщо форма не підтримується
    """
    # Використовуємо реєстр замість if/elif логіки
    from balloon.shapes.registry import get_shape_profile_from_registry
    return get_shape_profile_from_registry(shape_type, shape_params)

