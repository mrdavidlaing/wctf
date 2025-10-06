"""Tests for automated company research tool.

This module tests the research tools that generate prompts for the calling
agent and save research results.
"""

import tempfile
from datetime import date
from pathlib import Path

import pytest
import yaml

from wctf_mcp.tools.research import (
    get_research_prompt,
    save_research_results,
)
from wctf_mcp.utils.paths import (
    get_company_dir,
    get_facts_path,
    list_companies,
)
from wctf_mcp.utils.yaml_handler import read_yaml


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_yaml_content():
    """Sample YAML content for testing save_research_results."""
    return """company: "TestCorp"
research_date: "2025-10-02"

financial_health:
  facts_found:
    - fact: "Series A funding of $10 million raised"
      source: "TechCrunch"
      date: "2024-01-15"
      confidence: "explicit_statement"
    - fact: "Revenue of $2M in 2024"
      source: "Company website"
      date: "2024-12-31"
      confidence: "explicit_statement"
  missing_information:
    - "Burn rate not publicly disclosed"

market_position:
  facts_found:
    - fact: "TestCorp provides cloud infrastructure services"
      source: "Company website"
      date: "2025-10-02"
      confidence: "explicit_statement"
  missing_information:
    - "Market share percentage unknown"

organizational_stability:
  facts_found:
    - fact: "Jane Smith is CEO since 2020"
      source: "LinkedIn"
      date: "2025-10-02"
      confidence: "explicit_statement"
  missing_information: []

technical_culture:
  facts_found:
    - fact: "Primary tech stack is Python and Go"
      source: "Engineering blog"
      date: "2024-08-01"
      confidence: "explicit_statement"
  missing_information: []

summary:
  total_facts_found: 5
  information_completeness: "medium"
  most_recent_data_point: "2025-10-02"
  oldest_data_point: "2024-01-15"
"""


class TestGetResearchPrompt:
    """Tests for the get_research_prompt function."""

    def test_successful_prompt_generation(self):
        """Test successful generation of research prompt."""
        result = get_research_prompt(company_name="TestCorp")

        assert result["success"] is True
        assert result["company_name"] == "TestCorp"
        assert "research_prompt" in result
        assert "instructions" in result

    def test_prompt_includes_company_name(self):
        """Test that the prompt includes the company name."""
        company_name = "SpecificCorp"
        result = get_research_prompt(company_name=company_name)

        assert result["success"] is True
        assert company_name in result["research_prompt"]

    def test_prompt_includes_date(self):
        """Test that the prompt includes current date context."""
        result = get_research_prompt(company_name="DateTestCorp")

        assert result["success"] is True
        # Should contain current year at minimum
        current_year = str(date.today().year)
        assert current_year in result["research_prompt"]

    def test_prompt_has_instructions(self):
        """Test that instructions are included."""
        result = get_research_prompt(company_name="InstructCorp")

        assert result["success"] is True
        assert "instructions" in result
        assert "research" in result["instructions"].lower()
        assert "save_research_results_tool" in result["instructions"]

    def test_empty_company_name(self):
        """Test handling of empty company name."""
        result = get_research_prompt(company_name="")

        assert result["success"] is False
        assert "error" in result
        assert "empty" in result["error"].lower()

    def test_none_company_name(self):
        """Test handling of None as company name."""
        with pytest.raises(TypeError):
            get_research_prompt(company_name=None)

    def test_whitespace_only_company_name(self):
        """Test handling of whitespace-only company name."""
        result = get_research_prompt(company_name="   ")

        assert result["success"] is False
        assert "error" in result

    def test_special_characters_in_name(self):
        """Test prompt generation with special characters in name."""
        company_names = ["Test-Corp", "Test.io", "Test_Company"]

        for company_name in company_names:
            result = get_research_prompt(company_name=company_name)
            assert result["success"] is True
            assert company_name in result["research_prompt"]


class TestSaveResearchResults:
    """Tests for the save_research_results function."""

    def test_successful_save(self, temp_data_dir, sample_yaml_content):
        """Test successful saving of research results."""
        result = save_research_results(
            company_name="TestCorp",
            yaml_content=sample_yaml_content,
            base_path=temp_data_dir
        )

        assert result["success"] is True
        assert "TestCorp" in result["message"]
        assert result["facts_generated"] == 5
        assert result["information_completeness"] == "medium"

    def test_creates_directory_structure(self, temp_data_dir, sample_yaml_content):
        """Test that save creates proper directory structure."""
        company_dir = get_company_dir("NewCompany", base_path=temp_data_dir)
        assert not company_dir.exists()

        result = save_research_results(
            company_name="NewCompany",
            yaml_content=sample_yaml_content,
            base_path=temp_data_dir
        )

        assert result["success"] is True
        assert company_dir.exists()
        assert company_dir.is_dir()

    def test_saves_yaml_file(self, temp_data_dir, sample_yaml_content):
        """Test that YAML file is created and contains correct data."""
        result = save_research_results(
            company_name="SaveTestCorp",
            yaml_content=sample_yaml_content,
            base_path=temp_data_dir
        )

        assert result["success"] is True

        facts_path = get_facts_path("SaveTestCorp", base_path=temp_data_dir)
        assert facts_path.exists()

        facts_data = read_yaml(facts_path)
        assert facts_data["company"] == "TestCorp"
        assert facts_data["summary"]["total_facts_found"] == 5

    def test_merges_with_existing_file(self, temp_data_dir, sample_yaml_content):
        """Test that saving merges with existing facts file."""
        # Create initial file with some facts
        initial_yaml = """company: "UpdateCorp"
research_date: "2025-10-01"

financial_health:
  facts_found:
    - fact: "Previous funding fact"
      source: "Previous source"
      date: "2024-01-01"
      confidence: "explicit_statement"
  missing_information:
    - "Previous missing info"

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
  most_recent_data_point: "2024-01-01"
  oldest_data_point: "2024-01-01"
"""
        save_research_results(
            company_name="UpdateCorp",
            yaml_content=initial_yaml,
            base_path=temp_data_dir
        )

        # Save new research (should merge)
        result = save_research_results(
            company_name="UpdateCorp",
            yaml_content=sample_yaml_content,
            base_path=temp_data_dir
        )

        assert result["success"] is True

        # Verify data was merged, not replaced
        facts_path = get_facts_path("UpdateCorp", base_path=temp_data_dir)
        facts_data = read_yaml(facts_path)

        # Should have both old and new facts
        financial_facts = facts_data["financial_health"]["facts_found"]
        assert len(financial_facts) == 3  # 1 old + 2 new

        # Check that old fact is still there
        old_facts = [f for f in financial_facts if f["fact"] == "Previous funding fact"]
        assert len(old_facts) == 1

        # Check that new facts are there
        new_facts = [f for f in financial_facts if f["fact"] == "Series A funding of $10 million raised"]
        assert len(new_facts) == 1

        # Total should be updated
        assert facts_data["summary"]["total_facts_found"] == 6  # 1 old + 5 new

    def test_overwrites_malformed_existing_file(self, temp_data_dir, sample_yaml_content):
        """Test that saving overwrites a malformed existing facts file."""
        # Create malformed file
        company_dir = get_company_dir("MalformedCorp", base_path=temp_data_dir)
        company_dir.mkdir(parents=True)
        facts_path = get_facts_path("MalformedCorp", base_path=temp_data_dir)

        with open(facts_path, "w") as f:
            f.write("This is not valid YAML: {malformed")

        # Save new research (should overwrite the malformed file)
        result = save_research_results(
            company_name="MalformedCorp",
            yaml_content=sample_yaml_content,
            base_path=temp_data_dir
        )

        assert result["success"] is True

        # Verify new data replaced malformed data
        facts_data = read_yaml(facts_path)
        assert "financial_health" in facts_data
        assert facts_data["summary"]["total_facts_found"] == 5

    def test_invalid_yaml_content(self, temp_data_dir):
        """Test handling of invalid YAML content."""
        invalid_yaml = "This is not valid YAML: {incomplete"

        result = save_research_results(
            company_name="InvalidCorp",
            yaml_content=invalid_yaml,
            base_path=temp_data_dir
        )

        assert result["success"] is False
        assert "error" in result
        assert "parse" in result["error"].lower() or "yaml" in result["error"].lower()

    def test_missing_summary_section(self, temp_data_dir):
        """Test handling of YAML without summary section."""
        yaml_without_summary = """company: "NoSummaryCorp"
research_date: "2025-10-02"
financial_health:
  facts_found: []
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
"""

        result = save_research_results(
            company_name="NoSummaryCorp",
            yaml_content=yaml_without_summary,
            base_path=temp_data_dir
        )

        assert result["success"] is False
        assert "error" in result
        assert "summary" in result["error"].lower()

    def test_missing_categories(self, temp_data_dir):
        """Test handling of YAML missing required categories."""
        yaml_missing_cats = """company: "MissingCatsCorp"
research_date: "2025-10-02"
financial_health:
  facts_found: []
  missing_information: []
summary:
  total_facts_found: 0
  information_completeness: "low"
"""

        result = save_research_results(
            company_name="MissingCatsCorp",
            yaml_content=yaml_missing_cats,
            base_path=temp_data_dir
        )

        assert result["success"] is False
        assert "error" in result
        assert "missing required category sections" in result["error"].lower()
        assert "market_position" in result["error"]

    def test_empty_yaml_content(self, temp_data_dir):
        """Test handling of empty YAML content."""
        result = save_research_results(
            company_name="EmptyCorp",
            yaml_content="",
            base_path=temp_data_dir
        )

        assert result["success"] is False
        assert "error" in result

    def test_none_yaml_content(self, temp_data_dir):
        """Test handling of None as YAML content."""
        result = save_research_results(
            company_name="NoneCorp",
            yaml_content=None,
            base_path=temp_data_dir
        )

        assert result["success"] is False
        assert "error" in result

    def test_empty_company_name(self, temp_data_dir, sample_yaml_content):
        """Test handling of empty company name."""
        result = save_research_results(
            company_name="",
            yaml_content=sample_yaml_content,
            base_path=temp_data_dir
        )

        assert result["success"] is False
        assert "error" in result

    def test_none_company_name(self, temp_data_dir, sample_yaml_content):
        """Test handling of None as company name."""
        with pytest.raises(TypeError):
            save_research_results(
                company_name=None,
                yaml_content=sample_yaml_content,
                base_path=temp_data_dir
            )

    def test_return_structure(self, temp_data_dir, sample_yaml_content):
        """Test the structure of the return value."""
        result = save_research_results(
            company_name="StructureTest",
            yaml_content=sample_yaml_content,
            base_path=temp_data_dir
        )

        # Verify all required fields are present
        assert "success" in result
        assert "message" in result
        assert "company_name" in result
        assert "facts_generated" in result
        assert "information_completeness" in result
        assert "facts_file_path" in result

        # Verify field types
        assert isinstance(result["success"], bool)
        assert isinstance(result["message"], str)
        assert isinstance(result["company_name"], str)
        assert isinstance(result["facts_generated"], int)
        assert isinstance(result["information_completeness"], str)
        assert isinstance(result["facts_file_path"], str)

    def test_company_added_to_list(self, temp_data_dir, sample_yaml_content):
        """Test that saved company appears in companies list."""
        result = save_research_results(
            company_name="ListTestCorp",
            yaml_content=sample_yaml_content,
            base_path=temp_data_dir
        )

        assert result["success"] is True

        companies = list_companies(base_path=temp_data_dir)
        assert "ListTestCorp" in companies
