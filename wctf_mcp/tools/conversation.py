"""MCP tool for conversation guidance - surfaces relevant questions based on existing data.

This module provides a question bank organized by conversation stages and helps
guide research conversations by selecting appropriate questions based on what
information is already known about a company.

NO LLM CALLS - Pure data processing and question selection logic.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from wctf_mcp.utils.paths import get_facts_path, get_flags_path
from wctf_mcp.utils.yaml_handler import read_yaml


# Question Bank - organized by stage and category
QUESTION_BANK = {
    "opening": [
        # Financial Health - Opening
        {
            "question": "Can you tell me about the company's current financial situation?",
            "category": "financial_health",
            "why_important": "Understanding financial stability indicates company longevity and ability to invest in engineering",
        },
        {
            "question": "How is the company funded? (bootstrapped, VC-backed, public, etc.)",
            "category": "financial_health",
            "why_important": "Funding model affects growth expectations, pressure, and decision-making autonomy",
        },
        # Market Position - Opening
        {
            "question": "What's the company's position in the market? Who are the main competitors?",
            "category": "market_position",
            "why_important": "Market position affects job security and growth opportunities",
        },
        {
            "question": "What problem does the company solve, and who are the customers?",
            "category": "market_position",
            "why_important": "Understanding the product and customers helps assess market fit and sustainability",
        },
        # Organizational Stability - Opening
        {
            "question": "How long has the current leadership team been in place?",
            "category": "organizational_stability",
            "why_important": "Leadership stability indicates organizational maturity and consistent direction",
        },
        {
            "question": "What's the company size and how fast is it growing?",
            "category": "organizational_stability",
            "why_important": "Growth rate affects processes, culture stability, and career opportunities",
        },
        # Technical Culture - Opening
        {
            "question": "Can you describe the engineering culture and tech stack?",
            "category": "technical_culture",
            "why_important": "Engineering culture directly impacts daily work satisfaction and technical growth",
        },
        {
            "question": "How does the engineering team approach technical decision-making?",
            "category": "technical_culture",
            "why_important": "Decision-making autonomy is crucial for senior engineers",
        },
    ],
    "follow_up": [
        # Financial Health - Follow-up
        {
            "question": "What's the company's revenue trajectory over the past 2-3 years?",
            "category": "financial_health",
            "why_important": "Growth trends indicate sustainability and future investment capacity",
        },
        {
            "question": "Is the company profitable, or what's the path to profitability?",
            "category": "financial_health",
            "why_important": "Profitability affects runway and pressure for short-term results",
        },
        {
            "question": "What's the current runway and next funding milestone?",
            "category": "financial_health",
            "why_important": "Runway determines job security and helps predict organizational stress",
        },
        # Market Position - Follow-up
        {
            "question": "What's the company's market share and how has it changed recently?",
            "category": "market_position",
            "why_important": "Market share trends indicate competitive strength and growth potential",
        },
        {
            "question": "Who are the key competitors and how does the company differentiate?",
            "category": "market_position",
            "why_important": "Competitive positioning affects product strategy and technical priorities",
        },
        {
            "question": "What's the customer retention rate and growth rate?",
            "category": "market_position",
            "why_important": "Customer metrics indicate product-market fit and sustainable growth",
        },
        # Organizational Stability - Follow-up
        {
            "question": "What's the employee turnover rate, especially in engineering?",
            "category": "organizational_stability",
            "why_important": "Turnover indicates culture health and organizational satisfaction",
        },
        {
            "question": "Have there been recent layoffs or major reorganizations?",
            "category": "organizational_stability",
            "why_important": "Recent changes signal organizational stress or strategic shifts",
        },
        {
            "question": "How is the engineering team structured? (teams, reporting, autonomy)",
            "category": "organizational_stability",
            "why_important": "Structure affects collaboration, autonomy, and career paths",
        },
        # Technical Culture - Follow-up
        {
            "question": "What development practices does the team use? (CI/CD, code review, testing)",
            "category": "technical_culture",
            "why_important": "Development practices indicate technical maturity and quality focus",
        },
        {
            "question": "How much technical debt exists, and how is it managed?",
            "category": "technical_culture",
            "why_important": "Technical debt affects engineering satisfaction and velocity",
        },
        {
            "question": "What's the process for adopting new technologies or making architectural changes?",
            "category": "technical_culture",
            "why_important": "Innovation processes indicate technical leadership and growth opportunities",
        },
        # Cross-team Decisions - Follow-up
        {
            "question": "How are technical decisions made across teams? Who has final say?",
            "category": "cross_team_decisions",
            "why_important": "Decision-making authority affects technical influence and autonomy",
        },
        {
            "question": "How does product and engineering collaborate on roadmap and priorities?",
            "category": "cross_team_decisions",
            "why_important": "Product-engineering alignment affects work quality and satisfaction",
        },
        # Daily Work - Follow-up
        {
            "question": "What's a typical sprint or work cycle like?",
            "category": "daily_work",
            "why_important": "Work rhythm affects work-life balance and productivity",
        },
        {
            "question": "How much time is spent on meetings vs. focused coding work?",
            "category": "daily_work",
            "why_important": "Meeting load directly impacts engineering productivity and satisfaction",
        },
    ],
    "deep_dive": [
        # Financial Health - Deep Dive
        {
            "question": "What are the unit economics and key financial metrics the company tracks?",
            "category": "financial_health",
            "why_important": "Understanding business metrics helps assess long-term viability",
        },
        {
            "question": "How does the company allocate budget between engineering, sales, and other departments?",
            "category": "financial_health",
            "why_important": "Budget allocation reflects company priorities and engineering investment",
        },
        # Market Position - Deep Dive
        {
            "question": "What's the company's strategy for maintaining competitive advantage?",
            "category": "market_position",
            "why_important": "Competitive strategy affects technical priorities and innovation focus",
        },
        {
            "question": "What are the biggest market risks or threats the company faces?",
            "category": "market_position",
            "why_important": "Understanding risks helps assess job security and strategic challenges",
        },
        # Organizational Stability - Deep Dive
        {
            "question": "What's the company's approach to performance management and career development?",
            "category": "organizational_stability",
            "why_important": "Growth and feedback systems affect long-term career satisfaction",
        },
        {
            "question": "How does the company handle succession planning for key technical roles?",
            "category": "organizational_stability",
            "why_important": "Succession planning indicates organizational maturity and career opportunities",
        },
        {
            "question": "What's the company culture around work-life balance? (on-call, hours, flexibility)",
            "category": "organizational_stability",
            "why_important": "Work-life balance directly affects sustainability and job satisfaction",
        },
        # Technical Culture - Deep Dive
        {
            "question": "How does the company invest in engineering learning and development?",
            "category": "technical_culture",
            "why_important": "Learning opportunities affect long-term skill growth and career advancement",
        },
        {
            "question": "What's the approach to technical excellence vs. shipping quickly?",
            "category": "technical_culture",
            "why_important": "Quality vs. speed tradeoffs affect engineering pride and technical debt",
        },
        {
            "question": "How are technical failures handled? Is there a blameless culture?",
            "category": "technical_culture",
            "why_important": "Failure handling indicates psychological safety and innovation tolerance",
        },
        {
            "question": "What opportunities exist for technical leadership and architectural influence?",
            "category": "technical_culture",
            "why_important": "Leadership opportunities are crucial for senior engineer career growth",
        },
        # Strategic Alignment - Deep Dive
        {
            "question": "What's the 3-5 year technical vision, and how does it align with business goals?",
            "category": "strategic_alignment",
            "why_important": "Long-term vision indicates strategic thinking and future opportunities",
        },
        {
            "question": "How does engineering influence product strategy and business decisions?",
            "category": "strategic_alignment",
            "why_important": "Engineering influence affects technical satisfaction and strategic impact",
        },
        # Daily Work - Deep Dive
        {
            "question": "What's the on-call rotation and incident response process like?",
            "category": "daily_work",
            "why_important": "On-call expectations significantly affect work-life balance and stress",
        },
        {
            "question": "How much autonomy do engineers have in choosing what to work on?",
            "category": "daily_work",
            "why_important": "Autonomy is a key factor in senior engineer satisfaction",
        },
    ],
}


def _analyze_existing_data(
    company_name: str,
    base_path: Optional[Path] = None
) -> Dict[str, Any]:
    """Analyze existing facts and flags to determine what's missing.

    Returns:
        Dictionary with:
        - has_facts: bool
        - has_flags: bool
        - facts_completeness: str (high/medium/low)
        - empty_categories: list of category names
        - missing_information: dict of category -> list of missing items
        - missing_critical_data: list from flags
    """
    analysis = {
        "has_facts": False,
        "has_flags": False,
        "facts_completeness": "low",
        "empty_categories": [],
        "missing_information": {},
        "missing_critical_data": [],
    }

    # Check for facts file
    facts_path = get_facts_path(company_name, base_path=base_path)
    if facts_path.exists():
        try:
            facts_data = read_yaml(facts_path)
            if facts_data:
                analysis["has_facts"] = True

                # Analyze completeness
                summary = facts_data.get("summary", {})
                completeness = summary.get("information_completeness", "low")
                analysis["facts_completeness"] = completeness

                # Find empty categories (no facts found)
                categories = ["financial_health", "market_position",
                             "organizational_stability", "technical_culture"]

                for category in categories:
                    category_data = facts_data.get(category, {})
                    facts_found = category_data.get("facts_found", [])
                    missing_info = category_data.get("missing_information", [])

                    if not facts_found:
                        analysis["empty_categories"].append(category)

                    if missing_info:
                        analysis["missing_information"][category] = missing_info

        except Exception:
            # If we can't read facts, treat as no facts
            pass

    # Check for flags file
    flags_path = get_flags_path(company_name, base_path=base_path)
    if flags_path.exists():
        try:
            flags_data = read_yaml(flags_path)
            if flags_data:
                analysis["has_flags"] = True

                # Extract missing critical data
                missing_data = flags_data.get("missing_critical_data", [])
                analysis["missing_critical_data"] = missing_data

        except Exception:
            # If we can't read flags, treat as no flags
            pass

    return analysis


def _select_questions(
    stage: str,
    analysis: Dict[str, Any],
    max_questions: int = 8
) -> List[Dict[str, str]]:
    """Select relevant questions based on stage and data analysis.

    Pure logic - no LLM calls. Selects questions that target missing information.

    Args:
        stage: Conversation stage (opening/follow_up/deep_dive)
        analysis: Data analysis from _analyze_existing_data
        max_questions: Maximum number of questions to return

    Returns:
        List of question dictionaries
    """
    # Validate stage
    if stage not in QUESTION_BANK:
        stage = "opening"  # Default to opening

    all_questions = QUESTION_BANK[stage]

    # If no data exists, return opening questions (prioritize broad coverage)
    if not analysis["has_facts"] and stage == "opening":
        # Return diverse questions covering all main categories
        selected = []
        categories_covered = set()

        for q in all_questions:
            if q["category"] not in categories_covered:
                selected.append(q)
                categories_covered.add(q["category"])

            if len(selected) >= max_questions:
                break

        # Fill remaining slots if needed
        if len(selected) < max_questions:
            for q in all_questions:
                if q not in selected:
                    selected.append(q)
                    if len(selected) >= max_questions:
                        break

        return selected

    # If we have data, prioritize questions for areas with gaps
    priority_categories = set()

    # Add empty categories (highest priority)
    priority_categories.update(analysis["empty_categories"])

    # Add categories with explicit missing information
    priority_categories.update(analysis["missing_information"].keys())

    # Select questions, prioritizing gap areas
    selected = []
    remaining = []

    for q in all_questions:
        if q["category"] in priority_categories:
            selected.append(q)
        else:
            remaining.append(q)

    # Fill up to max_questions
    selected.extend(remaining)

    return selected[:max_questions]


def _suggest_stage(analysis: Dict[str, Any]) -> str:
    """Suggest appropriate conversation stage based on existing data.

    Args:
        analysis: Data analysis from _analyze_existing_data

    Returns:
        Suggested stage name
    """
    if not analysis["has_facts"]:
        return "opening"

    completeness = analysis["facts_completeness"]

    if completeness == "high":
        return "deep_dive"
    elif completeness == "medium":
        return "follow_up"
    else:
        # Low completeness or significant gaps
        if analysis["empty_categories"]:
            return "follow_up"  # Need to fill basic gaps
        else:
            return "deep_dive"  # Have basics, go deeper


def get_conversation_questions(
    company_name: str,
    stage: str = "opening",
    max_questions: int = 8,
    base_path: Optional[Path] = None
) -> Dict[str, Any]:
    """Get conversation guidance questions based on existing company data.

    This tool performs pure data operations - no LLM calls. It reads existing
    facts/flags and returns appropriate questions from a pre-built question bank.

    Args:
        company_name: Name of the company
        stage: Conversation stage (opening/follow_up/deep_dive)
        max_questions: Maximum number of questions to return (default 8)
        base_path: Optional base path for data directory (for testing)

    Returns:
        Dictionary with:
        - success: bool
        - stage: str (actual stage used)
        - questions: list of question dicts
        - suggested_stage: str (if different from requested)
        - data_summary: dict with analysis of existing data
        - error: str (if error occurred)
    """
    try:
        # Validate and normalize stage
        valid_stages = ["opening", "follow_up", "deep_dive"]
        if stage not in valid_stages:
            return {
                "success": False,
                "error": f"Invalid stage '{stage}'. Must be one of: {', '.join(valid_stages)}",
            }

        # Analyze existing data
        analysis = _analyze_existing_data(company_name, base_path=base_path)

        # Suggest appropriate stage based on data
        suggested_stage = _suggest_stage(analysis)

        # Select questions
        questions = _select_questions(stage, analysis, max_questions)

        result = {
            "success": True,
            "stage": stage,
            "questions": questions,
            "data_summary": {
                "has_facts": analysis["has_facts"],
                "has_flags": analysis["has_flags"],
                "facts_completeness": analysis["facts_completeness"],
                "empty_categories_count": len(analysis["empty_categories"]),
                "missing_information_categories": list(analysis["missing_information"].keys()),
            },
        }

        # Add suggestion if different from requested
        if suggested_stage != stage:
            result["suggestion"] = (
                f"Based on existing data, '{suggested_stage}' stage may be more appropriate. "
                f"Current data completeness: {analysis['facts_completeness']}"
            )
            result["suggested_stage"] = suggested_stage

        return result

    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting conversation questions for '{company_name}': {str(e)}",
        }
