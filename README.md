# WCTF MCP Server

A Model Context Protocol (MCP) server for managing **Worth Climbing Together Framework (WCTF) v3.1** company research data. This server provides structured access to company facts and evaluation flags for engineers researching potential employers.

## Overview

The WCTF MCP Server helps you:
- Track factual research about companies (financial health, market position, organizational stability, technical culture)
- Maintain evaluation flags (green flags, red flags, missing data)
- Query and analyze company data through Claude Desktop or other MCP clients
- **NEW in v3.1**: Evaluate team coordination styles and realignment ability (alpine/expedition/established route/orienteering/trail crew archetypes)

For complete framework details, see [WCTF_FRAMEWORK.md](WCTF_FRAMEWORK.md).

## WSL/Windows Architecture

This MCP server is designed to run on **Windows Subsystem for Linux (WSL)** and be called from **Claude Desktop on Windows**. This architecture provides:

- **Server runs in WSL**: Access to native Linux tools, better Python environment management with `uv`
- **Claude Desktop on Windows**: Native Windows application with full MCP support
- **Cross-platform communication**: Claude Desktop invokes the WSL command to run the server
- **Shared data access**: Data directory accessible from both Windows and WSL

### How It Works

1. Claude Desktop (Windows) starts the MCP server by running `wsl` command
2. WSL executes `uv run wctf-server` in the project directory
3. Server communicates with Claude Desktop via stdio (standard input/output)
4. Data files are stored in WSL filesystem for best performance

## Installation on WSL

### Prerequisites

- Windows 11 or Windows 10 with WSL2 enabled
- WSL distribution installed (Arch Linux, Ubuntu, or other)
- `uv` package manager installed in WSL

### Install uv (if not already installed)

```bash
# In WSL terminal
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install WCTF MCP Server

```bash
# Clone or navigate to the project directory
cd /home/mrdavidlaing/arch-workspace/wctf

# Install dependencies (including the wctf-server script)
uv sync --all-extras
```

### Verify Installation

```bash
# Test that the entry point is installed
uv run wctf-server --help 2>&1 | head -5

# Should start the MCP server (press Ctrl+C to exit)
# If it waits for input, the server is running correctly
```

## Claude Desktop Configuration (Windows)

### Configuration File Location

Claude Desktop configuration is stored at:
```
C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json
```

### Configuration JSON

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "wctf": {
      "command": "wsl",
      "args": [
        "-d",
        "archlinux",
        "bash",
        "-c",
        "cd /home/mrdavidlaing/arch-workspace/wctf && uv run wctf-server"
      ],
      "env": {
        "WCTF_DATA_DIR": "/home/mrdavidlaing/arch-workspace/wctf/data"
      }
    }
  }
}
```

**Important**: Replace `archlinux` with your WSL distribution name. To find it, run `wsl -l -v` from Windows Command Prompt.

### Path Handling Notes

**Important**: Use WSL paths in the configuration, not Windows paths.

- Correct: `/home/mrdavidlaing/arch-workspace/wctf`
- Incorrect: `C:\Users\...\wctf` or `\\wsl$\Ubuntu\home\mrdavidlaing\...`

When Claude Desktop runs `wsl` command, it executes in the WSL environment where WSL paths are native.

**Converting Paths**:
- Windows to WSL: `C:\Users\me\project` becomes `/mnt/c/Users/me/project`
- WSL to Windows: `/home/me/project` becomes `\\wsl$\Ubuntu\home\me\project`

For this project, data is stored in `/home/mrdavidlaing/arch-workspace/wctf/` which is in the WSL home directory.

## HTTP Server Mode (Alternative)

The WCTF MCP server can also run as a standalone HTTP server using Streamable HTTP transport. This mode is useful for:
- Local development and testing
- Running the server independently from Claude Desktop
- Accessing from multiple clients
- Network-based deployments

### Running the HTTP Server

Start the server:
```bash
cd /home/mrdavidlaing/arch-workspace/wctf
uv run wctf-server
```

The server will start on `http://127.0.0.1:8000/mcp`

### Claude Desktop Configuration for HTTP

For localhost HTTP servers, you need to use `npx mcp-remote` as a bridge. Claude Desktop's native "Add Custom Connector" UI requires HTTPS and is designed for remote deployments.

**Configuration File Location:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Add to your `claude_desktop_config.json`:**

```json
{
  "mcpServers": {
    "wctf": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:8000/mcp"
      ]
    }
  }
}
```

**What this does:**
- `npx -y mcp-remote` - Runs the mcp-remote package (auto-installs if needed)
- The package acts as a bridge between Claude Desktop (stdio) and your HTTP server
- Works with localhost HTTP URLs (no HTTPS certificate needed)

**After updating the config:**
1. Save the file
2. Completely restart Claude Desktop (quit and reopen)
3. The WCTF server will appear in your available tools

See `claude_desktop_config.example.json` for a complete example.

### HTTP vs stdio

**stdio mode (default):**
- Claude Desktop starts/stops server automatically
- Better for single-user local setup
- Simpler configuration

**HTTP mode:**
- Server runs independently
- Can serve multiple clients
- Better for development/debugging
- Allows server inspection and monitoring

## Testing the Connection

### 1. Test Server Manually

In WSL terminal:
```bash
cd /home/mrdavidlaing/arch-workspace/wctf
uv run wctf-server
```

The server should start and wait for input. Press Ctrl+C to exit.

### 2. Test from Claude Desktop

1. Save the configuration to `claude_desktop_config.json`
2. Restart Claude Desktop completely (not just close window)
3. Open Claude Desktop and check MCP connection status
4. Try asking Claude: "List the companies in the WCTF database"

### 3. Verify Tools Are Available

In Claude Desktop, the following tools should be available:
- `list_companies` - List all companies with research data
- `get_company_facts` - Get research facts for a specific company
- `get_company_flags` - Get evaluation flags for a specific company

## Troubleshooting

### Server Won't Start

**Problem**: Claude Desktop cannot connect to the MCP server

**Solutions**:
1. Verify WSL is running: Open WSL terminal and run `uname -a`
2. Test server manually in WSL: `cd /home/mrdavidlaing/arch-workspace/wctf && uv run wctf-server`
3. Check that `uv` is in WSL PATH: `which uv` (should show path like `/home/mrdavidlaing/.local/bin/uv`)
4. Verify project path is correct in `claude_desktop_config.json`

### Permission Denied

**Problem**: Cannot access files or directories

**Solutions**:
1. Check directory permissions: `ls -la /home/mrdavidlaing/arch-workspace/wctf`
2. Verify data directory exists: `ls -la /home/mrdavidlaing/arch-workspace/wctf/data`
3. Fix permissions if needed: `chmod -R u+rw /home/mrdavidlaing/arch-workspace/wctf`

### WCTF_DATA_DIR Not Set

**Problem**: Server cannot find data files

**Solutions**:
1. Verify `env` section in `claude_desktop_config.json` has `WCTF_DATA_DIR`
2. Use absolute WSL path, not relative path
3. Check path exists: In WSL run `ls -la $WCTF_DATA_DIR`

### UV Command Not Found

**Problem**: `/bin/bash: line 1: /usr/sbin/uv: No such file or directory` or `wsl: uv: command not found`

**Solutions**:
1. Verify you're using the correct WSL distribution with `-d` flag (e.g., `-d archlinux`)
2. Install uv in WSL: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. Restart WSL terminal to refresh PATH
4. Verify installation: `which uv`

**Note**: The `-d archlinux` flag is critical - WSL defaults to a different distribution if not specified, which may not have `uv` installed or may not have your project files.

### Server Starts But No Tools Available

**Problem**: MCP connection works but tools do not appear

**Solutions**:
1. Check server logs (Claude Desktop may show MCP errors)
2. Verify dependencies installed: `cd /home/mrdavidlaing/arch-workspace/wctf && uv sync --all-extras`
3. Test tool listing: Server should register 3 tools on startup
4. Restart Claude Desktop completely

### Path Issues with wsl$

**Problem**: Using `\\wsl$\...` paths in configuration

**Solutions**:
1. Do not use Windows UNC paths for WSL in config
2. Use native WSL paths: `/home/mrdavidlaing/arch-workspace/wctf` not `\\wsl$\Ubuntu\home\mrdavidlaing\...`
3. The `wsl` command already handles path translation

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=wctf_mcp --cov-report=html

# Run specific test file
uv run pytest tests/test_entry_point.py
```

### Project Structure

```
.
   wctf_mcp/              # Main package
      server.py          # MCP server implementation
      models.py          # Pydantic data models
      tools/             # MCP tool implementations
      utils/             # Utilities (YAML, paths)
   tests/                 # Test suite
   data/                  # Company research data
      <company>/
          company.facts.yaml
          company.flags.yaml
   pyproject.toml         # Project configuration
   README.md              # This file
```

## Usage

Once configured in Claude Desktop, you can interact with company research data:

**List all companies:**
```
List the companies in the WCTF database
```

**Get company facts:**
```
Show me the research facts for 1Password
```

**Get evaluation flags:**
```
What are the evaluation flags for Anthropic?
```

## Data Schema

### company.facts.yaml

Research facts organized by category:
- `financial_health` - Revenue, funding, profitability data
- `market_position` - Market share, competition, growth
- `organizational_stability` - Leadership, turnover, structure
- `technical_culture` - Engineering practices, tech stack, culture

### company.flags.yaml

Evaluation flags for decision making:
- `senior_engineer_alignment` - Fit assessment for senior engineers
- `green_flags` - Positive indicators (critical matches, strong positives)
- `red_flags` - Concerns (dealbreakers, concerning items)
- `missing_critical_data` - Information gaps to investigate
- `synthesis` - Overall evaluation and recommendation

## Changelog

### Version 4.0 - Energy Matrix Integration

**Released:** 2025-01-08

#### New Features

- **Energy Matrix Integration:** Evaluates whether daily work will energize or drain you
- **Profile Storage:** Personal profile in `data/profile.yaml` with energy drains, generators, and strengths
- **Task Implications:** Each flag now includes tasks you'll do with 20+ characteristics
- **Auto-Quadrant Calculation:** System automatically calculates which quadrant each task falls into
- **Sustainability Thresholds:** Checks if role meets ≥60% mutual, ≤20% burnout requirements
- **Energy Synthesis:** Aggregates task distribution and generates accept/reject signals

#### New MCP Tools

- `get_profile` - Get current profile for reference
- `update_profile` - Update profile with version increment
- `get_energy_summary` - Quick energy analysis view

#### Breaking Changes

- `MountainFlags` model now includes `profile_version_used` field
- `Flag` model now includes `task_implications` field
- Synthesis section now includes `energy_matrix_analysis`

#### Migration Guide

Existing flags files will continue to work. To use Energy Matrix features:

1. Create `data/profile.yaml` (see design doc for template)
2. Add `profile_version_used: "1.0"` to new flags files
3. Include `task_implications` with characteristics for each flag
4. System will auto-calculate quadrants and synthesis

#### What's Next (v4.1)

- Tune algorithm thresholds based on real evaluations
- Add organizational coherence pattern detection
- Support for re-evaluating companies with updated profile
- Calibration tools for time estimate accuracy

## Contributing

To add new company data:

1. Create company directory: `mkdir -p data/company-name`
2. Create facts file: `data/company-name/company.facts.yaml`
3. Create flags file: `data/company-name/company.flags.yaml`
4. Follow schema in `wctf_mcp/models.py`

## License

[Your license here]

## Support

For issues or questions:
- Check troubleshooting section above
- Review MCP server logs in Claude Desktop
- Test server manually in WSL first
- Verify configuration paths and permissions
