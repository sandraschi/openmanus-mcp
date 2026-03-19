"""Stdio MCP entrypoint (Cursor, Claude Desktop, etc.)."""

from openmanus_mcp.server import mcp


def main() -> None:
    """Run MCP over stdio — stdout is reserved for JSON-RPC."""
    mcp.run()


if __name__ == "__main__":
    main()
