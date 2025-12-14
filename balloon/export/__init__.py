"""
Модуль для експорту результатів розрахунку та викрійок
"""

# Імпортуємо з export_core.py (щоб уникнути конфлікту з пакетом export/)
from balloon.export_core import export_results_to_excel, export_pattern_to_excel, export_pattern_to_svg
from balloon.export.nesting import estimate_fabric_requirements

try:
    from balloon.export.pdf_export import export_pattern_to_pdf
    PDF_EXPORT_AVAILABLE = True
except ImportError:
    PDF_EXPORT_AVAILABLE = False
    export_pattern_to_pdf = None

try:
    from balloon.export.dxf_export import export_pattern_to_dxf
    DXF_EXPORT_AVAILABLE = True
except ImportError:
    DXF_EXPORT_AVAILABLE = False
    export_pattern_to_dxf = None

try:
    from balloon.export.report_generator import generate_pdf_report, generate_html_report
    REPORT_GENERATOR_AVAILABLE = True
except ImportError:
    REPORT_GENERATOR_AVAILABLE = False
    generate_pdf_report = None
    generate_html_report = None

__all__ = [
    'export_results_to_excel',
    'export_pattern_to_excel',
    'export_pattern_to_svg',
    'estimate_fabric_requirements',
]

if PDF_EXPORT_AVAILABLE:
    __all__.append('export_pattern_to_pdf')

if DXF_EXPORT_AVAILABLE:
    __all__.append('export_pattern_to_dxf')

if REPORT_GENERATOR_AVAILABLE:
    __all__.extend(['generate_pdf_report', 'generate_html_report'])
