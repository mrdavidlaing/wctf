"""Integration tests for company management MCP tools."""

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from wctf_mcp.tools.company import (
    get_company_facts,
    get_company_flags,
    list_companies,
)


@pytest.fixture
def test_data_dir(tmp_path: Path) -> Path:
    """Create a temporary test data directory with sample companies."""
    # Copy test fixtures to temp directory
    # The tools expect a data/ subdirectory, so we create that structure
    fixtures_dir = Path(__file__).parent / "fixtures" / "data"
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create company directories
    for company_dir in fixtures_dir.iterdir():
        if company_dir.is_dir():
            dest_dir = data_dir / company_dir.name
            dest_dir.mkdir(parents=True, exist_ok=True)

            # Copy YAML files
            for yaml_file in company_dir.glob("*.yaml"):
                (dest_dir / yaml_file.name).write_text(yaml_file.read_text())

    return tmp_path


class TestListCompanies:
    """Tests for list_companies tool."""

    def test_list_all_companies(self, test_data_dir: Path):
        """Test listing all companies in the data directory."""
        result = list_companies(base_path=test_data_dir)

        assert isinstance(result, dict)
        assert "companies" in result
        assert isinstance(result["companies"], list)

        # Should find our test companies
        companies = result["companies"]
        assert "test-company-1" in companies
        assert "test-company-2" in companies
        assert "empty-company" in companies

        # Should be sorted
        assert companies == sorted(companies)

    def test_list_companies_with_metadata(self, test_data_dir: Path):
        """Test that list_companies includes useful metadata."""
        result = list_companies(base_path=test_data_dir)

        assert "count" in result
        assert result["count"] >= 3  # At least our test companies

        # Check company details if provided
        if "company_details" in result:
            for company in result["company_details"]:
                assert "name" in company
                assert "has_facts" in company
                assert "has_flags" in company

    def test_list_companies_empty_directory(self, tmp_path: Path):
        """Test listing companies when data directory is empty."""
        empty_data_dir = tmp_path / "empty_data"
        empty_data_dir.mkdir()

        result = list_companies(base_path=tmp_path / "empty_data_parent")

        assert isinstance(result, dict)
        assert result.get("companies", []) == []
        assert result.get("count", 0) == 0

    def test_list_companies_nonexistent_directory(self, tmp_path: Path):
        """Test listing companies when data directory doesn't exist."""
        nonexistent = tmp_path / "does_not_exist"

        result = list_companies(base_path=nonexistent)

        assert isinstance(result, dict)
        assert result.get("companies", []) == []


class TestGetCompanyFacts:
    """Tests for get_company_facts tool."""

    def test_get_facts_success(self, test_data_dir: Path):
        """Test successfully retrieving company facts."""
        result = get_company_facts(
            company_name="test-company-1",
            base_path=test_data_dir
        )

        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "facts" in result

        facts = result["facts"]
        assert facts["company"] == "test-company-1"
        assert facts["research_date"] == "2025-01-15"
        assert "financial_health" in facts
        assert "summary" in facts

    def test_get_facts_formatting(self, test_data_dir: Path):
        """Test that facts are properly formatted and readable."""
        result = get_company_facts(
            company_name="test-company-1",
            base_path=test_data_dir
        )

        facts = result["facts"]

        # Check financial health structure
        financial = facts["financial_health"]
        assert "facts_found" in financial
        assert "missing_information" in financial

        # Check that facts have required fields
        for fact in financial["facts_found"]:
            assert "fact" in fact
            assert "source" in fact
            assert "date" in fact
            assert "confidence" in fact

        # Check summary
        summary = facts["summary"]
        assert "total_facts_found" in summary
        assert summary["total_facts_found"] == 5
        assert "information_completeness" in summary

    def test_get_facts_missing_company(self, test_data_dir: Path):
        """Test getting facts for a company that doesn't exist."""
        result = get_company_facts(
            company_name="nonexistent-company",
            base_path=test_data_dir
        )

        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "error" in result
        assert "not found" in result["error"].lower()

        # Should provide helpful guidance
        if "suggestion" in result:
            assert "list_companies" in result["suggestion"].lower()

    def test_get_facts_missing_facts_file(self, test_data_dir: Path):
        """Test getting facts when company exists but facts file doesn't."""
        result = get_company_facts(
            company_name="empty-company",
            base_path=test_data_dir
        )

        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "error" in result
        assert "facts" in result["error"].lower()

    def test_get_facts_malformed_yaml(self, tmp_path: Path):
        """Test handling of malformed YAML files."""
        # Create company with invalid YAML
        company_dir = tmp_path / "data" / "bad-company"
        company_dir.mkdir(parents=True)
        (company_dir / "company.facts.yaml").write_text("invalid: yaml: syntax: error:")

        result = get_company_facts(
            company_name="bad-company",
            base_path=tmp_path
        )

        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "error" in result
        assert "yaml" in result["error"].lower() or "parse" in result["error"].lower()

    def test_get_facts_minimal_data(self, test_data_dir: Path):
        """Test getting facts for company with minimal data."""
        result = get_company_facts(
            company_name="test-company-2",
            base_path=test_data_dir
        )

        assert isinstance(result, dict)
        assert result.get("success") is True

        facts = result["facts"]
        assert facts["company"] == "test-company-2"
        assert facts["summary"]["total_facts_found"] == 1
        assert facts["summary"]["information_completeness"] == "low"


class TestGetCompanyFlags:
    """Tests for get_company_flags tool."""

    def test_get_flags_success(self, test_data_dir: Path):
        """Test successfully retrieving company flags."""
        result = get_company_flags(
            company_name="test-company-1",
            base_path=test_data_dir
        )

        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "flags" in result

        flags = result["flags"]
        assert flags["company"] == "test-company-1"
        # evaluation_date could be a date object or string depending on YAML parsing
        assert "evaluation_date" in flags
        assert "senior_engineer_alignment" in flags
        assert "green_flags" in flags
        assert "red_flags" in flags
        assert "synthesis" in flags

    def test_get_flags_structure(self, test_data_dir: Path):
        """Test that flags have proper structure."""
        result = get_company_flags(
            company_name="test-company-1",
            base_path=test_data_dir
        )

        flags = result["flags"]

        # Check senior engineer alignment
        alignment = flags["senior_engineer_alignment"]
        assert "organizational_maturity" in alignment
        assert "technical_culture" in alignment
        assert alignment["technical_culture"] == "EXCELLENT"

        # Check green flags (double hierarchy: mountain elements -> severity -> flags)
        green = flags["green_flags"]
        assert "mountain_range" in green
        assert "chosen_peak" in green

        # Check that each mountain element has severity categories
        mountain_range = green["mountain_range"]
        assert "critical_matches" in mountain_range
        assert "strong_positives" in mountain_range

        # Each flag should have impact and confidence
        for flag_item in mountain_range["strong_positives"]:
            assert "flag" in flag_item
            assert "impact" in flag_item
            assert "confidence" in flag_item

        # Check synthesis
        synthesis = flags["synthesis"]
        assert "mountain_worth_climbing" in synthesis
        assert synthesis["mountain_worth_climbing"] in ["YES", "NO", "MAYBE"]
        assert "sustainability_confidence" in synthesis

    def test_get_flags_missing_company(self, test_data_dir: Path):
        """Test getting flags for a company that doesn't exist."""
        result = get_company_flags(
            company_name="nonexistent-company",
            base_path=test_data_dir
        )

        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_get_flags_missing_flags_file(self, test_data_dir: Path):
        """Test getting flags when company exists but flags file doesn't."""
        result = get_company_flags(
            company_name="test-company-2",  # Has facts but no flags
            base_path=test_data_dir
        )

        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "error" in result

        # Should be clear that flags are missing, not the company
        assert "flags" in result["error"].lower()

    def test_get_flags_graceful_degradation(self, test_data_dir: Path):
        """Test that missing flags file provides helpful guidance."""
        result = get_company_flags(
            company_name="test-company-2",
            base_path=test_data_dir
        )

        # Should provide guidance on next steps
        if "suggestion" in result:
            suggestion = result["suggestion"]
            # Should mention how to create flags or where to find company info
            assert len(suggestion) > 0


class TestRealDataCompatibility:
    """Tests using real company data to ensure compatibility."""

    def test_list_real_companies(self):
        """Test listing actual companies in data/ directory."""
        # Use default base_path (project root)
        result = list_companies()

        assert isinstance(result, dict)
        assert "companies" in result

        # Should find at least some of our known companies
        companies = result["companies"]
        known_companies = ["1Password", "mechanical-orchard", "anthropic"]

        # At least one should exist
        assert any(company in companies for company in known_companies)

    def test_get_real_company_facts(self):
        """Test getting facts from an actual company."""
        # Try 1Password as we know it exists
        result = get_company_facts(company_name="1Password")

        if result.get("success"):
            facts = result["facts"]
            assert facts["company"] == "1Password"
            assert "financial_health" in facts
            assert "summary" in facts

    def test_get_real_company_flags(self):
        """Test getting flags from an actual company."""
        # Try 1Password as we know it exists
        result = get_company_flags(company_name="1Password")

        if result.get("success"):
            flags = result["flags"]
            assert flags["company"] == "1Password"
            assert "synthesis" in flags


class TestResponseTimes:
    """Tests to ensure response times are acceptable."""

    def test_list_companies_performance(self, test_data_dir: Path):
        """Test that list_companies returns quickly."""
        import time

        start = time.time()
        result = list_companies(base_path=test_data_dir)
        elapsed = time.time() - start

        assert elapsed < 2.0  # Should complete in under 2 seconds
        assert result.get("companies") is not None

    def test_get_facts_performance(self, test_data_dir: Path):
        """Test that get_company_facts returns quickly."""
        import time

        start = time.time()
        result = get_company_facts(
            company_name="test-company-1",
            base_path=test_data_dir
        )
        elapsed = time.time() - start

        assert elapsed < 2.0  # Should complete in under 2 seconds
        assert result.get("success") is True

    def test_get_flags_performance(self, test_data_dir: Path):
        """Test that get_company_flags returns quickly."""
        import time

        start = time.time()
        result = get_company_flags(
            company_name="test-company-1",
            base_path=test_data_dir
        )
        elapsed = time.time() - start

        assert elapsed < 2.0  # Should complete in under 2 seconds
        assert result.get("success") is True


class TestErrorMessages:
    """Tests to ensure error messages are helpful."""

    def test_missing_company_error_message(self, test_data_dir: Path):
        """Test that missing company errors are clear and actionable."""
        result = get_company_facts(
            company_name="does-not-exist",
            base_path=test_data_dir
        )

        assert result.get("success") is False
        error = result.get("error", "")

        # Error should be clear
        assert "does-not-exist" in error or "not found" in error.lower()

        # Should guide to next steps
        suggestion = result.get("suggestion", "")
        if suggestion:
            assert "list" in suggestion.lower() or "available" in suggestion.lower()

    def test_malformed_yaml_error_message(self, tmp_path: Path):
        """Test that YAML parsing errors are helpful."""
        company_dir = tmp_path / "data" / "broken-yaml"
        company_dir.mkdir(parents=True)
        (company_dir / "company.facts.yaml").write_text("{ invalid yaml ]")

        result = get_company_facts(
            company_name="broken-yaml",
            base_path=tmp_path
        )

        assert result.get("success") is False
        error = result.get("error", "")

        # Should mention parsing or YAML
        assert "parse" in error.lower() or "yaml" in error.lower() or "invalid" in error.lower()
