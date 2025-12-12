"""
Конфігурація та фікстури для pytest
"""

import pytest
import sys
import os

# Додаємо шлях до модулів для імпорту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def sample_balloon_params():
    """Фікстура з прикладовими параметрами аеростата"""
    return {
        'gas_type': 'Гелій',
        'gas_volume': 10.0,
        'material': 'TPU',
        'thickness_mm': 35.0,
        'start_height': 0.0,
        'work_height': 1000.0,
        'ground_temp': 15.0,
        'inside_temp': 100.0,
        'mode': 'payload',
        'duration': 24.0,
        'perm_mult': 1.0
    }


@pytest.fixture
def sample_hot_air_params():
    """Фікстура з параметрами для гарячого повітря"""
    return {
        'gas_type': 'Гаряче повітря',
        'gas_volume': 100.0,
        'material': 'TPU',
        'thickness_mm': 50.0,
        'start_height': 0.0,
        'work_height': 500.0,
        'ground_temp': 15.0,
        'inside_temp': 100.0,
        'mode': 'payload',
        'duration': 0.0,
        'perm_mult': 1.0
    }

