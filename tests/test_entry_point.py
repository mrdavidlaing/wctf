"""Tests for the wctf-server script entry point."""

import subprocess
import sys
from pathlib import Path

import pytest


class TestEntryPoint:
    """Test the wctf-server script entry point."""

    def test_wctf_server_script_exists(self):
        """Test that wctf-server script is defined in pyproject.toml."""
        # Read pyproject.toml and verify script entry point is defined
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"

        assert pyproject_path.exists(), "pyproject.toml not found"

        content = pyproject_path.read_text()
        assert "[project.scripts]" in content, "No [project.scripts] section in pyproject.toml"
        assert 'wctf-server' in content, "wctf-server script not defined"
        assert 'wctf_mcp.server:main' in content, "wctf-server does not point to server:main"

    def test_main_function_exists(self):
        """Test that server.py has a main() function."""
        from wctf_mcp import server

        assert hasattr(server, 'main'), "server.py does not have a main() function"
        assert callable(server.main), "server.main is not callable"

    def test_main_function_is_async_compatible(self):
        """Test that main() function can be called (smoke test)."""
        # We don't actually run it (it would block), but we verify it's importable
        # and doesn't raise errors on import
        from wctf_mcp.server import main

        assert main is not None
        assert callable(main)

    def test_script_entry_point_callable_via_module(self):
        """Test that the script can be invoked via python -m."""
        # This just checks that the module structure is correct
        # We don't actually run it as it would block waiting for MCP input
        result = subprocess.run(
            [sys.executable, "-c", "from wctf_mcp.server import main; print('OK')"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        assert result.returncode == 0, f"Failed to import main: {result.stderr}"
        assert "OK" in result.stdout
