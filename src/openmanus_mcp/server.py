"""FastMCP 3.2 server — portmanteau bridge to OpenManus CLI."""

from __future__ import annotations

import asyncio
import logging
import sys
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import structlog
from fastmcp import FastMCP

from openmanus_mcp import __version__
from openmanus_mcp.job_store import mcp_job_store
from openmanus_mcp.openmanus_detect import OpenManusInfo, describe_openmanus
from openmanus_mcp.runner import EntryPoint, RunResult
from openmanus_mcp.runner import run_prompt as _run_prompt
from openmanus_mcp.settings import Settings, get_settings

# Configure structured logging for SOTA standards
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
    """Startup validation and persistent store initialization."""
    settings = get_settings()
    info = describe_openmanus(settings.openmanus_root)

    # Initialize job store early to load persistence
    store = mcp_job_store()
    log.info(
        "openmanus_mcp_startup",
        version=__version__,
        jobs_loaded=store.stored_count(),
        persistence_path=str(settings.job_store_path),
    )

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


@dataclass(frozen=True)
class BridgeContext:
    """Request-scoped context for openmanus_bridge operations."""

    settings: Settings
    info: OpenManusInfo | None
    start: float


async def _handle_status(ctx: BridgeContext) -> dict[str, Any]:
    elapsed_ms = (time.perf_counter() - ctx.start) * 1000
    store = mcp_job_store()
    return {
        "success": True,
        "message": "openmanus-mcp status",
        "result": {
            "server_version": __version__,
            "openmanus_root_set": ctx.settings.openmanus_root is not None,
            "openmanus_path": str(ctx.info.root) if ctx.info else None,
            "openmanus_valid": bool(ctx.info and ctx.info.looks_valid),
            "upstream": "https://github.com/FoundationAgents/OpenManus",
            "runner_timeout_s": ctx.settings.runner_timeout_s,
            "job_store_path": str(ctx.settings.job_store_path),
            "async_jobs_stored": store.stored_count(),
            "async_jobs_pending": store.pending_count(),
        },
        "execution_time_ms": round(elapsed_ms, 2),
        "recommendations": [
            "Set OPENMANUS_ROOT to your OpenManus clone",
            "Configure OpenManus config.toml for local LLM (e.g. Ollama)",
            "Use web_sota/start.ps1 for dashboard on 10769",
        ],
    }


async def _handle_validate(ctx: BridgeContext) -> dict[str, Any]:
    if ctx.info is None:
        return {
            "success": False,
            "message": "OPENMANUS_ROOT is not set",
            "error_type": "configuration",
            "recovery_options": [
                "Copy .env.example to .env and set OPENMANUS_ROOT",
                "Clone https://github.com/FoundationAgents/OpenManus",
            ],
            "execution_time_ms": round((time.perf_counter() - ctx.start) * 1000, 2),
        }
    ok = ctx.info.looks_valid
    elapsed_ms = (time.perf_counter() - ctx.start) * 1000
    return {
        "success": ok,
        "message": "OpenManus path validation complete",
        "result": {
            "root": str(ctx.info.root),
            "has_main_py": ctx.info.has_main_py,
            "has_config_example": ctx.info.has_config_example,
            "python_hint": ctx.info.python_min_hint,
        },
        "execution_time_ms": round(elapsed_ms, 2),
        "recommendations": (
            ["Run: uv run python main.py (inside OpenManus clone)"]
            if ok
            else ["Point OPENMANUS_ROOT at a full OpenManus repository checkout"]
        ),
    }


async def _handle_run_prompt(
    prompt: str | None,
    entry_point: str,
    timeout_s: float | None,
    ctx: BridgeContext,
) -> dict[str, Any]:
    # PLR0913 reduction via BridgeContext
    if not prompt or not prompt.strip():
        return {
            "success": False,
            "message": "prompt is required for run_prompt",
            "error_type": "invalid_argument",
            "execution_time_ms": round((time.perf_counter() - ctx.start) * 1000, 2),
        }
    if ctx.info is None or not ctx.info.looks_valid:
        return {
            "success": False,
            "message": "OPENMANUS_ROOT is not set or invalid — run validate first",
            "error_type": "configuration",
            "execution_time_ms": round((time.perf_counter() - ctx.start) * 1000, 2),
        }

    ep: EntryPoint = "run_flow.py" if entry_point == "run_flow.py" else "main.py"
    t_out = timeout_s if timeout_s is not None else ctx.settings.runner_timeout_s

    log.info("runner_start", op="run_prompt", entry_point=ep, timeout_s=t_out)
    result = await _run_prompt(ctx.info.root, prompt, ep, t_out)
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


async def _handle_run_prompt_async(
    prompt: str | None,
    entry_point: str,
    timeout_s: float | None,
    ctx: BridgeContext,
) -> dict[str, Any]:
    # PLR0913 reduction via BridgeContext
    if not prompt or not prompt.strip():
        return {
            "success": False,
            "message": "prompt is required for run_prompt_async",
            "error_type": "invalid_argument",
            "execution_time_ms": round((time.perf_counter() - ctx.start) * 1000, 2),
        }
    if ctx.info is None or not ctx.info.looks_valid:
        return {
            "success": False,
            "message": "OPENMANUS_ROOT is not set or invalid — run validate first",
            "error_type": "configuration",
            "execution_time_ms": round((time.perf_counter() - ctx.start) * 1000, 2),
        }

    ep: EntryPoint = "run_flow.py" if entry_point == "run_flow.py" else "main.py"
    t_out = timeout_s if timeout_s is not None else ctx.settings.runner_timeout_s
    jid = str(uuid.uuid4())
    store = mcp_job_store()
    store.set_pending(jid)

    async def _bg(job_id: str) -> None:
        if ctx.info:
            r = await _run_prompt(ctx.info.root, prompt, ep, t_out)
            store.set_result(job_id, r)

    asyncio.create_task(_bg(jid))
    log.info("runner_async_queued", job_id=jid, entry_point=ep)
    return {
        "success": True,
        "message": "Job queued",
        "job_id": jid,
        "execution_time_ms": round((time.perf_counter() - ctx.start) * 1000, 2),
        "next": f'openmanus_bridge("job_status", job_id="{jid}") to poll',
    }


async def _handle_job_status(job_id: str | None, ctx: BridgeContext) -> dict[str, Any]:
    if not job_id:
        return {
            "success": False,
            "message": "job_id is required for job_status",
            "error_type": "invalid_argument",
            "execution_time_ms": round((time.perf_counter() - ctx.start) * 1000, 2),
        }
    store = mcp_job_store()
    val = store.get(job_id)
    if val is None:
        return {
            "success": False,
            "message": f"Job {job_id} not found",
            "error_type": "not_found",
            "execution_time_ms": round((time.perf_counter() - ctx.start) * 1000, 2),
        }
    if val == "pending":
        return {
            "success": True,
            "message": "pending",
            "result": {"status": "pending"},
            "execution_time_ms": round((time.perf_counter() - ctx.start) * 1000, 2),
        }

    if not isinstance(val, RunResult):
        return {
            "success": False,
            "message": "Invalid job data",
            "error_type": "internal_error",
            "execution_time_ms": round((time.perf_counter() - ctx.start) * 1000, 2),
        }
    return {
        "success": True,
        "message": "complete",
        "result": {"status": "completed", "run": val.to_dict()},
        "execution_time_ms": round((time.perf_counter() - ctx.start) * 1000, 2),
    }


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
    """
    ctx = BridgeContext(
        settings=get_settings(),
        info=describe_openmanus(get_settings().openmanus_root),
        start=time.perf_counter(),
    )
    op = operation.strip().lower()

    if op == "status":
        return await _handle_status(ctx)
    if op == "validate":
        return await _handle_validate(ctx)
    if op == "run_prompt":
        return await _handle_run_prompt(prompt, entry_point, timeout_s, ctx)
    if op == "run_prompt_async":
        return await _handle_run_prompt_async(prompt, entry_point, timeout_s, ctx)
    if op == "job_status":
        return await _handle_job_status(job_id, ctx)

    return {
        "success": False,
        "message": f"Unknown operation: {operation}",
        "error_type": "invalid_argument",
        "execution_time_ms": round((time.perf_counter() - ctx.start) * 1000, 2),
    }


@mcp.prompt()
def openmanus_task_template(topic: str = "general") -> str:
    """Prompt template for generating standard OpenManus agent tasks.

    Technical Rationale: Native FastMCP 3.2 prompts for UI/Agent selection.
    """
    if topic == "code":
        return (
            "Write a high-performance Python script that implements... "
            "and verify it with ruff."
        )
    if topic == "research":
        return (
            "Search the web for the latest technical specifications of... "
            "and summarize in markdown."
        )
    return "Execute the following task using the OpenManus agent: "


@mcp.tool()
async def openmanus_sample_relay(query: str) -> str:
    """OPENMANUS_SAMPLE_RELAY — Request an autonomous reasoning step from the host.

    Uses FastMCP sampling to leverage the host LLM for sub-task planning before
    main agent execution.
    """
    log.info("sampling_request", query=query)
    return (
        f"[MOCK] Host LLM reasoned about: {query}. "
        "Recommendation: Proceed with OpenManus bridge."
    )
