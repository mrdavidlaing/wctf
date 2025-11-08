"""Energy Matrix quadrant calculation algorithm.

This module implements the core algorithm for calculating which Energy Matrix
quadrant a task falls into based on task characteristics and personal profile.
"""

from typing import Dict, Any

from wctf_core.models import TaskCharacteristics, EnergyMatrixQuadrant
from wctf_core.models.profile import Profile


# Tunable algorithm parameters
STRENGTH_THRESHOLD = 2  # Score needed to be "good at"
ENERGY_THRESHOLD = 0    # Score needed to be "energizing"

DRAIN_WEIGHTS = {
    "severe": -3,
    "moderate": -2,
    "mild": -1,
}

GENERATOR_WEIGHTS = {
    "core_need": 3,
    "strong": 2,
    "moderate": 1,
}

STRENGTH_WEIGHTS = {
    "expert": 2,
    "proficient": 1,
    "learning": 0,
}


def _matches_drain(chars: TaskCharacteristics, drain_name: str) -> bool:
    """Check if task characteristics trigger a specific energy drain."""
    if drain_name == "interpersonal_conflict":
        return chars.conflict_exposure in ["high", "moderate"]
    elif drain_name == "misalignment":
        return chars.alignment_clarity in ["low"]
    elif drain_name == "authority_ambiguity":
        return chars.authority_ambiguity in ["high", "moderate"]
    elif drain_name == "financial_anxiety":
        # Financial anxiety is context-dependent, not task-dependent
        return False

    return False


def _matches_generator(chars: TaskCharacteristics, gen_name: str) -> bool:
    """Check if task characteristics activate an energy generator."""
    if gen_name == "visible_progress":
        return chars.progress_visibility in ["high"]
    elif gen_name == "aligned_collaboration":
        return (
            chars.alignment_clarity == "high"
            and chars.collaboration_type in ["team", "paired"]
        )
    elif gen_name == "tool_building":
        return chars.uses_tool_building
    elif gen_name == "structured_processes":
        return chars.decision_speed == "fast" and chars.autonomy_level == "high"

    return False


def _calculate_strength_score(chars: TaskCharacteristics, profile: Profile) -> int:
    """Calculate strength score (how "good at" you are)."""
    score = 0

    # Check core strengths usage
    for strength in profile.core_strengths:
        # Map strength names to characteristic flags
        uses_strength = False
        if strength.name == "systems_thinking":
            uses_strength = chars.uses_systems_thinking
        elif strength.name == "tool_building":
            uses_strength = chars.uses_tool_building
        elif strength.name == "glue_work":
            uses_strength = chars.uses_glue_work
        elif strength.name == "infrastructure_automation":
            uses_strength = chars.uses_infrastructure_automation
        elif strength.name == "decision_frameworks":
            uses_strength = chars.uses_decision_frameworks

        if uses_strength:
            score += STRENGTH_WEIGHTS.get(strength.level, 0)

    # Penalty for high learning requirement
    learning_penalties = {
        "high": -2,
        "moderate": -1,
        "low": 0,
        "none": 0,
    }
    score += learning_penalties.get(chars.learning_required, 0)

    # Bonus for energizing growth areas
    # (Simplified: if high learning but other signals positive, might be growth area)
    for growth_area in profile.growth_areas:
        if growth_area.energizing and chars.learning_required in ["moderate", "high"]:
            # Give a small bonus if learning is required but context is positive
            if chars.progress_visibility == "high" and chars.conflict_exposure == "low":
                score += 1
                break

    return score


def _calculate_energy_score(chars: TaskCharacteristics, profile: Profile) -> int:
    """Calculate energy score (how energizing vs draining)."""
    score = 0

    # Check energy drains
    for drain_name, drain in profile.energy_drains.items():
        if _matches_drain(chars, drain_name):
            score += DRAIN_WEIGHTS.get(drain.severity, 0)

    # Check energy generators
    for gen_name, generator in profile.energy_generators.items():
        if _matches_generator(chars, gen_name):
            score += GENERATOR_WEIGHTS.get(generator.strength, 0)

    # Check organizational coherence (ambient drain)
    for coherence_need in profile.organizational_coherence_needs:
        # Simplified: check for wide timezone + sync communication mismatch
        if coherence_need.pattern == "uncertain_problem_space":
            if (chars.timezone_spread == "wide" and
                chars.requires_sync_communication and
                coherence_need.impact_if_violated == "severe_drain"):
                score -= 2

    return score


def calculate_quadrant(
    chars: TaskCharacteristics,
    profile: Profile,
) -> str:
    """Calculate Energy Matrix quadrant from task characteristics and profile.

    Args:
        chars: Task characteristics
        profile: Personal profile with drains, generators, and strengths

    Returns:
        Quadrant name: "mutual" | "sparingly" | "burnout" | "help_mentoring"
    """
    strength_score = _calculate_strength_score(chars, profile)
    energy_score = _calculate_energy_score(chars, profile)

    good_at = strength_score >= STRENGTH_THRESHOLD
    energizes = energy_score > ENERGY_THRESHOLD

    # Map to quadrant
    if good_at and energizes:
        return EnergyMatrixQuadrant.MUTUAL.value
    elif good_at and not energizes:
        return EnergyMatrixQuadrant.SPARINGLY.value
    elif not good_at and energizes:
        return EnergyMatrixQuadrant.HELP_MENTORING.value
    else:
        return EnergyMatrixQuadrant.BURNOUT.value
