"""Tests for profile operations."""

from datetime import date
from pathlib import Path
import pytest
import tempfile
import yaml

from wctf_core.operations.profile import get_profile, update_profile
from wctf_core.models.profile import Profile, EnergyDrain, EnergyGenerator, CoreStrength


@pytest.fixture
def temp_wctf_dir(tmp_path):
    """Create a temporary WCTF directory structure."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return tmp_path


def test_get_profile_loads_existing_profile(temp_wctf_dir, monkeypatch):
    """Test loading an existing profile."""
    # Setup: create a profile file
    profile_path = temp_wctf_dir / "data" / "profile.yaml"
    profile_data = {
        "profile_version": "1.0",
        "last_updated": "2025-01-08",
        "energy_drains": {
            "interpersonal_conflict": {
                "severity": "severe",
                "trigger": "childhood_trauma",
                "description": "Conflicts drain energy",
            }
        },
        "energy_generators": {
            "visible_progress": {
                "strength": "core_need",
                "description": "Building things energizes",
            }
        },
        "core_strengths": [
            {
                "name": "systems_thinking",
                "level": "expert",
                "description": "Designing complex systems",
            }
        ],
        "growth_areas": [],
    }

    with open(profile_path, "w") as f:
        yaml.dump(profile_data, f)

    # Mock the WCTF_ROOT to use our temp directory
    monkeypatch.setenv("WCTF_ROOT", str(temp_wctf_dir))

    # Execute
    result = get_profile()

    # Verify
    assert "profile_version" in result
    assert "1.0" in result
    assert "interpersonal_conflict" in result


def test_get_profile_returns_error_when_missing(temp_wctf_dir, monkeypatch):
    """Test error message when profile doesn't exist."""
    monkeypatch.setenv("WCTF_ROOT", str(temp_wctf_dir))

    result = get_profile()

    assert "error" in result.lower() or "not found" in result.lower()


def test_update_profile_increments_version(temp_wctf_dir, monkeypatch):
    """Test that updating profile increments version."""
    # Setup: create initial profile
    profile_path = temp_wctf_dir / "data" / "profile.yaml"
    profile_data = {
        "profile_version": "1.0",
        "last_updated": "2025-01-08",
        "energy_drains": {},
        "energy_generators": {},
        "core_strengths": [],
        "growth_areas": [],
    }

    with open(profile_path, "w") as f:
        yaml.dump(profile_data, f)

    monkeypatch.setenv("WCTF_ROOT", str(temp_wctf_dir))

    # Execute: update with new content
    updated_profile_yaml = """
profile_version: "1.0"
last_updated: "2025-01-08"
energy_drains:
  misalignment:
    severity: "severe"
    trigger: "blocks_progress"
    description: "Team moving in different directions"
energy_generators: {}
core_strengths: []
growth_areas: []
"""

    result = update_profile(updated_profile_yaml)

    # Verify: version should be incremented
    assert "1.1" in result

    # Verify: file was updated
    with open(profile_path) as f:
        saved_data = yaml.safe_load(f)

    assert saved_data["profile_version"] == "1.1"
    assert "misalignment" in saved_data["energy_drains"]
