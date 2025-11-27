"""Pydantic models for organizational mapping (orgmap and roles)."""

from pydantic import (
    BaseModel,
    Field,
    computed_field,
    field_validator,
    ValidationInfo,
    model_validator,
)
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

    @field_validator("estimated_headcount")
    @classmethod
    def validate_headcount(cls, v: str) -> str:
        """Ensure format like '40-50' or '800-1000'."""
        if "-" not in v:
            raise ValueError(f"Headcount must be range format like '40-50', got: {v}")
        return v


class CoordinationSignals(BaseModel):
    """Team coordination style indicators."""

    style_indicators: Literal[
        "alpine", "expedition", "established", "orienteering", "trail_crew"
    ]
    evidence: List[str] = Field(description="Observable signals of coordination style")
    realignment_signals: List[str] = Field(
        default_factory=list, description="Evidence of adaptation ability"
    )


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
    public_presence: List[str] = Field(
        default_factory=list, description="Talks, blog posts"
    )
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
    tech_focus: Dict[str, List[str]] = Field(
        description="primary and secondary tech areas"
    )
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
    company_slug: Optional[str] = None
    last_updated: str = Field(description="YYYY-MM-DD format")
    mapping_metadata: Dict = Field(description="sources, confidence, notes")
    peaks: List[Peak]

    @model_validator(mode="before")
    @classmethod
    def generate_slug(cls, data):
        """Auto-generate slug if not provided."""
        if (
            isinstance(data, dict)
            and not data.get("company_slug")
            and data.get("company")
        ):
            from wctf_core.utils.paths import slugify_company_name

            data["company_slug"] = slugify_company_name(data["company"])
        return data

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


class WCTFAnalysis(BaseModel):
    """WCTF framework analysis of role."""

    analyzed_date: Optional[str] = Field(None, description="YYYY-MM-DD when analyzed")
    coordination_style: Optional[
        Literal["alpine", "expedition", "established", "orienteering", "trail_crew"]
    ] = None
    terrain_match: Optional[Literal["good_fit", "workable", "mismatched"]] = None
    mountain_clarity: Optional[Literal["clear", "unclear", "conflicting"]] = None
    energy_matrix: Dict = Field(
        default_factory=dict, description="Predicted quadrants and tasks"
    )
    alignment_signals: Dict = Field(default_factory=dict, description="Green/red flags")

    @computed_field
    @property
    def is_complete(self) -> bool:
        """Check if analysis has been done."""
        return all(
            [
                self.analyzed_date,
                self.coordination_style,
                self.terrain_match,
                self.mountain_clarity,
            ]
        )


class Role(BaseModel):
    """Job role posting."""

    role_id: str = Field(
        description="Unique identifier, e.g., 'apple_202511_senior_swe_k8s'"
    )
    title: str
    url: str
    posted_date: str = Field(description="YYYY-MM-DD format")
    location: str

    # Link to orgmap
    rope_team_id: Optional[str] = Field(
        None, description="References company.orgmap.yaml"
    )
    rope_team_name: Optional[str] = None

    # Role details
    seniority: Literal["senior_ic", "staff_plus", "management"]
    description: str
    requirements: List[str] = Field(default_factory=list)
    salary_range: Optional[str] = None

    # WCTF Analysis
    wctf_analysis: Optional[WCTFAnalysis] = None

    @computed_field
    @property
    def is_mapped(self) -> bool:
        """Check if role is linked to orgmap."""
        return self.rope_team_id is not None

    @computed_field
    @property
    def is_analyzed(self) -> bool:
        """Check if WCTF analysis is complete."""
        return self.wctf_analysis.is_complete if self.wctf_analysis else False


class PeakRoles(BaseModel):
    """Roles for one VP org."""

    peak_id: str = Field(description="References company.orgmap.yaml")
    peak_name: str
    roles: List[Role]

    @computed_field
    @property
    def role_count(self) -> int:
        """Count roles in this peak."""
        return len(self.roles)

    @computed_field
    @property
    def analyzed_count(self) -> int:
        """Count roles with complete WCTF analysis."""
        return sum(1 for role in self.roles if role.is_analyzed)


class CompanyRoles(BaseModel):
    """All roles for company."""

    company: str
    company_slug: Optional[str] = None
    last_updated: str = Field(description="YYYY-MM-DD format")
    search_metadata: Dict = Field(description="sources, last_search_date")
    peaks: List[PeakRoles] = Field(default_factory=list)
    unmapped_roles: List[Role] = Field(
        default_factory=list, description="Roles not linked to orgmap"
    )

    @model_validator(mode="before")
    @classmethod
    def generate_slug(cls, data):
        """Auto-generate slug if not provided."""
        if (
            isinstance(data, dict)
            and not data.get("company_slug")
            and data.get("company")
        ):
            from wctf_core.utils.paths import slugify_company_name

            data["company_slug"] = slugify_company_name(data["company"])
        return data

    @computed_field
    @property
    def total_roles(self) -> int:
        """Count all roles."""
        return sum(p.role_count for p in self.peaks) + len(self.unmapped_roles)

    @computed_field
    @property
    def mapped_roles(self) -> int:
        """Count roles linked to orgmap."""
        return sum(p.role_count for p in self.peaks)

    @computed_field
    @property
    def unmapped_count(self) -> int:
        """Count roles not linked to orgmap."""
        return len(self.unmapped_roles)
