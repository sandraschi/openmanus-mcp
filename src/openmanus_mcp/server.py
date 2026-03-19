"""FastMCP 3.1 server — portmanteau bridge to OpenManus CLI."""

from __future__ import annotations

import logging
import sys
import time
from typing import Any
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastmcp import FastMCP

from openmanus_mcp.openmanus_detect import describe_openmanus
from openmanus_mcp.settings import get_settings

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

_stderr = logging.StreamHandler(sys.stderr)
_stderr.setFormatter(logging.Formatter("%(message)s"))
root = logging.getLogger()
root.setLevel(logging.INFO)
if not root.handlers:
    root.addHandler(_stderr)

log = structlog.get_logger(__name__)


@asynccontextmanager
async def server_lifespan(_mcp: FastMCP) -> AsyncIterator[None]:
    """Startup validation — fail loud with actionable stderr (MCP on stdout)."""
    settings = get_settings()
    info = describe_openmanus(settings.openmanus_root)
    if info is None:
        log.warning(
            "openmanus_mcp_startup",
            message="OPENMANUS_ROOT not set — tools will return setup hints only",
        )
    elif not info.looks_valid:
        log.warning(
            "openmanus_mcp_startup",
            message="OPENMANUS_ROOT does not look like OpenManus (missing main.py)",
            path=str(info.root),
        )
    else:
        log.info("openmanus_mcp_startup", message="OpenManus path OK", path=str(info.root))
    yield


mcp = FastMCP("openmanus-mcp", lifespan=server_lifespan)


@mcp.tool()
async def openmanus_bridge(
    operation: str,
    prompt: str | None = None,
) -> dict[str, Any]:
    """OPENMANUS_BRIDGE — Control plane for the OpenManus FOSS CLI wrapper.

    PORTMANTEAU PATTERN RATIONALE: Single entry for status, validation, and future
    run_prompt / attach so MCP clients avoid tool sprawl while we iterate v0.1.

    Args:
        operation: One of: status, validate, run_prompt (run_prompt stub in v0.1).
        prompt: Optional text for run_prompt (ignored until subprocess runner lands).

    Returns:
        Rich dict: success, message, result, recommendations.

    Examples:
        openmanus_bridge("status")
        openmanus_bridge("validate")
    """
    start = time.perf_counter()
    settings = get_settings()
    info = describe_openmanus(settings.openmanus_root)
    op = operation.strip().lower()

    if op == "status":
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "success": True,
            "message": "openmanus-mcp status",
            "result": {
                "server_version": "0.1.0",
                "openmanus_root_set": settings.openmanus_root is not None,
                "openmanus_path": str(info.root) if info else None,
                "openmanus_valid": bool(info and info.looks_valid),
                "upstream": "https://github.com/FoundationAgents/OpenManus",
            },
            "execution_time_ms": round(elapsed_ms, 2),
            "recommendations": [
                "Set OPENMANUS_ROOT to your OpenManus clone",
                "Configure OpenManus config.toml for local LLM (e.g. Ollama)",
                "Use web_sota/start.ps1 for dashboard on 10769",
            ],
        }

    if op == "validate":
        if info is None:
            return {
                "success": False,
                "message": "OPENMANUS_ROOT is not set",
                "error_type": "configuration",
                "recovery_options": [
                    "Copy .env.example to .env and set OPENMANUS_ROOT",
                    "Clone https://github.com/FoundationAgents/OpenManus",
                ],
                "execution_time_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        ok = info.looks_valid
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "success": ok,
            "message": "OpenManus path validation complete",
            "result": {
                "root": str(info.root),
                "has_main_py": info.has_main_py,
                "has_config_example": info.has_config_example,
                "python_hint": info.python_min_hint,
            },
            "execution_time_ms": round(elapsed_ms, 2),
            "recommendations": (
                ["Run: uv run python main.py (inside OpenManus clone)"]
                if ok
                else ["Point OPENMANUS_ROOT at a full OpenManus repository checkout"]
            ),
        }

    if op == "run_prompt":
        return {
            "success": False,
            "message": "run_prompt not implemented in v0.1 — scaffold only",
            "error_type": "not_implemented",
            "recovery_options": [
                "Run OpenManus directly: python main.py --prompt \"...\" in OPENMANUS_ROOT",
                "Watch this repo for v0.2 subprocess runner + streaming logs",
            ],
            "diagnostic_info": {"prompt_received": bool(prompt and prompt.strip())},
            "execution_time_ms": round((time.perf_counter() - start) * 1000, 2),
        }

    return {
        "success": False,
        "message": f"Unknown operation: {operation!r}",
        "error_type": "invalid_argument",
        "recovery_options": ["Use operation=status | validate | run_prompt"],
        "execution_time_ms": round((time.perf_counter() - start) * 1000, 2),
    }
