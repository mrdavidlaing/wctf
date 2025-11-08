"""Tests for profile MCP tools."""

from datetime import date
from pathlib import Path
import pytest
import yaml

from wctf_mcp.tools.profile_tools import (
    get_profile_tool,
    update_profile_tool,
)


@pytest.fixture
def temp_wctf_dir(tmp_path):
    """Create a temporary WCTF directory structure."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return tmp_path


@pytest.mark.asyncio
async def test_get_profile_tool_returns_profile(temp_wctf_dir, monkeypatch):
    """Test get_profile_tool returns formatted profile."""
    # Setup
    profile_path = temp_wctf_dir / "data" / "profile.yaml"
    profile_data = {
        "profile_version": "1.0",
        "last_updated": "2025-01-08",
        "energy_drains": {},
        "energy_generators": {},
        "core_strengths": [],
        "growth_areas": [],
    }

    with open(profile_path, "w") as f:
        yaml.dump(profile_data, f)

    monkeypatch.setenv("WCTF_ROOT", str(temp_wctf_dir))

    # Execute
    result = await get_profile_tool()

    # Verify
    assert len(result) == 1
    assert result[0].type == "text"
    assert "1.0" in result[0].text


@pytest.mark.asyncio
async def test_update_profile_tool_increments_version(temp_wctf_dir, monkeypatch):
    """Test update_profile_tool increments version."""
    # Setup
    profile_path = temp_wctf_dir / "data" / "profile.yaml"
    profile_data = {
        "profile_version": "1.0",
        "last_updated": "2025-01-08",
        "energy_drains": {},
        "energy_generators": {},
        "core_strengths": [],
        "growth_areas": [],
    }

    with open(profile_path, "w") as f:
        yaml.dump(profile_data, f)

    monkeypatch.setenv("WCTF_ROOT", str(temp_wctf_dir))

    # Execute
    updated_yaml = yaml.dump(profile_data)
    result = await update_profile_tool(updated_yaml)

    # Verify
    assert len(result) == 1
    assert "1.1" in result[0].text


@pytest.mark.asyncio
async def test_get_energy_summary_tool_returns_analysis(temp_wctf_dir, monkeypatch):
    """Test get_energy_summary_tool returns just the energy analysis."""
    # Setup company with energy analysis
    company_dir = temp_wctf_dir / "data" / "stage-1" / "testcorp"
    company_dir.mkdir(parents=True)

    flags_data = {
        "company": "TestCorp",
        "evaluation_date": "2025-01-08",
        "synthesis": {
            "energy_matrix_analysis": {
                "energy_sustainability": "MEDIUM",
                "predicted_daily_distribution": {
                    "mutual_green_flags": {"percentage": 50, "tasks_count": 3},
                },
            },
        },
    }

    with open(company_dir / "company.flags.yaml", "w") as f:
        yaml.dump(flags_data, f)

    monkeypatch.setenv("WCTF_ROOT", str(temp_wctf_dir))

    # Execute
    from wctf_mcp.tools.profile_tools import get_energy_summary_tool
    result = await get_energy_summary_tool("TestCorp")

    # Verify
    assert len(result) == 1
    assert "MEDIUM" in result[0].text
    assert "50" in result[0].text  # Should show percentage
