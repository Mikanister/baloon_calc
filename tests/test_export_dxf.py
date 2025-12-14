"""
Тести для модуля balloon.export.dxf_export
"""

import pytest
import tempfile
import os

# Перевіряємо доступність ezdxf
try:
    import ezdxf
    DXF_AVAILABLE = True
except ImportError:
    DXF_AVAILABLE = False

if DXF_AVAILABLE:
    from balloon.export.dxf_export import export_pattern_to_dxf


@pytest.mark.skipif(not DXF_AVAILABLE, reason="ezdxf not available")
class TestExportPatternToDxf:
    """Тести для функції export_pattern_to_dxf"""
    
    def test_export_sphere_pattern(self):
        """Експорт патерну сфери"""
        pattern = {
            'pattern_type': 'sphere_gore',
            'points': [(0.0, 0.0), (1.0, 1.0), (0.0, 2.0)],
            'num_gores': 12
        }
        
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as f:
            filename = f.name
        
        try:
            result = export_pattern_to_dxf(pattern, filename)
            assert os.path.exists(result)
            assert result.endswith('.dxf')
        finally:
            if os.path.exists(filename):
                os.remove(filename)
    
    def test_export_with_notches(self):
        """Експорт з мітками суміщення"""
        pattern = {
            'pattern_type': 'sphere_gore',
            'points': [(0.0, 0.0), (1.0, 1.0), (0.0, 2.0)],
            'num_gores': 12,
            'notches': [(0.5, 0.5), (0.5, 1.5)]
        }
        
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as f:
            filename = f.name
        
        try:
            result = export_pattern_to_dxf(pattern, filename, add_notches=True)
            assert os.path.exists(result)
        finally:
            if os.path.exists(filename):
                os.remove(filename)
    
    def test_export_empty_pattern(self):
        """Перевірка обробки порожнього патерну"""
        pattern = {
            'pattern_type': 'sphere_gore',
            'points': [],
            'num_gores': 12
        }
        
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as f:
            filename = f.name
        
        try:
            with pytest.raises(ValueError, match="не містить координат"):
                export_pattern_to_dxf(pattern, filename)
        finally:
            if os.path.exists(filename):
                os.remove(filename)

