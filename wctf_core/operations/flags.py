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
    element_template_green = {
        "critical_matches": [],
        "strong_positives": [],
    }
    element_template_red = {
        "dealbreakers": [],
        "concerning": [],
    }

    return {
        "company": company_name,
        "evaluation_date": str(date.today()),
        "evaluator_context": "Extracted from conversation notes",
        "green_flags": {
            "mountain_range": element_template_green.copy(),
            "chosen_peak": element_template_green.copy(),
            "rope_team_confidence": element_template_green.copy(),
            "daily_climb": element_template_green.copy(),
            "story_worth_telling": element_template_green.copy(),
        },
        "red_flags": {
            "mountain_range": element_template_red.copy(),
            "chosen_peak": element_template_red.copy(),
            "rope_team_confidence": element_template_red.copy(),
            "daily_climb": element_template_red.copy(),
            "story_worth_telling": element_template_red.copy(),
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
    company_name: str,
    evaluator_context: str,
    base_path: Optional[Path] = None,
) -> Dict[str, any]:
    """Get the prompt for extracting evaluation flags from research.

    Args:
        company_name: Name of the company being evaluated
        evaluator_context: Your evaluation criteria and context (e.g., "Senior engineer seeking...")
        base_path: Optional base path for data directory (for testing)

    Returns:
        - success: bool
        - company_name: str
        - extraction_prompt: str - Prompt for analyzing research facts

        On error:
        - success: False
        - error: str
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

    # Validate evaluator context
    if not evaluator_context or not isinstance(evaluator_context, str):
        return {
            "success": False,
            "error": "Invalid evaluator context. Must be a non-empty string.",
        }

    try:
        prompt_template = _load_extraction_prompt()
        evaluation_date = date.today().isoformat()

        prompt = prompt_template.format(
            company_name=company_name,
            conversation_notes=evaluator_context,
            evaluation_date=evaluation_date,
        )

        return {
            "success": True,
            "company_name": company_name,
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
        - success: bool
        - company_name: str
        - flags_file_path: str
        - message: str

        On error:
        - success: False
        - error: str
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

    # Validate flags_yaml
    if not flags_yaml or not isinstance(flags_yaml, str):
        return {
            "success": False,
            "error": "Invalid flags YAML. Must be a non-empty string.",
        }

    try:
        # Parse YAML content
        try:
            extracted_flags = yaml.safe_load(flags_yaml)
        except yaml.YAMLError as e:
            return {
                "success": False,
                "error": f"Failed to parse YAML content: {str(e)}",
                "company_name": company_name,
            }

        # Validate flag structure
        is_valid, error_msg = _validate_flag_structure(extracted_flags)
        if not is_valid:
            return {
                "success": False,
                "error": f"Invalid flag structure: {error_msg}",
                "company_name": company_name,
            }

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

        # Save merged flags
        write_yaml(flags_path, merged_flags)

        return {
            "success": True,
            "company_name": company_name,
            "flags_file_path": str(flags_path),
            "message": f"Successfully saved flags for {company_name}",
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to save flags: {str(e)}",
            "company_name": company_name,
        }


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
        - success: bool
        - company_name: str
        - flags_file_path: str
        - message: str
        OR
        - success: False
        - error: str
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

    # Validate flag type
    valid_flag_types = {"green", "red", "missing"}
    if flag_type not in valid_flag_types:
        return {
            "success": False,
            "error": f"Invalid flag type: {flag_type}. Must be one of: {', '.join(valid_flag_types)}",
        }

    # Validate mountain element
    if mountain_element not in MOUNTAIN_ELEMENTS:
        return {
            "success": False,
            "error": f"Invalid mountain element: {mountain_element}. Must be one of: {', '.join(MOUNTAIN_ELEMENTS)}",
        }

    # Validate appropriate fields for flag type
    if flag_type in ("green", "red"):
        if not flag or not impact or not confidence:
            return {
                "success": False,
                "error": f"For {flag_type} flags, must provide: flag, impact, confidence",
            }
        if not severity:
            return {
                "success": False,
                "error": f"For {flag_type} flags, must provide severity level",
            }

        # Validate severity level
        if flag_type == "green":
            valid_severities = {"critical_matches", "strong_positives"}
            if severity not in valid_severities:
                return {
                    "success": False,
                    "error": f"Invalid severity for green flag: {severity}. Must be one of: {', '.join(valid_severities)}",
                }
        elif flag_type == "red":
            valid_severities = {"dealbreakers", "concerning"}
            if severity not in valid_severities:
                return {
                    "success": False,
                    "error": f"Invalid severity for red flag: {severity}. Must be one of: {', '.join(valid_severities)}",
                }

    elif flag_type == "missing":
        if not question or not why_important or not how_to_find:
            return {
                "success": False,
                "error": "For missing data, must provide: question, why_important, how_to_find",
            }

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

        return {
            "success": True,
            "company_name": company_name,
            "flags_file_path": str(flags_path),
            "message": f"Successfully added {flag_type} flag for {company_name}",
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to add manual flag: {str(e)}",
            "company_name": company_name,
        }
