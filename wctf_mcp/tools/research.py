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
from wctf_mcp.utils.yaml_handler import write_yaml


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
            f"Please execute this research prompt using your web search capabilities. "
            f"When complete, provide the YAML output and I will save it to "
            f"data/{company_name}/company.facts.yaml"
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
            return {
                "success": False,
                "error": f"Failed to parse YAML content: {str(e)}",
                "company_name": company_name,
            }

        # Validate basic structure
        if not isinstance(facts_data, dict):
            return {
                "success": False,
                "error": "YAML content is not a valid dictionary",
                "company_name": company_name,
            }

        if "summary" not in facts_data:
            return {
                "success": False,
                "error": "YAML content missing required 'summary' section",
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

            # Write the facts file
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
