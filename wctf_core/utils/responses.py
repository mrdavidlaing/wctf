"""Standard response formats for WCTF operations.

This module provides consistent response structures across all save operations
in the WCTF SDK, making it easier to write predictable scripts.
"""

from pathlib import Path
from typing import Any, Dict, Optional

# Import slugify for company slug generation
from wctf_core.utils.paths import slugify_company_name


def success_response(
    company_name: str,
    file_path: Path,
    items_saved: int,
    message: str,
    operation: str = "updated",
) -> Dict[str, Any]:
    """Create a standardized success response.

    Args:
        company_name: Display name of the company (e.g., "Toast, Inc.")
        file_path: Path to the file that was saved
        items_saved: Number of items saved (facts, flags, etc.)
        message: Human-readable success message
        operation: Type of operation - "created", "updated", or "merged"

    Returns:
        Dictionary with standard success fields including both company_name
        (display name) and company_slug (normalized filesystem name)

    Example:
        >>> from pathlib import Path
        >>> response = success_response(
        ...     company_name="Toast, Inc.",
        ...     file_path=Path("/data/toast-inc/company.facts.yaml"),
        ...     items_saved=42,
        ...     message="Saved 42 facts for Toast, Inc.",
        ...     operation="updated"
        ... )
        >>> response['success']
        True
        >>> response['company_name']
        'Toast, Inc.'
        >>> response['company_slug']
        'toast-inc'
        >>> response['items_saved']
        42
    """
    return {
        "success": True,
        "message": message,
        "company_name": company_name,
        "company_slug": slugify_company_name(company_name),
        "file_path": str(file_path.absolute()),
        "items_saved": items_saved,
        "operation": operation,
    }


def error_response(
    error: str,
    message: Optional[str] = None,
    company_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standardized error response.

    Args:
        error: Technical error details
        message: Optional human-readable error message (defaults to error if not provided)
        company_name: Optional company display name for context

    Returns:
        Dictionary with standard error fields including both company_name
        and company_slug when company_name is provided

    Example:
        >>> response = error_response(
        ...     error="ValueError: Invalid YAML format",
        ...     message="Failed to parse YAML content",
        ...     company_name="Toast, Inc."
        ... )
        >>> response['success']
        False
        >>> response['message']
        'Failed to parse YAML content'
        >>> response['company_name']
        'Toast, Inc.'
        >>> response['company_slug']
        'toast-inc'
    """
    result = {
        "success": False,
        "message": message or error,  # Use error as message if no message provided
        "error": error,
    }
    if company_name:
        result["company_name"] = company_name
        result["company_slug"] = slugify_company_name(company_name)
    return result
