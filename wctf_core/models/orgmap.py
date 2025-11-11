"""Pydantic models for organizational mapping (orgmap and roles)."""

from pydantic import BaseModel, Field, computed_field, field_validator
from typing import List, Optional, Dict, Literal


class Leadership(BaseModel):
    """VP or Director leadership info."""

    vp_name: Optional[str] = None
    director_name: Optional[str] = None
    linkedin: Optional[str] = None
    tenure: Optional[str] = None
    reports_to: Optional[str] = None


class OrgMetrics(BaseModel):
    """Org size and growth metrics."""

    estimated_headcount: str = Field(description="e.g., '40-50' or '800-1000'")
    growth_trend: Literal["expanding", "stable", "contracting"]
    recent_changes: List[Dict[str, str]] = Field(default_factory=list)

    @field_validator('estimated_headcount')
    @classmethod
    def validate_headcount(cls, v: str) -> str:
        """Ensure format like '40-50' or '800-1000'."""
        if '-' not in v:
            raise ValueError(f"Headcount must be range format like '40-50', got: {v}")
        return v


class CoordinationSignals(BaseModel):
    """Team coordination style indicators."""

    style_indicators: Literal["alpine", "expedition", "established", "orienteering", "trail_crew"]
    evidence: List[str] = Field(description="Observable signals of coordination style")
    realignment_signals: List[str] = Field(default_factory=list, description="Evidence of adaptation ability")


class InsiderConnection(BaseModel):
    """Network contact info."""

    name: str
    relationship: str = Field(description="How you know them")
    role: str
    team: str
    last_contact: str = Field(description="YYYY-MM format")
    willing_to_intro: bool = Field(default=False)
