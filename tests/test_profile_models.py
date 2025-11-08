"""Tests for profile data models."""

from datetime import date
import pytest
from wctf_core.models.profile import (
    Profile,
    EnergyDrain,
    EnergyGenerator,
    CoreStrength,
    GrowthArea,
)


def test_profile_basic_structure():
    """Test basic profile structure validates correctly."""
    profile = Profile(
        profile_version="1.0",
        last_updated=date(2025, 1, 8),
        energy_drains={
            "interpersonal_conflict": EnergyDrain(
                severity="severe",
                trigger="childhood_trauma",
                description="Conflicts in close working relationships",
            )
        },
        energy_generators={
            "visible_progress": EnergyGenerator(
                strength="core_need",
                description="Building things, shipping features",
            )
        },
        core_strengths=[
            CoreStrength(
                name="systems_thinking",
                level="expert",
                description="Designing complex interconnected systems",
            )
        ],
        growth_areas=[],
    )

    assert profile.profile_version == "1.0"
    assert "interpersonal_conflict" in profile.energy_drains
    assert profile.energy_drains["interpersonal_conflict"].severity == "severe"


def test_drain_severity_validation():
    """Test that drain severity only accepts valid values."""
    with pytest.raises(ValueError):
        EnergyDrain(
            severity="invalid",
            trigger="test",
            description="test",
        )


def test_generator_strength_validation():
    """Test that generator strength only accepts valid values."""
    with pytest.raises(ValueError):
        EnergyGenerator(
            strength="invalid",
            description="test",
        )


def test_strength_level_validation():
    """Test that strength level only accepts valid values."""
    with pytest.raises(ValueError):
        CoreStrength(
            name="test",
            level="invalid",
            description="test",
        )
