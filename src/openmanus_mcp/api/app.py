"""FastAPI substrate for web_sota (health + OpenManus install probe + run endpoint)."""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from openmanus_mcp import __version__
from openmanus_mcp.api.fleet_routes import router as fleet_router
from openmanus_mcp.api.supervisor_routes import router as supervisor_router
from openmanus_mcp.bridge_dry_run import dry_run_openmanus_bridge
from openmanus_mcp.bridge_schema import build_mcp_tools_manifest
from openmanus_mcp.chat_personas import list_personas_public, persona_system_prompt
from openmanus_mcp.chat_proxy import (
    completion_lmstudio,
    completion_ollama,
    resolve_lmstudio_model,
    resolve_ollama_model,
)
from openmanus_mcp.concurrency import api_run_limiter
from openmanus_mcp.job_store import api_job_store
from openmanus_mcp.openmanus_detect import describe_openmanus
from openmanus_mcp.runner import EntryPoint, RunResult
from openmanus_mcp.runner import run_prompt as _run_prompt
from openmanus_mcp.settings import get_settings
from openmanus_mcp.skills_catalog import (
    ChatContext,
    SkillConfig,
    assemble_chat_system_layers,
    discover_skills,
    estimate_skills_prompt_chars,
    prepend_skills_to_run_prompt,
    read_skill_body,
)
from openmanus_mcp.supervisor.schedules import schedule_count
from openmanus_mcp.supervisor.state import get_heartbeat
from openmanus_mcp.supervisor.worker import start_supervisor, stop_supervisor
from openmanus_mcp.system_info import list_gpus as _list_gpus_raw

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    start_supervisor()
    yield
    await stop_supervisor()


app = FastAPI(
    title="openmanus-mcp API",
    version=__version__,
    description="REST bridge for SOTA webapp; MCP runs via stdio separately.",
    lifespan=_lifespan,
)

_ui_port = int(get_settings().api_port) + 1
try:
    _ui_port = int(os.environ.get("OPENMANUS_MCP_UI_PORT", str(_ui_port)))
except ValueError:
    _ui_port = int(get_settings().api_port) + 1

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://127.0.0.1:{_ui_port}",
        f"http://localhost:{_ui_port}",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Local-only dashboard variants (for alternate mapped ports like federation hubs).
    allow_origin_regex=r"^https?://(127\.0\.0\.1|localhost)(:\d+)?$",
)

app.include_router(fleet_router, prefix="/api/v1")
app.include_router(supervisor_router, prefix="/api/v1")


def _repo_root() -> Path:
    """openmanus_mcp/api/app.py → parents[3] == repository root."""
    return Path(__file__).resolve().parents[3]


def _list_doc_filenames(repo: Path) -> list[str]:
    docs = repo / "docs"
    if not docs.is_dir():
        return []
    return sorted(p.name for p in docs.iterdir() if p.is_file() and p.suffix.lower() == ".md")


def _safe_doc_basename(name: str) -> str:
    if name.strip() != name or "/" in name or "\\" in name:
        raise HTTPException(status_code=400, detail="Invalid document name")
    base = Path(name).name
    if base != name:
        raise HTTPException(status_code=400, detail="Invalid document name")
    return base


@app.get("/api/v1/mcp/tools")
async def mcp_tools_manifest() -> dict[str, Any]:
    """MCP inspector payload for web_sota /tools (built from bridge_schema + settings)."""
    return build_mcp_tools_manifest(get_settings())


@app.get("/api/v1/settings/runtime")
async def runtime_public_settings() -> dict[str, Any]:
    """Effective non-secret configuration (env + defaults) for the dashboard."""
    s = get_settings()
    lim = api_run_limiter()
    return {
        "version": __version__,
        "openmanus_root": str(s.openmanus_root) if s.openmanus_root else None,
        "openmanus_fleet_root": str(s.openmanus_fleet_root) if s.openmanus_fleet_root else None,
        "api_host": s.api_host,
        "api_port": s.api_port,
        "runner_timeout_s": s.runner_timeout_s,
        "job_store_max_completed": s.job_store_max_completed,
        "ollama_base_url": s.ollama_base_url,
        "lmstudio_base_url": s.lmstudio_base_url,
        "adaptive_run_cap": lim.cap,
        "adaptive_run_metrics": lim.metrics,
    }


@app.get("/api/v1/chat/personas")
async def chat_personas_public() -> dict[str, Any]:
    """Persona metadata for SOTA Chat (labels + descriptions)."""
    return {"personas": list_personas_public()}


@app.get("/api/v1/skills")
async def skills_list() -> dict[str, Any]:
    """OpenClaw-style catalog: compact index fields only (full SKILL.md via /skills/{id})."""
    s = get_settings()
    metas = discover_skills(extra_dirs_semicolon=s.skills_extra_dirs)
    return {
        "skills": [m.to_public_dict() for m in metas],
        "estimated_index_chars": estimate_skills_prompt_chars(metas),
    }


@app.get("/api/v1/skills/{skill_id}")
async def skills_one(skill_id: str) -> dict[str, Any]:
    """Full SKILL.md body for UI preview or tooling (path-validated)."""
    s = get_settings()
    loaded = read_skill_body(
        skill_id,
        extra_dirs_semicolon=s.skills_extra_dirs,
        max_chars=s.max_skill_inject_chars,
    )
    if loaded is None:
        raise HTTPException(status_code=404, detail="skill not found or not readable")
    name, body = loaded
    metas = discover_skills(extra_dirs_semicolon=s.skills_extra_dirs)
    meta_row = next((m.to_public_dict() for m in metas if m.skill_id == skill_id), None)
    return {"skill": meta_row, "name": name, "body": body}


@app.get("/api/v1/system/gpu")
async def system_gpu() -> dict[str, Any]:
    """Host GPU / display adapter hints (hardware awareness)."""
    return _list_gpus_raw()


@app.get("/api/v1/system")
async def system_info() -> dict[str, Any]:
    """System resources for Status/Audit page."""
    cpu = 0.0
    mem = {"total": 0, "used": 0, "percent": 0.0}
    if HAS_PSUTIL:
        cpu = psutil.cpu_percent(interval=0.3)
        m = psutil.virtual_memory()
        mem = {"total": m.total, "used": m.used, "percent": m.percent}
    gpu_data = _list_gpus_raw()
    gpu_name = (gpu_data.get("gpus") or [{}])[0].get("name", "unknown") if gpu_data.get("gpus") else "unknown"
    return {
        "cpu": cpu,
        "memory": mem,
        "platform": gpu_data.get("platform", "unknown"),
        "gpu": gpu_name,
    }


@app.get("/api/v1/glama")
async def glama_manifest() -> dict[str, Any]:
    """Serve repo glama.json for Apps hub / Glama discovery."""
    path = _repo_root() / "glama.json"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="glama.json not found")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/v1/docs")
async def docs_index() -> dict[str, Any]:
    """List markdown files under docs/ (dynamic — no hardcoded manifest)."""
    return {"documents": _list_doc_filenames(_repo_root())}


@app.get("/api/v1/docs/{doc_name}", response_class=PlainTextResponse)
async def project_doc(doc_name: str) -> PlainTextResponse:
    """Markdown/plain help source for integrated Help viewer."""
    safe = _safe_doc_basename(doc_name)
    allowed = frozenset(_list_doc_filenames(_repo_root()))
    if safe not in allowed:
        raise HTTPException(status_code=404, detail="Unknown or missing document")
    path = _repo_root() / "docs" / safe
    return PlainTextResponse(
        path.read_text(encoding="utf-8"),
        media_type="text/markdown; charset=utf-8",
    )


@app.get("/api/v1/glom/ollama")
async def glom_ollama() -> dict[str, Any]:
    """Server-side probe for Ollama (uses OPENMANUS_OLLAMA_BASE_URL)."""
    settings = get_settings()
    url = f"{settings.ollama_base_url.rstrip('/')}/api/tags"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(url)
            body: Any
            try:
                body = r.json()
            except Exception:
                body = {"text": r.text[:300]}
            return {
                "reachable": r.is_success,
                "status_code": r.status_code,
                "url": url,
                "body": body,
            }
    except Exception as e:
        return {"reachable": False, "error": str(e), "url": url}


@app.get("/api/v1/glom/lmstudio")
async def glom_lmstudio() -> dict[str, Any]:
    """Server-side probe for LM Studio (uses OPENMANUS_LMSTUDIO_BASE_URL)."""
    settings = get_settings()
    url = f"{settings.lmstudio_base_url.rstrip('/')}/v1/models"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(url)
            body: Any
            try:
                body = r.json()
            except Exception:
                body = {"text": r.text[:300]}
            return {
                "reachable": r.is_success,
                "status_code": r.status_code,
                "url": url,
                "body": body,
            }
    except Exception as e:
        return {"reachable": False, "error": str(e), "url": url}


# ── Request / response models ────────────────────────────────────────────────


class DryRunBridgeRequest(BaseModel):
    operation: str
    prompt: str | None = None
    entry_point: str = "main.py"
    timeout_s: float | None = None
    job_id: str | None = None


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1, max_length=200_000)


class ChatCompletionRequest(BaseModel):
    provider: Literal["ollama", "lmstudio"]
    intent: Literal["refine", "chat"] = "chat"
    persona: str = "reductionist"
    model: str | None = None
    messages: list[ChatMessage] = Field(..., min_length=1)
    page_context: str | None = Field(default=None, max_length=8_000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    skills_mode: Literal["off", "index"] = Field(
        default="index",
        description="OpenClaw-style: inject skill index into system prompt (chat).",
    )
    skill_ids: list[str] = Field(
        default_factory=list,
        description="Optional full SKILL.md injection for these ids.",
        max_length=8,
    )


class RunRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Task text for the OpenManus agent")
    entry_point: str = Field(default="main.py", description="main.py or run_flow.py")
    timeout_s: float | None = Field(default=None, description="Override runner timeout")
    skill_ids: list[str] = Field(
        default_factory=list,
        description="Optional SKILL.md playbooks prepended to prompt.",
        max_length=8,
    )


class RunAsyncRequest(RunRequest):
    pass


class RunResponse(BaseModel):
    success: bool
    message: str
    result: dict[str, Any] | None = None


class RunAsyncResponse(BaseModel):
    success: bool
    message: str
    job_id: str


class JobStatusResponse(BaseModel):
    success: bool
    status: str  # pending | complete | not_found
    job_id: str
    result: dict[str, Any] | None = None


@app.post("/api/v1/mcp/dry-run")
async def mcp_dry_run(body: DryRunBridgeRequest) -> dict[str, Any]:
    """Validate an openmanus_bridge-style call without spawning OpenManus."""
    return dry_run_openmanus_bridge(
        operation=body.operation,
        prompt=body.prompt,
        entry_point=body.entry_point,
        timeout_s=body.timeout_s,
        job_id=body.job_id,
    )


@app.post("/api/v1/chat/completions")
async def chat_completions(body: ChatCompletionRequest) -> dict[str, Any]:
    """Proxy chat/refine to local Ollama or LM Studio (OpenAI-compatible)."""
    settings = get_settings()
    intent = body.intent
    sys_msg = persona_system_prompt(body.persona, intent=intent)

    config = SkillConfig(
        extra_dirs_semicolon=settings.skills_extra_dirs,
        max_skill_inject_chars=settings.max_skill_inject_chars,
    )

    ctx = ChatContext(
        persona_system=sys_msg,
        intent=intent,
        skills_mode=body.skills_mode,
        skill_ids=body.skill_ids,
        page_context=body.page_context,
    )
    layers = assemble_chat_system_layers(ctx=ctx, config=config)
    oai_messages: list[dict[str, str]] = list(layers)
    for m in body.messages:
        oai_messages.append({"role": m.role, "content": m.content})

    model = ""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            if body.provider == "ollama":
                model = await resolve_ollama_model(client, settings.ollama_base_url, body.model)
            else:
                model = await resolve_lmstudio_model(client, settings.lmstudio_base_url, body.model)
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error_type": "upstream_http",
            "error": f"Model list HTTP {e.response.status_code}: {e!s}",
        }
    except Exception as e:
        return {
            "success": False,
            "error_type": "upstream",
            "error": str(e),
        }

    out: dict[str, Any] = {}
    try:
        if body.provider == "ollama":
            out = await completion_ollama(
                base=settings.ollama_base_url,
                model=model,
                messages=oai_messages,
                temperature=body.temperature,
            )
        else:
            out = await completion_lmstudio(
                base=settings.lmstudio_base_url,
                model=model,
                messages=oai_messages,
                temperature=body.temperature,
            )
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error_type": "upstream_http",
            "error": f"Completion HTTP {e.response.status_code}: {(e.response.text or '')[:500]}",
            "model": model,
            "provider": body.provider,
        }
    except Exception as e:
        return {
            "success": False,
            "error_type": "upstream",
            "error": str(e),
            "model": model,
            "provider": body.provider,
        }

    if not out.get("success"):
        return {**out, "model": model, "provider": body.provider}

    return {
        "success": True,
        "provider": body.provider,
        "model": model,
        "message": {"role": "assistant", "content": out["content"]},
        "intent": intent,
    }


# ── Existing routes ──────────────────────────────────────────────────────────


@app.get("/api/v1/health")
async def health() -> dict[str, Any]:
    return {"ok": True, "service": "openmanus-mcp", "version": __version__}


@app.get("/api/capabilities")
async def capabilities() -> dict[str, Any]:
    """Runtime capability introspection endpoint (WEBAPP_STANDARDS.md §1.4)."""
    import datetime
    return {
        "status": "ok",
        "server": {"name": "openmanus-mcp", "version": __version__, "fastmcp": "3.2"},
        "tool_surface": {
            "total": 5,
            "portmanteau_count": 1,
            "atomic_count": 4,
            "portmanteau_tools": ["openmanus_bridge"],
            "atomic_tools": ["status", "validate", "run_prompt", "run_prompt_async", "job_status"],
        },
        "features": {
            "sampling": False,
            "agentic_workflows": True,
            "prompts": True,
            "resources": True,
            "skills": True,
        },
        "inventory": {
            "workflow_tools": ["openmanus_bridge"],
            "prompt_names": ["agent_instructions"],
            "resource_uris": ["skill://"],
            "skill_uris": ["skill://openmanus-bridge"],
        },
        "runtime": {
            "transport": "stdio",
            "surface_mode": "portmanteau",
        },
        "fleet": {
            "frontend_port": 10769,
            "backend_port": 10768,
            "mcp_command": "uv run -m openmanus_mcp",
        },
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }


@app.get("/api/v1/status")
async def status() -> dict[str, Any]:
    settings = get_settings()
    info = describe_openmanus(settings.openmanus_root)
    lim = api_run_limiter()
    return {
        "version": __version__,
        "openmanus_root": str(settings.openmanus_root) if settings.openmanus_root else None,
        "openmanus_valid": bool(info and info.looks_valid),
        "runner_timeout_s": settings.runner_timeout_s,
        "job_store_max_completed": settings.job_store_max_completed,
        "job_store_path": str(settings.job_store_path),
        "async_jobs_stored": api_job_store().stored_count(),
        "async_jobs_pending": api_job_store().pending_count(),
        "adaptive_run_cap": lim.cap,
        "adaptive_run_active": lim.active,
        "adaptive_run_available": lim.available,
        "adaptive_run_metrics": lim.metrics,
        "ollama_base_url": settings.ollama_base_url,
        "lmstudio_base_url": settings.lmstudio_base_url,
        "supervisor_enabled": settings.supervisor_enabled,
        "supervisor_tick_s": settings.supervisor_tick_s,
        "supervisor_schedules": schedule_count(),
        "supervisor_heartbeat": get_heartbeat().to_public_dict(),
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


# ── Runner routes ────────────────────────────────────────────────────────────


@app.post("/api/v1/run", response_model=RunResponse)
async def run_sync(body: RunRequest) -> RunResponse:
    """Run OpenManus synchronously. Waits for completion (up to timeout_s)."""
    settings = get_settings()
    info = describe_openmanus(settings.openmanus_root)
    if info is None or not info.looks_valid:
        return RunResponse(
            success=False,
            message="OPENMANUS_ROOT is not set or invalid. Set OPENMANUS_ROOT and restart.",
        )

    config = SkillConfig(
        extra_dirs_semicolon=settings.skills_extra_dirs,
        max_skill_inject_chars=settings.max_skill_inject_chars,
    )

    ep: EntryPoint = "run_flow.py" if body.entry_point == "run_flow.py" else "main.py"
    t_out = body.timeout_s if body.timeout_s is not None else settings.runner_timeout_s
    final_prompt = prepend_skills_to_run_prompt(
        body.prompt,
        body.skill_ids,
        config=config,
    )
    lim = api_run_limiter()
    await lim.acquire()
    try:
        result = await _run_prompt(info.root, final_prompt, ep, t_out)
    finally:
        await lim.release()
    return RunResponse(
        success=result.success,
        message="complete" if result.success else (result.error or "run failed"),
        result=result.to_dict(),
    )


@app.post("/api/v1/run/async", response_model=RunAsyncResponse)
async def run_async(body: RunAsyncRequest) -> RunAsyncResponse:
    """Fire-and-forget — returns job_id immediately. Poll /api/v1/run/jobs/{job_id}."""
    settings = get_settings()
    info = describe_openmanus(settings.openmanus_root)
    if info is None or not info.looks_valid:
        return RunAsyncResponse(
            success=False,
            message="OPENMANUS_ROOT is not set or invalid",
            job_id="",
        )

    config = SkillConfig(
        extra_dirs_semicolon=settings.skills_extra_dirs,
        max_skill_inject_chars=settings.max_skill_inject_chars,
    )

    ep: EntryPoint = "run_flow.py" if body.entry_point == "run_flow.py" else "main.py"
    t_out = body.timeout_s if body.timeout_s is not None else settings.runner_timeout_s
    final_prompt = prepend_skills_to_run_prompt(
        body.prompt,
        body.skill_ids,
        config=config,
    )
    jid = str(uuid.uuid4())
    store = api_job_store()
    store.set_pending(jid)

    async def _bg(job_id: str) -> None:
        lim = api_run_limiter()
        await lim.acquire()
        try:
            r = await _run_prompt(info.root, final_prompt, ep, t_out)
            store.set_result(job_id, r)
        finally:
            await lim.release()

    asyncio.create_task(_bg(jid))
    return RunAsyncResponse(success=True, message="queued", job_id=jid)


@app.get("/api/v1/run/jobs/{job_id}", response_model=JobStatusResponse)
async def job_status_api(job_id: str) -> JobStatusResponse:
    """Poll an async run job."""
    val = api_job_store().get(job_id)
    if val is None:
        return JobStatusResponse(success=False, status="not_found", job_id=job_id)
    if val == "pending":
        return JobStatusResponse(success=True, status="pending", job_id=job_id)

    # S101 fix: use if instead of assert
    if not isinstance(val, RunResult):
        return JobStatusResponse(success=False, status="invalid_data", job_id=job_id)

    return JobStatusResponse(
        success=True,
        status="complete",
        job_id=job_id,
        result=val.to_dict(),
    )
