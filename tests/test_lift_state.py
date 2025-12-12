import pytest

from baloon.analysis import _compute_lift_state


def test_compute_lift_state_positive_lift_helium():
    state = _compute_lift_state(
        gas_type="Гелій",
        material="TPU",
        thickness_mm=35,
        gas_volume=10.0,
        height=0,
        ground_temp=15.0,
        inside_temp=100.0,
    )
    assert state["net_lift_per_m3"] > 0
    assert state["payload"] > 0
    assert state["required_volume"] > 0
    assert state["mass_shell"] > 0


def test_compute_lift_state_no_lift_when_negative_volume():
    state = _compute_lift_state(
        gas_type="Гелій",
        material="TPU",
        thickness_mm=35,
        gas_volume=0.0,
        height=0,
        ground_temp=15.0,
        inside_temp=100.0,
    )
    # При нульовому об'ємі підйомна сила має бути нульовою або від'ємною
    assert state["lift"] <= 0
    # Навантаження може бути від'ємним через масу оболонки, але має бути близьким до нуля
    assert state["payload"] <= 0.5  # Допускаємо невелику похибку через масу оболонки
    # net_lift_per_m3 може бути будь-яким, оскільки об'єм = 0


def test_compute_lift_state_with_pear_shape():
    """Перевірка розрахунку для грушоподібної форми"""
    state = _compute_lift_state(
        gas_type="Гелій",
        material="TPU",
        thickness_mm=35,
        gas_volume=10.0,
        height=1000,
        ground_temp=15.0,
        inside_temp=100.0,
        shape_type="pear",
        shape_params={"pear_height": 3.0}
    )
    assert state["net_lift_per_m3"] > 0
    assert state["payload"] > 0
    assert state["required_volume"] > 0
    assert state["mass_shell"] > 0


def test_compute_lift_state_with_cigar_shape():
    """Перевірка розрахунку для сигароподібної форми"""
    state = _compute_lift_state(
        gas_type="Гелій",
        material="TPU",
        thickness_mm=35,
        gas_volume=10.0,
        height=1000,
        ground_temp=15.0,
        inside_temp=100.0,
        shape_type="cigar",
        shape_params={"cigar_radius": 1.0}
    )
    assert state["net_lift_per_m3"] > 0
    assert state["payload"] > 0
    assert state["required_volume"] > 0
    assert state["mass_shell"] > 0


def test_compute_lift_state_with_pillow_shape():
    """Перевірка розрахунку для форми подушки"""
    state = _compute_lift_state(
        gas_type="Гелій",
        material="TPU",
        thickness_mm=35,
        gas_volume=10.0,
        height=1000,
        ground_temp=15.0,
        inside_temp=100.0,
        shape_type="pillow",
        shape_params={"pillow_len": 3.0, "pillow_wid": 2.0}
    )
    assert state["net_lift_per_m3"] > 0
    assert state["payload"] > 0
    assert state["required_volume"] > 0


def test_compute_lift_state_without_shape_params():
    """Перевірка розрахунку без параметрів форми (автоматичний розрахунок)"""
    state = _compute_lift_state(
        gas_type="Гелій",
        material="TPU",
        thickness_mm=35,
        gas_volume=10.0,
        height=1000,
        ground_temp=15.0,
        inside_temp=100.0,
        shape_type="pear",
        shape_params={}
    )
    assert state["net_lift_per_m3"] > 0
    assert state["payload"] > 0
    assert state["required_volume"] > 0

