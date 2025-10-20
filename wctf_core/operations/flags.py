"""MCP tools for flag extraction and management.

This module provides tools for extracting evaluation flags from conversation notes
and manually adding flags. Following the pattern from research.py, the extract_flags
tool returns a prompt for the calling agent rather than making LLM calls directly.
"""

from datetime import date
from pathlib import Path
from typing import Dict, Optional

import yaml

from wctf_core.utils.paths import (
    ensure_company_dir,
    get_flags_path,
    slugify_company_name,
)
from wctf_core.utils.responses import success_response, error_response
from wctf_core.utils.yaml_handler import read_yaml, write_yaml


# Valid mountain elements (the five elements of career evaluation)
MOUNTAIN_ELEMENTS = {
    "mountain_range",      # Financial & Market Foundation
    "chosen_peak",         # Technical Culture & Work Quality
    "rope_team_confidence", # Leadership & Organization
    "daily_climb",         # Day-to-Day Experience
    "story_worth_telling", # Growth & Legacy
}


def _load_extraction_prompt() -> str:
    """Load the mountain flags extraction prompt template."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "mountain_flags.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Extraction prompt template not found at {prompt_path}")

    with open(prompt_path, "r") as f:
        return f.read()


def _initialize_flags_structure(company_name: str) -> Dict:
    """Initialize empty flags structure with double hierarchy (mountain elements -> severity)."""
    # Create separate dict instances for each mountain element to avoid shared references
    return {
        "company": company_name,
        "evaluation_date": str(date.today()),
        "evaluator_context": "Extracted from conversation notes",
        "green_flags": {
            "mountain_range": {
                "critical_matches": [],
                "strong_positives": [],
            },
            "chosen_peak": {
                "critical_matches": [],
                "strong_positives": [],
            },
            "rope_team_confidence": {
                "critical_matches": [],
                "strong_positives": [],
            },
            "daily_climb": {
                "critical_matches": [],
                "strong_positives": [],
            },
            "story_worth_telling": {
                "critical_matches": [],
                "strong_positives": [],
            },
        },
        "red_flags": {
            "mountain_range": {
                "dealbreakers": [],
                "concerning": [],
            },
            "chosen_peak": {
                "dealbreakers": [],
                "concerning": [],
            },
            "rope_team_confidence": {
                "dealbreakers": [],
                "concerning": [],
            },
            "daily_climb": {
                "dealbreakers": [],
                "concerning": [],
            },
            "story_worth_telling": {
                "dealbreakers": [],
                "concerning": [],
            },
        },
        "missing_critical_data": [],
    }


def _validate_flag_structure(flag_data: Dict) -> tuple[bool, Optional[str]]:
    """Validate that extracted flags have proper double hierarchy structure.

    Returns:
        (is_valid, error_message) tuple
    """
    if not isinstance(flag_data, dict):
        return False, "Flag data must be a dictionary"

    # Check for required top-level keys
    if "green_flags" not in flag_data and "red_flags" not in flag_data and "missing_critical_data" not in flag_data:
        return False, "Flag data must contain at least one of: green_flags, red_flags, missing_critical_data"

    # Validate green flags structure (double hierarchy: element -> severity -> flags)
    if "green_flags" in flag_data:
        if not isinstance(flag_data["green_flags"], dict):
            return False, "green_flags must be a dictionary"

        for element, severity_categories in flag_data["green_flags"].items():
            if element not in MOUNTAIN_ELEMENTS:
                return False, f"Invalid mountain element in green_flags: {element}. Must be one of: {', '.join(MOUNTAIN_ELEMENTS)}"

            if not isinstance(severity_categories, dict):
                return False, f"Severity categories for {element} must be a dictionary"

            # Check for valid severity categories
            valid_green_severities = {"critical_matches", "strong_positives"}
            for severity, flags in severity_categories.items():
                if severity not in valid_green_severities:
                    return False, f"Invalid green flag severity: {severity}. Must be one of: {', '.join(valid_green_severities)}"

                if not isinstance(flags, list):
                    return False, f"Flags for {element}.{severity} must be a list"

                for flag in flags:
                    if not isinstance(flag, dict):
                        return False, f"Each flag must be a dictionary"

                    required_fields = {"flag", "impact", "confidence"}
                    missing_fields = required_fields - set(flag.keys())
                    if missing_fields:
                        return False, f"Flag missing required fields: {', '.join(missing_fields)}"

    # Validate red flags structure (double hierarchy)
    if "red_flags" in flag_data:
        if not isinstance(flag_data["red_flags"], dict):
            return False, "red_flags must be a dictionary"

        for element, severity_categories in flag_data["red_flags"].items():
            if element not in MOUNTAIN_ELEMENTS:
                return False, f"Invalid mountain element in red_flags: {element}. Must be one of: {', '.join(MOUNTAIN_ELEMENTS)}"

            if not isinstance(severity_categories, dict):
                return False, f"Severity categories for {element} must be a dictionary"

            # Check for valid severity categories
            valid_red_severities = {"dealbreakers", "concerning"}
            for severity, flags in severity_categories.items():
                if severity not in valid_red_severities:
                    return False, f"Invalid red flag severity: {severity}. Must be one of: {', '.join(valid_red_severities)}"

                if not isinstance(flags, list):
                    return False, f"Flags for {element}.{severity} must be a list"

                for flag in flags:
                    if not isinstance(flag, dict):
                        return False, f"Each flag must be a dictionary"

                    required_fields = {"flag", "impact", "confidence"}
                    missing_fields = required_fields - set(flag.keys())
                    if missing_fields:
                        return False, f"Flag missing required fields: {', '.join(missing_fields)}"

    # Validate missing critical data structure
    if "missing_critical_data" in flag_data:
        if not isinstance(flag_data["missing_critical_data"], list):
            return False, "missing_critical_data must be a list"

        for item in flag_data["missing_critical_data"]:
            if not isinstance(item, dict):
                return False, "Each missing data item must be a dictionary"

            required_fields = {"question", "why_important", "how_to_find", "mountain_element"}
            missing_fields = required_fields - set(item.keys())
            if missing_fields:
                return False, f"Missing data item missing required fields: {', '.join(missing_fields)}"

            if item["mountain_element"] not in MOUNTAIN_ELEMENTS:
                return False, f"Invalid mountain element in missing_critical_data: {item['mountain_element']}"

    return True, None


def _merge_flags(existing: Dict, new: Dict) -> Dict:
    """Merge new flags into existing flags structure (double hierarchy).

    Appends new flags to existing lists within element -> severity structure.
    """
    merged = existing.copy()

    # Update evaluation date to latest
    merged["evaluation_date"] = str(date.today())

    # Merge green flags (double hierarchy: element -> severity -> flags)
    if "green_flags" in new:
        for element, severity_categories in new["green_flags"].items():
            if element in MOUNTAIN_ELEMENTS:
                if element not in merged["green_flags"]:
                    merged["green_flags"][element] = {
                        "critical_matches": [],
                        "strong_positives": [],
                    }

                # Merge each severity category
                for severity in ["critical_matches", "strong_positives"]:
                    if severity in severity_categories:
                        if severity not in merged["green_flags"][element]:
                            merged["green_flags"][element][severity] = []
                        merged["green_flags"][element][severity].extend(
                            severity_categories[severity]
                        )

    # Merge red flags (double hierarchy)
    if "red_flags" in new:
        for element, severity_categories in new["red_flags"].items():
            if element in MOUNTAIN_ELEMENTS:
                if element not in merged["red_flags"]:
                    merged["red_flags"][element] = {
                        "dealbreakers": [],
                        "concerning": [],
                    }

                # Merge each severity category
                for severity in ["dealbreakers", "concerning"]:
                    if severity in severity_categories:
                        if severity not in merged["red_flags"][element]:
                            merged["red_flags"][element][severity] = []
                        merged["red_flags"][element][severity].extend(
                            severity_categories[severity]
                        )

    # Merge missing critical data
    if "missing_critical_data" in new:
        if "missing_critical_data" not in merged:
            merged["missing_critical_data"] = []
        merged["missing_critical_data"].extend(new["missing_critical_data"])

    return merged


def get_flags_extraction_prompt_op(
    base_path: Optional[Path] = None,
) -> Dict[str, any]:
    """Get the prompt for extracting evaluation flags from research.

    The prompt expects research facts to be provided in the conversation context,
    similar to the insider interview workflow.

    Args:
        base_path: Optional base path for data directory (for testing, currently unused)

    Returns:
        - success: bool
        - extraction_prompt: str - Prompt for analyzing research facts

        On error:
        - success: False
        - error: str
    """
    try:
        prompt = _load_extraction_prompt()

        return {
            "success": True,
            "extraction_prompt": prompt,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate extraction prompt: {str(e)}",
        }


def save_flags_op(
    company_name: str,
    flags_yaml: str,
    base_path: Optional[Path] = None,
) -> Dict[str, any]:
    """Save extracted evaluation flags to company.flags.yaml.

    Args:
        company_name: Name of the company being evaluated
        flags_yaml: Complete YAML content with extracted flags
        base_path: Optional base path for data directory (for testing)

    Returns:
        Dictionary with:
        - success: bool - Whether save completed successfully
        - message: str - Human-readable confirmation
        - company_name: str - Display name of company
        - company_slug: str - Normalized name for filesystem
        - file_path: str - Path to saved flags file
        - items_saved: int - Number of flags saved
        - operation: str - "created", "updated", or "merged"

        On error:
        - success: False
        - message: str - Human-readable error explanation
        - error: str - Technical error details
        - company_name: str - Display name (if available)
        - company_slug: str - Normalized name (if available)
    """
    # Validate company name
    if company_name is None:
        raise TypeError("Company name cannot be None")

    if not isinstance(company_name, str) or not company_name.strip():
        return error_response(
            error="Invalid company name. Company name must be a non-empty string.",
            message="Company name must be a valid string"
        )

    company_name = company_name.strip()

    # Validate flags_yaml
    if not flags_yaml or not isinstance(flags_yaml, str):
        return error_response(
            error="Invalid flags YAML. Must be a non-empty string.",
            message="Flags YAML content is required"
        )

    try:
        # Parse YAML content
        try:
            extracted_flags = yaml.safe_load(flags_yaml)
        except yaml.YAMLError as e:
            return error_response(
                error=f"Failed to parse YAML content: {str(e)}",
                message="Failed to parse YAML content",
                company_name=company_name
            )

        # Validate flag structure
        is_valid, error_msg = _validate_flag_structure(extracted_flags)
        if not is_valid:
            return error_response(
                error=f"Invalid flag structure: {error_msg}",
                message="Invalid flag structure",
                company_name=company_name
            )

        # Ensure company directory exists
        ensure_company_dir(company_name, base_path=base_path)
        flags_path = get_flags_path(company_name, base_path=base_path)

        # Load existing flags or initialize new structure
        if flags_path.exists():
            try:
                existing_flags = read_yaml(flags_path)
                if not existing_flags:  # Empty file
                    existing_flags = _initialize_flags_structure(company_name)
            except Exception:
                # If read fails, initialize new structure
                existing_flags = _initialize_flags_structure(company_name)
        else:
            existing_flags = _initialize_flags_structure(company_name)

        # Merge new flags with existing
        merged_flags = _merge_flags(existing_flags, extracted_flags)

        # Ensure company_slug field is present
        if 'company_slug' not in merged_flags:
            merged_flags['company_slug'] = slugify_company_name(company_name)

        # Count flags
        flag_count = 0
        if "green_flags" in merged_flags:
            for element, severities in merged_flags["green_flags"].items():
                for severity, flags in severities.items():
                    flag_count += len(flags)
        if "red_flags" in merged_flags:
            for element, severities in merged_flags["red_flags"].items():
                for severity, flags in severities.items():
                    flag_count += len(flags)
        if "missing_critical_data" in merged_flags:
            flag_count += len(merged_flags["missing_critical_data"])
        
        # Determine operation type BEFORE writing
        operation = "merged" if flags_path.exists() else "created"
        
        # Save merged flags
        write_yaml(flags_path, merged_flags)

        return success_response(
            company_name=company_name,
            file_path=flags_path,
            items_saved=flag_count,
            message=f"Successfully saved {flag_count} flags for {company_name}",
            operation=operation
        )

    except Exception as e:
        return error_response(
            error=f"Failed to save flags: {str(e)}",
            message="Failed to save flags",
            company_name=company_name
        )


def add_manual_flag(
    company_name: str,
    flag_type: str,
    mountain_element: str,
    severity: Optional[str] = None,
    flag: Optional[str] = None,
    impact: Optional[str] = None,
    confidence: Optional[str] = None,
    question: Optional[str] = None,
    why_important: Optional[str] = None,
    how_to_find: Optional[str] = None,
    base_path: Optional[Path] = None,
) -> Dict[str, any]:
    """Add a manual flag to company evaluation (double hierarchy structure).

    This is a pure data operation that validates and saves a manually created flag.

    Args:
        company_name: Name of the company
        flag_type: Type of flag - "green", "red", or "missing"
        mountain_element: Which mountain element this relates to
        severity: Severity level - for green: "critical_matches" or "strong_positives"
                 for red: "dealbreakers" or "concerning" (required for green/red flags)
        flag: Flag text (for green/red flags)
        impact: Impact description (for green/red flags)
        confidence: Confidence level (for green/red flags)
        question: Question text (for missing data)
        why_important: Why it matters (for missing data)
        how_to_find: How to find the answer (for missing data)
        base_path: Optional base path for data directory (for testing)

    Returns:
        Dictionary with:
        - success: bool - Whether save completed successfully
        - message: str - Human-readable confirmation
        - company_name: str - Display name of company
        - company_slug: str - Normalized name for filesystem
        - file_path: str - Path to saved flags file
        - items_saved: int - Always 1 (one flag added)
        - operation: str - Always "updated" (adding to existing)

        On error:
        - success: False
        - message: str - Human-readable error explanation
        - error: str - Technical error details
        - company_name: str - Display name (if available)
        - company_slug: str - Normalized name (if available)
    """
    # Validate company name
    if company_name is None:
        raise TypeError("Company name cannot be None")

    if not isinstance(company_name, str) or not company_name.strip():
        return error_response(
            error="Invalid company name. Company name must be a non-empty string.",
            message="Company name must be a valid string"
        )

    company_name = company_name.strip()

    # Validate flag type
    valid_flag_types = {"green", "red", "missing"}
    if flag_type not in valid_flag_types:
        return error_response(
            error=f"Invalid flag type: {flag_type}. Must be one of: {', '.join(valid_flag_types)}",
            message="Invalid flag type"
        )

    # Validate mountain element
    if mountain_element not in MOUNTAIN_ELEMENTS:
        return error_response(
            error=f"Invalid mountain element: {mountain_element}. Must be one of: {', '.join(MOUNTAIN_ELEMENTS)}",
            message="Invalid mountain element"
        )

    # Validate appropriate fields for flag type
    if flag_type in ("green", "red"):
        if not flag or not impact or not confidence:
            return error_response(
                error=f"For {flag_type} flags, must provide: flag, impact, confidence",
                message=f"Missing required fields for {flag_type} flag"
            )
        if not severity:
            return error_response(
                error=f"For {flag_type} flags, must provide severity level",
                message="Severity level is required"
            )

        # Validate severity level
        if flag_type == "green":
            valid_severities = {"critical_matches", "strong_positives"}
            if severity not in valid_severities:
                return error_response(
                    error=f"Invalid severity for green flag: {severity}. Must be one of: {', '.join(valid_severities)}",
                    message="Invalid severity for green flag"
                )
        elif flag_type == "red":
            valid_severities = {"dealbreakers", "concerning"}
            if severity not in valid_severities:
                return error_response(
                    error=f"Invalid severity for red flag: {severity}. Must be one of: {', '.join(valid_severities)}",
                    message="Invalid severity for red flag"
                )

    elif flag_type == "missing":
        if not question or not why_important or not how_to_find:
            return error_response(
                error="For missing data, must provide: question, why_important, how_to_find",
                message="Missing required fields for missing data"
            )

    try:
        # Ensure company directory exists
        ensure_company_dir(company_name, base_path=base_path)
        flags_path = get_flags_path(company_name, base_path=base_path)

        # Load existing flags or initialize new structure
        if flags_path.exists():
            try:
                flags_data = read_yaml(flags_path)
                if not flags_data:  # Empty file
                    flags_data = _initialize_flags_structure(company_name)
            except Exception:
                # If read fails, initialize new structure
                flags_data = _initialize_flags_structure(company_name)
        else:
            flags_data = _initialize_flags_structure(company_name)

        # Add the new flag (double hierarchy: element -> severity -> flags)
        if flag_type == "green":
            if mountain_element not in flags_data["green_flags"]:
                flags_data["green_flags"][mountain_element] = {
                    "critical_matches": [],
                    "strong_positives": [],
                }

            if severity not in flags_data["green_flags"][mountain_element]:
                flags_data["green_flags"][mountain_element][severity] = []

            flags_data["green_flags"][mountain_element][severity].append({
                "flag": flag,
                "impact": impact,
                "confidence": confidence,
            })

        elif flag_type == "red":
            if mountain_element not in flags_data["red_flags"]:
                flags_data["red_flags"][mountain_element] = {
                    "dealbreakers": [],
                    "concerning": [],
                }

            if severity not in flags_data["red_flags"][mountain_element]:
                flags_data["red_flags"][mountain_element][severity] = []

            flags_data["red_flags"][mountain_element][severity].append({
                "flag": flag,
                "impact": impact,
                "confidence": confidence,
            })

        elif flag_type == "missing":
            if "missing_critical_data" not in flags_data:
                flags_data["missing_critical_data"] = []

            flags_data["missing_critical_data"].append({
                "question": question,
                "why_important": why_important,
                "how_to_find": how_to_find,
                "mountain_element": mountain_element,
            })

        # Update evaluation date
        flags_data["evaluation_date"] = str(date.today())

        # Ensure company_slug field is present
        if 'company_slug' not in flags_data:
            flags_data['company_slug'] = slugify_company_name(company_name)

        # Save updated flags
        write_yaml(flags_path, flags_data)

        return success_response(
            company_name=company_name,
            file_path=flags_path,
            items_saved=1,  # Added one flag
            message=f"Successfully added {flag_type} flag for {company_name}",
            operation="updated"  # Always updating existing flags structure
        )

    except Exception as e:
        return error_response(
            error=f"Failed to add manual flag: {str(e)}",
            message="Failed to add manual flag",
            company_name=company_name
        )
