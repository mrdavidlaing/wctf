"""MCP tool for automated company research.

This module provides tools for generating research prompts and saving
research results. The calling agent (e.g., Claude Desktop) executes the
research using its own web search capabilities.
"""

from datetime import date
from pathlib import Path
from typing import Dict, Optional

import yaml

from wctf_mcp.utils.paths import (
    ensure_company_dir,
    get_facts_path,
)
from wctf_mcp.utils.yaml_handler import read_yaml, write_yaml, YAMLHandlerError


def _load_research_prompt() -> str:
    """Load the Layer 1 research prompt template from the prompts directory."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "layer1_research.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Research prompt template not found at {prompt_path}")

    with open(prompt_path, "r") as f:
        return f.read()


def get_research_prompt(company_name: str) -> Dict[str, str]:
    """Get the research prompt for a company.

    Returns a structured research prompt that the calling agent can execute
    using its own web search capabilities.

    Args:
        company_name: Name of the company to research

    Returns:
        Dictionary with:
        - success: bool - Whether prompt was generated successfully
        - company_name: str - Name of company to research
        - research_prompt: str - The formatted research prompt
        - instructions: str - Instructions for the calling agent
        OR (on error):
        - success: False
        - error: str - Error message
    """
    # Validate company name - raise TypeError for None
    if company_name is None:
        raise TypeError("Company name cannot be None")

    if not isinstance(company_name, str):
        return {
            "success": False,
            "error": "Invalid company name. Company name must be a non-empty string.",
        }

    if not company_name.strip():
        return {
            "success": False,
            "error": "Invalid company name. Company name cannot be empty or whitespace.",
        }

    company_name = company_name.strip()

    try:
        # Load and customize the research prompt
        prompt_template = _load_research_prompt()
        research_date = date.today().isoformat()

        prompt = prompt_template.format(
            company_name=company_name,
            research_date=research_date
        )

        instructions = (
            f"STOP: Before executing this research, ask the user to enable Research mode "
            f"in Claude Desktop (the Research toggle/button in the UI). "
            f"Wait for them to confirm 'ready', then proceed with the research prompt below. "
            f"\n\n"
            f"After completing research:\n"
            f"1. Check if company already has facts: call get_company_facts_tool('{company_name}')\n"
            f"2. If existing facts found, semantically compare to avoid duplicates\n"
            f"3. Merge duplicate facts (combine sources, use latest date)\n"
            f"4. Save only new or enhanced facts with save_research_results_tool"
        )

        return {
            "success": True,
            "company_name": company_name,
            "research_prompt": prompt,
            "instructions": instructions,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate research prompt: {str(e)}",
        }


def save_research_results(
    company_name: str,
    yaml_content: str,
    base_path: Optional[Path] = None,
) -> Dict[str, str]:
    """Save research results to company.facts.yaml.

    Takes YAML content (as a string) from the calling agent and saves it
    to the appropriate company directory.

    Args:
        company_name: Name of the company
        yaml_content: YAML content as a string (from research results)
        base_path: Optional base path for data directory (for testing)

    Returns:
        Dictionary with:
        - success: bool - Whether save completed successfully
        - message: str - Human-readable result message
        - company_name: str - Name of company researched
        - facts_generated: int - Number of facts found
        - information_completeness: str - "high", "medium", or "low"
        - facts_file_path: str - Path to generated facts file
        OR (on error):
        - success: False
        - error: str - Error message
        - company_name: str - Name of company (if available)
    """
    # Validate company name
    if company_name is None:
        raise TypeError("Company name cannot be None")

    if not isinstance(company_name, str):
        return {
            "success": False,
            "error": "Invalid company name. Company name must be a non-empty string.",
        }

    if not company_name.strip():
        return {
            "success": False,
            "error": "Invalid company name. Company name cannot be empty or whitespace.",
        }

    company_name = company_name.strip()

    # Validate YAML content
    if not yaml_content or not isinstance(yaml_content, str):
        return {
            "success": False,
            "error": "Invalid YAML content. Must be a non-empty string.",
            "company_name": company_name,
        }

    try:
        # Parse YAML content
        try:
            facts_data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            # Show first 200 chars of what was received to help debug
            preview = yaml_content[:200] + "..." if len(yaml_content) > 200 else yaml_content
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
                    "Expected a YAML object with company, research_date, category sections, and summary."
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

        # Validate each category has facts_found (or accept 'facts' as alias)
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

            # Accept both 'facts_found' and 'facts' as valid keys
            if 'facts_found' not in cat_data and 'facts' not in cat_data:
                return {
                    "success": False,
                    "error": (
                        f"Category '{category}' missing 'facts_found' array. "
                        f"Each category must have a 'facts_found' array (or 'facts') containing research findings. "
                        f"Found keys: {', '.join(cat_data.keys())}"
                    ),
                    "company_name": company_name,
                }

            # Normalize 'facts' to 'facts_found' if needed
            if 'facts' in cat_data and 'facts_found' not in cat_data:
                cat_data['facts_found'] = cat_data.pop('facts')

        if "summary" not in facts_data:
            return {
                "success": False,
                "error": (
                    "YAML content missing required 'summary' section. "
                    "Summary must include: total_facts_found, information_completeness, "
                    "most_recent_data_point, oldest_data_point"
                ),
                "company_name": company_name,
            }

        # Extract summary information
        summary = facts_data.get("summary", {})
        facts_count = summary.get("total_facts_found", 0)
        completeness = summary.get("information_completeness", "unknown")

        # Create company directory and save facts file
        try:
            company_dir = ensure_company_dir(company_name, base_path=base_path)
            facts_path = get_facts_path(company_name, base_path=base_path)

            # Check if facts file exists and merge if it does
            if facts_path.exists():
                try:
                    existing_data = read_yaml(facts_path)

                    # Merge facts_found arrays for each category
                    for category in ['financial_health', 'market_position', 'organizational_stability', 'technical_culture']:
                        if category in existing_data and category in facts_data:
                            # Merge facts_found arrays
                            if 'facts_found' in existing_data[category] and 'facts_found' in facts_data[category]:
                                facts_data[category]['facts_found'] = (
                                    existing_data[category]['facts_found'] +
                                    facts_data[category]['facts_found']
                                )

                            # Merge missing_information arrays
                            if 'missing_information' in existing_data[category] and 'missing_information' in facts_data[category]:
                                facts_data[category]['missing_information'] = list(set(
                                    existing_data[category]['missing_information'] +
                                    facts_data[category]['missing_information']
                                ))

                    # Update summary with new totals
                    if 'summary' in facts_data:
                        total_facts = sum(
                            len(facts_data.get(cat, {}).get('facts_found', []))
                            for cat in ['financial_health', 'market_position', 'organizational_stability', 'technical_culture']
                        )
                        facts_data['summary']['total_facts_found'] = total_facts

                except YAMLHandlerError:
                    # If existing file is malformed, overwrite it
                    pass

            # Write the merged facts file
            write_yaml(facts_path, facts_data)

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save facts file: {str(e)}",
                "company_name": company_name,
            }

        # Build success message with appropriate tone based on completeness
        if completeness == "low" or facts_count < 10:
            message = (
                f"Research saved for {company_name} with limited information. "
                f"Saved {facts_count} facts (completeness: {completeness}). "
                f"Consider additional research or manual verification."
            )
        elif completeness == "high" and facts_count >= 30:
            message = (
                f"Research saved successfully for {company_name}. "
                f"Saved {facts_count} facts (completeness: {completeness})."
            )
        else:
            message = (
                f"Research saved for {company_name}. "
                f"Saved {facts_count} facts (completeness: {completeness})."
            )

        return {
            "success": True,
            "message": message,
            "company_name": company_name,
            "facts_generated": facts_count,
            "information_completeness": completeness,
            "facts_file_path": str(facts_path),
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error saving research: {str(e)}",
            "company_name": company_name,
        }
