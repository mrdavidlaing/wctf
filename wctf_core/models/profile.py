"""Pydantic models for Energy Matrix profile data.

The profile captures your personal energy drains, generators, strengths,
and organizational coherence needs. It's stored in data/profile.yaml and
versioned in git to track self-knowledge evolution.
"""

from datetime import date as Date
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DrainSeverity(str, Enum):
    """Severity levels for energy drains."""
    SEVERE = "severe"
    MODERATE = "moderate"
    MILD = "mild"


class GeneratorStrength(str, Enum):
    """Strength levels for energy generators."""
    CORE_NEED = "core_need"
    STRONG = "strong"
    MODERATE = "moderate"


class SkillLevel(str, Enum):
    """Skill proficiency levels."""
    EXPERT = "expert"
    PROFICIENT = "proficient"
    LEARNING = "learning"


class EnergyDrain(BaseModel):
    """An activity or situation that depletes your energy reserves."""

    severity: DrainSeverity = Field(..., description="How much this drains you")
    trigger: str = Field(..., description="What triggers this drain")
    description: str = Field(..., description="Description of this drain")


class EnergyGenerator(BaseModel):
    """An activity or situation that restores/amplifies your energy."""

    strength: GeneratorStrength = Field(..., description="How much this energizes you")
    description: str = Field(..., description="Description of this generator")


class CoreStrength(BaseModel):
    """An established area of expertise."""

    name: str = Field(..., description="Name of this strength")
    level: SkillLevel = Field(..., description="Your proficiency level")
    description: str = Field(..., description="Description of this strength")


class GrowthArea(BaseModel):
    """An area where you're actively learning."""

    name: str = Field(..., description="Name of this growth area")
    current_level: SkillLevel = Field(..., description="Your current level")
    energizing: bool = Field(..., description="Does learning this energize you?")
    description: str = Field(..., description="Description of this growth area")


class CommunicationPreferences(BaseModel):
    """Communication and decision-making preferences."""

    async_work_capability: str = Field(..., description="Preference for async work")
    timezone_flexibility: str = Field(..., description="Max timezone spread tolerance")
    decision_making_speed_needs: Dict[str, str] = Field(
        default_factory=dict,
        description="Decision speed needs in different contexts"
    )
    meeting_intensity_tolerance: Dict[str, int] = Field(
        default_factory=dict,
        description="Meeting load tolerance"
    )


class OrganizationalCoherenceNeed(BaseModel):
    """A pattern describing organizational coherence requirements."""

    pattern: str = Field(..., description="The organizational pattern")
    requires_one_of: List[str] = Field(
        default_factory=list,
        description="Must have at least one of these"
    )
    incompatible_with: List[str] = Field(
        default_factory=list,
        description="Cannot coexist with these"
    )
    impact_if_violated: str = Field(..., description="Impact when violated")
    description: str = Field(..., description="Description of this need")


class Profile(BaseModel):
    """Complete personal profile for Energy Matrix evaluation.

    This captures your energy drains, generators, strengths, and
    organizational needs. Git tracks version history.
    """

    profile_version: str = Field(..., description="Profile schema version")
    last_updated: Date = Field(..., description="Last update date")

    energy_drains: Dict[str, EnergyDrain] = Field(
        default_factory=dict,
        description="Things that deplete your energy"
    )
    energy_generators: Dict[str, EnergyGenerator] = Field(
        default_factory=dict,
        description="Things that restore/amplify energy"
    )
    core_strengths: List[CoreStrength] = Field(
        default_factory=list,
        description="Established areas of expertise"
    )
    growth_areas: List[GrowthArea] = Field(
        default_factory=list,
        description="Areas where you're actively learning"
    )
    communication_preferences: Optional[CommunicationPreferences] = Field(
        default=None,
        description="Communication and decision-making preferences"
    )
    organizational_coherence_needs: List[OrganizationalCoherenceNeed] = Field(
        default_factory=list,
        description="Organizational coherence requirements"
    )
