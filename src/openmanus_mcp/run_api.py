"""Run FastAPI with uvicorn (webapp backend)."""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    host = os.environ.get("OPENMANUS_MCP_API_HOST", "127.0.0.1")
    port = int(os.environ.get("OPENMANUS_MCP_API_PORT", "10768"))
    uvicorn.run(
        "openmanus_mcp.api.app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
