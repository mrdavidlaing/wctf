"""MCP tool for extracting insider interview facts.

This module provides tools for extracting structured facts from insider
interview transcripts and saving them to company.insider.yaml files.
"""

from datetime import date as Date
from pathlib import Path
from typing import Dict, Optional

import yaml

from wctf_mcp.utils.paths import (
    ensure_company_dir,
    get_insider_facts_path,
)
from wctf_mcp.utils.yaml_handler import read_yaml, write_yaml, YAMLHandlerError


def _load_extraction_prompt() -> str:
    """Load the insider interview extraction prompt template."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "insider_interview_extraction.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Extraction prompt template not found at {prompt_path}")

    with open(prompt_path, "r") as f:
        return f.read()


def _deduplicate_facts(facts_list: list) -> list:
    """Remove exact duplicate facts while preserving order.

    Deduplicates based on (fact, source, date) tuple to catch exact duplicates.

    Args:
        facts_list: List of fact dictionaries

    Returns:
        List of unique facts, preserving order (keeps first occurrence)
    """
    unique_facts = []
    seen = set()

    for fact in facts_list:
        # Create key from fact text, source, and date
        fact_key = (
            fact.get("fact", ""),
            fact.get("source", ""),
            str(fact.get("date", ""))
        )

        if fact_key not in seen:
            seen.add(fact_key)
            unique_facts.append(fact)

    return unique_facts


def get_insider_extraction_prompt(
    company_name: str,
    interview_date: str,
    interviewee_name: str,
    interviewee_role: Optional[str] = None,
) -> Dict[str, any]:
    """Generate an extraction prompt for analyzing an insider interview transcript.

    Returns a formatted prompt that guides the LLM to extract structured facts
    from the interview transcript (already in conversation context), classifying
    them as objective or subjective.

    Args:
        company_name: Name of the company
        interview_date: Date of interview (YYYY-MM-DD format)
        interviewee_name: Name of the person interviewed
        interviewee_role: Optional role/title of the interviewee

    Returns:
        Dictionary with:
        - success: bool - Whether prompt was generated successfully
        - company_name: str - Name of company
        - extraction_prompt: str - The formatted extraction prompt
        - instructions: str - Instructions for next step

        On error:
        - success: False
        - error: str - Error message
        - company_name: str (if available)
    """
    # Validate company name
    if company_name is None:
        raise TypeError("Company name cannot be None")

    if not isinstance(company_name, str) or not company_name.strip():
        return {
            "success": False,
            "error": "Invalid company name. Company name must be a non-empty string.",
        }

    company_name = company_name.strip()

    # Validate interview_date
    if not interview_date or not isinstance(interview_date, str):
        return {
            "success": False,
            "error": "Invalid interview_date. Must be a non-empty string in YYYY-MM-DD format.",
            "company_name": company_name,
        }

    # Validate interviewee_name
    if not interviewee_name or not isinstance(interviewee_name, str):
        return {
            "success": False,
            "error": "Invalid interviewee_name. Must be a non-empty string.",
            "company_name": company_name,
        }

    try:
        prompt_template = _load_extraction_prompt()

        prompt = prompt_template.format(
            company_name=company_name,
            interviewee_name=interviewee_name,
            interviewee_role=interviewee_role or "Unknown",
            interview_date=interview_date,
        )

        instructions = (
            f"After analyzing the transcript and extracting facts, call "
            f"save_insider_facts_tool with the extracted YAML to save it to "
            f"data/{company_name}/company.insider.yaml"
        )

        return {
            "success": True,
            "company_name": company_name,
            "extraction_prompt": prompt,
            "instructions": instructions,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate extraction prompt: {str(e)}",
            "company_name": company_name,
        }


def save_insider_facts(
    company_name: str,
    interview_date: str,
    interviewee_name: str,
    extracted_facts_yaml: str,
    interviewee_role: Optional[str] = None,
    base_path: Optional[Path] = None,
) -> Dict[str, any]:
    """Save extracted insider interview facts to company.insider.yaml.

    Takes YAML content with extracted facts and saves them to the appropriate
    company directory. Merges with existing insider facts if the file already exists.

    Args:
        company_name: Name of the company
        interview_date: Date of interview (YYYY-MM-DD format)
        interviewee_name: Name of the person interviewed
        extracted_facts_yaml: YAML content with extracted facts (from LLM analysis)
        interviewee_role: Optional role/title of the interviewee
        base_path: Optional base path for data directory (for testing)

    Returns:
        Dictionary with:
        - success: bool - Whether save completed successfully
        - company_name: str
        - facts_saved: bool
        - facts_file_path: str
        - facts_count: int
        - message: str

        On error:
        - success: False
        - error: str
        - company_name: str
    """
    # Validate company name
    if company_name is None:
        raise TypeError("Company name cannot be None")

    if not isinstance(company_name, str) or not company_name.strip():
        return {
            "success": False,
            "error": "Invalid company name. Company name must be a non-empty string.",
        }

    company_name = company_name.strip()

    # Validate interview_date
    if not interview_date or not isinstance(interview_date, str):
        return {
            "success": False,
            "error": "Invalid interview_date. Must be a non-empty string in YYYY-MM-DD format.",
            "company_name": company_name,
        }

    # Validate interviewee_name
    if not interviewee_name or not isinstance(interviewee_name, str):
        return {
            "success": False,
            "error": "Invalid interviewee_name. Must be a non-empty string.",
            "company_name": company_name,
        }

    # Validate YAML content
    if not extracted_facts_yaml or not isinstance(extracted_facts_yaml, str):
        return {
            "success": False,
            "error": "Invalid YAML content. Must be a non-empty string.",
            "company_name": company_name,
        }

    try:
        # Parse YAML content
        try:
            facts_data = yaml.safe_load(extracted_facts_yaml)
        except yaml.YAMLError as e:
            preview = extracted_facts_yaml[:200] + "..." if len(extracted_facts_yaml) > 200 else extracted_facts_yaml
            return {
                "success": False,
                "error": (
                    f"Failed to parse YAML content: {str(e)}\n\n"
                    f"Received content (first 200 chars):\n{preview}\n\n"
                    f"Make sure the content is valid YAML format."
                ),
                "company_name": company_name,
            }

        # Validate basic structure
        if not isinstance(facts_data, dict):
            return {
                "success": False,
                "error": (
                    "YAML content is not a valid dictionary. "
                    "Expected a YAML object with company, last_updated, category sections, and summary."
                ),
                "company_name": company_name,
            }

        # Check for required categories
        required_categories = ['financial_health', 'market_position', 'organizational_stability', 'technical_culture']
        missing_categories = [cat for cat in required_categories if cat not in facts_data]

        if missing_categories:
            return {
                "success": False,
                "error": (
                    f"YAML content missing required category sections: {', '.join(missing_categories)}. "
                    f"All four categories are required: financial_health, market_position, "
                    f"organizational_stability, technical_culture. "
                    f"Found sections: {', '.join(facts_data.keys())}"
                ),
                "company_name": company_name,
            }

        # Validate each category has facts_found
        for category in required_categories:
            cat_data = facts_data[category]
            if not isinstance(cat_data, dict):
                return {
                    "success": False,
                    "error": (
                        f"Category '{category}' must be a dictionary with 'facts_found' and 'missing_information' fields. "
                        f"Got: {type(cat_data).__name__}"
                    ),
                    "company_name": company_name,
                }

            if 'facts_found' not in cat_data:
                return {
                    "success": False,
                    "error": (
                        f"Category '{category}' missing 'facts_found' array. "
                        f"Each category must have a 'facts_found' array containing extracted facts. "
                        f"Found keys: {', '.join(cat_data.keys())}"
                    ),
                    "company_name": company_name,
                }

            # Validate fact_type field in each fact
            for fact in cat_data.get('facts_found', []):
                if 'fact_type' not in fact:
                    return {
                        "success": False,
                        "error": (
                            f"Fact in '{category}' missing required 'fact_type' field. "
                            f"Each fact must have fact_type: 'objective' or 'subjective'. "
                            f"Fact: {fact.get('fact', 'unknown')[:50]}"
                        ),
                        "company_name": company_name,
                    }

                if fact['fact_type'] not in ['objective', 'subjective']:
                    return {
                        "success": False,
                        "error": (
                            f"Invalid fact_type '{fact['fact_type']}' in '{category}'. "
                            f"Must be 'objective' or 'subjective'. "
                            f"Fact: {fact.get('fact', 'unknown')[:50]}"
                        ),
                        "company_name": company_name,
                    }

        if "summary" not in facts_data:
            return {
                "success": False,
                "error": (
                    "YAML content missing required 'summary' section. "
                    "Summary must include: total_facts_found, information_completeness, "
                    "most_recent_interview, oldest_interview, total_interviews, interviewees"
                ),
                "company_name": company_name,
            }

        # Deduplicate incoming facts
        for category in required_categories:
            if category in facts_data and 'facts_found' in facts_data[category]:
                facts_data[category]['facts_found'] = _deduplicate_facts(
                    facts_data[category]['facts_found']
                )

        # Update summary after deduplication
        if 'summary' in facts_data:
            facts_data['summary']['total_facts_found'] = sum(
                len(facts_data.get(cat, {}).get('facts_found', []))
                for cat in required_categories
            )

        # Create company directory and get facts path
        try:
            company_dir = ensure_company_dir(company_name, base_path=base_path)
            facts_path = get_insider_facts_path(company_name, base_path=base_path)

            # Check if insider facts file exists and merge if it does
            if facts_path.exists():
                try:
                    existing_data = read_yaml(facts_path)

                    # Merge facts_found arrays for each category with deduplication
                    for category in required_categories:
                        if category in existing_data and category in facts_data:
                            # Merge facts_found arrays
                            if 'facts_found' in existing_data[category] and 'facts_found' in facts_data[category]:
                                combined = (
                                    existing_data[category]['facts_found'] +
                                    facts_data[category]['facts_found']
                                )
                                facts_data[category]['facts_found'] = _deduplicate_facts(combined)

                            # Merge missing_information arrays
                            if 'missing_information' in existing_data[category] and 'missing_information' in facts_data[category]:
                                facts_data[category]['missing_information'] = list(set(
                                    existing_data[category]['missing_information'] +
                                    facts_data[category]['missing_information']
                                ))

                    # Merge summary metadata
                    if 'summary' in existing_data and 'summary' in facts_data:
                        # Add new interviewee to list
                        existing_interviewees = existing_data['summary'].get('interviewees', [])
                        new_interviewees = facts_data['summary'].get('interviewees', [])

                        # Deduplicate interviewees by name
                        all_interviewees = existing_interviewees + new_interviewees
                        seen_names = set()
                        unique_interviewees = []
                        for interviewee in all_interviewees:
                            if interviewee['name'] not in seen_names:
                                seen_names.add(interviewee['name'])
                                unique_interviewees.append(interviewee)

                        facts_data['summary']['interviewees'] = unique_interviewees
                        facts_data['summary']['total_interviews'] = len(unique_interviewees)

                        # Update date ranges
                        all_dates = [i['interview_date'] for i in unique_interviewees]
                        facts_data['summary']['most_recent_interview'] = max(all_dates)
                        facts_data['summary']['oldest_interview'] = min(all_dates)

                    # Update summary with new totals
                    total_facts = sum(
                        len(facts_data.get(cat, {}).get('facts_found', []))
                        for cat in required_categories
                    )
                    facts_data['summary']['total_facts_found'] = total_facts

                except YAMLHandlerError:
                    # If existing file is malformed, overwrite it
                    pass

            # Write the merged facts file
            write_yaml(facts_path, facts_data)

            facts_count = facts_data.get('summary', {}).get('total_facts_found', 0)

            return {
                "success": True,
                "company_name": company_name,
                "facts_saved": True,
                "facts_file_path": str(facts_path),
                "facts_count": facts_count,
                "message": f"Successfully saved {facts_count} insider facts for {company_name}",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save insider facts: {str(e)}",
                "company_name": company_name,
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error processing insider facts: {str(e)}",
            "company_name": company_name,
        }
