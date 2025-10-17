"""Safe YAML read/write operations for WCTF MCP server."""

from pathlib import Path
from typing import Any, Dict, Union

import yaml


class YAMLHandlerError(Exception):
    """Exception raised for YAML handler errors."""

    pass


def read_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Read and parse a YAML file safely.

    Args:
        file_path: Path to the YAML file to read

    Returns:
        Dictionary containing the parsed YAML data

    Raises:
        YAMLHandlerError: If file doesn't exist or YAML is malformed
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise YAMLHandlerError(f"File does not exist: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            # safe_load returns None for empty files
            return data if data is not None else {}
    except yaml.YAMLError as e:
        raise YAMLHandlerError(f"Failed to parse YAML file {file_path}: {e}")
    except Exception as e:
        raise YAMLHandlerError(f"Error reading file {file_path}: {e}")


def write_yaml(file_path: Union[str, Path], data: Dict[str, Any]) -> None:
    """Write data to a YAML file safely.

    Args:
        file_path: Path to the YAML file to write
        data: Dictionary to write as YAML

    Raises:
        YAMLHandlerError: If writing fails
    """
    file_path = Path(file_path)

    # Create parent directories if they don't exist
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise YAMLHandlerError(f"Failed to create parent directories for {file_path}: {e}")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
    except Exception as e:
        raise YAMLHandlerError(f"Error writing to file {file_path}: {e}")
