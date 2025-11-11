"""Organizational mapping operations."""

import yaml
from typing import Dict, Optional
from pathlib import Path

from wctf_core.models.orgmap import CompanyOrgMap
from wctf_core.utils.yaml_handler import write_yaml, read_yaml
from wctf_core.utils.paths import get_orgmap_path, ensure_company_dir


def save_orgmap(company_name: str, orgmap_yaml: str, base_path: Optional[Path] = None) -> Dict:
    """Validate and save organizational map.

    Args:
        company_name: Company name
        orgmap_yaml: YAML string with org structure
        base_path: Optional custom data directory

    Returns:
        Dict with success status and saved orgmap

    Example:
        >>> result = save_orgmap("Chronosphere", orgmap_yaml)  # doctest: +SKIP
        >>> result['success']
        True
    """
    try:
        # Parse and validate with Pydantic
        orgmap_data = yaml.safe_load(orgmap_yaml)
        orgmap = CompanyOrgMap(**orgmap_data)

        # Save to file
        ensure_company_dir(company_name, base_path)
        orgmap_path = get_orgmap_path(company_name, base_path)
        write_yaml(orgmap_path, orgmap.model_dump())

        return {
            'success': True,
            'orgmap': orgmap.model_dump(),
            'path': str(orgmap_path)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_orgmap(company_name: str, base_path: Optional[Path] = None) -> Dict:
    """Read existing organizational map.

    Args:
        company_name: Company name
        base_path: Optional custom data directory

    Returns:
        Dict with orgmap data or error

    Example:
        >>> result = get_orgmap("Chronosphere")  # doctest: +SKIP
        >>> len(result['orgmap']['peaks'])
        3
    """
    try:
        orgmap_path = get_orgmap_path(company_name, base_path)
        if not orgmap_path.exists():
            return {
                'success': False,
                'error': f'No orgmap found for {company_name}'
            }

        orgmap_data = read_yaml(orgmap_path)
        orgmap = CompanyOrgMap(**orgmap_data)

        return {
            'success': True,
            'orgmap': orgmap.model_dump()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
