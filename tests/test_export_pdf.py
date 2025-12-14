"""
Тести для модуля balloon.export.pdf_export
"""

import pytest
import tempfile
import os

# Перевіряємо доступність reportlab
try:
    import reportlab
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

if PDF_AVAILABLE:
    from balloon.export.pdf_export import (
        _calculate_tiles,
        export_pattern_to_pdf
    )


@pytest.mark.skipif(not PDF_AVAILABLE, reason="reportlab not available")
class TestCalculateTiles:
    """Тести для функції _calculate_tiles"""
    
    def test_single_tile(self):
        """Перевірка одного tile для маленької викрійки"""
        tiles = _calculate_tiles(100.0, 150.0, overlap_mm=10.0)
        
        assert len(tiles) == 1
        assert tiles[0]['row'] == 0
        assert tiles[0]['col'] == 0
        assert tiles[0]['width_mm'] > 0
        assert tiles[0]['height_mm'] > 0
    
    def test_multiple_tiles(self):
        """Перевірка кількох tiles для великої викрійки"""
        # Викрійка більша за A4 (210x297 мм)
        tiles = _calculate_tiles(500.0, 600.0, overlap_mm=10.0)
        
        assert len(tiles) > 1
        # Перевіряємо, що всі tiles мають правильні координати
        for tile in tiles:
            assert 'row' in tile
            assert 'col' in tile
            assert 'x_start_mm' in tile
            assert 'y_start_mm' in tile
            assert tile['x_start_mm'] >= 0
            assert tile['y_start_mm'] >= 0
    
    def test_overlap(self):
        """Перевірка перекриття між tiles"""
        tiles = _calculate_tiles(500.0, 600.0, overlap_mm=20.0)
        
        if len(tiles) > 1:
            # Перевіряємо, що є перекриття через page_x_mm та page_y_mm
            assert tiles[0].get('page_x_mm', 0) == 20.0
            assert tiles[0].get('page_y_mm', 0) == 20.0


@pytest.mark.skipif(not PDF_AVAILABLE, reason="reportlab not available")
class TestExportPatternToPdf:
    """Тести для функції export_pattern_to_pdf"""
    
    def test_export_sphere_pattern(self):
        """Експорт патерну сфери"""
        pattern = {
            'pattern_type': 'sphere_gore',
            'points': [(0.0, 0.0), (1.0, 1.0), (0.0, 2.0)],
            'num_gores': 12,
            'meridian_length': 3.14
        }
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            filename = f.name
        
        try:
            result = export_pattern_to_pdf(pattern, filename)
            assert os.path.exists(result)
            assert result.endswith('.pdf')
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
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            filename = f.name
        
        try:
            result = export_pattern_to_pdf(pattern, filename, add_notches=True)
            assert os.path.exists(result)
        finally:
            if os.path.exists(filename):
                os.remove(filename)
    
    def test_export_with_centerline(self):
        """Експорт з центральною лінією"""
        pattern = {
            'pattern_type': 'sphere_gore',
            'points': [(0.0, 0.0), (1.0, 1.0), (0.0, 2.0)],
            'num_gores': 12
        }
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            filename = f.name
        
        try:
            result = export_pattern_to_pdf(pattern, filename, add_centerline=True)
            assert os.path.exists(result)
        finally:
            if os.path.exists(filename):
                os.remove(filename)

