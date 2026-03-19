"""Single source of truth for openmanus_bridge operations (MCP + REST manifest).

The FastMCP tool `openmanus_bridge` in server.py implements these operations.
API GET /api/v1/mcp/tools builds JSON from this module + runtime Settings.
"""

from __future__ import annotations

from typing import Any

from openmanus_mcp.settings import Settings

# Operation names accepted by openmanus_bridge (lowercase).
BRIDGE_OPERATION_NAMES: tuple[str, ...] = (
    "status",
    "validate",
    "run_prompt",
    "run_prompt_async",
    "job_status",
)

BRIDGE_OPERATIONS: list[dict[str, Any]] = [
    {
        "name": "status",
        "summary": "Server and OPENMANUS_ROOT health (fast).",
        "parameters": {},
    },
    {
        "name": "validate",
        "summary": "Detailed OpenManus checkout validation.",
        "parameters": {},
    },
    {
        "name": "run_prompt",
        "summary": "Run OpenManus subprocess once; waits for completion.",
        "parameters": {
            "prompt": {"type": "string", "required": True},
            "entry_point": {
                "type": "string",
                "enum": ["main.py", "run_flow.py"],
                "default": "main.py",
            },
            "timeout_s": {"type": "number", "required": False},
        },
    },
    {
        "name": "run_prompt_async",
        "summary": "Queue a run; returns job_id. Poll job_status.",
        "parameters": {
            "prompt": {"type": "string", "required": True},
            "entry_point": {
                "type": "string",
                "enum": ["main.py", "run_flow.py"],
                "default": "main.py",
            },
            "timeout_s": {"type": "number", "required": False},
        },
    },
    {
        "name": "job_status",
        "summary": "Poll async job by job_id.",
        "parameters": {"job_id": {"type": "string", "required": True}},
    },
]


def api_public_base(settings: Settings) -> str:
    """Absolute base URL for this process (no trailing slash)."""
    host = settings.api_host
    if ":" in host and not host.startswith("["):
        pass
    return f"http://{host}:{settings.api_port}"


def build_mcp_tools_manifest(settings: Settings) -> dict[str, Any]:
    base = api_public_base(settings)
    return {
        "server": "openmanus-mcp",
        "stdio_tool": "openmanus_bridge",
        "description": (
            "Unified bridge for OpenManus runner, validation, and async jobs. "
            "Same operations via MCP stdio or REST."
        ),
        "operations": list(BRIDGE_OPERATIONS),
        "operation_names": list(BRIDGE_OPERATION_NAMES),
        "rest_mirror": {
            "health": f"{base}/api/v1/health",
            "status": f"{base}/api/v1/status",
            "run_sync": f"{base}/api/v1/run",
            "run_async": f"{base}/api/v1/run/async",
            "job_poll": f"{base}/api/v1/run/jobs/{{job_id}}",
            "mcp_tools": f"{base}/api/v1/mcp/tools",
            "mcp_dry_run": f"{base}/api/v1/mcp/dry-run",
            "runtime_settings": f"{base}/api/v1/settings/runtime",
            "docs_index": f"{base}/api/v1/docs",
            "glama": f"{base}/api/v1/glama",
            "glom_ollama": f"{base}/api/v1/glom/ollama",
            "glom_lmstudio": f"{base}/api/v1/glom/lmstudio",
            "chat_completions": f"{base}/api/v1/chat/completions",
            "chat_personas": f"{base}/api/v1/chat/personas",
            "system_gpu": f"{base}/api/v1/system/gpu",
        },
        "glom_endpoints": {
            "ollama_base_url": settings.ollama_base_url,
            "ollama_tags_path": "/api/tags",
            "lmstudio_base_url": settings.lmstudio_base_url,
            "lmstudio_models_path": "/v1/models",
        },
    }
