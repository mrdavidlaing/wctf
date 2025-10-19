"""Pydantic models for WCTF Core SDK data structures.

These models validate the schema for company data files:
- company.facts.yaml: Public research facts
- company.insider.yaml: Insider interview facts
- company.flags.yaml: Evaluation flags and decisions

All models use Pydantic v2 for validation and serialization.
"""

from datetime import date as Date
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_serializer, model_validator

from wctf_core.utils.paths import slugify_company_name


class ConfidenceLevel(str, Enum):
    """Confidence levels for facts.

    Indicates how directly the fact was stated or observed:
    - EXPLICIT_STATEMENT: Directly stated in source
    - IMPLIED: Can be reasonably inferred from source
    - FIRSTHAND_ACCOUNT: From direct participant/observer (insider interviews)
    """

    EXPLICIT_STATEMENT = "explicit_statement"
    IMPLIED = "implied"
    FIRSTHAND_ACCOUNT = "firsthand_account"


class FactType(str, Enum):
    """Types of facts from insider interviews."""

    OBJECTIVE = "objective"
    SUBJECTIVE = "subjective"


class ImpactLevel(str, Enum):
    """Impact levels for various assessments."""

    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    POOR = "POOR"


class FlagSeverity(str, Enum):
    """Flag severity levels."""

    YES = "YES"
    NO = "NO"
    MAYBE = "MAYBE"


class Fact(BaseModel):
    """A single fact about a company from public research.

    Facts are concrete, verifiable statements about a company with
    citations and confidence levels.

    Example:
        >>> from datetime import date
        >>> fact = Fact(
        ...     fact="Raised $200M Series C in Q2 2024",
        ...     source="TechCrunch, Company blog",
        ...     date=date(2024, 6, 15),
        ...     confidence=ConfidenceLevel.EXPLICIT_STATEMENT
        ... )
        >>> fact.fact
        'Raised $200M Series C in Q2 2024'
    """

    fact: str = Field(..., description="The factual statement")
    source: str = Field(..., description="Source of the fact")
    date: Date = Field(..., description="Date of the fact")
    confidence: ConfidenceLevel = Field(..., description="Confidence level in this fact")


class FactsCategory(BaseModel):
    """A category of facts with found and missing information."""

    facts_found: List[Fact] = Field(default_factory=list, description="Facts found in this category")
    missing_information: List[str] = Field(default_factory=list, description="Information not found")


class CompanyFacts(BaseModel):
    """Complete facts structure for a company from public research.

    Organizes research findings into four key categories with summary metadata.
    Corresponds to company.facts.yaml file structure.

    Categories:
    - financial_health: Revenue, funding, profitability, runway
    - market_position: Market share, competition, growth trends
    - organizational_stability: Leadership, turnover, structure
    - technical_culture: Engineering practices, tech stack, culture

    Example:
        >>> from datetime import date
        >>> facts = CompanyFacts(
        ...     company="Stripe",
        ...     research_date=date(2025, 1, 15),
        ...     financial_health=FactsCategory(facts_found=[], missing_information=[]),
        ...     market_position=FactsCategory(facts_found=[], missing_information=[]),
        ...     organizational_stability=FactsCategory(facts_found=[], missing_information=[]),
        ...     technical_culture=FactsCategory(facts_found=[], missing_information=[]),
        ...     summary={"total_facts_found": 0, "information_completeness": "low"}
        ... )
        >>> facts.company
        'Stripe'
    """

    company: str = Field(..., description="Company display name")
    company_slug: Optional[str] = Field(None, description="Slugified company name for filesystem (auto-generated if not provided)")
    research_date: Date = Field(..., description="Date when research was conducted")
    financial_health: FactsCategory = Field(..., description="Financial health facts")
    market_position: FactsCategory = Field(..., description="Market position facts")
    organizational_stability: FactsCategory = Field(..., description="Organizational stability facts")
    technical_culture: FactsCategory = Field(..., description="Technical culture facts")
    summary: Dict[str, Any] = Field(..., description="Summary of all findings")

    @model_validator(mode='after')
    def generate_slug_if_missing(self) -> 'CompanyFacts':
        """Auto-generate company_slug from company name if not provided."""
        if self.company_slug is None:
            self.company_slug = slugify_company_name(self.company)
        return self

    @field_serializer("research_date")
    def serialize_research_date(self, value: Date) -> str:
        """Serialize research_date as ISO format string."""
        return value.isoformat()


class InsiderFact(BaseModel):
    """A single fact from an insider interview."""

    fact: str = Field(..., description="The factual statement")
    source: str = Field(..., description="Source with name and role (e.g., 'John Doe (Senior Engineer)')")
    date: Date = Field(..., description="Date of the interview")
    confidence: ConfidenceLevel = Field(..., description="Confidence level (should be firsthand_account)")
    fact_type: FactType = Field(..., description="Type of fact: objective or subjective")
    context: Optional[str] = Field(None, description="Additional context for the fact")


class InsiderFactsCategory(BaseModel):
    """A category of insider facts with found and missing information."""

    facts_found: List[InsiderFact] = Field(default_factory=list, description="Facts found in this category")
    missing_information: List[str] = Field(default_factory=list, description="Information not found")


class InterviewMetadata(BaseModel):
    """Metadata about an interview."""

    name: str = Field(..., description="Interviewee name")
    role: Optional[str] = Field(None, description="Interviewee role")
    interview_date: Date = Field(..., description="Date of interview")

    @field_serializer("interview_date")
    def serialize_interview_date(self, value: Date) -> str:
        """Serialize interview_date as ISO format string."""
        return value.isoformat()


class CompanyInsiderFacts(BaseModel):
    """Complete insider facts structure for a company."""

    company: str = Field(..., description="Company display name")
    company_slug: Optional[str] = Field(None, description="Slugified company name for filesystem (auto-generated if not provided)")
    last_updated: Date = Field(..., description="Date when last updated")
    financial_health: InsiderFactsCategory = Field(..., description="Financial health facts")
    market_position: InsiderFactsCategory = Field(..., description="Market position facts")
    organizational_stability: InsiderFactsCategory = Field(..., description="Organizational stability facts")
    technical_culture: InsiderFactsCategory = Field(..., description="Technical culture facts")
    summary: Dict[str, Any] = Field(..., description="Summary including interview metadata")

    @model_validator(mode='after')
    def generate_slug_if_missing(self) -> 'CompanyInsiderFacts':
        """Auto-generate company_slug from company name if not provided."""
        if self.company_slug is None:
            self.company_slug = slugify_company_name(self.company)
        return self

    @field_serializer("last_updated")
    def serialize_last_updated(self, value: Date) -> str:
        """Serialize last_updated as ISO format string."""
        return value.isoformat()


class Flag(BaseModel):
    """A flag (positive or negative) about a company."""

    flag: str = Field(..., description="The flag observation")
    impact: str = Field(..., description="Impact of this flag")
    confidence: str = Field(..., description="Confidence level in this flag")


class MountainElementGreenFlags(BaseModel):
    """Green flags for a single mountain element, organized by severity."""

    critical_matches: List[Flag] = Field(
        default_factory=list,
        description="Critical positive matches - exactly what you're looking for"
    )
    strong_positives: List[Flag] = Field(
        default_factory=list,
        description="Strong positive signals - generally good indicators"
    )


class MountainElementRedFlags(BaseModel):
    """Red flags for a single mountain element, organized by severity."""

    dealbreakers: List[Flag] = Field(
        default_factory=list,
        description="Dealbreaker concerns - would eliminate this option"
    )
    concerning: List[Flag] = Field(
        default_factory=list,
        description="Concerning signals - worth investigating further"
    )


class MissingCriticalData(BaseModel):
    """Information that is critical but missing."""

    question: str = Field(..., description="The question that needs answering")
    why_important: str = Field(..., description="Why this information is important")
    how_to_find: str = Field(..., description="How to find this information")
    mountain_element: str = Field(..., description="Which mountain element this relates to")


class CompanyFlags(BaseModel):
    """Complete flags structure for a company evaluation.

    Uses double hierarchy: mountain elements (what aspect) -> severity (how important).
    """

    company: str = Field(..., description="Company display name")
    company_slug: Optional[str] = Field(None, description="Slugified company name for filesystem (auto-generated if not provided)")
    evaluation_date: Date = Field(..., description="Date when evaluation was done")
    evaluator_context: str = Field(..., description="Context of the evaluator")
    staff_engineer_alignment: Dict[str, str] = Field(
        ..., description="Alignment with staff engineer criteria"
    )
    green_flags: Dict[str, MountainElementGreenFlags] = Field(
        ...,
        description="Positive indicators organized by mountain element (mountain_range, chosen_peak, rope_team_confidence, daily_climb, story_worth_telling)"
    )
    red_flags: Dict[str, MountainElementRedFlags] = Field(
        ...,
        description="Negative indicators organized by mountain element"
    )
    missing_critical_data: List[MissingCriticalData] = Field(
        ..., description="Critical missing information"
    )
    synthesis: Dict[str, Any] = Field(..., description="Overall synthesis and recommendation")

    @model_validator(mode='after')
    def generate_slug_if_missing(self) -> 'CompanyFlags':
        """Auto-generate company_slug from company name if not provided."""
        if self.company_slug is None:
            self.company_slug = slugify_company_name(self.company)
        return self

    @field_serializer("evaluation_date")
    def serialize_evaluation_date(self, value: Date) -> str:
        """Serialize evaluation_date as ISO format string."""
        return value.isoformat()
