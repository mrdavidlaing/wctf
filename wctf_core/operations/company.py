"""MCP tools for company management operations.

This module provides tools for listing companies and retrieving their
facts and evaluation flags.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from wctf_core.utils.paths import (
    get_company_dir,
    get_facts_path,
    get_flags_path,
    list_companies as list_companies_util,
)
from wctf_core.utils.yaml_handler import YAMLHandlerError, read_yaml


def list_companies(base_path: Optional[Path] = None) -> Dict[str, Any]:
    """List all companies with research data.

    Returns a dictionary containing:
    - companies: List of company names (sorted)
    - count: Total number of companies
    - company_details: Optional list with metadata for each company

    Args:
        base_path: Optional base path for data directory (for testing)

    Returns:
        Dictionary with company list and metadata
    """
    try:
        companies = list_companies_util(base_path=base_path)

        # Build detailed info about each company
        company_details = []
        for company in companies:
            try:
                facts_path = get_facts_path(company, base_path=base_path)
                flags_path = get_flags_path(company, base_path=base_path)

                company_details.append({
                    "name": company,
                    "has_facts": facts_path.exists(),
                    "has_flags": flags_path.exists(),
                })
            except Exception:
                # If we can't get details for a company, skip it
                company_details.append({
                    "name": company,
                    "has_facts": False,
                    "has_flags": False,
                })

        return {
            "companies": companies,
            "count": len(companies),
            "company_details": company_details,
        }

    except Exception as e:
        return {
            "companies": [],
            "count": 0,
            "error": f"Error listing companies: {str(e)}",
        }


def get_company_facts(
    company_name: str,
    base_path: Optional[Path] = None
) -> Dict[str, Any]:
    """Get facts for a specific company.

    Loads and returns the complete company.facts.yaml file content.

    Args:
        company_name: Name of the company
        base_path: Optional base path for data directory (for testing)

    Returns:
        Dictionary with either:
        - success: True, facts: <facts data>
        - success: False, error: <error message>, suggestion: <next steps>
    """
    try:
        # Check if company directory exists
        company_dir = get_company_dir(company_name, base_path=base_path)
        if not company_dir.exists():
            available_companies = list_companies_util(base_path=base_path)
            return {
                "success": False,
                "error": f"Company '{company_name}' not found",
                "suggestion": f"Available companies: {', '.join(available_companies[:5])}"
                             + (f" (and {len(available_companies) - 5} more)"
                                if len(available_companies) > 5 else "")
                             + ". Use list_companies to see all available companies.",
            }

        # Get facts file path
        facts_path = get_facts_path(company_name, base_path=base_path)

        # Check if facts file exists
        if not facts_path.exists():
            return {
                "success": False,
                "error": f"Facts file not found for company '{company_name}'",
                "suggestion": "The company directory exists but company.facts.yaml is missing. "
                             "You may need to create this file first.",
            }

        # Read and return the facts
        try:
            facts_data = read_yaml(facts_path)

            if not facts_data:
                return {
                    "success": False,
                    "error": f"Facts file for '{company_name}' is empty",
                    "suggestion": "The facts file exists but contains no data.",
                }

            return {
                "success": True,
                "facts": facts_data,
            }

        except YAMLHandlerError as e:
            return {
                "success": False,
                "error": f"Error parsing facts file for '{company_name}': {str(e)}",
                "suggestion": "The YAML file may be malformed. Check the file syntax.",
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error retrieving facts for '{company_name}': {str(e)}",
        }


def get_company_flags(
    company_name: str,
    base_path: Optional[Path] = None
) -> Dict[str, Any]:
    """Get evaluation flags for a specific company.

    Loads and returns the complete company.flags.yaml file content.

    Args:
        company_name: Name of the company
        base_path: Optional base path for data directory (for testing)

    Returns:
        Dictionary with either:
        - success: True, flags: <flags data>
        - success: False, error: <error message>, suggestion: <next steps>
    """
    try:
        # Check if company directory exists
        company_dir = get_company_dir(company_name, base_path=base_path)
        if not company_dir.exists():
            available_companies = list_companies_util(base_path=base_path)
            return {
                "success": False,
                "error": f"Company '{company_name}' not found",
                "suggestion": f"Available companies: {', '.join(available_companies[:5])}"
                             + (f" (and {len(available_companies) - 5} more)"
                                if len(available_companies) > 5 else "")
                             + ". Use list_companies to see all available companies.",
            }

        # Get flags file path
        flags_path = get_flags_path(company_name, base_path=base_path)

        # Check if flags file exists
        if not flags_path.exists():
            # Check if facts exist to provide better guidance
            facts_path = get_facts_path(company_name, base_path=base_path)
            has_facts = facts_path.exists()

            suggestion = "The company directory exists but company.flags.yaml is missing."
            if has_facts:
                suggestion += " Facts file exists - you may want to create flags based on the facts."
            else:
                suggestion += " Consider researching the company first (create facts file)."

            return {
                "success": False,
                "error": f"Flags file not found for company '{company_name}'",
                "suggestion": suggestion,
            }

        # Read and return the flags
        try:
            flags_data = read_yaml(flags_path)

            if not flags_data:
                return {
                    "success": False,
                    "error": f"Flags file for '{company_name}' is empty",
                    "suggestion": "The flags file exists but contains no data.",
                }

            return {
                "success": True,
                "flags": flags_data,
            }

        except YAMLHandlerError as e:
            return {
                "success": False,
                "error": f"Error parsing flags file for '{company_name}': {str(e)}",
                "suggestion": "The YAML file may be malformed. Check the file syntax.",
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error retrieving flags for '{company_name}': {str(e)}",
        }
