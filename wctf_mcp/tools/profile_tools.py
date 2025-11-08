"""MCP tools for Energy Matrix profile management."""

import yaml
from pathlib import Path
import os

from mcp import types

from wctf_core.operations.profile import get_profile, update_profile
from wctf_core.utils.paths import get_flags_path


async def get_profile_tool() -> list[types.TextContent]:
    """Get current profile.yaml for reference during flag extraction.

    Returns the full profile including energy drains, generators, strengths,
    and organizational coherence needs.

    Returns:
        List containing single TextContent with profile YAML.
    """
    result = get_profile()
    return [types.TextContent(type="text", text=result)]


async def update_profile_tool(updated_profile_yaml: str) -> list[types.TextContent]:
    """Update profile.yaml with new self-knowledge.

    Args:
        updated_profile_yaml: Complete profile YAML content

    Actions:
        - Increments profile_version (e.g., "1.0" -> "1.1")
        - Updates last_updated timestamp
        - Writes to data/profile.yaml

    Returns:
        List containing single TextContent with success/error message.
    """
    result = update_profile(updated_profile_yaml)
    return [types.TextContent(type="text", text=result)]


async def get_energy_summary_tool(company_name: str) -> list[types.TextContent]:
    """Get just the energy_matrix_analysis from synthesis.

    Quick view of energy distribution without full flags.

    Args:
        company_name: Company to analyze

    Returns:
        List containing single TextContent with energy analysis.
    """
    try:
        # Get base_path from WCTF_ROOT environment variable
        wctf_root = os.getenv("WCTF_ROOT")
        base_path = Path(wctf_root) if wctf_root else None

        flags_path = get_flags_path(company_name, base_path=base_path)

        if not flags_path.exists():
            error_msg = f"ERROR: No flags found for {company_name}\n\nRun flag extraction first"
            return [types.TextContent(type="text", text=error_msg)]

        with open(flags_path) as f:
            flags_data = yaml.safe_load(f)

        synthesis = flags_data.get("synthesis", {})
        energy_analysis = synthesis.get("energy_matrix_analysis")

        if not energy_analysis:
            error_msg = f"ERROR: No Energy Matrix analysis for {company_name}\n\nFlags may not have profile_version_used set"
            return [types.TextContent(type="text", text=error_msg)]

        # Format energy analysis
        result = f"Energy Matrix Analysis for {company_name}\n\n"
        result += yaml.dump({"energy_matrix_analysis": energy_analysis}, default_flow_style=False)

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        error_msg = f"ERROR: Error getting energy summary: {e}"
        return [types.TextContent(type="text", text=error_msg)]
