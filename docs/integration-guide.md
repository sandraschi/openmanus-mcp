# openmanus-mcp Integration Guide

## MCP Client Configuration

### Claude Desktop

```json
{
  "mcpServers": {
    "openmanus-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "openmanus_mcp"],
      "env": {
        "OPENMANUS_MCP_API_KEY": "your-secret-key"
      }
    }
  }
}
```

### Cursor IDE

In Cursor settings → MCP Servers:

```json
{
  "openmanus-mcp": {
    "command": "uv",
    "args": ["run", "python", "-m", "openmanus_mcp"]
  }
}
```

### Windsurf

In `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "openmanus-mcp": {
    "command": "uv",
    "args": ["run", "python", "-m", "openmanus_mcp"]
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENMANUS_ROOT` | `../OpenManus` | Path to OpenManus clone |
| `OPENMANUS_MCP_API_KEY` | *(auto-generated)* | Bearer token for REST API auth |
| `OPENMANUS_MCP_KEY_FILE` | `{repo}/.api_key` | Where auto-generated key is written |
| `LOCAL_COMPUTER_NO_PROMPT` | *(unset)* | Set to disable computer use confirmation gate |

## Security Workflows

### Run an agent with computer use

```python
# The agent now has these tools:
# - bash: shell commands (denylisted)
# - computer: mouse/keyboard/screenshot (confirmation gated)
# - python_execute: run Python (restricted)
# - browser_use: browse the web
# - str_replace_editor: edit files

await agent.run("Find the latest invoice PDF, rename it, and email it")
```

### API Authentication

```powershell
# Generate a key
$env:OPENMANUS_MCP_API_KEY = "sk-" + (openssl rand -hex 32)

# Or let it auto-generate (written to .api_key)
uv run python -m openmanus_mcp.run_api
# Output: WARNING: No OPENMANUS_MCP_API_KEY set. Auto-generated key: abc123...
```
