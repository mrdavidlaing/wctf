"""Pydantic models for WCTF MCP server data structures.

These models validate the schema for company.facts.yaml and company.flags.yaml files.
"""

from datetime import date as Date
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    """Confidence levels for facts."""

    EXPLICIT_STATEMENT = "explicit_statement"
    IMPLIED = "implied"


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
    """A single fact about a company."""

    fact: str = Field(..., description="The factual statement")
    source: str = Field(..., description="Source of the fact")
    date: Date = Field(..., description="Date of the fact")
    confidence: ConfidenceLevel = Field(..., description="Confidence level in this fact")


class FactsCategory(BaseModel):
    """A category of facts with found and missing information."""

    facts_found: List[Fact] = Field(default_factory=list, description="Facts found in this category")
    missing_information: List[str] = Field(default_factory=list, description="Information not found")


class CompanyFacts(BaseModel):
    """Complete facts structure for a company."""

    company: str = Field(..., description="Company name")
    research_date: Date = Field(..., description="Date when research was conducted")
    financial_health: FactsCategory = Field(..., description="Financial health facts")
    market_position: FactsCategory = Field(..., description="Market position facts")
    organizational_stability: FactsCategory = Field(..., description="Organizational stability facts")
    technical_culture: FactsCategory = Field(..., description="Technical culture facts")
    summary: Dict[str, Any] = Field(..., description="Summary of all findings")

    class Config:
        """Pydantic config."""

        json_encoders = {Date: lambda v: v.isoformat()}


class GreenFlag(BaseModel):
    """A positive indicator about a company."""

    flag: str = Field(..., description="The green flag observation")
    impact: str = Field(..., description="Impact of this flag")
    confidence: str = Field(..., description="Confidence level in this flag")


class RedFlag(BaseModel):
    """A negative indicator about a company."""

    flag: str = Field(..., description="The red flag observation")
    impact: str = Field(..., description="Impact of this flag")
    confidence: str = Field(..., description="Confidence level in this flag")


class MissingCriticalData(BaseModel):
    """Information that is critical but missing."""

    question: str = Field(..., description="The question that needs answering")
    why_important: str = Field(..., description="Why this information is important")
    how_to_find: str = Field(..., description="How to find this information")


class CompanyFlags(BaseModel):
    """Complete flags structure for a company evaluation."""

    company: str = Field(..., description="Company name")
    evaluation_date: Date = Field(..., description="Date when evaluation was done")
    evaluator_context: str = Field(..., description="Context of the evaluator")
    senior_engineer_alignment: Dict[str, str] = Field(
        ..., description="Alignment with senior engineer criteria"
    )
    green_flags: Dict[str, List[GreenFlag]] = Field(..., description="Positive indicators")
    red_flags: Dict[str, List[RedFlag]] = Field(..., description="Negative indicators")
    missing_critical_data: List[MissingCriticalData] = Field(
        ..., description="Critical missing information"
    )
    synthesis: Dict[str, Any] = Field(..., description="Overall synthesis and recommendation")

    class Config:
        """Pydantic config."""

        json_encoders = {Date: lambda v: v.isoformat()}
