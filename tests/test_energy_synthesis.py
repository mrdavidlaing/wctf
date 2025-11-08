"""Tests for Energy Matrix synthesis generation."""

from datetime import date
import pytest

from wctf_core.models import (
    CompanyFlags,
    Flag,
    TaskImplication,
    TaskCharacteristics,
)
from wctf_core.models.profile import Profile, EnergyDrain, EnergyGenerator, CoreStrength
from wctf_core.energy_matrix.synthesis import generate_energy_synthesis


@pytest.fixture
def sample_profile():
    """Create a sample profile."""
    return Profile(
        profile_version="1.0",
        last_updated=date(2025, 1, 8),
        energy_drains={
            "interpersonal_conflict": EnergyDrain(
                severity="severe",
                trigger="test",
                description="test",
            ),
        },
        energy_generators={
            "visible_progress": EnergyGenerator(
                strength="core_need",
                description="test",
            ),
        },
        core_strengths=[
            CoreStrength(
                name="systems_thinking",
                level="expert",
                description="test",
            ),
        ],
        growth_areas=[],
    )


@pytest.fixture
def sample_flags_with_quadrants():
    """Create sample flags with calculated quadrants."""
    return CompanyFlags(
        company="TestCorp",
        evaluation_date=date(2025, 1, 8),
        evaluator_context="Test",
        profile_version_used="1.0",
        staff_engineer_alignment={
            "organizational_maturity": "GOOD",
            "technical_culture": "EXCELLENT",
            "decision_making": "GOOD",
            "work_sustainability": "EXCELLENT",
            "growth_trajectory": "GOOD",
        },
        green_flags={
            "mountain_range": {
                "critical_matches": [
                    Flag(
                        flag="Good tech stack",
                        impact="High",
                        confidence="High",
                        task_implications=[
                            TaskImplication(
                                task="Build systems",
                                time_estimate_pct="30%",
                                energy_matrix_quadrant="mutual",
                                characteristics=TaskCharacteristics(
                                    conflict_exposure="low",
                                    alignment_clarity="high",
                                    authority_ambiguity="low",
                                    progress_visibility="high",
                                    autonomy_level="high",
                                    decision_speed="fast",
                                    learning_required="low",
                                    collaboration_type="team",
                                    meeting_intensity="low",
                                    requires_sync_communication=False,
                                    timezone_spread="narrow",
                                ),
                            ),
                        ],
                    ),
                ],
                "strong_positives": [],
            },
            "chosen_peak": {"critical_matches": [], "strong_positives": []},
            "rope_team_confidence": {"critical_matches": [], "strong_positives": []},
            "daily_climb": {"critical_matches": [], "strong_positives": []},
            "story_worth_telling": {"critical_matches": [], "strong_positives": []},
        },
        red_flags={
            "mountain_range": {
                "dealbreakers": [
                    Flag(
                        flag="Lots of conflict",
                        impact="High",
                        confidence="High",
                        task_implications=[
                            TaskImplication(
                                task="Navigate conflicts",
                                time_estimate_pct="40%",
                                energy_matrix_quadrant="burnout",
                                characteristics=TaskCharacteristics(
                                    conflict_exposure="high",
                                    alignment_clarity="low",
                                    authority_ambiguity="high",
                                    progress_visibility="low",
                                    autonomy_level="low",
                                    decision_speed="slow",
                                    learning_required="moderate",
                                    collaboration_type="cross_team",
                                    meeting_intensity="high",
                                    requires_sync_communication=True,
                                    timezone_spread="wide",
                                ),
                            ),
                        ],
                    ),
                ],
                "concerning": [],
            },
            "chosen_peak": {"dealbreakers": [], "concerning": []},
            "rope_team_confidence": {"dealbreakers": [], "concerning": []},
            "daily_climb": {"dealbreakers": [], "concerning": []},
            "story_worth_telling": {"dealbreakers": [], "concerning": []},
        },
        missing_critical_data=[],
    )


def test_generate_energy_synthesis_calculates_distribution(sample_flags_with_quadrants, sample_profile):
    """Test that synthesis calculates quadrant distribution."""
    synthesis = generate_energy_synthesis(sample_flags_with_quadrants, sample_profile)

    assert "energy_matrix_analysis" in synthesis
    assert "predicted_daily_distribution" in synthesis["energy_matrix_analysis"]

    dist = synthesis["energy_matrix_analysis"]["predicted_daily_distribution"]
    assert "mutual_green_flags" in dist
    assert "burnout_red_flags" in dist

    # Should have 30% mutual and 40% burnout based on time estimates
    assert dist["mutual_green_flags"]["percentage"] == 30
    assert dist["burnout_red_flags"]["percentage"] == 40


def test_generate_energy_synthesis_checks_thresholds(sample_flags_with_quadrants, sample_profile):
    """Test that synthesis checks sustainability thresholds."""
    synthesis = generate_energy_synthesis(sample_flags_with_quadrants, sample_profile)

    thresholds = synthesis["energy_matrix_analysis"]["threshold_analysis"]

    # 30% mutual < 60% required
    assert thresholds["meets_green_minimum"] is False

    # 40% burnout > 20% allowed
    assert thresholds["exceeds_red_maximum"] is True


def test_generate_energy_synthesis_sets_sustainability_rating(sample_flags_with_quadrants, sample_profile):
    """Test that synthesis sets energy_sustainability rating."""
    synthesis = generate_energy_synthesis(sample_flags_with_quadrants, sample_profile)

    # With 40% burnout and 30% mutual, should be LOW
    assert synthesis["energy_matrix_analysis"]["energy_sustainability"] == "LOW"
