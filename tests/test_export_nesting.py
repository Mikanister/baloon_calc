"""
Тести для модуля balloon.export.nesting
"""

import pytest
from balloon.export.nesting import estimate_fabric_requirements


class TestEstimateFabricRequirements:
    """Тести для функції estimate_fabric_requirements"""
    
    def test_basic_estimation(self):
        """Базова оцінка вимог до тканини"""
        pattern = {
            'pattern_type': 'sphere_gore',
            'num_gores': 12,
            'meridian_length': 3.14,  # м
            'max_width': 1.0  # м
        }
        
        result = estimate_fabric_requirements(pattern, fabric_width_mm=1500.0)
        
        assert 'fabric_length_m' in result
        assert 'fabric_area_m2' in result
        assert 'waste_percent' in result
        assert result['fabric_length_m'] > 0
        assert result['fabric_area_m2'] > 0
    
    def test_pillow_pattern(self):
        """Оцінка для подушки"""
        pattern = {
            'pattern_type': 'pillow',
            'length': 3.0,
            'width': 2.0,
            'panels': [
                {'width': 3.0, 'height': 2.0},
                {'width': 3.0, 'height': 2.0}
            ]
        }
        
        result = estimate_fabric_requirements(pattern, fabric_width_mm=1500.0)
        
        assert result['fabric_length_m'] > 0
        assert result['waste_percent'] >= 0
    
    def test_narrow_fabric(self):
        """Перевірка з вузькою тканиною"""
        pattern = {
            'pattern_type': 'sphere_gore',
            'num_gores': 12,
            'meridian_length': 3.14,
            'max_width': 1.0
        }
        
        result = estimate_fabric_requirements(pattern, fabric_width_mm=500.0)
        
        # З вузькою тканиною потрібно більше довжини
        assert result['fabric_length_m'] > 0
    
    def test_wide_fabric(self):
        """Перевірка з широкою тканиною"""
        pattern = {
            'pattern_type': 'sphere_gore',
            'num_gores': 12,
            'meridian_length': 3.14,
            'max_width': 1.0
        }
        
        result_wide = estimate_fabric_requirements(pattern, fabric_width_mm=2000.0)
        result_narrow = estimate_fabric_requirements(pattern, fabric_width_mm=1000.0)
        
        # Широка тканина потребує менше довжини
        assert result_wide['fabric_length_m'] <= result_narrow['fabric_length_m']

