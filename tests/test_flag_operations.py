"""Tests for flag operations with Energy Matrix integration.

These tests verify that flag operations correctly integrate with the Energy Matrix
calculator and synthesis modules to auto-calculate quadrants.
"""

from datetime import date
from pathlib import Path
import pytest
import yaml

from wctf_core.operations.flags import save_flags_op


@pytest.fixture
def temp_wctf_dir(tmp_path):
    """Create a temporary WCTF directory structure."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return tmp_path


def test_save_flags_auto_calculates_quadrants(temp_wctf_dir, monkeypatch):
    """Test that save_flags auto-calculates Energy Matrix quadrants."""
    # Setup profile
    profile_path = temp_wctf_dir / "data" / "profile.yaml"
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_data = {
        "profile_version": "1.0",
        "last_updated": "2025-01-08",
        "energy_drains": {},
        "energy_generators": {
            "visible_progress": {
                "strength": "core_need",
                "description": "test",
            },
        },
        "core_strengths": [
            {
                "name": "systems_thinking",
                "level": "expert",
                "description": "test",
            },
        ],
        "growth_areas": [],
        "organizational_coherence_needs": [],
    }
    with open(profile_path, "w") as f:
        yaml.dump(profile_data, f)

    monkeypatch.setenv("WCTF_ROOT", str(temp_wctf_dir))

    # Create flags with task implications (no quadrant set)
    flags_yaml = """
company: "TestCorp"
evaluation_date: "2025-01-08"
evaluator_context: "Test"
profile_version_used: "1.0"
green_flags:
  mountain_range:
    critical_matches:
      - flag: "Good tech"
        impact: "High"
        confidence: "High"
        task_implications:
          - task: "Build stuff"
            time_estimate_pct: "30%"
            characteristics:
              conflict_exposure: "low"
              alignment_clarity: "high"
              authority_ambiguity: "low"
              progress_visibility: "high"
              autonomy_level: "high"
              decision_speed: "fast"
              learning_required: "low"
              uses_systems_thinking: true
              uses_tool_building: false
              uses_glue_work: false
              uses_infrastructure_automation: false
              uses_decision_frameworks: false
              collaboration_type: "team"
              meeting_intensity: "low"
              requires_sync_communication: false
              timezone_spread: "narrow"
    strong_positives: []
  chosen_peak:
    critical_matches: []
    strong_positives: []
  rope_team_confidence:
    critical_matches: []
    strong_positives: []
  daily_climb:
    critical_matches: []
    strong_positives: []
  story_worth_telling:
    critical_matches: []
    strong_positives: []
red_flags:
  mountain_range:
    dealbreakers: []
    concerning: []
  chosen_peak:
    dealbreakers: []
    concerning: []
  rope_team_confidence:
    dealbreakers: []
    concerning: []
  daily_climb:
    dealbreakers: []
    concerning: []
  story_worth_telling:
    dealbreakers: []
    concerning: []
missing_critical_data: []
"""

    # Execute
    result = save_flags_op("TestCorp", flags_yaml, base_path=temp_wctf_dir)

    # Verify save succeeded
    assert result["success"] is True

    # Load saved file and check quadrant was calculated
    from wctf_core.utils.paths import get_flags_path
    flags_path = get_flags_path("TestCorp", base_path=temp_wctf_dir)
    assert flags_path.exists()

    with open(flags_path) as f:
        saved_flags = yaml.safe_load(f)

    # Verify quadrant was calculated
    task_impl = saved_flags["green_flags"]["mountain_range"]["critical_matches"][0]["task_implications"][0]
    assert "energy_matrix_quadrant" in task_impl
    assert task_impl["energy_matrix_quadrant"] in ["moare", "sparingly", "burnout", "help_mentoring"]

    # Verify synthesis was generated
    assert "synthesis" in saved_flags
    assert "energy_matrix_analysis" in saved_flags["synthesis"]
    analysis = saved_flags["synthesis"]["energy_matrix_analysis"]

    assert "profile_version_used" in analysis
    assert analysis["profile_version_used"] == "1.0"

    assert "predicted_daily_distribution" in analysis
    assert "threshold_analysis" in analysis
    assert "energy_sustainability" in analysis
    assert analysis["energy_sustainability"] in ["HIGH", "MEDIUM", "LOW"]
