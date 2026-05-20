"""FastMCP 3.2 server — portmanteau bridge to OpenManus CLI."""

from __future__ import annotations

import asyncio
import logging
import sys
import os
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import structlog
from fastmcp import Context, FastMCP, Resource

from openmanus_mcp import __version__
from openmanus_mcp.job_store import mcp_job_store
from openmanus_mcp.openmanus_detect import OpenManusInfo, describe_openmanus
from openmanus_mcp.runner import EntryPoint, RunResult
from openmanus_mcp.runner import run_prompt as _run_prompt
from openmanus_mcp.settings import Settings, get_settings
from openmanus_mcp.skills_catalog import discover_skills, get_skill_content
from openmanus_mcp.system_info import list_gpus

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
_BACKGROUND_TASKS: set[asyncio.Task[Any]] = set()
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
            "openmanus_mcp_startup_warn",
            message="OPENMANUS_ROOT not set — tools will return setup hints only",
        )
    elif not info.looks_valid:
        log.warning(
            "openmanus_mcp_startup_warn",
            message="OPENMANUS_ROOT does not look like OpenManus (missing main.py)",
            path=str(info.root),
        )
    else:
        log.info("openmanus_mcp_startup", message="OpenManus path OK", path=str(info.root))

    yield


mcp = FastMCP("openmanus-mcp", lifespan=server_lifespan)

# MCP Bridge — Proxy external MCP servers via MCP_BRIDGE_URLS
_bridge_proxies: list[str] = []
bridge_urls = os.getenv("MCP_BRIDGE_URLS", "")
if bridge_urls:
    try:
        from fastmcp.server import create_proxy
        for url in bridge_urls.split(","):
            url = url.strip()
            if url:
                try:
                    mcp.add_provider(create_proxy(url))
                    _bridge_proxies.append(url)
                except Exception:
                    pass
    except ImportError:
        pass


@dataclass(frozen=True)
class BridgeContext:
    """Request-scoped context for openmanus_bridge operations."""

    settings: Settings
    info: OpenManusInfo | None
    start: float


async def _handle_status(ctx: BridgeContext) -> dict[str, Any]:
    elapsed_ms = (time.perf_counter() - ctx.start) * 1000
    store = mcp_job_store()
    gpu_info = list_gpus()
    gpu_names = [g.get("name", "Unknown") for g in gpu_info["gpus"]]
    gpu_str = ", ".join(gpu_names) if gpu_names else "None"
    return {
        "success": True,
        "message": "openmanus-mcp status (SOTA High-Fidelity)",
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
            "hardware": gpu_info,
            "fleet_root": str(ctx.settings.fleet_root),
        },
        "execution_time_ms": round(elapsed_ms, 2),
        "recommendations": [
            "Set OPENMANUS_ROOT to your OpenManus clone",
            "Configure OpenManus config.toml for local LLM (e.g. Ollama or LM Studio)",
            "Use web_sota/start.ps1 for dashboard on 10769",
            f"Detected GPU: {gpu_str}",
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

    task = asyncio.create_task(_bg(jid))
    _BACKGROUND_TASKS.add(task)
    task.add_done_callback(_BACKGROUND_TASKS.discard)
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


async def _discover_fleet_mcp(settings: Settings) -> dict[str, Any]:
    """Dynamically scan for onboarded fleet members and generate MCP config."""
    mcp_servers = {}
    mcp_servers["openmanus-mcp"] = {
        "command": "uv",
        "args": ["run", "python", "-m", "openmanus_mcp"],
        "cwd": str(settings.repo_root),
    }
    fleet_dir = settings.fleet_root
    if fleet_dir.is_dir():
        for item in fleet_dir.iterdir():
            if item.is_dir() and (item / "pyproject.toml").exists():
                name = item.name
                # Heuristic for Windows venv
                venv_py = item / ".venv" / "Scripts" / "python.exe"
                if venv_py.exists():
                    mcp_servers[name] = {
                        "command": str(venv_py),
                        "args": ["-m", name.replace("-", "_")],
                        "cwd": str(item),
                    }
                else:
                    mcp_servers[name] = {
                        "command": "uv",
                        "args": ["run", "python", "-m", name.replace("-", "_")],
                        "cwd": str(item),
                    }
    return mcp_servers


async def _handle_fleet(ctx: BridgeContext) -> dict[str, Any]:
    elapsed_ms = (time.perf_counter() - ctx.start) * 1000
    mcp_servers = await _discover_fleet_mcp(ctx.settings)
    return {
        "success": True,
        "message": f"Discovered {len(mcp_servers)} fleet members",
        "result": {"mcpServers": mcp_servers},
        "execution_time_ms": round(elapsed_ms, 2),
    }


@mcp.resource("skills://{skill_id}")
def get_skill_resource(skill_id: str) -> str:
    """Read a specific skill's SKILL.md content."""
    settings = get_settings()
    content = get_skill_content(skill_id, extra_dirs_semicolon=settings.skills_extra_dirs)
    if content is None:
        raise ValueError(f"Skill {skill_id} not found")
    return content


@mcp.list_resources()
async def list_skills_resources() -> list[mcp.Resource]:
    """List all discovered skills as MCP resources."""
    settings = get_settings()
    metas = discover_skills(extra_dirs_semicolon=settings.skills_extra_dirs)
    return [
        Resource(
            uri=f"skills://{m.skill_id}",
            name=m.name,
            description=m.description,
            mime_type="text/markdown",
        )
        for m in metas
    ]


@mcp.resource("fleet://config")
async def get_fleet_config_resource() -> str:
    """Dynamically generated Cursor/MCP config for all fleet members."""
    import json

    servers = await _discover_fleet_mcp(get_settings())
    return json.dumps({"mcpServers": servers}, indent=2)


@mcp.tool()
async def openmanus_bridge(
    operation: str,
    prompt: str | None = None,
    entry_point: str = "main.py",
    timeout_s: float | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    """OPENMANUS_BRIDGE — Control plane for the OpenManus FOSS CLI wrapper.

    PORTMANTEAU PATTERN: Single entry point for status/validate/run/async/fleet.

    Operations:
        status           — server + path health check (fast)
        validate         — detailed OpenManus install validation (fast)
        run_prompt       — synchronous subprocess run; waits for completion
        run_prompt_async — fire-and-forget; returns job_id immediately
        job_status       — poll an async job by job_id
        fleet            — dynamically discover onboarded fleet members

    Args:
        operation:    One of: status, validate, run_prompt, run_prompt_async, job_status, fleet.
        prompt:       Task text for run_prompt / run_prompt_async.
        entry_point:  "main.py" (default) or "run_flow.py".
        timeout_s:    Override runner timeout (seconds). Uses Settings.runner_timeout_s if None.
        job_id:       Required for job_status.
    """
    settings = get_settings()
    ctx = BridgeContext(
        settings=settings,
        info=describe_openmanus(settings.openmanus_root),
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
    if op == "fleet":
        return await _handle_fleet(ctx)

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
async def openmanus_sample_relay(query: str, ctx: Context) -> str:
    """OPENMANUS_SAMPLE_RELAY — Delegate a sub-task reasoning step to the host LLM via sampling.

    Sends *query* to the MCP client's LLM (e.g. Claude Desktop, Cursor) and returns its
    response. Useful for pre-flight planning, prompt refinement, or OpenManus task
    decomposition before invoking openmanus_bridge(run_prompt).

    Falls back gracefully when the client does not support sampling (returns an
    explanatory string rather than raising).

    Args:
        query: The question or sub-task to reason about.
        ctx:   FastMCP context — injected automatically, do not pass manually.
    """
    log.info("sampling_request", query=query[:120])
    system_prompt = (
        "You are a planning assistant for the OpenManus agent framework. "
        "Given the user's query, briefly analyse what OpenManus tools or steps "
        "would best accomplish the task, and recommend a clear next action. "
        "Be concise (≤150 words)."
    )
    try:
        result = await ctx.sample(
            messages=query,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=300,
        )
        text = result.text or ""
        log.info("sampling_response", chars=len(text))
        return text
    except Exception as exc:
        # Client doesn't support sampling, or transport error — degrade gracefully
        log.warning("sampling_unavailable", exc=str(exc))
        return (
            f"[sampling unavailable: {exc}] "
            "Tip: use openmanus_bridge(\"run_prompt\", prompt=...) to execute the task directly."
        )
