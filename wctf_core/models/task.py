"""Task-related models for Energy Matrix calculations.

These models describe task characteristics and implications for
determining which Energy Matrix quadrant a task falls into.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ConflictLevel(str, Enum):
    """Conflict exposure levels."""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    NONE = "none"


class ClarityLevel(str, Enum):
    """Clarity/ambiguity levels."""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


class DecisionSpeed(str, Enum):
    """Decision-making speed."""
    FAST = "fast"
    MODERATE = "moderate"
    SLOW = "slow"


class LearningRequired(str, Enum):
    """Learning requirement levels."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class CollaborationType(str, Enum):
    """Types of collaboration."""
    SOLO = "solo"
    PAIRED = "paired"
    TEAM = "team"
    CROSS_TEAM = "cross_team"


class MeetingIntensity(str, Enum):
    """Meeting load intensity."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class TimezoneSpread(str, Enum):
    """Timezone spread of collaboration."""
    CO_LOCATED = "co_located"
    NARROW = "narrow"      # 0-6 hours
    MODERATE = "moderate"  # 6-12 hours
    WIDE = "wide"          # 12+ hours


class EnergyMatrixQuadrant(str, Enum):
    """Energy Matrix quadrants."""
    MOARE = "moare"                      # Good at + energizes (Give me MOARE!)
    SPARINGLY = "sparingly"              # Good at + drains
    HELP_MENTORING = "help_mentoring"    # Not good at + energizes
    BURNOUT = "burnout"                  # Not good at + drains


class TaskCharacteristics(BaseModel):
    """Fine-grained characteristics of a task for Energy Matrix calculation.

    These characteristics are matched against your profile to determine
    which Energy Matrix quadrant the task falls into.
    """
    # Conflict & alignment
    conflict_exposure: ConflictLevel = Field(..., description="Exposure to interpersonal conflict")
    alignment_clarity: ClarityLevel = Field(..., description="Clarity of team alignment")
    authority_ambiguity: ClarityLevel = Field(..., description="Ambiguity in ownership/authority")

    # Progress & autonomy
    progress_visibility: ClarityLevel = Field(..., description="Visibility of forward progress")
    autonomy_level: ClarityLevel = Field(..., description="Level of autonomous decision-making")
    decision_speed: DecisionSpeed = Field(..., description="Speed of decision-making")

    # Skill alignment (matched against profile.core_strengths)
    learning_required: LearningRequired = Field(..., description="Amount of new learning required")
    uses_systems_thinking: bool = Field(default=False, description="Uses systems thinking strength")
    uses_tool_building: bool = Field(default=False, description="Uses tool building strength")
    uses_glue_work: bool = Field(default=False, description="Uses glue work strength")
    uses_infrastructure_automation: bool = Field(default=False, description="Uses infra automation strength")
    uses_decision_frameworks: bool = Field(default=False, description="Uses decision frameworks strength")

    # Work context
    collaboration_type: CollaborationType = Field(..., description="Type of collaboration")
    meeting_intensity: MeetingIntensity = Field(..., description="Meeting load intensity")
    requires_sync_communication: bool = Field(..., description="Requires synchronous communication")
    timezone_spread: TimezoneSpread = Field(..., description="Timezone spread of team")


class TaskImplication(BaseModel):
    """A task implication for a flag with Energy Matrix characteristics.

    Describes what you'll actually DO day-to-day because of a flag,
    with detailed characteristics for quadrant calculation.
    """
    task: str = Field(..., description="Description of the task")
    time_estimate_pct: str = Field(..., description="Estimated % of time (e.g., '20-30%')")
    energy_matrix_quadrant: Optional[EnergyMatrixQuadrant] = Field(
        default=None,
        description="Auto-calculated quadrant (mutual/sparingly/burnout/help_mentoring)"
    )
    characteristics: TaskCharacteristics = Field(..., description="Task characteristics for quadrant calculation")
    notes: Optional[str] = Field(default=None, description="Additional notes")
