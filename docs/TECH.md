# Technical reference

## Stack

| Layer | Technology |
|-------|------------|
| MCP | **FastMCP 3.2.0 GA** (Portmanteau Bridge), stdio |
| API | **FastAPI**, **uvicorn** |
| UI | **Vite 6**, **React 19** |
| Config | **pydantic-settings**, `.env` |
| Quality | **Ruff**, **MyPy**, **pytest**, **pre-commit** |
| Build | **.mcpb** SOTA bundle |

**Standards:** [AGENT_PROTOCOL](https://github.com/sandraschi/mcp-central-docs/blob/main/standards/AGENT_PROTOCOLS.md) (v1.20 compliance).

## Ports

| Service | Port |
|---------|------|
| FastAPI | **10768** |
| Vite dev | **10769** |

Forbidden in this project: 3000, 5173, 8000, 8080 (per org webapp rules).

## Repository layout

```
src/openmanus_mcp/
  __main__.py            # stdio MCP entry
  server.py              # FastMCP (bridge) + mcp.prompt() + sampling
  run_api.py             # uvicorn
  job_store.py           # Persistent JSON storage (~/.openmanus-mcp/jobs.json)
  api/app.py             # FastAPI app + CORS + lifespan (supervisor)
  api/fleet_routes.py    # fleet REST
  api/supervisor_routes.py  # supervisor heartbeat, schedules, connectors list
  skills_catalog.py      # SKILL.md discovery + chat system assembly
  skills/                # bundled AgentSkills-style folders (e.g. mcp_builder/SKILL.md)
  connectors/            # static connector registry (email, yahboom, calibre)
  supervisor/            # heartbeat state, schedules store, background worker
  concurrency.py         # adaptive run cap (shared by run + supervisor)
  fleet/                 # onboard service
  data/fleet_catalog.json
web_sota/                # React dashboard (Run activities, Chat + skills)
fleet/                   # local clones (gitignored except .gitkeep)
scripts/
  build_mcpb.ps1         # Automated SOTA bundle generation
tests/
  conftest.py            # Dual-mode (Mock/Integration) test provider
```

## Agentic Features (FastMCP 3.2.0)

| Feature | Implementation | Purpose |
|------|-------------------------|---------|
| **Prompts** | `@mcp.prompt()` | Pre-defined **System Context** for host LLMs (e.g. `instruct_openmanus`). |
| **Sampling** | `ctx.sample()` | Allows bridge to delegate sub-tasks back to the host model. |
| **Resources** | `mcp.resource()` | (Planned) exposing local docs/logs as MCP resources. |

**Runner:** `src/openmanus_mcp/runner.py` — asyncio subprocess, **stdout/stderr** line drain, timeout, **40k** char cap. **`main.py`**: **`--prompt`** when the prompt has no newlines; else stdin. **`run_flow.py`**: stdin only (upstream uses `input()`).

## REST API (selected)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | Liveness |
| GET | `/api/v1/status` | OpenManus path probe + async job counts |
| GET | `/api/v1/fleet/catalog` | Curated fleet list + onboard state |
| GET | `/api/v1/fleet/members` | Onboarded members detail |
| POST | `/api/v1/fleet/onboard` | Clone + install |
| POST | `/api/v1/fleet/webapp/start` | Windows PowerShell launch |
| POST | `/api/v1/run` | Sync OpenManus run |
| POST | `/api/v1/run/async` | Queue run → `job_id` |
| GET | `/api/v1/run/jobs/{job_id}` | Poll result (shared across MCP and API) |

## Environment variables

See **`.env.example`**. Notable:

- **`OPENMANUS_ROOT`** — upstream OpenManus clone
- **`OPENMANUS_FLEET_ROOT`** — fleet workspace (optional)
- **`OPENMANUS_MCP_API_PORT`** (default **10768**)
- **`OPENMANUS_JOB_STORE_PATH`** — location of `jobs.json` (disk-persistent)
- **`OPENMANUS_RUNNER_TIMEOUT_S`** — default **300**
- **`OPENMANUS_LMSTUDIO_BASE_URL`** (default **`http://127.0.0.1:1234`**)

## Development commands

- **Scripts:** `.\scripts\build_mcpb.ps1` (to generate `.mcpb`)
- **Linting:** `uv run ruff check .`, `uv run mypy .`
- **Testing:** `uv run pytest` (Mock mode), `uv run pytest --integration` (Engine mode).

← [Documentation index](README.md) · [ARCHITECTURE.md](ARCHITECTURE.md)
