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
    assert state["net_lift_per_m3"] > 0
    assert state["lift"] == 0
    assert state["payload"] == 0

