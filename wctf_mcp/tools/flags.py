"""MCP tools for flag extraction and management.

This module provides tools for extracting evaluation flags from conversation notes
and manually adding flags. Following the pattern from research.py, the extract_flags
tool returns a prompt for the calling agent rather than making LLM calls directly.
"""

from datetime import date
from pathlib import Path
from typing import Dict, Optional

import yaml

from wctf_mcp.utils.paths import (
    ensure_company_dir,
    get_flags_path,
)
from wctf_mcp.utils.yaml_handler import read_yaml, write_yaml


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
    """Initialize empty flags structure with all mountain elements."""
    return {
        "company": company_name,
        "evaluation_date": str(date.today()),
        "evaluator_context": "Extracted from conversation notes",
        "green_flags": {
            "mountain_range": [],
            "chosen_peak": [],
            "rope_team_confidence": [],
            "daily_climb": [],
            "story_worth_telling": [],
        },
        "red_flags": {
            "mountain_range": [],
            "chosen_peak": [],
            "rope_team_confidence": [],
            "daily_climb": [],
            "story_worth_telling": [],
        },
        "missing_critical_data": [],
    }


def _validate_flag_structure(flag_data: Dict) -> tuple[bool, Optional[str]]:
    """Validate that extracted flags have proper structure.

    Returns:
        (is_valid, error_message) tuple
    """
    if not isinstance(flag_data, dict):
        return False, "Flag data must be a dictionary"

    # Check for required top-level keys
    if "green_flags" not in flag_data and "red_flags" not in flag_data and "missing_critical_data" not in flag_data:
        return False, "Flag data must contain at least one of: green_flags, red_flags, missing_critical_data"

    # Validate green flags structure
    if "green_flags" in flag_data:
        if not isinstance(flag_data["green_flags"], dict):
            return False, "green_flags must be a dictionary"

        for element, flags in flag_data["green_flags"].items():
            if element not in MOUNTAIN_ELEMENTS:
                return False, f"Invalid mountain element in green_flags: {element}. Must be one of: {', '.join(MOUNTAIN_ELEMENTS)}"

            if not isinstance(flags, list):
                return False, f"Flags for {element} must be a list"

            for flag in flags:
                if not isinstance(flag, dict):
                    return False, f"Each flag must be a dictionary"

                required_fields = {"flag", "impact", "confidence"}
                missing_fields = required_fields - set(flag.keys())
                if missing_fields:
                    return False, f"Flag missing required fields: {', '.join(missing_fields)}"

    # Validate red flags structure
    if "red_flags" in flag_data:
        if not isinstance(flag_data["red_flags"], dict):
            return False, "red_flags must be a dictionary"

        for element, flags in flag_data["red_flags"].items():
            if element not in MOUNTAIN_ELEMENTS:
                return False, f"Invalid mountain element in red_flags: {element}. Must be one of: {', '.join(MOUNTAIN_ELEMENTS)}"

            if not isinstance(flags, list):
                return False, f"Flags for {element} must be a list"

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
    """Merge new flags into existing flags structure.

    Appends new flags to existing lists, preserving all data.
    """
    merged = existing.copy()

    # Update evaluation date to latest
    merged["evaluation_date"] = str(date.today())

    # Merge green flags
    if "green_flags" in new:
        for element, flags in new["green_flags"].items():
            if element in MOUNTAIN_ELEMENTS:
                if element not in merged["green_flags"]:
                    merged["green_flags"][element] = []
                merged["green_flags"][element].extend(flags)

    # Merge red flags
    if "red_flags" in new:
        for element, flags in new["red_flags"].items():
            if element in MOUNTAIN_ELEMENTS:
                if element not in merged["red_flags"]:
                    merged["red_flags"][element] = []
                merged["red_flags"][element].extend(flags)

    # Merge missing critical data
    if "missing_critical_data" in new:
        if "missing_critical_data" not in merged:
            merged["missing_critical_data"] = []
        merged["missing_critical_data"].extend(new["missing_critical_data"])

    return merged


def extract_flags(
    company_name: str,
    conversation_notes: str,
    extracted_flags_yaml: Optional[str] = None,
    base_path: Optional[Path] = None,
) -> Dict[str, any]:
    """Extract evaluation flags from conversation notes.

    This tool works in two modes:

    1. **Prompt Generation Mode** (when extracted_flags_yaml is None):
       Returns a prompt for the calling agent to analyze the conversation notes.

    2. **Result Processing Mode** (when extracted_flags_yaml is provided):
       Processes the LLM's extracted flags and saves them to the flags file.

    Args:
        company_name: Name of the company being evaluated
        conversation_notes: Raw conversation notes to analyze
        extracted_flags_yaml: Optional YAML content with extracted flags (from LLM)
        base_path: Optional base path for data directory (for testing)

    Returns:
        In Prompt Generation Mode:
        - success: bool
        - company_name: str
        - extraction_prompt: str - Prompt for LLM to analyze notes
        - instructions: str - Instructions for the calling agent

        In Result Processing Mode:
        - success: bool
        - company_name: str
        - flags_saved: bool
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

    # Validate conversation notes
    if not conversation_notes or not isinstance(conversation_notes, str):
        return {
            "success": False,
            "error": "Invalid conversation notes. Must be a non-empty string.",
        }

    # MODE 1: Generate prompt for LLM
    if extracted_flags_yaml is None:
        try:
            prompt_template = _load_extraction_prompt()
            evaluation_date = date.today().isoformat()

            prompt = prompt_template.format(
                company_name=company_name,
                conversation_notes=conversation_notes,
                evaluation_date=evaluation_date,
            )

            instructions = (
                f"Please analyze these conversation notes using the prompt above. "
                f"When complete, provide the YAML output and I will save it to "
                f"data/{company_name}/company.flags.yaml"
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
            }

    # MODE 2: Process LLM-provided flags
    try:
        # Parse YAML content
        try:
            extracted_flags = yaml.safe_load(extracted_flags_yaml)
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

        # Save merged flags
        write_yaml(flags_path, merged_flags)

        return {
            "success": True,
            "company_name": company_name,
            "flags_saved": True,
            "flags_file_path": str(flags_path),
            "message": f"Successfully extracted and saved flags for {company_name}",
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to process extracted flags: {str(e)}",
            "company_name": company_name,
        }


def add_manual_flag(
    company_name: str,
    flag_type: str,
    mountain_element: str,
    flag: Optional[str] = None,
    impact: Optional[str] = None,
    confidence: Optional[str] = None,
    question: Optional[str] = None,
    why_important: Optional[str] = None,
    how_to_find: Optional[str] = None,
    base_path: Optional[Path] = None,
) -> Dict[str, any]:
    """Add a manual flag to company evaluation.

    This is a pure data operation that validates and saves a manually created flag.

    Args:
        company_name: Name of the company
        flag_type: Type of flag - "green", "red", or "missing"
        mountain_element: Which mountain element this relates to
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

        # Add the new flag
        if flag_type == "green":
            if mountain_element not in flags_data["green_flags"]:
                flags_data["green_flags"][mountain_element] = []

            flags_data["green_flags"][mountain_element].append({
                "flag": flag,
                "impact": impact,
                "confidence": confidence,
            })

        elif flag_type == "red":
            if mountain_element not in flags_data["red_flags"]:
                flags_data["red_flags"][mountain_element] = []

            flags_data["red_flags"][mountain_element].append({
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
