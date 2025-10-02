"""Path utilities for managing data directories and company folders."""

from pathlib import Path
from typing import List, Optional


class PathsError(Exception):
    """Exception raised for path-related errors."""

    pass


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

    Args:
        company_name: Name of the company
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Path to the company directory
    """
    data_dir = get_data_dir(base_path)
    return data_dir / company_name


def ensure_company_dir(company_name: str, base_path: Optional[Path] = None) -> Path:
    """Ensure the company directory exists, creating it if necessary.

    Args:
        company_name: Name of the company
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Path to the company directory

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
