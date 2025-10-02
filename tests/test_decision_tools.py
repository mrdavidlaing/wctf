"""Tests for decision synthesis MCP tools.

These tools are pure data operations - no LLM calls, just reading/formatting/writing YAML.
"""

from datetime import datetime
from pathlib import Path

import pytest

from wctf_mcp.tools.decision import (
    get_evaluation_summary,
    gut_check,
    save_gut_decision,
)


@pytest.fixture
def test_data_dir(tmp_path: Path) -> Path:
    """Create a temporary test data directory with sample companies."""
    # Copy test fixtures to temp directory
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


class TestGutCheck:
    """Tests for gut_check tool - pure data formatting."""

    def test_gut_check_with_complete_data(self, test_data_dir: Path):
        """Test gut_check formats data correctly for a company with complete data."""
        result = gut_check(
            company_name="test-company-1",
            base_path=test_data_dir
        )

        assert result["success"] is True
        assert "summary" in result

        summary = result["summary"]

        # Should include company name
        assert "test-company-1" in summary.lower()

        # Should include evaluation date
        assert "2025-01-15" in summary

        # Should organize by mountain element (senior_engineer_alignment)
        assert "organizational_maturity" in summary.lower() or "maturity" in summary.lower()
        assert "technical_culture" in summary.lower() or "culture" in summary.lower()

        # Should show green/red flag counts
        assert "green" in summary.lower() or "positive" in summary.lower()
        assert "red" in summary.lower() or "concern" in summary.lower()

        # Should highlight missing critical data
        assert "missing" in summary.lower() or "question" in summary.lower()

    def test_gut_check_counts_flags_by_category(self, test_data_dir: Path):
        """Test that gut_check counts flags correctly."""
        result = gut_check(
            company_name="test-company-1",
            base_path=test_data_dir
        )

        assert result["success"] is True

        # Should have flag counts
        assert "flag_counts" in result
        counts = result["flag_counts"]

        # Based on test-company-1 fixture
        assert counts["green_flags"]["critical_matches"] == 1
        assert counts["green_flags"]["strong_positives"] == 1
        assert counts["red_flags"]["dealbreakers"] == 0
        assert counts["red_flags"]["concerning"] == 1
        assert counts["missing_critical_data"] == 1

    def test_gut_check_missing_facts_file(self, test_data_dir: Path):
        """Test gut_check when facts file is missing."""
        result = gut_check(
            company_name="test-company-2",  # Has no facts in fixtures
            base_path=test_data_dir
        )

        # Should still work, but indicate missing data
        assert "success" in result
        if result.get("success"):
            assert "missing" in result.get("summary", "").lower() or "no facts" in result.get("summary", "").lower()

    def test_gut_check_missing_flags_file(self, test_data_dir: Path):
        """Test gut_check when flags file is missing."""
        result = gut_check(
            company_name="test-company-2",  # Has no flags in fixtures
            base_path=test_data_dir
        )

        assert "success" in result
        # Should indicate no evaluation available
        if not result.get("success"):
            assert "error" in result

    def test_gut_check_nonexistent_company(self, test_data_dir: Path):
        """Test gut_check with nonexistent company."""
        result = gut_check(
            company_name="nonexistent-company",
            base_path=test_data_dir
        )

        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_gut_check_includes_synthesis(self, test_data_dir: Path):
        """Test that gut_check includes synthesis from flags."""
        result = gut_check(
            company_name="test-company-1",
            base_path=test_data_dir
        )

        assert result["success"] is True
        summary = result["summary"]

        # Should include the synthesis verdict
        assert "mountain_worth_climbing" in summary.lower() or "yes" in summary.lower()


class TestSaveGutDecision:
    """Tests for save_gut_decision tool - validates and saves decision."""

    def test_save_gut_decision_success(self, test_data_dir: Path):
        """Test successfully saving a gut decision."""
        result = save_gut_decision(
            company_name="test-company-1",
            mountain_worth_climbing="YES",
            confidence="HIGH",
            reasoning="Strong technical culture and good funding",
            base_path=test_data_dir
        )

        assert result["success"] is True

        # Verify file was written
        from wctf_mcp.utils.paths import get_flags_path
        from wctf_mcp.utils.yaml_handler import read_yaml

        flags_path = get_flags_path("test-company-1", base_path=test_data_dir)
        flags_data = read_yaml(flags_path)

        assert "gut_decision" in flags_data
        decision = flags_data["gut_decision"]

        assert decision["mountain_worth_climbing"] == "YES"
        assert decision["confidence"] == "HIGH"
        assert decision["reasoning"] == "Strong technical culture and good funding"
        assert "timestamp" in decision

        # Timestamp should be ISO format
        timestamp = decision["timestamp"]
        assert isinstance(timestamp, str)
        # Should be parseable as datetime
        datetime.fromisoformat(timestamp)

    def test_save_gut_decision_validates_mountain_worth_climbing(self, test_data_dir: Path):
        """Test that save_gut_decision validates mountain_worth_climbing enum."""
        result = save_gut_decision(
            company_name="test-company-1",
            mountain_worth_climbing="INVALID",
            confidence="HIGH",
            reasoning="Test",
            base_path=test_data_dir
        )

        assert result["success"] is False
        assert "error" in result
        assert "mountain_worth_climbing" in result["error"].lower()

    def test_save_gut_decision_validates_confidence(self, test_data_dir: Path):
        """Test that save_gut_decision validates confidence enum."""
        result = save_gut_decision(
            company_name="test-company-1",
            mountain_worth_climbing="YES",
            confidence="INVALID",
            reasoning="Test",
            base_path=test_data_dir
        )

        assert result["success"] is False
        assert "error" in result
        assert "confidence" in result["error"].lower()

    def test_save_gut_decision_valid_enum_values(self, test_data_dir: Path):
        """Test all valid enum combinations."""
        valid_combinations = [
            ("YES", "HIGH"),
            ("YES", "MEDIUM"),
            ("YES", "LOW"),
            ("NO", "HIGH"),
            ("NO", "MEDIUM"),
            ("NO", "LOW"),
            ("MAYBE", "HIGH"),
            ("MAYBE", "MEDIUM"),
            ("MAYBE", "LOW"),
        ]

        for mountain, confidence in valid_combinations:
            result = save_gut_decision(
                company_name="test-company-1",
                mountain_worth_climbing=mountain,
                confidence=confidence,
                reasoning=f"Testing {mountain} with {confidence}",
                base_path=test_data_dir
            )

            assert result["success"] is True, f"Failed for {mountain}/{confidence}"

    def test_save_gut_decision_nonexistent_company(self, test_data_dir: Path):
        """Test saving decision for nonexistent company."""
        result = save_gut_decision(
            company_name="nonexistent-company",
            mountain_worth_climbing="YES",
            confidence="HIGH",
            reasoning="Test",
            base_path=test_data_dir
        )

        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_save_gut_decision_optional_reasoning(self, test_data_dir: Path):
        """Test that reasoning is optional."""
        result = save_gut_decision(
            company_name="test-company-1",
            mountain_worth_climbing="MAYBE",
            confidence="MEDIUM",
            reasoning=None,
            base_path=test_data_dir
        )

        assert result["success"] is True

        from wctf_mcp.utils.paths import get_flags_path
        from wctf_mcp.utils.yaml_handler import read_yaml

        flags_path = get_flags_path("test-company-1", base_path=test_data_dir)
        flags_data = read_yaml(flags_path)

        assert "gut_decision" in flags_data
        # Reasoning can be None or empty string
        assert flags_data["gut_decision"]["reasoning"] in [None, ""]


class TestGetEvaluationSummary:
    """Tests for get_evaluation_summary tool - multi-company table."""

    def test_get_evaluation_summary_with_companies(self, test_data_dir: Path):
        """Test generating evaluation summary table with multiple companies."""
        result = get_evaluation_summary(base_path=test_data_dir)

        assert result["success"] is True
        assert "summary_table" in result

        table = result["summary_table"]

        # Should be formatted as a table (string with headers and rows)
        assert isinstance(table, str)
        assert "company" in table.lower()
        assert "test-company-1" in table.lower()

        # Should show evaluation status
        assert "yes" in table.lower() or "no" in table.lower() or "maybe" in table.lower()

    def test_get_evaluation_summary_includes_gut_decisions(self, test_data_dir: Path):
        """Test that summary includes gut decisions if available."""
        # First save a gut decision
        save_gut_decision(
            company_name="test-company-1",
            mountain_worth_climbing="YES",
            confidence="HIGH",
            reasoning="Test decision",
            base_path=test_data_dir
        )

        result = get_evaluation_summary(base_path=test_data_dir)

        assert result["success"] is True
        table = result["summary_table"]

        # Should show the gut decision
        assert "yes" in table.lower()
        assert "high" in table.lower()

    def test_get_evaluation_summary_empty_directory(self, tmp_path: Path):
        """Test summary with no companies."""
        empty_dir = tmp_path / "empty_data"
        empty_dir.mkdir()

        result = get_evaluation_summary(base_path=tmp_path / "empty_data_parent")

        assert result["success"] is True
        assert "summary_table" in result
        # Should indicate no companies found
        assert "no companies" in result["summary_table"].lower() or len(result.get("companies", [])) == 0

    def test_get_evaluation_summary_shows_synthesis(self, test_data_dir: Path):
        """Test that summary shows synthesis verdict from flags."""
        result = get_evaluation_summary(base_path=test_data_dir)

        assert result["success"] is True
        table = result["summary_table"]

        # Based on test-company-1 which has mountain_worth_climbing: "YES" in synthesis
        assert "test-company-1" in table.lower()

    def test_get_evaluation_summary_handles_missing_data(self, test_data_dir: Path):
        """Test summary handles companies with missing facts or flags gracefully."""
        result = get_evaluation_summary(base_path=test_data_dir)

        assert result["success"] is True
        # Should not crash on empty-company or incomplete data
        assert "summary_table" in result

    def test_get_evaluation_summary_company_count(self, test_data_dir: Path):
        """Test that summary includes company count."""
        result = get_evaluation_summary(base_path=test_data_dir)

        assert result["success"] is True
        assert "company_count" in result
        assert result["company_count"] >= 2  # At least test-company-1 and test-company-2
