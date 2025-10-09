"""Tests for insider interview fact extraction tool.

This module tests the insider interview tools that extract structured facts
from interview transcripts and save them to company.insider.yaml files.
"""

import tempfile
from datetime import date
from pathlib import Path

import pytest
import yaml

from wctf_mcp.tools.insider import (
    get_insider_extraction_prompt,
    save_insider_facts,
    _deduplicate_facts,
)
from wctf_mcp.utils.paths import (
    get_company_dir,
    get_insider_facts_path,
)
from wctf_mcp.utils.yaml_handler import read_yaml


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_transcript():
    """Sample interview transcript for testing."""
    return """
    Me: How's the company doing financially?
    Them: We're doing well. $400M ARR as of September, and we're profitable.
    Me: How big is the team?
    Them: About 600 people. My team specifically is 3 engineers.
    Me: How's the culture?
    Them: Much better than my last company. People are relaxed and supportive.
    """


@pytest.fixture
def sample_extracted_yaml():
    """Sample extracted facts YAML for testing."""
    return """company: "TestCorp"
last_updated: "2025-10-08"

financial_health:
  facts_found:
    - fact: "Company generates $400M ARR as of September 2024"
      source: "John Doe (Senior Engineer)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
    - fact: "Company is profitable"
      source: "John Doe (Senior Engineer)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
  missing_information:
    - "Burn rate and runway"

market_position:
  facts_found:
    - fact: "Competing against Datadog in observability market"
      source: "John Doe (Senior Engineer)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
  missing_information: []

organizational_stability:
  facts_found:
    - fact: "Culture is more relaxed than previous companies"
      source: "John Doe (Senior Engineer)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "subjective"
      context: "Compared to HubSpot"
    - fact: "Teams are small, 3-4 people each"
      source: "John Doe (Senior Engineer)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
  missing_information: []

technical_culture:
  facts_found:
    - fact: "Tech stack is Go backend and TypeScript frontend"
      source: "John Doe (Senior Engineer)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
  missing_information:
    - "Code review SLA"

summary:
  total_facts_found: 6
  information_completeness: "high"
  most_recent_interview: "2025-10-08"
  oldest_interview: "2025-10-08"
  total_interviews: 1
  interviewees:
    - name: "John Doe"
      role: "Senior Engineer"
      interview_date: "2025-10-08"
"""


class TestGetInsiderExtractionPrompt:
    """Tests for get_insider_extraction_prompt function."""

    def test_successful_prompt_generation(self, sample_transcript):
        """Test successful generation of extraction prompt."""
        result = get_insider_extraction_prompt(
            company_name="TestCorp",
            transcript=sample_transcript,
            interview_date="2025-10-08",
            interviewee_name="John Doe",
            interviewee_role="Senior Engineer"
        )

        assert result["success"] is True
        assert result["company_name"] == "TestCorp"
        assert "extraction_prompt" in result
        assert "instructions" in result

    def test_prompt_includes_context(self, sample_transcript):
        """Test that the prompt includes interview context."""
        result = get_insider_extraction_prompt(
            company_name="TestCorp",
            transcript=sample_transcript,
            interview_date="2025-10-08",
            interviewee_name="John Doe",
            interviewee_role="Senior Engineer"
        )

        prompt = result["extraction_prompt"]
        assert "TestCorp" in prompt
        assert "John Doe" in prompt
        assert "Senior Engineer" in prompt
        assert "2025-10-08" in prompt

    def test_prompt_without_role(self, sample_transcript):
        """Test prompt generation when role is not provided."""
        result = get_insider_extraction_prompt(
            company_name="TestCorp",
            transcript=sample_transcript,
            interview_date="2025-10-08",
            interviewee_name="John Doe"
        )

        assert result["success"] is True
        assert "extraction_prompt" in result

    def test_invalid_company_name(self, sample_transcript):
        """Test error handling for invalid company name."""
        result = get_insider_extraction_prompt(
            company_name="",
            transcript=sample_transcript,
            interview_date="2025-10-08",
            interviewee_name="John Doe"
        )

        assert result["success"] is False
        assert "error" in result

    def test_invalid_transcript(self):
        """Test error handling for invalid transcript."""
        result = get_insider_extraction_prompt(
            company_name="TestCorp",
            transcript="",
            interview_date="2025-10-08",
            interviewee_name="John Doe"
        )

        assert result["success"] is False
        assert "error" in result

    def test_invalid_interview_date(self, sample_transcript):
        """Test error handling for invalid interview date."""
        result = get_insider_extraction_prompt(
            company_name="TestCorp",
            transcript=sample_transcript,
            interview_date="",
            interviewee_name="John Doe"
        )

        assert result["success"] is False
        assert "error" in result

    def test_invalid_interviewee_name(self, sample_transcript):
        """Test error handling for invalid interviewee name."""
        result = get_insider_extraction_prompt(
            company_name="TestCorp",
            transcript=sample_transcript,
            interview_date="2025-10-08",
            interviewee_name=""
        )

        assert result["success"] is False
        assert "error" in result


class TestSaveInsiderFacts:
    """Tests for save_insider_facts function."""

    def test_save_new_facts(self, temp_data_dir, sample_extracted_yaml):
        """Test saving extracted facts to new file."""
        result = save_insider_facts(
            company_name="TestCorp",
            interview_date="2025-10-08",
            interviewee_name="John Doe",
            extracted_facts_yaml=sample_extracted_yaml,
            interviewee_role="Senior Engineer",
            base_path=temp_data_dir
        )

        assert result["success"] is True
        assert result["facts_saved"] is True
        assert result["facts_count"] == 6

        # Verify file was created
        facts_path = get_insider_facts_path("TestCorp", base_path=temp_data_dir)
        assert facts_path.exists()

        # Verify content
        saved_data = read_yaml(facts_path)
        assert saved_data["company"] == "TestCorp"
        assert len(saved_data["financial_health"]["facts_found"]) == 2
        assert len(saved_data["organizational_stability"]["facts_found"]) == 2

    def test_merge_with_existing_facts(self, temp_data_dir, sample_extracted_yaml):
        """Test merging new facts with existing insider facts."""
        # First save
        save_insider_facts(
            company_name="TestCorp",
            interview_date="2025-10-08",
            interviewee_name="John Doe",
            extracted_facts_yaml=sample_extracted_yaml,
            interviewee_role="Senior Engineer",
            base_path=temp_data_dir
        )

        # Create second interview with different facts
        second_yaml = """company: "TestCorp"
last_updated: "2025-10-15"

financial_health:
  facts_found:
    - fact: "No layoffs planned for 2025"
      source: "Jane Smith (VP Engineering)"
      date: "2025-10-15"
      confidence: "firsthand_account"
      fact_type: "objective"
  missing_information: []

market_position:
  facts_found: []
  missing_information: []

organizational_stability:
  facts_found: []
  missing_information: []

technical_culture:
  facts_found:
    - fact: "Using GitHub Copilot for all engineers"
      source: "Jane Smith (VP Engineering)"
      date: "2025-10-15"
      confidence: "firsthand_account"
      fact_type: "objective"
  missing_information: []

summary:
  total_facts_found: 2
  information_completeness: "medium"
  most_recent_interview: "2025-10-15"
  oldest_interview: "2025-10-15"
  total_interviews: 1
  interviewees:
    - name: "Jane Smith"
      role: "VP Engineering"
      interview_date: "2025-10-15"
"""

        # Second save
        result = save_insider_facts(
            company_name="TestCorp",
            interview_date="2025-10-15",
            interviewee_name="Jane Smith",
            extracted_facts_yaml=second_yaml,
            interviewee_role="VP Engineering",
            base_path=temp_data_dir
        )

        assert result["success"] is True
        assert result["facts_count"] == 8  # 6 from first + 2 from second

        # Verify merged content
        facts_path = get_insider_facts_path("TestCorp", base_path=temp_data_dir)
        saved_data = read_yaml(facts_path)

        # Check facts were merged
        assert len(saved_data["financial_health"]["facts_found"]) == 3  # 2 + 1
        assert len(saved_data["technical_culture"]["facts_found"]) == 2  # 1 + 1

        # Check interviewees were merged
        assert saved_data["summary"]["total_interviews"] == 2
        assert len(saved_data["summary"]["interviewees"]) == 2
        assert saved_data["summary"]["most_recent_interview"] == "2025-10-15"
        assert saved_data["summary"]["oldest_interview"] == "2025-10-08"

    def test_deduplicates_exact_duplicates(self, temp_data_dir):
        """Test that saving removes exact duplicate facts."""
        yaml_with_dupes = """company: "TestCorp"
last_updated: "2025-10-08"

financial_health:
  facts_found:
    - fact: "$400M ARR"
      source: "John Doe (Engineer)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
    - fact: "$400M ARR"
      source: "John Doe (Engineer)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
  missing_information: []

market_position:
  facts_found: []
  missing_information: []

organizational_stability:
  facts_found: []
  missing_information: []

technical_culture:
  facts_found: []
  missing_information: []

summary:
  total_facts_found: 2
  information_completeness: "low"
  most_recent_interview: "2025-10-08"
  oldest_interview: "2025-10-08"
  total_interviews: 1
  interviewees:
    - name: "John Doe"
      role: "Engineer"
      interview_date: "2025-10-08"
"""

        result = save_insider_facts(
            company_name="TestCorp",
            interview_date="2025-10-08",
            interviewee_name="John Doe",
            extracted_facts_yaml=yaml_with_dupes,
            interviewee_role="Engineer",
            base_path=temp_data_dir
        )

        assert result["success"] is True
        assert result["facts_count"] == 1  # Deduplicated to 1

        # Verify only one fact saved
        facts_path = get_insider_facts_path("TestCorp", base_path=temp_data_dir)
        saved_data = read_yaml(facts_path)
        assert len(saved_data["financial_health"]["facts_found"]) == 1

    def test_invalid_yaml_format(self, temp_data_dir):
        """Test error handling for invalid YAML."""
        invalid_yaml = "not: valid: yaml: content:"

        result = save_insider_facts(
            company_name="TestCorp",
            interview_date="2025-10-08",
            interviewee_name="John Doe",
            extracted_facts_yaml=invalid_yaml,
            base_path=temp_data_dir
        )

        assert result["success"] is False
        assert "error" in result
        assert "Failed to parse YAML" in result["error"]

    def test_missing_required_categories(self, temp_data_dir):
        """Test error handling when required categories are missing."""
        incomplete_yaml = """company: "TestCorp"
last_updated: "2025-10-08"

financial_health:
  facts_found: []
  missing_information: []

market_position:
  facts_found: []
  missing_information: []

summary:
  total_facts_found: 0
"""

        result = save_insider_facts(
            company_name="TestCorp",
            interview_date="2025-10-08",
            interviewee_name="John Doe",
            extracted_facts_yaml=incomplete_yaml,
            base_path=temp_data_dir
        )

        assert result["success"] is False
        assert "missing required category sections" in result["error"]

    def test_missing_fact_type_field(self, temp_data_dir):
        """Test error handling when fact_type field is missing."""
        yaml_without_fact_type = """company: "TestCorp"
last_updated: "2025-10-08"

financial_health:
  facts_found:
    - fact: "$400M ARR"
      source: "John Doe (Engineer)"
      date: "2025-10-08"
      confidence: "firsthand_account"
  missing_information: []

market_position:
  facts_found: []
  missing_information: []

organizational_stability:
  facts_found: []
  missing_information: []

technical_culture:
  facts_found: []
  missing_information: []

summary:
  total_facts_found: 1
  information_completeness: "low"
  most_recent_interview: "2025-10-08"
  oldest_interview: "2025-10-08"
  total_interviews: 1
  interviewees: []
"""

        result = save_insider_facts(
            company_name="TestCorp",
            interview_date="2025-10-08",
            interviewee_name="John Doe",
            extracted_facts_yaml=yaml_without_fact_type,
            base_path=temp_data_dir
        )

        assert result["success"] is False
        assert "missing required 'fact_type' field" in result["error"]

    def test_invalid_fact_type_value(self, temp_data_dir):
        """Test error handling for invalid fact_type value."""
        yaml_with_invalid_type = """company: "TestCorp"
last_updated: "2025-10-08"

financial_health:
  facts_found:
    - fact: "$400M ARR"
      source: "John Doe (Engineer)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "invalid_type"
  missing_information: []

market_position:
  facts_found: []
  missing_information: []

organizational_stability:
  facts_found: []
  missing_information: []

technical_culture:
  facts_found: []
  missing_information: []

summary:
  total_facts_found: 1
  information_completeness: "low"
  most_recent_interview: "2025-10-08"
  oldest_interview: "2025-10-08"
  total_interviews: 1
  interviewees: []
"""

        result = save_insider_facts(
            company_name="TestCorp",
            interview_date="2025-10-08",
            interviewee_name="John Doe",
            extracted_facts_yaml=yaml_with_invalid_type,
            base_path=temp_data_dir
        )

        assert result["success"] is False
        assert "Invalid fact_type" in result["error"]
        assert "Must be 'objective' or 'subjective'" in result["error"]


class TestDeduplicateFacts:
    """Tests for the _deduplicate_facts helper function."""

    def test_removes_exact_duplicates(self):
        """Test that exact duplicates are removed."""
        facts = [
            {"fact": "A", "source": "X", "date": "2025-01-01"},
            {"fact": "B", "source": "Y", "date": "2025-01-02"},
            {"fact": "A", "source": "X", "date": "2025-01-01"},  # Duplicate
        ]

        result = _deduplicate_facts(facts)
        assert len(result) == 2
        assert result[0]["fact"] == "A"
        assert result[1]["fact"] == "B"

    def test_preserves_order(self):
        """Test that order is preserved (first occurrence kept)."""
        facts = [
            {"fact": "First", "source": "X", "date": "2025-01-01"},
            {"fact": "Second", "source": "Y", "date": "2025-01-02"},
            {"fact": "First", "source": "X", "date": "2025-01-01"},
        ]

        result = _deduplicate_facts(facts)
        assert len(result) == 2
        assert result[0]["fact"] == "First"
        assert result[1]["fact"] == "Second"

    def test_different_sources_not_duplicates(self):
        """Test that same fact from different sources is not a duplicate."""
        facts = [
            {"fact": "Same fact", "source": "Source A", "date": "2025-01-01"},
            {"fact": "Same fact", "source": "Source B", "date": "2025-01-01"},
        ]

        result = _deduplicate_facts(facts)
        assert len(result) == 2

    def test_different_dates_not_duplicates(self):
        """Test that same fact with different dates is not a duplicate."""
        facts = [
            {"fact": "Same fact", "source": "Source A", "date": "2025-01-01"},
            {"fact": "Same fact", "source": "Source A", "date": "2025-01-02"},
        ]

        result = _deduplicate_facts(facts)
        assert len(result) == 2

    def test_empty_list(self):
        """Test handling of empty list."""
        result = _deduplicate_facts([])
        assert len(result) == 0

    def test_single_fact(self):
        """Test handling of single fact."""
        facts = [{"fact": "Only one", "source": "X", "date": "2025-01-01"}]
        result = _deduplicate_facts(facts)
        assert len(result) == 1
