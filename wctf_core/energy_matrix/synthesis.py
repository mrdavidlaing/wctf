"""Energy Matrix synthesis generation.

This module aggregates task implications across all flags to generate
the overall Energy Matrix analysis in the synthesis section.
"""

from typing import Dict, Any, List
import re

from wctf_core.models import CompanyFlags, Flag, TaskImplication
from wctf_core.models.profile import Profile


def _parse_time_estimate(time_estimate_pct: str) -> int:
    """Parse time estimate percentage string.

    Handles formats like:
    - "30%" -> 30
    - "20-30%" -> 25 (midpoint)
    - "15-20%" -> 17.5 -> 17 (rounded)
    """
    # Extract numbers
    numbers = re.findall(r'\d+', time_estimate_pct)
    if not numbers:
        return 0

    # If range, take midpoint
    if len(numbers) == 2:
        return (int(numbers[0]) + int(numbers[1])) // 2

    return int(numbers[0])


def _aggregate_quadrant_distribution(flags: CompanyFlags) -> Dict[str, Dict[str, Any]]:
    """Aggregate task implications by quadrant."""
    distribution = {
        "mutual_green_flags": {"percentage": 0, "tasks_count": 0},
        "sparingly_yellow_flags": {"percentage": 0, "tasks_count": 0},
        "burnout_red_flags": {"percentage": 0, "tasks_count": 0},
        "help_mentoring_yellow_flags": {"percentage": 0, "tasks_count": 0},
    }

    # Collect all task implications
    all_implications: List[TaskImplication] = []

    # Collect from green flags (critical_matches and strong_positives)
    for mountain_element in flags.green_flags.values():
        all_implications.extend(
            impl
            for flag in mountain_element.critical_matches
            for impl in flag.task_implications
        )
        all_implications.extend(
            impl
            for flag in mountain_element.strong_positives
            for impl in flag.task_implications
        )

    # Collect from red flags (dealbreakers and concerning)
    for mountain_element in flags.red_flags.values():
        all_implications.extend(
            impl
            for flag in mountain_element.dealbreakers
            for impl in flag.task_implications
        )
        all_implications.extend(
            impl
            for flag in mountain_element.concerning
            for impl in flag.task_implications
        )

    # Aggregate by quadrant
    for impl in all_implications:
        if impl.energy_matrix_quadrant is None:
            continue

        time_pct = _parse_time_estimate(impl.time_estimate_pct)

        if impl.energy_matrix_quadrant == "mutual":
            distribution["mutual_green_flags"]["percentage"] += time_pct
            distribution["mutual_green_flags"]["tasks_count"] += 1
        elif impl.energy_matrix_quadrant == "sparingly":
            distribution["sparingly_yellow_flags"]["percentage"] += time_pct
            distribution["sparingly_yellow_flags"]["tasks_count"] += 1
        elif impl.energy_matrix_quadrant == "burnout":
            distribution["burnout_red_flags"]["percentage"] += time_pct
            distribution["burnout_red_flags"]["tasks_count"] += 1
        elif impl.energy_matrix_quadrant == "help_mentoring":
            distribution["help_mentoring_yellow_flags"]["percentage"] += time_pct
            distribution["help_mentoring_yellow_flags"]["tasks_count"] += 1

    return distribution


def _check_thresholds(distribution: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
    """Check sustainability thresholds."""
    mutual_pct = distribution["mutual_green_flags"]["percentage"]
    burnout_pct = distribution["burnout_red_flags"]["percentage"]
    sparingly_pct = distribution["sparingly_yellow_flags"]["percentage"]
    help_mentoring_pct = distribution["help_mentoring_yellow_flags"]["percentage"]

    return {
        "meets_green_minimum": mutual_pct >= 60,
        "exceeds_red_maximum": burnout_pct > 20,
        "exceeds_yellow_maximum": (sparingly_pct + help_mentoring_pct) > 30,
    }


def _calculate_sustainability_rating(
    distribution: Dict[str, Dict[str, Any]],
    thresholds: Dict[str, bool],
) -> str:
    """Calculate overall energy sustainability rating."""
    mutual_pct = distribution["mutual_green_flags"]["percentage"]
    burnout_pct = distribution["burnout_red_flags"]["percentage"]

    # LOW: exceeds burnout threshold OR far below mutual threshold
    if thresholds["exceeds_red_maximum"] or mutual_pct < 40:
        return "LOW"

    # MEDIUM: meets minimums but not ideal
    if thresholds["meets_green_minimum"] and not thresholds["exceeds_red_maximum"]:
        if thresholds["exceeds_yellow_maximum"]:
            return "MEDIUM"
        return "HIGH"

    return "MEDIUM"


def generate_energy_synthesis(flags: CompanyFlags, profile: Profile) -> Dict[str, Any]:
    """Generate Energy Matrix analysis for synthesis section.

    Args:
        flags: Company flags with calculated task quadrants
        profile: Personal profile

    Returns:
        Dictionary with energy_matrix_analysis to add to synthesis
    """
    distribution = _aggregate_quadrant_distribution(flags)
    thresholds = _check_thresholds(distribution)
    sustainability = _calculate_sustainability_rating(distribution, thresholds)

    # Generate key insights
    key_insights = []
    total_draining = (
        distribution["sparingly_yellow_flags"]["percentage"]
        + distribution["burnout_red_flags"]["percentage"]
    )
    if total_draining >= 50:
        key_insights.append(
            f"{total_draining}% of work in draining quadrants (sparingly + burnout)"
        )

    if distribution["burnout_red_flags"]["percentage"] > 20:
        key_insights.append(
            f"{distribution['burnout_red_flags']['percentage']}% burnout quadrant work exceeds 20% threshold"
        )

    if distribution["mutual_green_flags"]["percentage"] < 60:
        key_insights.append(
            f"Insufficient mutual quadrant work ({distribution['mutual_green_flags']['percentage']}% vs 60% needed)"
        )

    # Generate decision factors
    decision_factors = []
    if thresholds["exceeds_red_maximum"]:
        decision_factors.append(
            f"REJECT: {distribution['burnout_red_flags']['percentage']}% burnout quadrant exceeds 20% threshold"
        )

    if not thresholds["meets_green_minimum"]:
        decision_factors.append(
            f"RED: Only {distribution['mutual_green_flags']['percentage']}% mutual quadrant (need ≥60%)"
        )

    return {
        "energy_matrix_analysis": {
            "profile_version_used": profile.profile_version,
            "predicted_daily_distribution": distribution,
            "threshold_analysis": thresholds,
            "energy_sustainability": sustainability,
            "key_insights": key_insights,
            "decision_factors": decision_factors,
        }
    }
