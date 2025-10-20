"""MCP tools for decision synthesis operations.

This module provides pure data operations for decision making:
- gut_check: Reads facts/flags and formats a summary
- save_gut_decision: Validates and saves a decision with timestamp
- get_evaluation_summary: Generates a table of all companies

NO LLM calls - these are pure YAML read/write/format operations.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from wctf_core.utils.paths import (
    get_company_dir,
    get_facts_path,
    get_flags_path,
    list_companies as list_companies_util,
)
from wctf_core.utils.responses import success_response, error_response
from wctf_core.utils.yaml_handler import YAMLHandlerError, read_yaml, write_yaml


def gut_check(
    company_name: str,
    base_path: Optional[Path] = None
) -> Dict[str, Any]:
    """Present a gut-check summary for decision making.

    Pure data formatting - reads facts/flags and organizes for human review.
    No LLM calls, no decisions made.

    Args:
        company_name: Name of the company
        base_path: Optional base path for data directory (for testing)

    Returns:
        Dictionary with either:
        - success: True, summary: <formatted text>, flag_counts: <counts dict>
        - success: False, error: <error message>
    """
    try:
        # Check if company exists
        company_dir = get_company_dir(company_name, base_path=base_path)
        if not company_dir.exists():
            available_companies = list_companies_util(base_path=base_path)
            return error_response(
                error=f"Company '{company_name}' not found. "
                      f"Available companies: {', '.join(available_companies[:5])}"
                      + (f" (and {len(available_companies) - 5} more)"
                         if len(available_companies) > 5 else ""),
                message=f"Company '{company_name}' not found",
                company_name=company_name
            )

        # Read facts and flags
        facts_path = get_facts_path(company_name, base_path=base_path)
        flags_path = get_flags_path(company_name, base_path=base_path)

        facts_data = None
        flags_data = None

        if facts_path.exists():
            try:
                facts_data = read_yaml(facts_path)
            except YAMLHandlerError:
                pass

        if flags_path.exists():
            try:
                flags_data = read_yaml(flags_path)
            except YAMLHandlerError:
                pass

        # Count flags by category (double hierarchy: element -> severity -> flags)
        flag_counts = {
            "green_flags": {
                "critical_matches": 0,
                "strong_positives": 0,
            },
            "red_flags": {
                "dealbreakers": 0,
                "concerning": 0,
            },
            "missing_critical_data": 0,
            "by_element": {},  # Per-element breakdown
        }

        if flags_data:
            green_flags = flags_data.get("green_flags", {})
            red_flags = flags_data.get("red_flags", {})

            # Count across all mountain elements
            for element, severity_categories in green_flags.items():
                if isinstance(severity_categories, dict):
                    flag_counts["green_flags"]["critical_matches"] += len(
                        severity_categories.get("critical_matches", [])
                    )
                    flag_counts["green_flags"]["strong_positives"] += len(
                        severity_categories.get("strong_positives", [])
                    )

                    # Track per-element counts
                    if element not in flag_counts["by_element"]:
                        flag_counts["by_element"][element] = {
                            "green_critical": 0,
                            "green_strong": 0,
                            "red_dealbreakers": 0,
                            "red_concerning": 0,
                        }
                    flag_counts["by_element"][element]["green_critical"] = len(
                        severity_categories.get("critical_matches", [])
                    )
                    flag_counts["by_element"][element]["green_strong"] = len(
                        severity_categories.get("strong_positives", [])
                    )

            for element, severity_categories in red_flags.items():
                if isinstance(severity_categories, dict):
                    flag_counts["red_flags"]["dealbreakers"] += len(
                        severity_categories.get("dealbreakers", [])
                    )
                    flag_counts["red_flags"]["concerning"] += len(
                        severity_categories.get("concerning", [])
                    )

                    # Track per-element counts
                    if element not in flag_counts["by_element"]:
                        flag_counts["by_element"][element] = {
                            "green_critical": 0,
                            "green_strong": 0,
                            "red_dealbreakers": 0,
                            "red_concerning": 0,
                        }
                    flag_counts["by_element"][element]["red_dealbreakers"] = len(
                        severity_categories.get("dealbreakers", [])
                    )
                    flag_counts["by_element"][element]["red_concerning"] = len(
                        severity_categories.get("concerning", [])
                    )

            flag_counts["missing_critical_data"] = len(flags_data.get("missing_critical_data", []))

        # Format the summary
        summary_lines = []
        summary_lines.append(f"# Gut Check: {company_name}")
        summary_lines.append("")

        # Evaluation date
        if flags_data and "evaluation_date" in flags_data:
            summary_lines.append(f"Evaluation Date: {flags_data['evaluation_date']}")
            summary_lines.append("")

        # Mountain Elements (senior_engineer_alignment)
        if flags_data and "senior_engineer_alignment" in flags_data:
            summary_lines.append("## Mountain Elements")
            alignment = flags_data["senior_engineer_alignment"]
            for element, rating in alignment.items():
                summary_lines.append(f"- {element.replace('_', ' ').title()}: {rating}")
            summary_lines.append("")

        # Flag Summary (Overall)
        summary_lines.append("## Flag Summary (Overall)")
        summary_lines.append(f"- Green Flags (Critical): {flag_counts['green_flags']['critical_matches']}")
        summary_lines.append(f"- Green Flags (Strong): {flag_counts['green_flags']['strong_positives']}")
        summary_lines.append(f"- Red Flags (Dealbreakers): {flag_counts['red_flags']['dealbreakers']}")
        summary_lines.append(f"- Red Flags (Concerning): {flag_counts['red_flags']['concerning']}")
        summary_lines.append(f"- Missing Critical Data: {flag_counts['missing_critical_data']}")
        summary_lines.append("")

        # Per-Element Breakdown
        if flag_counts["by_element"]:
            summary_lines.append("## Flag Breakdown by Mountain Element")
            element_names = {
                "mountain_range": "Mountain Range (Financial & Market)",
                "chosen_peak": "Chosen Peak (Technical Culture)",
                "rope_team_confidence": "Rope Team (Leadership & Org)",
                "daily_climb": "Daily Climb (Work Experience)",
                "story_worth_telling": "Story Worth Telling (Growth & Legacy)",
            }
            for element, counts in sorted(flag_counts["by_element"].items()):
                element_name = element_names.get(element, element)
                total_green = counts["green_critical"] + counts["green_strong"]
                total_red = counts["red_dealbreakers"] + counts["red_concerning"]

                # Simple visual indicator
                if total_green > total_red * 2:
                    indicator = "✓✓✓"
                elif total_green > total_red:
                    indicator = "✓✓"
                elif total_green > 0 or total_red == 0:
                    indicator = "✓"
                elif total_red > total_green * 2:
                    indicator = "⚠️⚠️"
                elif total_red > total_green:
                    indicator = "⚠️"
                else:
                    indicator = "~"

                summary_lines.append(
                    f"- {element_name}: {indicator} "
                    f"({counts['green_critical']} critical, {counts['green_strong']} strong, "
                    f"{counts['red_dealbreakers']} dealbreakers, {counts['red_concerning']} concerning)"
                )
            summary_lines.append("")

        # Synthesis verdict (if available)
        if flags_data and "synthesis" in flags_data:
            synthesis = flags_data["synthesis"]
            summary_lines.append("## Synthesis")
            if "mountain_worth_climbing" in synthesis:
                summary_lines.append(f"- Mountain Worth Climbing: {synthesis['mountain_worth_climbing']}")
            if "sustainability_confidence" in synthesis:
                summary_lines.append(f"- Sustainability Confidence: {synthesis['sustainability_confidence']}")
            if "primary_strengths" in synthesis:
                summary_lines.append("- Primary Strengths:")
                for strength in synthesis["primary_strengths"]:
                    summary_lines.append(f"  - {strength}")
            if "primary_risks" in synthesis:
                summary_lines.append("- Primary Risks:")
                for risk in synthesis["primary_risks"]:
                    summary_lines.append(f"  - {risk}")
            summary_lines.append("")

        # Missing critical information
        if flags_data and flag_counts["missing_critical_data"] > 0:
            summary_lines.append("## Missing Critical Information")
            for missing in flags_data.get("missing_critical_data", []):
                summary_lines.append(f"- {missing.get('question', 'Unknown question')}")
                summary_lines.append(f"  Why: {missing.get('why_important', 'Not specified')}")
            summary_lines.append("")

        # Data availability warnings
        warnings = []
        if not facts_data:
            warnings.append("⚠️  No facts data available")
        if not flags_data:
            warnings.append("⚠️  No evaluation flags available")

        if warnings:
            summary_lines.append("## Warnings")
            for warning in warnings:
                summary_lines.append(warning)
            summary_lines.append("")

        return {
            "success": True,
            "summary": "\n".join(summary_lines),
            "flag_counts": flag_counts,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating gut check for '{company_name}': {str(e)}",
        }


def save_gut_decision(
    company_name: str,
    mountain_worth_climbing: str,
    confidence: str,
    reasoning: Optional[str] = None,
    base_path: Optional[Path] = None
) -> Dict[str, Any]:
    """Save a gut decision to the company's flags file.

    Validates enum values and saves with ISO timestamp.
    Pure data operation - no LLM calls.

    Args:
        company_name: Name of the company
        mountain_worth_climbing: YES, NO, or MAYBE
        confidence: HIGH, MEDIUM, or LOW
        reasoning: Optional reasoning text
        base_path: Optional base path for data directory (for testing)

    Returns:
        Dictionary with:
        - success: bool - Whether save completed successfully
        - message: str - Human-readable confirmation
        - company_name: str - Display name of company
        - company_slug: str - Normalized name for filesystem
        - file_path: str - Path to saved flags file
        - items_saved: int - Always 1 (one decision saved)
        - operation: str - Always "updated" (updating flags file)

        On error:
        - success: False
        - message: str - Human-readable error explanation
        - error: str - Technical error details
        - company_name: str - Display name (if available)
        - company_slug: str - Normalized name (if available)
    """
    try:
        # Validate enum values
        valid_mountain_values = ["YES", "NO", "MAYBE"]
        valid_confidence_values = ["HIGH", "MEDIUM", "LOW"]

        if mountain_worth_climbing not in valid_mountain_values:
            return error_response(
                error=f"Invalid mountain_worth_climbing value: '{mountain_worth_climbing}'. "
                      f"Must be one of: {', '.join(valid_mountain_values)}",
                message="Invalid mountain_worth_climbing value"
            )

        if confidence not in valid_confidence_values:
            return error_response(
                error=f"Invalid confidence value: '{confidence}'. "
                      f"Must be one of: {', '.join(valid_confidence_values)}",
                message="Invalid confidence value"
            )

        # Check if company exists
        company_dir = get_company_dir(company_name, base_path=base_path)
        if not company_dir.exists():
            available_companies = list_companies_util(base_path=base_path)
            return error_response(
                error=f"Company '{company_name}' not found. "
                      f"Available companies: {', '.join(available_companies[:5])}"
                      + (f" (and {len(available_companies) - 5} more)"
                         if len(available_companies) > 5 else ""),
                message=f"Company '{company_name}' not found",
                company_name=company_name
            )

        # Get flags file path
        flags_path = get_flags_path(company_name, base_path=base_path)

        # Read existing flags or create new structure
        if flags_path.exists():
            try:
                flags_data = read_yaml(flags_path)
            except YAMLHandlerError:
                flags_data = {}
        else:
            flags_data = {}

        # Add gut_decision with timestamp
        flags_data["gut_decision"] = {
            "mountain_worth_climbing": mountain_worth_climbing,
            "confidence": confidence,
            "reasoning": reasoning or "",
            "timestamp": datetime.now().isoformat(),
        }

        # Write back to file
        write_yaml(flags_path, flags_data)

        return success_response(
            company_name=company_name,
            file_path=flags_path,
            items_saved=1,  # One decision saved
            message=f"Gut decision saved for {company_name}: "
                    f"{mountain_worth_climbing} (confidence: {confidence})",
            operation="updated"  # Always updating flags file
        )

    except Exception as e:
        return error_response(
            error=f"Error saving gut decision for '{company_name}': {str(e)}",
            message="Error saving gut decision",
            company_name=company_name
        )


def get_evaluation_summary(
    base_path: Optional[Path] = None
) -> Dict[str, Any]:
    """Generate a summary table of all company evaluations.

    Pure data operation - reads all companies and formats as a table.
    No LLM calls.

    Args:
        base_path: Optional base path for data directory (for testing)

    Returns:
        Dictionary with:
        - success: True
        - summary_table: <formatted table string>
        - company_count: <number of companies>
        - companies: <list of company details>
    """
    try:
        companies = list_companies_util(base_path=base_path)

        if not companies:
            return {
                "success": True,
                "summary_table": "No companies found in the database.",
                "company_count": 0,
                "companies": [],
            }

        # Gather data for each company
        company_summaries: List[Dict[str, Any]] = []

        for company in companies:
            flags_path = get_flags_path(company, base_path=base_path)

            company_data = {
                "name": company,
                "has_evaluation": flags_path.exists(),
                "synthesis_verdict": None,
                "gut_decision": None,
                "gut_confidence": None,
            }

            if flags_path.exists():
                try:
                    flags_data = read_yaml(flags_path)

                    # Get synthesis verdict
                    if "synthesis" in flags_data:
                        synthesis = flags_data["synthesis"]
                        company_data["synthesis_verdict"] = synthesis.get("mountain_worth_climbing")

                    # Get gut decision if available
                    if "gut_decision" in flags_data:
                        gut = flags_data["gut_decision"]
                        company_data["gut_decision"] = gut.get("mountain_worth_climbing")
                        company_data["gut_confidence"] = gut.get("confidence")

                except YAMLHandlerError:
                    pass

            company_summaries.append(company_data)

        # Format as table
        table_lines = []
        table_lines.append("# Company Evaluation Summary")
        table_lines.append("")
        table_lines.append(f"Total companies: {len(companies)}")
        table_lines.append("")

        # Table header
        table_lines.append("| Company | Synthesis | Gut Decision | Confidence |")
        table_lines.append("|---------|-----------|--------------|------------|")

        # Table rows
        for comp in sorted(company_summaries, key=lambda x: x["name"]):
            name = comp["name"]
            synthesis = comp["synthesis_verdict"] or "-"
            gut_decision = comp["gut_decision"] or "-"
            confidence = comp["gut_confidence"] or "-"

            table_lines.append(f"| {name} | {synthesis} | {gut_decision} | {confidence} |")

        return {
            "success": True,
            "summary_table": "\n".join(table_lines),
            "company_count": len(companies),
            "companies": company_summaries,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating evaluation summary: {str(e)}",
            "summary_table": "",
            "company_count": 0,
            "companies": [],
        }
