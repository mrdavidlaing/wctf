"""Tests for flag extraction and manual flag tools.

These tests verify the get_flags_extraction_prompt_op, save_flags_op, and
add_manual_flag tools work correctly.
"""

from datetime import date
from pathlib import Path

import pytest
import yaml

from wctf_core.operations.flags import (
    add_manual_flag,
    get_flags_extraction_prompt_op,
    save_flags_op,
)


# Sample evaluator context for testing
SAMPLE_EVALUATOR_CONTEXT = """
Senior engineer seeking:
- Financial stability and growth trajectory
- Modern technical stack
- Strong remote culture
- Sustainable work-life balance
- Learning opportunities in distributed systems
"""

# Sample flags YAML (what would be extracted after analysis)
SAMPLE_FLAGS_YAML = """
green_flags:
  mountain_range:
    critical_matches:
      - flag: "Profitable with $50M ARR"
        impact: "Financial stability means sustainable engineering projects"
        confidence: "High - directly stated by manager"
    strong_positives: []

  chosen_peak:
    critical_matches:
      - flag: "Using Rust extensively in backend services"
        impact: "Modern technical stack with serious engineering investment"
        confidence: "High - directly stated"
    strong_positives:
      - flag: "Deploy 10x per day"
        impact: "Mature CI/CD indicates low deployment friction"
        confidence: "High - specific metric provided"

  rope_team_confidence:
    critical_matches: []
    strong_positives: []

  daily_climb:
    critical_matches:
      - flag: "Fully remote company since 2020"
        impact: "Established remote culture, not pandemic experiment"
        confidence: "High - directly stated"
    strong_positives: []

  story_worth_telling:
    critical_matches: []
    strong_positives: []

red_flags:
  mountain_range:
    dealbreakers: []
    concerning:
      - flag: "Recent layoffs in Q4 2024 (10% of staff)"
        impact: "Financial instability or management misjudgment on hiring"
        confidence: "High - directly stated"

  chosen_peak:
    dealbreakers: []
    concerning: []

  rope_team_confidence:
    dealbreakers: []
    concerning: []

  daily_climb:
    dealbreakers: []
    concerning:
      - flag: "20+ hours/week in meetings"
        impact: "Severe maker time constraint, limits deep work"
        confidence: "High - manager explicitly mentioned"

  story_worth_telling:
    dealbreakers: []
    concerning: []

missing_critical_data:
  - question: "What's the actual compensation range for senior engineers?"
    why_important: "Critical for financial decision"
    how_to_find: "Ask directly in recruiter call or Glassdoor research"
    mountain_element: "daily_climb"

  - question: "What specific distributed systems challenges?"
    why_important: "Determines learning opportunity quality"
    how_to_find: "Ask for concrete project examples in technical interview"
    mountain_element: "story_worth_telling"
"""


class TestGetFlagsExtractionPrompt:
    """Tests for get_flags_extraction_prompt_op."""

    def test_returns_prompt(self, tmp_path):
        """Test that get_flags_extraction_prompt_op returns a prompt."""
        result = get_flags_extraction_prompt_op(
            company_name="TestCorp",
            evaluator_context=SAMPLE_EVALUATOR_CONTEXT,
            base_path=tmp_path,
        )

        assert result["success"] is True
        assert result["company_name"] == "TestCorp"
        assert "extraction_prompt" in result

        # Verify prompt contains key elements
        prompt = result["extraction_prompt"]
        assert "TestCorp" in prompt
        assert SAMPLE_EVALUATOR_CONTEXT in prompt
        assert "mountain_range" in prompt.lower()
        assert "chosen_peak" in prompt.lower()
        assert "rope_team_confidence" in prompt.lower()
        assert "daily_climb" in prompt.lower()
        assert "story_worth_telling" in prompt.lower()

    def test_validates_company_name(self, tmp_path):
        """Test company name validation."""
        # None should raise TypeError
        with pytest.raises(TypeError):
            get_flags_extraction_prompt_op(
                company_name=None,
                evaluator_context="test",
                base_path=tmp_path
            )

        # Empty string should return error
        result = get_flags_extraction_prompt_op(
            company_name="",
            evaluator_context="test",
            base_path=tmp_path
        )
        assert result["success"] is False
        assert "error" in result

        # Whitespace only should return error
        result = get_flags_extraction_prompt_op(
            company_name="   ",
            evaluator_context="test",
            base_path=tmp_path
        )
        assert result["success"] is False
        assert "error" in result

    def test_validates_evaluator_context(self, tmp_path):
        """Test evaluator context validation."""
        # Empty context
        result = get_flags_extraction_prompt_op(
            company_name="TestCorp",
            evaluator_context="",
            base_path=tmp_path,
        )
        assert result["success"] is False
        assert "error" in result

        # None context
        result = get_flags_extraction_prompt_op(
            company_name="TestCorp",
            evaluator_context=None,
            base_path=tmp_path,
        )
        assert result["success"] is False
        assert "error" in result


class TestSaveFlags:
    """Tests for save_flags_op."""

    def test_saves_flags(self, tmp_path):
        """Test that save_flags_op saves flags to file."""
        result = save_flags_op(
            company_name="TestCorp",
            flags_yaml=SAMPLE_FLAGS_YAML,
            base_path=tmp_path,
        )

        assert result["success"] is True
        assert "flags_file_path" in result
        assert result["company_name"] == "TestCorp"

        # Verify the file was created (use slugified path)
        from wctf_core.utils.paths import get_flags_path
        flags_path = get_flags_path("TestCorp", base_path=tmp_path)
        assert flags_path.exists()

        # Verify the content
        with open(flags_path) as f:
            flags_data = yaml.safe_load(f)

        assert flags_data["company"] == "TestCorp"
        assert "green_flags" in flags_data
        assert "red_flags" in flags_data
        assert "missing_critical_data" in flags_data

        # Verify mountain elements are present
        assert "mountain_range" in flags_data["green_flags"]
        assert "chosen_peak" in flags_data["green_flags"]
        assert "daily_climb" in flags_data["green_flags"]

    def test_merges_with_existing_flags(self, tmp_path):
        """Test that save_flags_op merges with existing flags."""
        # Create existing flags file (use slugified path)
        from wctf_core.utils.paths import ensure_company_dir
        company_dir = ensure_company_dir("TestCorp", base_path=tmp_path)

        existing_flags = {
            "company": "TestCorp",
            "evaluation_date": "2025-10-01",
            "evaluator_context": "Initial evaluation",
            "green_flags": {
                "mountain_range": {
                    "critical_matches": [
                        {
                            "flag": "Existing flag",
                            "impact": "Existing impact",
                            "confidence": "High"
                        }
                    ],
                    "strong_positives": []
                },
                "chosen_peak": {"critical_matches": [], "strong_positives": []},
                "rope_team_confidence": {"critical_matches": [], "strong_positives": []},
                "daily_climb": {"critical_matches": [], "strong_positives": []},
                "story_worth_telling": {"critical_matches": [], "strong_positives": []}
            },
            "red_flags": {
                "mountain_range": {"dealbreakers": [], "concerning": []},
                "chosen_peak": {"dealbreakers": [], "concerning": []},
                "rope_team_confidence": {"dealbreakers": [], "concerning": []},
                "daily_climb": {"dealbreakers": [], "concerning": []},
                "story_worth_telling": {"dealbreakers": [], "concerning": []}
            },
            "missing_critical_data": []
        }

        flags_file = company_dir / "company.flags.yaml"
        with open(flags_file, "w") as f:
            yaml.safe_dump(existing_flags, f)

        # Save new flags
        result = save_flags_op(
            company_name="TestCorp",
            flags_yaml=SAMPLE_FLAGS_YAML,
            base_path=tmp_path,
        )

        assert result["success"] is True

        # Verify both old and new flags are present
        with open(flags_file) as f:
            flags_data = yaml.safe_load(f)

        mountain_range_critical = flags_data["green_flags"]["mountain_range"]["critical_matches"]
        assert len(mountain_range_critical) == 2  # 1 existing + 1 new

        flag_texts = [f["flag"] for f in mountain_range_critical]
        assert "Existing flag" in flag_texts
        assert "Profitable with $50M ARR" in flag_texts

    def test_validates_mountain_elements(self, tmp_path):
        """Test that save_flags_op validates mountain elements."""
        invalid_yaml = """
green_flags:
  invalid_element:
    critical_matches:
      - flag: "Test flag"
        impact: "Test impact"
        confidence: "High"
    strong_positives: []
"""

        result = save_flags_op(
            company_name="TestCorp",
            flags_yaml=invalid_yaml,
            base_path=tmp_path,
        )

        assert result["success"] is False
        assert "error" in result
        assert "invalid_element" in result["error"].lower() or "mountain element" in result["error"].lower()

    def test_validates_flag_structure(self, tmp_path):
        """Test that save_flags_op validates flag structure."""
        # Missing required fields
        invalid_yaml = """
green_flags:
  mountain_range:
    critical_matches:
      - flag: "Test flag"
        # missing impact and confidence
"""

        result = save_flags_op(
            company_name="TestCorp",
            flags_yaml=invalid_yaml,
            base_path=tmp_path,
        )

        assert result["success"] is False
        assert "error" in result

    def test_validates_company_name(self, tmp_path):
        """Test company name validation."""
        # None should raise TypeError
        with pytest.raises(TypeError):
            save_flags_op(
                company_name=None,
                flags_yaml=SAMPLE_FLAGS_YAML,
                base_path=tmp_path
            )

        # Empty string should return error
        result = save_flags_op(
            company_name="",
            flags_yaml=SAMPLE_FLAGS_YAML,
            base_path=tmp_path
        )
        assert result["success"] is False
        assert "error" in result


class TestAddManualFlag:
    """Tests for add_manual_flag tool."""

    def test_add_manual_flag_green_flag(self, tmp_path):
        """Test adding a manual green flag."""
        # Create company directory
        company_dir = tmp_path / "data" / "TestCorp"
        company_dir.mkdir(parents=True)

        result = add_manual_flag(
            company_name="TestCorp",
            flag_type="green",
            mountain_element="mountain_range",
            severity="critical_matches",
            flag="Company is profitable",
            impact="Financial stability for long-term projects",
            confidence="High - from annual report",
            base_path=tmp_path,
        )

        assert result["success"] is True
        assert "flags_file_path" in result

        # Verify file was created
        from wctf_core.utils.paths import get_flags_path
        flags_path = get_flags_path("TestCorp", base_path=tmp_path)
        assert flags_path.exists()

        # Verify content (double hierarchy)
        with open(flags_path) as f:
            flags_data = yaml.safe_load(f)

        assert flags_data["company"] == "TestCorp"
        assert len(flags_data["green_flags"]["mountain_range"]["critical_matches"]) == 1
        assert flags_data["green_flags"]["mountain_range"]["critical_matches"][0]["flag"] == "Company is profitable"

    def test_add_manual_flag_red_flag(self, tmp_path):
        """Test adding a manual red flag."""
        # Create company directory
        company_dir = tmp_path / "data" / "TestCorp"
        company_dir.mkdir(parents=True)

        result = add_manual_flag(
            company_name="TestCorp",
            flag_type="red",
            mountain_element="daily_climb",
            severity="concerning",
            flag="Poor work-life balance reported",
            impact="Unsustainable workload leads to burnout",
            confidence="Medium - from Glassdoor reviews",
            base_path=tmp_path,
        )

        assert result["success"] is True

        # Verify content
        from wctf_core.utils.paths import get_flags_path
        flags_path = get_flags_path("TestCorp", base_path=tmp_path)
        with open(flags_path) as f:
            flags_data = yaml.safe_load(f)

        assert len(flags_data["red_flags"]["daily_climb"]["concerning"]) == 1
        assert flags_data["red_flags"]["daily_climb"]["concerning"][0]["flag"] == "Poor work-life balance reported"

    def test_add_manual_flag_missing_data(self, tmp_path):
        """Test adding missing critical data."""
        # Create company directory
        company_dir = tmp_path / "data" / "TestCorp"
        company_dir.mkdir(parents=True)

        result = add_manual_flag(
            company_name="TestCorp",
            flag_type="missing",
            mountain_element="chosen_peak",
            question="What is the deployment frequency?",
            why_important="Indicates CI/CD maturity and deployment friction",
            how_to_find="Ask during technical interview",
            base_path=tmp_path,
        )

        assert result["success"] is True

        # Verify content
        from wctf_core.utils.paths import get_flags_path
        flags_path = get_flags_path("TestCorp", base_path=tmp_path)
        with open(flags_path) as f:
            flags_data = yaml.safe_load(f)

        assert len(flags_data["missing_critical_data"]) == 1
        missing = flags_data["missing_critical_data"][0]
        assert missing["question"] == "What is the deployment frequency?"
        assert missing["mountain_element"] == "chosen_peak"

    def test_add_manual_flag_validates_flag_type(self, tmp_path):
        """Test that add_manual_flag validates flag type."""
        result = add_manual_flag(
            company_name="TestCorp",
            flag_type="invalid",
            mountain_element="mountain_range",
            flag="Test",
            impact="Test",
            confidence="High",
            base_path=tmp_path,
        )

        assert result["success"] is False
        assert "error" in result

    def test_add_manual_flag_validates_mountain_element(self, tmp_path):
        """Test that add_manual_flag validates mountain element."""
        result = add_manual_flag(
            company_name="TestCorp",
            flag_type="green",
            mountain_element="invalid_element",
            flag="Test",
            impact="Test",
            confidence="High",
            base_path=tmp_path,
        )

        assert result["success"] is False
        assert "error" in result

    def test_add_manual_flag_validates_company_name(self, tmp_path):
        """Test that add_manual_flag validates company name."""
        # None should raise TypeError
        with pytest.raises(TypeError):
            add_manual_flag(
                company_name=None,
                flag_type="green",
                mountain_element="mountain_range",
                flag="Test",
                impact="Test",
                confidence="High",
                base_path=tmp_path,
            )

        # Empty string
        result = add_manual_flag(
            company_name="",
            flag_type="green",
            mountain_element="mountain_range",
            flag="Test",
            impact="Test",
            confidence="High",
            base_path=tmp_path,
        )
        assert result["success"] is False

    def test_add_manual_flag_appends_to_existing(self, tmp_path):
        """Test that add_manual_flag appends to existing flags."""
        # Create company directory and existing flags (use slugified path)
        from wctf_core.utils.paths import ensure_company_dir
        company_dir = ensure_company_dir("TestCorp", base_path=tmp_path)

        existing_flags = {
            "company": "TestCorp",
            "evaluation_date": str(date.today()),
            "evaluator_context": "Manual evaluation",
            "green_flags": {
                "mountain_range": {
                    "critical_matches": [
                        {
                            "flag": "Existing flag",
                            "impact": "Existing impact",
                            "confidence": "High"
                        }
                    ],
                    "strong_positives": []
                }
            },
            "red_flags": {},
            "missing_critical_data": []
        }

        flags_file = company_dir / "company.flags.yaml"
        with open(flags_file, "w") as f:
            yaml.safe_dump(existing_flags, f)

        # Add new flag
        result = add_manual_flag(
            company_name="TestCorp",
            flag_type="green",
            mountain_element="mountain_range",
            severity="critical_matches",
            flag="New flag",
            impact="New impact",
            confidence="High",
            base_path=tmp_path,
        )

        assert result["success"] is True

        # Verify both flags present
        with open(flags_file) as f:
            flags_data = yaml.safe_load(f)

        assert len(flags_data["green_flags"]["mountain_range"]["critical_matches"]) == 2

    def test_add_manual_flag_preserves_yaml_readability(self, tmp_path):
        """Test that flags file remains human-readable."""
        # Create company directory
        company_dir = tmp_path / "data" / "TestCorp"
        company_dir.mkdir(parents=True)

        # Add a flag
        add_manual_flag(
            company_name="TestCorp",
            flag_type="green",
            mountain_element="mountain_range",
            severity="critical_matches",
            flag="Test flag",
            impact="Test impact",
            confidence="High",
            base_path=tmp_path,
        )

        # Read raw file content
        from wctf_core.utils.paths import get_flags_path
        flags_path = get_flags_path("TestCorp", base_path=tmp_path)
        content = flags_path.read_text()

        # Verify it's formatted nicely
        assert "company: TestCorp" in content
        assert "green_flags:" in content
        assert "mountain_range:" in content
        assert "critical_matches:" in content
        assert "- flag:" in content
        # Should not be all on one line
        assert content.count("\n") > 5

    def test_add_manual_flag_requires_appropriate_fields(self, tmp_path):
        """Test that add_manual_flag requires correct fields for each flag type."""
        # Green/red flags need flag, impact, confidence
        result = add_manual_flag(
            company_name="TestCorp",
            flag_type="green",
            mountain_element="mountain_range",
            # Missing flag, impact, confidence
            base_path=tmp_path,
        )
        assert result["success"] is False

        # Missing data needs question, why_important, how_to_find
        result = add_manual_flag(
            company_name="TestCorp",
            flag_type="missing",
            mountain_element="mountain_range",
            # Missing question fields
            flag="Should not work",
            impact="Should not work",
            confidence="Should not work",
            base_path=tmp_path,
        )
        assert result["success"] is False
