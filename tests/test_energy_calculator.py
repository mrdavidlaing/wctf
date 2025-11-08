"""Tests for Energy Matrix quadrant calculation."""

from datetime import date
import pytest

from wctf_core.models import TaskCharacteristics
from wctf_core.models.profile import (
    Profile,
    EnergyDrain,
    EnergyGenerator,
    CoreStrength,
    GrowthArea,
)
from wctf_core.energy_matrix.calculator import calculate_quadrant


@pytest.fixture
def sample_profile():
    """Create a sample profile for testing."""
    return Profile(
        profile_version="1.0",
        last_updated=date(2025, 1, 8),
        energy_drains={
            "interpersonal_conflict": EnergyDrain(
                severity="severe",
                trigger="childhood_trauma",
                description="Conflicts drain energy",
            ),
            "misalignment": EnergyDrain(
                severity="severe",
                trigger="blocks_progress",
                description="Team misalignment drains energy",
            ),
        },
        energy_generators={
            "visible_progress": EnergyGenerator(
                strength="core_need",
                description="Progress energizes",
            ),
            "tool_building": EnergyGenerator(
                strength="core_need",
                description="Building tools energizes",
            ),
        },
        core_strengths=[
            CoreStrength(
                name="systems_thinking",
                level="expert",
                description="Expert at systems",
            ),
            CoreStrength(
                name="tool_building",
                level="expert",
                description="Expert at tools",
            ),
        ],
        growth_areas=[
            GrowthArea(
                name="ai_workflows",
                current_level="learning",
                energizing=True,
                description="Learning AI workflows",
            ),
        ],
    )


def test_mutual_quadrant_high_skill_high_energy(sample_profile):
    """Test task with high skill + high energy = mutual quadrant."""
    chars = TaskCharacteristics(
        # Low conflict, high progress = energizing
        conflict_exposure="low",
        alignment_clarity="high",
        authority_ambiguity="low",
        progress_visibility="high",
        autonomy_level="high",
        decision_speed="fast",
        # Uses core strengths = good at
        learning_required="low",
        uses_systems_thinking=True,
        uses_tool_building=True,
        # Good work context
        collaboration_type="team",
        meeting_intensity="low",
        requires_sync_communication=False,
        timezone_spread="narrow",
    )

    quadrant = calculate_quadrant(chars, sample_profile)

    assert quadrant == "mutual"


def test_burnout_quadrant_low_skill_low_energy(sample_profile):
    """Test task with low skill + low energy = burnout quadrant."""
    chars = TaskCharacteristics(
        # High conflict, low progress = draining
        conflict_exposure="high",
        alignment_clarity="low",
        authority_ambiguity="high",
        progress_visibility="low",
        autonomy_level="low",
        decision_speed="slow",
        # Not using strengths = not good at
        learning_required="high",
        uses_systems_thinking=False,
        uses_tool_building=False,
        # Bad work context
        collaboration_type="cross_team",
        meeting_intensity="high",
        requires_sync_communication=True,
        timezone_spread="wide",
    )

    quadrant = calculate_quadrant(chars, sample_profile)

    assert quadrant == "burnout"


def test_sparingly_quadrant_high_skill_low_energy(sample_profile):
    """Test task with high skill + low energy = sparingly quadrant."""
    chars = TaskCharacteristics(
        # High conflict = draining even if skilled
        conflict_exposure="high",
        alignment_clarity="low",
        authority_ambiguity="moderate",
        progress_visibility="moderate",
        autonomy_level="high",
        decision_speed="moderate",
        # Uses strengths = good at
        learning_required="low",
        uses_systems_thinking=True,
        uses_tool_building=False,
        # Mixed context
        collaboration_type="cross_team",
        meeting_intensity="moderate",
        requires_sync_communication=True,
        timezone_spread="moderate",
    )

    quadrant = calculate_quadrant(chars, sample_profile)

    assert quadrant == "sparingly"


def test_help_mentoring_quadrant_low_skill_high_energy(sample_profile):
    """Test task with low skill + high energy = help_mentoring quadrant."""
    chars = TaskCharacteristics(
        # Low conflict, high progress = energizing
        conflict_exposure="low",
        alignment_clarity="high",
        authority_ambiguity="low",
        progress_visibility="high",
        autonomy_level="moderate",
        decision_speed="moderate",
        # High learning but energizing growth area = not good at yet but energizing
        learning_required="high",
        uses_systems_thinking=False,
        uses_tool_building=False,
        # Good context
        collaboration_type="team",
        meeting_intensity="low",
        requires_sync_communication=False,
        timezone_spread="narrow",
    )

    # Note: This would match a growth area if we had the matching logic
    quadrant = calculate_quadrant(chars, sample_profile)

    assert quadrant == "help_mentoring"
