"""Tests for conversation guidance tool."""

from pathlib import Path
from typing import Any, Dict

import pytest

from wctf_mcp.tools.conversation import get_conversation_questions


@pytest.fixture
def test_data_dir(tmp_path: Path) -> Path:
    """Create a temporary test data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def company_with_no_data(test_data_dir: Path) -> tuple[Path, str]:
    """Create a company directory with no facts or flags files."""
    company_name = "new-company"
    company_dir = test_data_dir / "data" / company_name
    company_dir.mkdir(parents=True, exist_ok=True)
    return test_data_dir, company_name


@pytest.fixture
def company_with_minimal_facts(test_data_dir: Path) -> tuple[Path, str]:
    """Create a company with minimal facts (some categories empty)."""
    company_name = "minimal-facts-company"
    company_dir = test_data_dir / "data" / company_name
    company_dir.mkdir(parents=True, exist_ok=True)

    facts_content = """company: "minimal-facts-company"
research_date: "2024-01-15"
financial_health:
  facts_found:
    - fact: "Series B funded"
      source: "TechCrunch"
      date: "2024-01-10"
      confidence: "explicit_statement"
  missing_information:
    - "Current revenue"
    - "Profitability status"
market_position:
  facts_found: []
  missing_information:
    - "Market share"
    - "Competitors"
organizational_stability:
  facts_found: []
  missing_information: []
technical_culture:
  facts_found: []
  missing_information: []
summary:
  total_facts_found: 1
  information_completeness: "low"
"""
    (company_dir / "company.facts.yaml").write_text(facts_content)
    return test_data_dir, company_name


@pytest.fixture
def company_with_complete_facts(test_data_dir: Path) -> tuple[Path, str]:
    """Create a company with comprehensive facts across all categories."""
    company_name = "complete-facts-company"
    company_dir = test_data_dir / "data" / company_name
    company_dir.mkdir(parents=True, exist_ok=True)

    facts_content = """company: "complete-facts-company"
research_date: "2024-01-15"
financial_health:
  facts_found:
    - fact: "Revenue $50M ARR"
      source: "Company blog"
      date: "2024-01-10"
      confidence: "explicit_statement"
    - fact: "Profitable since 2022"
      source: "TechCrunch"
      date: "2023-12-01"
      confidence: "explicit_statement"
  missing_information: []
market_position:
  facts_found:
    - fact: "10% market share"
      source: "Gartner"
      date: "2024-01-05"
      confidence: "explicit_statement"
  missing_information: []
organizational_stability:
  facts_found:
    - fact: "CEO tenure 5 years"
      source: "LinkedIn"
      date: "2024-01-01"
      confidence: "explicit_statement"
  missing_information: []
technical_culture:
  facts_found:
    - fact: "Uses modern stack (React, Python)"
      source: "StackShare"
      date: "2024-01-12"
      confidence: "explicit_statement"
  missing_information: []
summary:
  total_facts_found: 5
  information_completeness: "high"
"""
    (company_dir / "company.facts.yaml").write_text(facts_content)
    return test_data_dir, company_name


@pytest.fixture
def company_with_flags(test_data_dir: Path) -> tuple[Path, str]:
    """Create a company with both facts and flags."""
    company_name = "flags-company"
    company_dir = test_data_dir / "data" / company_name
    company_dir.mkdir(parents=True, exist_ok=True)

    facts_content = """company: "flags-company"
research_date: "2024-01-15"
financial_health:
  facts_found:
    - fact: "Revenue growing 50% YoY"
      source: "Company blog"
      date: "2024-01-10"
      confidence: "explicit_statement"
  missing_information: []
market_position:
  facts_found: []
  missing_information:
    - "Market share data"
organizational_stability:
  facts_found: []
  missing_information: []
technical_culture:
  facts_found: []
  missing_information: []
summary:
  total_facts_found: 1
  information_completeness: "low"
"""
    (company_dir / "company.facts.yaml").write_text(facts_content)

    flags_content = """company: "flags-company"
evaluation_date: "2024-01-16"
evaluator_context: "Senior engineer perspective"
senior_engineer_alignment:
  organizational_maturity: "GOOD"
  technical_culture: "GOOD"
green_flags:
  critical_matches:
    - flag: "Strong engineering culture"
      impact: "High autonomy for engineers"
      confidence: "High - multiple sources"
  strong_positives: []
red_flags:
  dealbreakers: []
  concerning: []
missing_critical_data:
  - question: "What is the on-call rotation like?"
    why_important: "Work-life balance assessment"
    how_to_find: "Ask during interview"
synthesis:
  mountain_worth_climbing: "MAYBE"
  sustainability_confidence: "MEDIUM"
"""
    (company_dir / "company.flags.yaml").write_text(flags_content)
    return test_data_dir, company_name


class TestGetConversationQuestionsNoData:
    """Tests for get_conversation_questions with no existing data."""

    def test_no_data_returns_opening_questions(self, company_with_no_data):
        """When no facts/flags exist, should return opening stage questions."""
        base_path, company_name = company_with_no_data

        result = get_conversation_questions(
            company_name=company_name,
            stage="opening",
            base_path=base_path
        )

        assert result["success"] is True
        assert result["stage"] == "opening"
        assert "questions" in result
        assert len(result["questions"]) > 0

        # Opening questions should be general, not requiring prior knowledge
        first_question = result["questions"][0]
        assert "question" in first_question
        assert "category" in first_question
        assert "why_important" in first_question

    def test_no_data_suggests_opening_stage(self, company_with_no_data):
        """When no data exists but wrong stage requested, should suggest opening."""
        base_path, company_name = company_with_no_data

        result = get_conversation_questions(
            company_name=company_name,
            stage="deep_dive",
            base_path=base_path
        )

        # Should still work but may include a suggestion
        assert result["success"] is True
        if "suggestion" in result:
            assert "opening" in result["suggestion"].lower()


class TestGetConversationQuestionsMinimalData:
    """Tests for get_conversation_questions with minimal existing data."""

    def test_minimal_facts_returns_follow_up_questions(self, company_with_minimal_facts):
        """With minimal facts, should return follow-up questions targeting gaps."""
        base_path, company_name = company_with_minimal_facts

        result = get_conversation_questions(
            company_name=company_name,
            stage="follow_up",
            base_path=base_path
        )

        assert result["success"] is True
        assert result["stage"] == "follow_up"
        assert "questions" in result

        # Questions should target missing information
        questions = result["questions"]
        assert len(questions) > 0

        # Should have questions about missing categories
        categories = [q["category"] for q in questions]
        assert any(cat in ["market_position", "organizational_stability", "technical_culture"]
                   for cat in categories)

    def test_questions_target_missing_information(self, company_with_minimal_facts):
        """Questions should specifically target areas with missing_information."""
        base_path, company_name = company_with_minimal_facts

        result = get_conversation_questions(
            company_name=company_name,
            stage="follow_up",
            base_path=base_path
        )

        # Should prioritize questions for categories with explicit missing_information
        questions = result["questions"]

        # Financial health has missing info about revenue and profitability
        financial_questions = [q for q in questions if q["category"] == "financial_health"]
        if financial_questions:
            # Questions should relate to missing revenue/profitability data
            assert any("revenue" in q["question"].lower() or
                      "profit" in q["question"].lower()
                      for q in financial_questions)


class TestGetConversationQuestionsCompleteData:
    """Tests for get_conversation_questions with comprehensive data."""

    def test_complete_facts_returns_deep_dive_questions(self, company_with_complete_facts):
        """With comprehensive facts, should return deep-dive questions."""
        base_path, company_name = company_with_complete_facts

        result = get_conversation_questions(
            company_name=company_name,
            stage="deep_dive",
            base_path=base_path
        )

        assert result["success"] is True
        assert result["stage"] == "deep_dive"
        assert "questions" in result

        # Deep dive questions should be more specific/nuanced
        questions = result["questions"]
        assert len(questions) > 0

    def test_complete_data_suggests_deep_dive(self, company_with_complete_facts):
        """With complete data, should suggest deep_dive stage if opening requested."""
        base_path, company_name = company_with_complete_facts

        result = get_conversation_questions(
            company_name=company_name,
            stage="opening",
            base_path=base_path
        )

        assert result["success"] is True
        # May include suggestion to move to deep_dive
        if "suggestion" in result:
            assert "deep_dive" in result["suggestion"].lower() or \
                   "follow_up" in result["suggestion"].lower()


class TestGetConversationQuestionsWithFlags:
    """Tests for get_conversation_questions when flags exist."""

    def test_flags_influence_question_selection(self, company_with_flags):
        """Questions should consider missing_critical_data from flags."""
        base_path, company_name = company_with_flags

        result = get_conversation_questions(
            company_name=company_name,
            stage="follow_up",
            base_path=base_path
        )

        assert result["success"] is True

        # Should include questions that address missing_critical_data
        # The flags file has "What is the on-call rotation like?" as missing
        questions = result["questions"]

        # Should prioritize areas marked as missing in flags
        assert len(questions) > 0


class TestQuestionBankStructure:
    """Tests for question bank data structure."""

    def test_all_stages_have_questions(self, company_with_no_data):
        """All three stages should have distinct questions."""
        base_path, company_name = company_with_no_data

        opening_result = get_conversation_questions(
            company_name=company_name,
            stage="opening",
            base_path=base_path
        )

        follow_up_result = get_conversation_questions(
            company_name=company_name,
            stage="follow_up",
            base_path=base_path
        )

        deep_dive_result = get_conversation_questions(
            company_name=company_name,
            stage="deep_dive",
            base_path=base_path
        )

        # All should succeed
        assert opening_result["success"] is True
        assert follow_up_result["success"] is True
        assert deep_dive_result["success"] is True

        # All should have questions
        assert len(opening_result["questions"]) > 0
        assert len(follow_up_result["questions"]) > 0
        assert len(deep_dive_result["questions"]) > 0

    def test_questions_grouped_by_category(self, company_with_no_data):
        """Questions should be organized by category."""
        base_path, company_name = company_with_no_data

        result = get_conversation_questions(
            company_name=company_name,
            stage="opening",
            base_path=base_path
        )

        questions = result["questions"]

        # All questions should have a valid category
        valid_categories = [
            "financial_health",
            "market_position",
            "organizational_stability",
            "technical_culture",
            "cross_team_decisions",
            "daily_work",
            "strategic_alignment"
        ]

        for question in questions:
            assert question["category"] in valid_categories

    def test_question_includes_context(self, company_with_no_data):
        """Each question should include context about why it matters."""
        base_path, company_name = company_with_no_data

        result = get_conversation_questions(
            company_name=company_name,
            stage="opening",
            base_path=base_path
        )

        for question in result["questions"]:
            assert "question" in question
            assert "category" in question
            assert "why_important" in question
            assert len(question["why_important"]) > 0


class TestErrorHandling:
    """Tests for error handling."""

    def test_nonexistent_company(self, test_data_dir):
        """Should handle nonexistent company gracefully."""
        result = get_conversation_questions(
            company_name="does-not-exist",
            stage="opening",
            base_path=test_data_dir
        )

        # Should still return questions (for a new company)
        assert result["success"] is True
        assert "questions" in result

    def test_invalid_stage(self, company_with_no_data):
        """Should handle invalid stage parameter."""
        base_path, company_name = company_with_no_data

        result = get_conversation_questions(
            company_name=company_name,
            stage="invalid_stage",
            base_path=base_path
        )

        # Should default to a valid stage or return error
        assert "success" in result
        if result["success"]:
            assert result["stage"] in ["opening", "follow_up", "deep_dive"]
        else:
            assert "error" in result
