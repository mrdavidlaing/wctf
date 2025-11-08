"""Operations for profile management."""

import os
from datetime import date
from pathlib import Path
from typing import Dict, Any

import yaml

from wctf_core.models.profile import Profile


def _get_profile_path() -> Path:
    """Get the path to profile.yaml."""
    wctf_root = os.getenv("WCTF_ROOT", os.getcwd())
    return Path(wctf_root) / "data" / "profile.yaml"


def _success_response(title: str, content: str) -> str:
    """Format a success response.

    Args:
        title: Success title/header
        content: Success content/details

    Returns:
        Formatted success message
    """
    return f"{title}\n\n{content}"


def _error_response(message: str) -> str:
    """Format an error response.

    Args:
        message: Error message

    Returns:
        Formatted error message
    """
    return f"Error: {message}"


def get_profile() -> str:
    """Get current profile.yaml for reference during flag extraction.

    Returns the full profile including energy drains, generators, strengths,
    and organizational coherence needs.

    Returns:
        Formatted profile YAML as string, or error message if not found.
    """
    profile_path = _get_profile_path()

    if not profile_path.exists():
        return _error_response(
            f"Profile not found at {profile_path}. "
            "Create data/profile.yaml to use Energy Matrix features."
        )

    try:
        with open(profile_path) as f:
            profile_data = yaml.safe_load(f)

        # Validate with Pydantic model
        profile = Profile(**profile_data)

        # Return as formatted YAML
        return _success_response(
            f"Profile v{profile.profile_version} (updated {profile.last_updated})",
            yaml.dump(profile_data, default_flow_style=False, sort_keys=False)
        )

    except Exception as e:
        return _error_response(f"Error loading profile: {e}")


def update_profile(updated_profile_yaml: str) -> str:
    """Update profile.yaml with new self-knowledge.

    Args:
        updated_profile_yaml: Complete profile YAML content

    Actions:
        - Increments profile_version (e.g., "1.0" -> "1.1")
        - Updates last_updated timestamp
        - Writes to data/profile.yaml

    Returns:
        Success message with new version, or error message.
    """
    profile_path = _get_profile_path()

    try:
        # Parse the updated profile
        updated_data = yaml.safe_load(updated_profile_yaml)

        # Validate with Pydantic
        profile = Profile(**updated_data)

        # Increment version (e.g., "1.0" -> "1.1")
        current_version = profile.profile_version
        if "." in current_version:
            major, minor = current_version.split(".")
            new_version = f"{major}.{int(minor) + 1}"
        else:
            new_version = f"{current_version}.1"

        # Update metadata
        updated_data["profile_version"] = new_version
        updated_data["last_updated"] = str(date.today())

        # Ensure parent directory exists
        profile_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(profile_path, "w") as f:
            yaml.dump(updated_data, f, default_flow_style=False, sort_keys=False)

        return _success_response(
            f"Profile updated to v{new_version}",
            f"Saved to {profile_path}"
        )

    except Exception as e:
        return _error_response(f"Error updating profile: {e}")
