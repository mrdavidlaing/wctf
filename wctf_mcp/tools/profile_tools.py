"""MCP tools for Energy Matrix profile management."""

from mcp import types

from wctf_core.operations.profile import get_profile, update_profile


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
