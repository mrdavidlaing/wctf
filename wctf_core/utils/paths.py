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


def get_stage_dir(stage: int, base_path: Optional[Path] = None) -> Path:
    """Get the directory path for a specific stage.

    Args:
        stage: Stage number (1, 2, 3, etc.)
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Path to the stage directory (e.g., data/stage-1)
    """
    data_dir = get_data_dir(base_path)
    return data_dir / f"stage-{stage}"


def get_company_dir(
    company_name: str, stage: Optional[int] = None, base_path: Optional[Path] = None
) -> Path:
    """Get the directory path for a specific company.

    Company names are automatically slugified to create filesystem-safe
    directory names (lowercase, hyphens only).

    Args:
        company_name: Display name of the company (will be slugified)
        stage: Optional stage number. If provided, returns path in that stage.
               If not provided, searches for company across all stages.
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Path to the company directory (using slugified name)

    Raises:
        PathsError: If stage not provided and company not found in any stage

    Example:
        >>> get_company_dir("Toast, Inc.", stage=1)  # doctest: +SKIP
        PosixPath('.../data/stage-1/toast-inc')
    """
    slug = slugify_company_name(company_name)

    if stage is not None:
        # Return path in specified stage
        stage_dir = get_stage_dir(stage, base_path)
        return stage_dir / slug

    # Search for company across all stages
    found_stage, _ = find_company(company_name, base_path)
    if found_stage is None:
        raise PathsError(
            f"Company '{company_name}' not found in any stage. "
            f"Please specify stage parameter or ensure company exists."
        )

    stage_dir = get_stage_dir(found_stage, base_path)
    return stage_dir / slug


def find_company(
    company_name: str, base_path: Optional[Path] = None
) -> tuple[Optional[int], Optional[Path]]:
    """Find a company across all stages.

    Args:
        company_name: Name of the company to find
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Tuple of (stage_number, company_dir_path) if found, (None, None) if not found

    Example:
        >>> find_company("Toast, Inc.")  # doctest: +SKIP
        (1, PosixPath('.../data/stage-1/toast-inc'))
    """
    slug = slugify_company_name(company_name)
    data_dir = get_data_dir(base_path)

    if not data_dir.exists():
        return (None, None)

    # Check each stage subdirectory
    for stage_dir in sorted(data_dir.iterdir()):
        if not stage_dir.is_dir() or not stage_dir.name.startswith("stage-"):
            continue

        # Extract stage number from directory name (e.g., "stage-1" -> 1)
        try:
            stage_num = int(stage_dir.name.split("-")[1])
        except (IndexError, ValueError):
            continue

        company_dir = stage_dir / slug
        if company_dir.exists() and company_dir.is_dir():
            return (stage_num, company_dir)

    return (None, None)


def ensure_company_dir(
    company_name: str, stage: int = 1, base_path: Optional[Path] = None
) -> Path:
    """Ensure the company directory exists, creating it if necessary.

    Company names are automatically slugified for directory creation.

    Args:
        company_name: Display name of the company (will be slugified)
        stage: Stage number (defaults to 1)
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Path to the company directory (using slugified name)

    Raises:
        PathsError: If directory creation fails
    """
    company_dir = get_company_dir(company_name, stage=stage, base_path=base_path)

    try:
        company_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise PathsError(f"Failed to create company directory {company_dir}: {e}")

    return company_dir


def get_facts_path(
    company_name: str, stage: Optional[int] = None, base_path: Optional[Path] = None
) -> Path:
    """Get the path to the company.facts.yaml file for a company.

    Args:
        company_name: Name of the company
        stage: Optional stage number. If not provided, searches across stages.
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Path to the company.facts.yaml file

    Raises:
        PathsError: If stage not provided and company not found in any stage
    """
    company_dir = get_company_dir(company_name, stage=stage, base_path=base_path)
    return company_dir / "company.facts.yaml"


def get_flags_path(
    company_name: str, stage: Optional[int] = None, base_path: Optional[Path] = None
) -> Path:
    """Get the path to the company.flags.yaml file for a company.

    Args:
        company_name: Name of the company
        stage: Optional stage number. If not provided, searches across stages.
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Path to the company.flags.yaml file

    Raises:
        PathsError: If stage not provided and company not found in any stage
    """
    company_dir = get_company_dir(company_name, stage=stage, base_path=base_path)
    return company_dir / "company.flags.yaml"


def get_insider_facts_path(
    company_name: str, stage: Optional[int] = None, base_path: Optional[Path] = None
) -> Path:
    """Get the path to the company.insider.yaml file for a company.

    Args:
        company_name: Name of the company
        stage: Optional stage number. If not provided, searches across stages.
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Path to the company.insider.yaml file

    Raises:
        PathsError: If stage not provided and company not found in any stage
    """
    company_dir = get_company_dir(company_name, stage=stage, base_path=base_path)
    return company_dir / "company.insider.yaml"


def list_companies(
    stage: Optional[int] = None, base_path: Optional[Path] = None
) -> List[str]:
    """List all companies that have directories in the data folder.

    Args:
        stage: Optional stage number. If provided, lists companies in that stage only.
               If not provided, lists companies across all stages.
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        Sorted list of company directory names (slugs)
    """
    data_dir = get_data_dir(base_path)

    if not data_dir.exists():
        return []

    companies = []

    if stage is not None:
        # List companies in specific stage
        stage_dir = get_stage_dir(stage, base_path)
        if stage_dir.exists():
            companies = [item.name for item in stage_dir.iterdir() if item.is_dir()]
    else:
        # List companies across all stages
        for stage_dir in sorted(data_dir.iterdir()):
            if not stage_dir.is_dir() or not stage_dir.name.startswith("stage-"):
                continue

            for company_dir in stage_dir.iterdir():
                if company_dir.is_dir() and company_dir.name not in companies:
                    companies.append(company_dir.name)

    return sorted(companies)


def list_all_companies_by_stage(
    base_path: Optional[Path] = None,
) -> List[tuple[int, str]]:
    """List all companies with their stage information.

    Args:
        base_path: Optional base path. If not provided, uses project root.

    Returns:
        List of (stage, company_slug) tuples, sorted by stage then company name

    Example:
        >>> list_all_companies_by_stage()  # doctest: +SKIP
        [(1, 'company-a'), (1, 'company-b'), (2, 'company-c')]
    """
    data_dir = get_data_dir(base_path)

    if not data_dir.exists():
        return []

    companies = []

    for stage_dir in sorted(data_dir.iterdir()):
        if not stage_dir.is_dir() or not stage_dir.name.startswith("stage-"):
            continue

        try:
            stage_num = int(stage_dir.name.split("-")[1])
        except (IndexError, ValueError):
            continue

        for company_dir in sorted(stage_dir.iterdir()):
            if company_dir.is_dir():
                companies.append((stage_num, company_dir.name))

    return companies
