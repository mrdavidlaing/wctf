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
