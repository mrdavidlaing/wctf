"""Role search operations."""

import yaml
from typing import Dict, Optional
from pathlib import Path

from wctf_core.models.orgmap import CompanyRoles
from wctf_core.utils.yaml_handler import write_yaml, read_yaml
from wctf_core.utils.paths import get_roles_path


def save_roles(
    company_name: str, roles_yaml: str, base_path: Optional[Path] = None
) -> Dict:
    """Validate and save role search results.

    Args:
        company_name: Company name
        roles_yaml: YAML string with roles
        base_path: Optional custom data directory

    Returns:
        Dict with success status and saved roles

    Example:
        >>> result = save_roles("Apple", roles_yaml)  # doctest: +SKIP
        >>> result['success']
        True
    """
    try:
        # Parse and validate with Pydantic
        roles_data = yaml.safe_load(roles_yaml)
        roles = CompanyRoles(**roles_data)

        # Save to file
        roles_path = get_roles_path(company_name, base_path)
        # Ensure parent directory exists
        roles_path.parent.mkdir(parents=True, exist_ok=True)
        write_yaml(roles_path, roles.model_dump())

        return {"success": True, "roles": roles.model_dump(), "path": str(roles_path)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_roles(company_name: str, base_path: Optional[Path] = None) -> Dict:
    """Read existing roles.

    Args:
        company_name: Company name
        base_path: Optional custom data directory

    Returns:
        Dict with roles data or error

    Example:
        >>> result = get_roles("Apple")  # doctest: +SKIP
        >>> result['roles']['total_roles']
        15
    """
    try:
        roles_path = get_roles_path(company_name, base_path)
        if not roles_path.exists():
            return {"success": False, "error": f"No roles found for {company_name}"}

        roles_data = read_yaml(roles_path)
        roles = CompanyRoles(**roles_data)

        return {"success": True, "roles": roles.model_dump()}
    except Exception as e:
        return {"success": False, "error": str(e)}
