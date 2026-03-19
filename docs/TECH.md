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
  __main__.py          # stdio MCP entry
  server.py            # FastMCP + openmanus_bridge
  run_api.py           # uvicorn
  api/app.py           # FastAPI app + CORS
  api/fleet_routes.py  # fleet REST
  fleet/               # onboard service
  data/fleet_catalog.json
web_sota/              # React dashboard
fleet/                 # local clones (gitignored except .gitkeep)
tests/
```

## MCP tools

| Tool | Operations (v0.1 alpha) |
|------|-------------------------|
| `openmanus_bridge` | `status`, `validate`, `run_prompt` (stub) |

Docstrings follow portmanteau / enhanced-response patterns from central docs.

## REST API (selected)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | Liveness |
| GET | `/api/v1/status` | OpenManus path probe |
| GET | `/api/v1/fleet/catalog` | Curated fleet list + onboard state |
| GET | `/api/v1/fleet/members` | Onboarded members detail |
| POST | `/api/v1/fleet/onboard` | Clone + install |
| POST | `/api/v1/fleet/webapp/start` | Windows PowerShell launch |

Vite proxies **`/api`** → **10768**.

## Environment variables

See **`.env.example`**. Notable:

- **`OPENMANUS_ROOT`** — upstream OpenManus clone
- **`OPENMANUS_FLEET_ROOT`** — fleet workspace (optional)
- **`OPENMANUS_MCP_API_HOST`** / **`OPENMANUS_MCP_API_PORT`**

## Development commands

- **just:** [justfile](../justfile) — `just`, `just api`, `just test`, `just build-web`, `just check-glama`
- **Manual:** `uv run ruff check src tests`, `uv run pytest`

**Contributing / releases:** [CONTRIBUTING.md](../CONTRIBUTING.md) · [RELEASING.md](../RELEASING.md)

## Glama

[GLAMA.md](GLAMA.md) · root **`glama.json`** (registry `packages` + `mcpServers` metadata).

## CI

GitHub Actions: Ruff, pytest, `web_sota` production build (see `.github/workflows/`).

**Roadmap (incl. My robots):** [ARCHITECTURE.md#roadmap-informal](ARCHITECTURE.md#roadmap-informal)

← [Documentation index](README.md) · [INSTALL.md](INSTALL.md)
