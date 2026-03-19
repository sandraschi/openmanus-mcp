"""FastMCP 3.1 server — portmanteau bridge to OpenManus CLI."""

from __future__ import annotations

import asyncio
import logging
import sys
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastmcp import FastMCP

from openmanus_mcp import __version__
from openmanus_mcp.job_store import mcp_job_store
from openmanus_mcp.bridge_schema import BRIDGE_OPERATION_NAMES
from openmanus_mcp.openmanus_detect import describe_openmanus
from openmanus_mcp.runner import EntryPoint, RunResult
from openmanus_mcp.runner import run_prompt as _run_prompt
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

# In-memory job store for run_prompt_async results (keyed by job_id).
# Fine for single-process MCP server; not shared across restarts.
_jobs: dict[str, RunResult | str] = {}  # value: RunResult or "pending"


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
    entry_point: str = "main.py",
    timeout_s: float | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    """OPENMANUS_BRIDGE — Control plane for the OpenManus FOSS CLI wrapper.

    PORTMANTEAU PATTERN: Single entry point for status/validate/run/async.

    Operations:
        status           — server + path health check (fast)
        validate         — detailed OpenManus install validation (fast)
        run_prompt       — synchronous subprocess run; waits for completion
        run_prompt_async — fire-and-forget; returns job_id immediately
        job_status       — poll an async job by job_id

    Args:
        operation:    One of: status, validate, run_prompt, run_prompt_async, job_status.
        prompt:       Task text for run_prompt / run_prompt_async.
        entry_point:  "main.py" (default) or "run_flow.py".
        timeout_s:    Override runner timeout (seconds). Uses Settings.runner_timeout_s if None.
        job_id:       Required for job_status.

    Examples:
        openmanus_bridge("status")
        openmanus_bridge("validate")
        openmanus_bridge("run_prompt", prompt="Search the web for today's weather in Vienna")
        openmanus_bridge("run_prompt_async", prompt="...")  # returns {job_id: ...}
        openmanus_bridge("job_status", job_id="<id>")
    """
    start = time.perf_counter()
    settings = get_settings()
    info = describe_openmanus(settings.openmanus_root)
    op = operation.strip().lower()

    # ── status ──────────────────────────────────────────────────────────────
    if op == "status":
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "success": True,
            "message": "openmanus-mcp status",
            "result": {
                "server_version": __version__,
                "openmanus_root_set": settings.openmanus_root is not None,
                "openmanus_path": str(info.root) if info else None,
                "openmanus_valid": bool(info and info.looks_valid),
                "upstream": "https://github.com/FoundationAgents/OpenManus",
                "runner_timeout_s": settings.runner_timeout_s,
                "job_store_max_completed": settings.job_store_max_completed,
                "async_jobs_stored": mcp_job_store().stored_count(),
                "async_jobs_pending": mcp_job_store().pending_count(),
            },
            "execution_time_ms": round(elapsed_ms, 2),
            "recommendations": [
                "Set OPENMANUS_ROOT to your OpenManus clone",
                "Configure OpenManus config.toml for local LLM (e.g. Ollama)",
                "Use web_sota/start.ps1 for dashboard on 10769",
            ],
        }

    # ── validate ─────────────────────────────────────────────────────────────
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

    # ── run_prompt (synchronous) ─────────────────────────────────────────────
    if op == "run_prompt":
        if not prompt or not prompt.strip():
            return {
                "success": False,
                "message": "prompt is required for run_prompt",
                "error_type": "invalid_argument",
                "execution_time_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        if info is None or not info.looks_valid:
            return {
                "success": False,
                "message": "OPENMANUS_ROOT is not set or invalid — run validate first",
                "error_type": "configuration",
                "execution_time_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        ep: EntryPoint = "run_flow.py" if entry_point == "run_flow.py" else "main.py"
        t_out = timeout_s if timeout_s is not None else settings.runner_timeout_s

        log.info("runner_start", op="run_prompt", entry_point=ep, timeout_s=t_out)
        result = await _run_prompt(info.root, prompt, ep, t_out)
        log.info(
            "runner_done",
            success=result.success,
            exit_code=result.exit_code,
            timed_out=result.timed_out,
            ms=round(result.execution_time_ms, 1),
        )
        return {
            "success": result.success,
            "message": "run_prompt complete" if result.success else (result.error or "run failed"),
            "result": result.to_dict(),
        }

    # ── run_prompt_async (fire and forget) ────────────────────────────────────
    if op == "run_prompt_async":
        if not prompt or not prompt.strip():
            return {
                "success": False,
                "message": "prompt is required for run_prompt_async",
                "error_type": "invalid_argument",
                "execution_time_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        if info is None or not info.looks_valid:
            return {
                "success": False,
                "message": "OPENMANUS_ROOT is not set or invalid — run validate first",
                "error_type": "configuration",
                "execution_time_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        ep = "run_flow.py" if entry_point == "run_flow.py" else "main.py"
        t_out = timeout_s if timeout_s is not None else settings.runner_timeout_s
        jid = str(uuid.uuid4())
        store = mcp_job_store()
        store.set_pending(jid)

        async def _bg(job_id: str) -> None:
            r = await _run_prompt(info.root, prompt, ep, t_out)  # type: ignore[arg-type]
            store.set_result(job_id, r)

        asyncio.create_task(_bg(jid))
        log.info("runner_async_queued", job_id=jid, entry_point=ep)
        return {
            "success": True,
            "message": "Job queued",
            "job_id": jid,
            "execution_time_ms": round((time.perf_counter() - start) * 1000, 2),
            "next": f'openmanus_bridge("job_status", job_id="{jid}") to poll',
        }

    # ── job_status ────────────────────────────────────────────────────────────
    if op == "job_status":
        if not job_id:
            return {
                "success": False,
                "message": "job_id is required for job_status",
                "error_type": "invalid_argument",
                "execution_time_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        val = mcp_job_store().get(job_id)
        if val is None:
            return {
                "success": False,
                "message": f"Unknown job_id: {job_id}",
                "error_type": "not_found",
                "execution_time_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        if val == "pending":
            return {
                "success": True,
                "message": "pending",
                "status": "pending",
                "job_id": job_id,
                "execution_time_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        # RunResult
        assert isinstance(val, RunResult)
        return {
            "success": True,
            "message": "complete",
            "status": "complete",
            "job_id": job_id,
            "result": val.to_dict(),
            "execution_time_ms": round((time.perf_counter() - start) * 1000, 2),
        }

    return {
        "success": False,
        "message": f"Unknown operation: {operation!r}",
        "error_type": "invalid_argument",
        "recovery_options": [f"Use one of: {', '.join(BRIDGE_OPERATION_NAMES)}"],
        "execution_time_ms": round((time.perf_counter() - start) * 1000, 2),
    }
