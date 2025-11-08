"""Integration tests for complete Energy Matrix workflow."""

from datetime import date
import pytest
import yaml

from wctf_core.operations.profile import get_profile, update_profile
from wctf_core.operations.flags import save_flags_op
from wctf_core.operations.company import get_company_flags


@pytest.fixture
def setup_wctf_with_profile(tmp_path, monkeypatch):
    """Setup WCTF directory with profile."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Create profile
    profile_data = {
        "profile_version": "1.0",
        "last_updated": "2025-01-08",
        "energy_drains": {
            "interpersonal_conflict": {
                "severity": "severe",
                "trigger": "childhood_trauma",
                "description": "Conflicts drain energy",
            },
        },
        "energy_generators": {
            "visible_progress": {
                "strength": "core_need",
                "description": "Progress energizes",
            },
        },
        "core_strengths": [
            {
                "name": "systems_thinking",
                "level": "expert",
                "description": "Expert systems thinker",
            },
        ],
        "growth_areas": [],
    }

    profile_path = data_dir / "profile.yaml"
    with open(profile_path, "w") as f:
        yaml.dump(profile_data, f)

    monkeypatch.setenv("WCTF_ROOT", str(tmp_path))

    return tmp_path


def test_complete_energy_workflow(setup_wctf_with_profile):
    """Test complete workflow: profile -> flags with tasks -> synthesis."""

    # Step 1: Get profile
    profile_result = get_profile()
    assert "1.0" in profile_result
    assert "systems_thinking" in profile_result

    # Step 2: Save flags with task implications
    flags_yaml = """
company: "AppleDublin"
evaluation_date: "2025-01-08"
evaluator_context: "Test evaluation"
profile_version_used: "1.0"
green_flags:
  mountain_range:
    critical_matches:
      - flag: "Modern tech stack"
        impact: "Matches expertise"
        confidence: "High"
        task_implications:
          - task: "Build K8s operators"
            time_estimate_pct: "20%"
            characteristics:
              conflict_exposure: "low"
              alignment_clarity: "high"
              authority_ambiguity: "low"
              progress_visibility: "high"
              autonomy_level: "high"
              decision_speed: "fast"
              uses_systems_thinking: true
              learning_required: "low"
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
    dealbreakers:
      - flag: "Siloed teams with conflicts"
        impact: "High conflict exposure"
        confidence: "High"
        task_implications:
          - task: "Navigate cross-silo conflicts"
            time_estimate_pct: "40%"
            characteristics:
              conflict_exposure: "high"
              alignment_clarity: "low"
              authority_ambiguity: "high"
              progress_visibility: "low"
              autonomy_level: "low"
              decision_speed: "slow"
              uses_systems_thinking: false
              learning_required: "moderate"
              collaboration_type: "cross_team"
              meeting_intensity: "high"
              requires_sync_communication: true
              timezone_spread: "moderate"
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

    save_result = save_flags_op("AppleDublin", flags_yaml, base_path=setup_wctf_with_profile)
    assert save_result["success"] is True

    # Step 3: Get flags back and verify synthesis
    flags_result = get_company_flags("AppleDublin", base_path=setup_wctf_with_profile)
    assert flags_result["success"] is True

    flags_data = flags_result["flags"]

    # Verify synthesis exists
    assert "synthesis" in flags_data
    assert "energy_matrix_analysis" in flags_data["synthesis"]

    synthesis = flags_data["synthesis"]["energy_matrix_analysis"]

    # Should have 20% moare and 40% burnout
    assert synthesis["predicted_daily_distribution"]["moare_green_flags"]["percentage"] == 20
    assert synthesis["predicted_daily_distribution"]["burnout_red_flags"]["percentage"] == 40

    # Should fail thresholds
    assert synthesis["threshold_analysis"]["meets_green_minimum"] is False
    assert synthesis["threshold_analysis"]["exceeds_red_maximum"] is True

    # Should have LOW sustainability
    assert synthesis["energy_sustainability"] == "LOW"
