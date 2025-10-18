"""Path utilities for managing data directories and company folders."""

import re
from pathlib import Path
from typing import List, Optional


class PathsError(Exception):
    """Exception raised for path-related errors."""

    pass


def slugify_company_name(company_name: str) -> str:
    """Convert company name to filesystem-safe slug.

    Converts company names to lowercase slugs with hyphens, suitable for
    directory names. Removes special characters and collapses whitespace.

    Args:
        company_name: The display name of the company

    Returns:
        Slugified name suitable for filesystem use

    Example:
        >>> slugify_company_name("Toast, Inc.")
        'toast-inc'
        >>> slugify_company_name("Affirm Holdings Inc.")
        'affirm-holdings-inc'
        >>> slugify_company_name("Cato Networks")
        'cato-networks'
        >>> slugify_company_name("1Password")
        '1password'
        >>> slugify_company_name("Meta-Dublin")
        'meta-dublin'
    """
    # Convert to lowercase
    slug = company_name.lower()

    # Replace spaces and special characters with hyphens
    # Keep alphanumeric and hyphens, replace everything else
    slug = re.sub(r'[^a-z0-9-]+', '-', slug)

    # Collapse multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)

    # Strip leading/trailing hyphens
    slug = slug.strip('-')

    return slug


def get_data_dir(base_path: Optional[Path] = None) -> Path:
    """Get the data directory path.

    Args:
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Path to the data directory
    """
    if base_path is None:
        # Default to project root / data
        # Assumes we're in wctf_mcp/utils/paths.py, so go up 2 levels
        base_path = Path(__file__).parent.parent.parent

    return base_path / "data"


def get_company_dir(company_name: str, base_path: Optional[Path] = None) -> Path:
    """Get the directory path for a specific company.

    Company names are automatically slugified to create filesystem-safe
    directory names (lowercase, hyphens only).

    Args:
        company_name: Display name of the company (will be slugified)
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Path to the company directory (using slugified name)

    Example:
        >>> get_company_dir("Toast, Inc.")  # doctest: +SKIP
        PosixPath('.../data/toast-inc')
    """
    data_dir = get_data_dir(base_path)
    slug = slugify_company_name(company_name)
    return data_dir / slug


def ensure_company_dir(company_name: str, base_path: Optional[Path] = None) -> Path:
    """Ensure the company directory exists, creating it if necessary.

    Company names are automatically slugified for directory creation.

    Args:
        company_name: Display name of the company (will be slugified)
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Path to the company directory (using slugified name)

    Raises:
        PathsError: If directory creation fails
    """
    company_dir = get_company_dir(company_name, base_path)

    try:
        company_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise PathsError(f"Failed to create company directory {company_dir}: {e}")

    return company_dir


def get_facts_path(company_name: str, base_path: Optional[Path] = None) -> Path:
    """Get the path to the company.facts.yaml file for a company.

    Args:
        company_name: Name of the company
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Path to the company.facts.yaml file
    """
    company_dir = get_company_dir(company_name, base_path)
    return company_dir / "company.facts.yaml"


def get_flags_path(company_name: str, base_path: Optional[Path] = None) -> Path:
    """Get the path to the company.flags.yaml file for a company.

    Args:
        company_name: Name of the company
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Path to the company.flags.yaml file
    """
    company_dir = get_company_dir(company_name, base_path)
    return company_dir / "company.flags.yaml"


def get_insider_facts_path(company_name: str, base_path: Optional[Path] = None) -> Path:
    """Get the path to the company.insider.yaml file for a company.

    Args:
        company_name: Name of the company
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Path to the company.insider.yaml file
    """
    company_dir = get_company_dir(company_name, base_path)
    return company_dir / "company.insider.yaml"


def list_companies(base_path: Optional[Path] = None) -> List[str]:
    """List all companies that have directories in the data folder.

    Args:
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Sorted list of company names
    """
    data_dir = get_data_dir(base_path)

    if not data_dir.exists():
        return []

    companies = [
        item.name for item in data_dir.iterdir() if item.is_dir()
    ]

    return sorted(companies)
