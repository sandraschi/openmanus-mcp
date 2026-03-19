# openmanus-mcp

![Alpha](https://img.shields.io/badge/status-alpha-orange)
[![CI](https://github.com/sandraschi/openmanus-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sandraschi/openmanus-mcp/actions/workflows/ci.yml)

**FastMCP 3.1** MCP server + **SOTA webapp** wrapping **[OpenManus](https://github.com/FoundationAgents/OpenManus)** (FOSS CLI, **100% local LLM** when you configure Ollama / LM Studio in OpenManus). Not Manus.im.

> **Stability:** **Alpha** — APIs, tools, and config may change. Pin a tag for anything serious; see [RELEASING.md](RELEASING.md).

| Item | Value |
|------|--------|
| **Python** | 3.12+ |
| **Framework** | FastMCP 3.1+, FastAPI, Vite + React |
| **Webapp ports** | Backend **10768**, frontend **10769** ([WEBAPP_PORTS](https://github.com/sandraschi/mcp-central-docs/blob/main/operations/WEBAPP_PORTS.md)) |
| **Standards** | [mcp-central-docs / AGENT_PROTOCOLS](https://github.com/sandraschi/mcp-central-docs/blob/main/standards/AGENT_PROTOCOLS.md) |

**GitHub topics:** `manus` `openmanus` `mcp` `ollama` `local-llm` `zeropaid` `fuckzuck` `cli-wrapper` — see [.github/TOPICS.md](.github/TOPICS.md).

## Status (alpha)

**0.1.0a1** — MCP tool `openmanus_bridge` (`status`, `validate`, `run_prompt` stub), FastAPI health/status, web shell. Subprocess runner + streaming UI planned.

## Quick start

Clone this repo and OpenManus separately (any directory you like):

```powershell
git clone https://github.com/sandraschi/openmanus-mcp.git
cd openmanus-mcp
Copy-Item .env.example .env
# Edit .env: set OPENMANUS_ROOT to your OpenManus clone (see .env.example)
uv sync --extra dev
uv run pytest
uv run python -m openmanus_mcp
```

### Cursor / MCP client

Use the **absolute path to your clone** for `cwd` (Cursor does not expand `~` on Windows the same way everywhere):

```json
{
  "mcpServers": {
    "openmanus-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "openmanus_mcp"],
      "cwd": "/absolute/path/to/openmanus-mcp"
    }
  }
}
```

Set `OPENMANUS_ROOT` in the environment or `.env` in the repo root (`uv` loads from the project directory).

### Webapp

From the **repository root** (the folder that contains `web_sota`):

```powershell
Set-Location $PSScriptRoot
# or: cd <your-clone>\openmanus-mcp

Set-Location .\web_sota
npm install
Set-Location ..
.\web_sota\start.ps1
```

- UI: <http://127.0.0.1:10769> — sidebar **Fleet** for curated onboarding (clone into `fleet/`, install, optional webapp start)  
- API: <http://127.0.0.1:10768/api/v1/health> · fleet APIs under `/api/v1/fleet/*`

## Development

- **Just:** [justfile](justfile) — `just` / `just api` / `just test` / `just build-web` / `just check-glama` ([just.systems](https://just.systems/))
- **Glama:** [glama.json](glama.json) + [docs/GLAMA.md](docs/GLAMA.md) (registry + `mcpServers` block, ports **10768/10769**)
- **Lint / format:** `uv run ruff check src tests` · `uv run ruff format src tests`
- **Pre-commit:** `uv sync --extra dev` then `pre-commit install` (Ruff check + format on commit)
- **Contributing / releases:** [CONTRIBUTING.md](CONTRIBUTING.md) · [RELEASING.md](RELEASING.md)

## MCP tools

| Tool | Purpose |
|------|---------|
| `openmanus_bridge` | `operation=status` \| `validate` \| `run_prompt` (stub) |

## Repo layout

```
src/openmanus_mcp/   # FastMCP server + FastAPI
web_sota/            # Vite React dashboard
tests/
```

## Fleet: “My Computer”–class desktop control

**This repo alone does not give you desktop automation.** For the full composable stack you also install **[pywinauto-mcp](https://github.com/sandraschi/pywinauto-mcp)** (Windows UI MCP) and register **both** servers in your client. **openmanus-mcp** provides the dashboard webapp (**10769**); upstream **pywinauto-mcp** is currently **MCP-only** (no separate webapp in that repo).

**Automate (Windows):** from repo root run `.\scripts\Bootstrap-Fleet.ps1` — clones/siblings **pywinauto-mcp**, creates its `.venv`, `uv pip install -e .`, syncs this repo + `web_sota` npm, and writes **`examples/cursor-fleet.generated.json`** (gitignored) for Cursor. Details: **[docs/FLEET.md](docs/FLEET.md)** · template **`examples/cursor-fleet.template.json`**.

Vendor desktop agents are one bundle; **our** approach is **composable MCP**: OpenManus-style agents plus **[pywinauto-mcp](https://github.com/sandraschi/pywinauto-mcp)** (Win32 click/type/scrape) plus OCR / Windows-ops servers as needed. **High risk** — use VMs, allowlists, and human gates. Architecture: [mcp-central-docs — FLEET_COMPUTER_USE_MCP.md](https://github.com/sandraschi/mcp-central-docs/blob/main/patterns/FLEET_COMPUTER_USE_MCP.md).

## License

MIT
