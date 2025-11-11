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


class RopeTeam(BaseModel):
    """Director-level team cluster."""

    team_id: str = Field(description="Unique identifier, e.g., 'apple_k8s_platform'")
    team_name: str
    leadership: Leadership
    mission: str
    estimated_size: str = Field(description="e.g., '40-50 engineers'")
    tech_focus: List[str] = Field(description="Primary technologies")
    public_presence: List[str] = Field(default_factory=list, description="Talks, blog posts")
    insider_info: Optional[Dict] = Field(default=None, description="Contact and notes")

    @computed_field
    @property
    def has_insider_connection(self) -> bool:
        """Check if we have insider contact for this team."""
        return self.insider_info is not None


class Peak(BaseModel):
    """VP-level organization."""

    peak_id: str = Field(description="Unique identifier, e.g., 'apple_cloud_services'")
    peak_name: str
    leadership: Leadership
    mission: str
    org_metrics: OrgMetrics
    tech_focus: Dict[str, List[str]] = Field(description="primary and secondary tech areas")
    coordination_signals: CoordinationSignals
    insider_connections: List[InsiderConnection] = Field(default_factory=list)
    rope_teams: List[RopeTeam] = Field(default_factory=list)

    @computed_field
    @property
    def total_insider_connections(self) -> int:
        """Count insider connections across all rope teams."""
        return len(self.insider_connections) + sum(
            1 for team in self.rope_teams if team.has_insider_connection
        )


class CompanyOrgMap(BaseModel):
    """Complete organizational map."""

    company: str
    company_slug: str
    last_updated: str = Field(description="YYYY-MM-DD format")
    mapping_metadata: Dict = Field(description="sources, confidence, notes")
    peaks: List[Peak]

    @field_validator('company_slug', mode='before')
    @classmethod
    def generate_slug(cls, v, info):
        """Auto-generate slug if not provided."""
        if not v and 'company' in info.data:
            from wctf_core.utils.paths import slugify_company_name
            return slugify_company_name(info.data['company'])
        return v

    @computed_field
    @property
    def total_peaks(self) -> int:
        """Count VP orgs."""
        return len(self.peaks)

    @computed_field
    @property
    def total_rope_teams(self) -> int:
        """Count Director teams across all peaks."""
        return sum(len(peak.rope_teams) for peak in self.peaks)
