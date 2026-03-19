---
name: mcp-builder
description: Scaffold and harden a FastMCP 3.1 MCP server with portmanteau tools, REST mirror, and docs
---

# MCP builder skill

Use when the user asks to create or refactor an MCP server.

## Checklist

1. **Stack**: Python 3.12+, FastMCP 3.1+, `pyproject.toml`, `ruff`, optional `pytest`.
2. **Tools**: Prefer portmanteau tools with an `operation` parameter over dozens of thin wrappers.
3. **Returns**: Structured dicts with `success`, `message` or `error`, and actionable fields.
4. **Docs**: README install, env vars, and one architecture note; link central docs patterns if applicable.
5. **Safety**: No silent destructive defaults; validate paths; Windows vs POSIX notes in scripts.
6. **MCPB** (optional): `mcpb.json` + packaging standards if shipping to a marketplace.

## Snippet — tool skeleton

```python
from fastmcp import FastMCP

mcp = FastMCP("example")


@mcp.tool()
async def example_ops(operation: str, payload: str = "") -> dict:
    """EXAMPLE_OPS — Portmanteau surface.

    Args:
        operation: Sub-command name.
        payload: JSON or plain text parameter bag.

    Returns:
        Rich response dict.
    """
    return {"success": True, "operation": operation, "echo": payload}
```

## Anti-patterns

- Duplicating the same logic in MCP tool and HTTP route without a shared core module.
- Returning unstructured prose-only replies for machine clients.
- Hard-coded ports outside your org’s registered range (see central WEBAPP_PORTS).
