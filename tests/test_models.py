"""Tests for Pydantic models validating YAML schema."""

import pytest
from datetime import date
from pydantic import ValidationError

from wctf_mcp.models import (
    Fact,
    FactsCategory,
    CompanyFacts,
    GreenFlag,
    RedFlag,
    MissingCriticalData,
    CompanyFlags,
    ConfidenceLevel,
    ImpactLevel,
    FlagSeverity,
)


class TestFactModel:
    """Test the Fact model."""

    def test_valid_fact(self):
        """Test creating a valid fact."""
        fact = Fact(
            fact="Test fact",
            source="Test source",
            date=date(2025, 1, 1),
            confidence="explicit_statement",
        )
        assert fact.fact == "Test fact"
        assert fact.source == "Test source"
        assert fact.date == date(2025, 1, 1)
        assert fact.confidence == "explicit_statement"

    def test_fact_with_implied_confidence(self):
        """Test fact with implied confidence level."""
        fact = Fact(
            fact="Test fact",
            source="Test source",
            date=date(2025, 1, 1),
            confidence="implied",
        )
        assert fact.confidence == "implied"

    def test_fact_invalid_confidence(self):
        """Test that invalid confidence raises ValidationError."""
        with pytest.raises(ValidationError):
            Fact(
                fact="Test fact",
                source="Test source",
                date=date(2025, 1, 1),
                confidence="invalid",
            )


class TestFactsCategory:
    """Test the FactsCategory model."""

    def test_valid_category(self):
        """Test creating a valid facts category."""
        category = FactsCategory(
            facts_found=[
                Fact(
                    fact="Test fact",
                    source="Test source",
                    date=date(2025, 1, 1),
                    confidence="explicit_statement",
                )
            ],
            missing_information=["Missing data 1", "Missing data 2"],
        )
        assert len(category.facts_found) == 1
        assert len(category.missing_information) == 2

    def test_empty_category(self):
        """Test category with empty lists."""
        category = FactsCategory(facts_found=[], missing_information=[])
        assert len(category.facts_found) == 0
        assert len(category.missing_information) == 0

    def test_category_optional_missing_info(self):
        """Test that missing_information is optional."""
        category = FactsCategory(
            facts_found=[
                Fact(
                    fact="Test",
                    source="Source",
                    date=date(2025, 1, 1),
                    confidence="explicit_statement",
                )
            ]
        )
        assert category.missing_information == []


class TestCompanyFacts:
    """Test the CompanyFacts model."""

    def test_valid_company_facts(self):
        """Test creating valid company facts."""
        facts = CompanyFacts(
            company="Test Company",
            research_date=date(2025, 9, 27),
            financial_health=FactsCategory(facts_found=[], missing_information=[]),
            market_position=FactsCategory(facts_found=[], missing_information=[]),
            organizational_stability=FactsCategory(facts_found=[], missing_information=[]),
            technical_culture=FactsCategory(facts_found=[], missing_information=[]),
            summary={
                "total_facts_found": 0,
                "information_completeness": "low",
                "most_recent_data_point": "2025-09-27",
                "oldest_data_point": "2025-09-27",
            },
        )
        assert facts.company == "Test Company"
        assert facts.research_date == date(2025, 9, 27)

    def test_company_facts_with_all_fields(self):
        """Test company facts with complete data."""
        facts = CompanyFacts(
            company="Complete Company",
            research_date=date(2025, 9, 27),
            financial_health=FactsCategory(
                facts_found=[
                    Fact(
                        fact="Revenue $100M",
                        source="Annual report",
                        date=date(2025, 1, 1),
                        confidence="explicit_statement",
                    )
                ],
                missing_information=["Burn rate"],
            ),
            market_position=FactsCategory(facts_found=[], missing_information=[]),
            organizational_stability=FactsCategory(facts_found=[], missing_information=[]),
            technical_culture=FactsCategory(facts_found=[], missing_information=[]),
            summary={
                "total_facts_found": 1,
                "information_completeness": "medium",
                "strengths": ["Strong revenue"],
                "concerns": ["High burn rate"],
                "verdict": "VIABLE",
                "recommendation": "Proceed with caution",
            },
        )
        assert len(facts.financial_health.facts_found) == 1
        assert facts.summary["verdict"] == "VIABLE"

    def test_company_facts_missing_required_fields(self):
        """Test that missing required fields raises ValidationError."""
        with pytest.raises(ValidationError):
            CompanyFacts(
                company="Test",
                # Missing research_date and categories
            )


class TestGreenFlag:
    """Test the GreenFlag model."""

    def test_valid_green_flag(self):
        """Test creating a valid green flag."""
        flag = GreenFlag(
            flag="Strong revenue growth",
            impact="Indicates financial stability",
            confidence="Very high - multiple sources",
        )
        assert flag.flag == "Strong revenue growth"
        assert flag.impact == "Indicates financial stability"
        assert flag.confidence == "Very high - multiple sources"


class TestRedFlag:
    """Test the RedFlag model."""

    def test_valid_red_flag(self):
        """Test creating a valid red flag."""
        flag = RedFlag(
            flag="High employee turnover",
            impact="May indicate cultural issues",
            confidence="Medium - Glassdoor reviews",
        )
        assert flag.flag == "High employee turnover"
        assert flag.impact == "May indicate cultural issues"
        assert flag.confidence == "Medium - Glassdoor reviews"


class TestMissingCriticalData:
    """Test the MissingCriticalData model."""

    def test_valid_missing_data(self):
        """Test creating valid missing critical data."""
        missing = MissingCriticalData(
            question="What is the engineering team size?",
            why_important="Determines team dynamics",
            how_to_find="Ask during interview",
        )
        assert missing.question == "What is the engineering team size?"
        assert missing.why_important == "Determines team dynamics"
        assert missing.how_to_find == "Ask during interview"


class TestCompanyFlags:
    """Test the CompanyFlags model."""

    def test_valid_company_flags(self):
        """Test creating valid company flags."""
        flags = CompanyFlags(
            company="Test Company",
            evaluation_date=date(2025, 9, 28),
            evaluator_context="Senior engineer perspective",
            senior_engineer_alignment={
                "organizational_maturity": "GOOD",
                "technical_culture": "EXCELLENT",
                "decision_making": "GOOD",
                "work_sustainability": "EXCELLENT",
                "growth_trajectory": "GOOD",
            },
            green_flags={
                "critical_matches": [],
                "strong_positives": [],
            },
            red_flags={
                "dealbreakers": [],
                "concerning": [],
            },
            missing_critical_data=[],
            synthesis={
                "mountain_worth_climbing": "YES",
                "sustainability_confidence": "HIGH",
                "primary_strengths": ["Strong tech culture"],
                "primary_risks": ["Rapid growth"],
                "confidence_level": "HIGH",
                "next_investigation": "Interview team",
            },
        )
        assert flags.company == "Test Company"
        assert flags.synthesis["mountain_worth_climbing"] == "YES"

    def test_company_flags_with_complete_data(self):
        """Test company flags with all sections populated."""
        flags = CompanyFlags(
            company="Complete Company",
            evaluation_date=date(2025, 9, 28),
            evaluator_context="25yr staff engineer",
            senior_engineer_alignment={
                "organizational_maturity": "EXCELLENT",
                "technical_culture": "GOOD",
                "decision_making": "EXCELLENT",
                "work_sustainability": "GOOD",
                "growth_trajectory": "EXCELLENT",
            },
            green_flags={
                "critical_matches": [
                    GreenFlag(
                        flag="Profitable",
                        impact="Financial stability",
                        confidence="High",
                    )
                ],
                "strong_positives": [
                    GreenFlag(
                        flag="Remote first",
                        impact="Work flexibility",
                        confidence="High",
                    )
                ],
            },
            red_flags={
                "dealbreakers": [],
                "concerning": [
                    RedFlag(
                        flag="Low Glassdoor rating",
                        impact="Cultural concerns",
                        confidence="Medium",
                    )
                ],
            },
            missing_critical_data=[
                MissingCriticalData(
                    question="Team size?",
                    why_important="Understand scale",
                    how_to_find="Ask in interview",
                )
            ],
            synthesis={
                "mountain_worth_climbing": "YES",
                "sustainability_confidence": "HIGH",
                "primary_strengths": ["Strong financials", "Good tech"],
                "primary_risks": ["Culture questions"],
                "confidence_level": "MEDIUM",
                "next_investigation": "Deep dive on culture",
            },
        )
        assert len(flags.green_flags["critical_matches"]) == 1
        assert len(flags.red_flags["concerning"]) == 1
        assert len(flags.missing_critical_data) == 1

    def test_company_flags_missing_required_fields(self):
        """Test that missing required fields raises ValidationError."""
        with pytest.raises(ValidationError):
            CompanyFlags(
                company="Test",
                # Missing evaluation_date and other required fields
            )


class TestEnums:
    """Test enum models."""

    def test_confidence_level(self):
        """Test ConfidenceLevel enum."""
        assert ConfidenceLevel.EXPLICIT_STATEMENT == "explicit_statement"
        assert ConfidenceLevel.IMPLIED == "implied"

    def test_impact_level(self):
        """Test ImpactLevel enum."""
        assert ImpactLevel.EXCELLENT == "EXCELLENT"
        assert ImpactLevel.GOOD == "GOOD"
        assert ImpactLevel.POOR == "POOR"

    def test_flag_severity(self):
        """Test FlagSeverity enum."""
        assert FlagSeverity.YES == "YES"
        assert FlagSeverity.NO == "NO"
        assert FlagSeverity.MAYBE == "MAYBE"
