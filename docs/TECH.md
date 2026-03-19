# Technical reference

## Stack

| Layer | Technology |
|-------|------------|
| MCP | **FastMCP 3.1+**, stdio |
| API | **FastAPI**, **uvicorn** |
| UI | **Vite 6**, **React 19** |
| Config | **pydantic-settings**, `.env` |
| Quality | **Ruff**, **pytest**, **pre-commit** |

**Standards:** [AGENT_PROTOCOLS](https://github.com/sandraschi/mcp-central-docs/blob/main/standards/AGENT_PROTOCOLS.md) (central docs).

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
  server.py              # FastMCP + openmanus_bridge
  run_api.py             # uvicorn
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
tests/
```

## MCP tools

| Tool | Operations (v0.1 beta) |
|------|-------------------------|
| `openmanus_bridge` | `status`, `validate`, `run_prompt`, `run_prompt_async`, `job_status` |

Docstrings follow portmanteau / enhanced-response patterns from central docs.

**Runner:** `src/openmanus_mcp/runner.py` — asyncio subprocess, **stdout/stderr** line drain, timeout, **40k** char cap. **`main.py`**: **`--prompt`** when the prompt has no newlines; else stdin. **`run_flow.py`**: stdin only (upstream uses `input()`).

## REST API (selected)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | Liveness |
| GET | `/api/v1/status` | OpenManus path probe |
| GET | `/api/v1/fleet/catalog` | Curated fleet list + onboard state |
| GET | `/api/v1/fleet/members` | Onboarded members detail |
| POST | `/api/v1/fleet/onboard` | Clone + install |
| POST | `/api/v1/fleet/webapp/start` | Windows PowerShell launch |
| POST | `/api/v1/run` | Sync OpenManus run (body: `prompt`, `entry_point`, optional `timeout_s`) |
| POST | `/api/v1/run/async` | Queue run → `job_id` |
| GET | `/api/v1/run/jobs/{job_id}` | Poll `pending` / `complete` + result |
| POST | `/api/v1/chat/completions` | Proxy to Ollama / LM Studio; optional **skills** (`skills_mode`, `skill_ids`) |
| GET | `/api/v1/skills` | List discovered skills + estimated index size |
| GET | `/api/v1/skills/{id}` | Full `SKILL.md` body (path-validated) |
| GET | `/api/v1/supervisor/heartbeat` | Supervisor tick / uptime (if enabled) |
| GET/POST | `/api/v1/supervisor/schedules` | List / create interval schedules |
| DELETE/PATCH | `/api/v1/supervisor/schedules/{id}` | Remove / enable-disable |
| GET | `/api/v1/connectors` | Connector catalog (metadata + proactive hints) |
| GET | `/api/v1/status` | OpenManus probe + async job counts + **supervisor** fields |

Vite proxies **`/api`** → **10768**. **Run** uses run endpoints + activity presets; **Chat** uses completions + skills; **Logger** records navigation and run events.

## Environment variables

See **`.env.example`**. Notable:

- **`OPENMANUS_ROOT`** — upstream OpenManus clone
- **`OPENMANUS_FLEET_ROOT`** — fleet workspace (optional)
- **`OPENMANUS_MCP_API_HOST`** / **`OPENMANUS_MCP_API_PORT`**
- **`OPENMANUS_RUNNER_TIMEOUT_S`** — subprocess wall-clock cap per run (default **300**)
- **`OPENMANUS_JOB_STORE_MAX_COMPLETED`** — max completed async jobs retained in memory per process (default **100**, FIFO eviction)
- **`OPENMANUS_LMSTUDIO_BASE_URL`** — LM Studio OpenAI-compatible base (default **`http://127.0.0.1:1234`**)
- **`OPENMANUS_SUPERVISOR_ENABLED`** — `true` / `false` (default **false**) — background schedule runner
- **`OPENMANUS_SUPERVISOR_TICK_S`** — tick interval in seconds (default **30**, min **5**)
- **`OPENMANUS_SKILLS_EXTRA_DIRS`** — semicolon-separated extra roots to scan for `SKILL.md` (override precedence before bundled)
- **`OPENMANUS_MAX_SKILL_INJECT_CHARS`** — cap when inlining full skill into chat (default **24000**)

See [SUPERVISOR.md](SUPERVISOR.md) · [SKILLS_OPENCLAW.md](SKILLS_OPENCLAW.md) · root **`.env.example`**.

## Development commands

- **just:** [justfile](../justfile) — `just`, `just api`, `just test`, `just build-web`, `just check-glama`
- **Manual:** `uv run ruff check src tests`, `uv run pytest`

**Contributing / releases:** [CONTRIBUTING.md](../CONTRIBUTING.md) · [RELEASING.md](../RELEASING.md)

## Glama

[GLAMA.md](GLAMA.md) · root **`glama.json`** (registry `packages` + `mcpServers` metadata).

## CI

GitHub Actions: Ruff, pytest, `web_sota` production build (see `.github/workflows/`).

**Roadmap:** [ARCHITECTURE.md#roadmap-informal](ARCHITECTURE.md#roadmap-informal) · [OpenClaw-style stack](ARCHITECTURE.md#openclaw-style-features-shipped--planned) · [Hierarchical agents](ARCHITECTURE.md#hierarchical-local-agent-fleet-arxiv-informed)

## LM Studio and vLLM notes

- LM Studio is the easiest local single-user path.
- vLLM is usually better for higher concurrency/throughput serving (continuous batching, stronger scheduler).
- For setup details in this project, see [LMSTUDIO.md](LMSTUDIO.md).

← [Documentation index](README.md) · [INSTALL.md](INSTALL.md)
