"""FastAPI substrate for web_sota (health + OpenManus install probe)."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from openmanus_mcp import __version__
from openmanus_mcp.openmanus_detect import describe_openmanus
from openmanus_mcp.settings import get_settings

app = FastAPI(
    title="openmanus-mcp API",
    version=__version__,
    description="REST bridge for SOTA webapp; MCP runs via stdio separately.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:10769",
        "http://localhost:10769",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health() -> dict[str, Any]:
    return {"ok": True, "service": "openmanus-mcp", "version": __version__}


@app.get("/api/v1/status")
async def status() -> dict[str, Any]:
    settings = get_settings()
    info = describe_openmanus(settings.openmanus_root)
    return {
        "version": __version__,
        "openmanus_root": str(settings.openmanus_root) if settings.openmanus_root else None,
        "openmanus_valid": bool(info and info.looks_valid),
        "openmanus_details": (
            {
                "has_main_py": info.has_main_py,
                "has_config_example": info.has_config_example,
                "python_hint": info.python_min_hint,
            }
            if info
            else None
        ),
    }
