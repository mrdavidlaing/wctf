# Development Guide

## Running the Server

The server supports two transport modes:

### stdio (Default - Recommended for Development)

```bash
uv run wctf-server
```

**Benefits:**
- ✅ **Automatic "hot reload"** - code changes picked up on next tool call
- ✅ No server restart needed
- ✅ No connection state to break
- ✅ Simple debugging (logs to stderr)

**How it works:** Each MCP request spawns a fresh Python process, so code is always up-to-date.

**Claude Desktop config:**

*For native Linux/macOS* (`~/Library/Application Support/Claude/claude_desktop_config.json` or `~/.config/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "wctf": {
      "command": "uv",
      "args": ["run", "wctf-server"],
      "env": {
        "WCTF_DATA_DIR": "/path/to/wctf/data"
      }
    }
  }
}
```

*For WSL* (`C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "wctf": {
      "command": "wsl",
      "args": [
        "-d", "archlinux",
        "--cd", "/home/mrdavidlaing/arch-workspace/wctf",
        "uv", "run", "wctf-server"
      ],
      "env": {
        "WCTF_DATA_DIR": "/home/mrdavidlaing/arch-workspace/wctf/data"
      }
    }
  }
}
```

**Note for WSL:**
- Replace `"archlinux"` with your WSL distro name if different (check with `wsl -l` in PowerShell)
- The `--cd` flag changes to the project directory before running the command
- Use Linux paths inside the WSL environment
- Claude Desktop (Windows) will pipe stdio through the WSL boundary

### streamable-http (For HTTP-based connections)

```bash
WCTF_TRANSPORT=streamable-http uv run wctf-server
```

**Benefits:**
- ✅ Faster (persistent process, no startup overhead)
- ✅ Potentially discoverable

**Drawbacks:**
- ❌ Requires server restart for code changes
- ❌ Connection breaks may require Claude Desktop restart

**Use when:** You need HTTP transport or network-based access

## Making Changes

### With stdio (default):
1. **Edit code** - make your changes
2. **Save file**
3. **Next tool call in Claude Desktop** automatically picks up changes
4. No restart needed! 🎉

### With streamable-http:
1. **Edit code**
2. **Stop server** (Ctrl+C)
3. **Restart:** `WCTF_TRANSPORT=streamable-http uv run wctf-server`
4. If Claude Desktop hangs, restart it

## Testing Changes

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=wctf_mcp --cov-report=html
```

## Debugging

Server logs show:
- Tool calls being made
- Success/failure of operations
- File operations

Set `logging.basicConfig(level=logging.DEBUG)` in `server.py` for verbose output.
