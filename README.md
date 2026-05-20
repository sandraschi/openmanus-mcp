# openmanus-mcp — MCP bridge + dashboard for OpenManus

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>

FastMCP 3.2 server that wraps [OpenManus](https://github.com/FoundationAgents/OpenManus) (FOSS agent framework) into MCP tools, with a SOTA fleet webapp dashboard.

Includes **Windows-native computer use** (mouse/keyboard/screenshot via win32 API) and **bash execution** — both with security hardening.

## Architecture

```
MCP hosts ←→ openmanus-mcp (FastMCP 3.2, stdio)
                   ↕ subprocess / REST
              OpenManus agent
                   ├── bash (denylisted)
                   ├── computer (local win32)
                   ├── python_execute (restricted)
                   ├── browser_use (Playwright)
                   └── str_replace_editor (workspace-scoped)
```

- **FastAPI** backend on `:10768` — `/api/v1/*` for webapp + fleet
- **Vite + React** dashboard on `:10769` — SOTA fleet standards
- **OpenManus** fork at `sandraschi/OpenManus` — security-hardened

## Features

| Capability | Detail |
|------------|--------|
| **Computer use** | Windows-native mouse/keyboard/screenshot (win32 API, no Docker/cloud needed) |
| **Bash execution** | Full terminal with denylist (rm -rf /, sudo, useradd, dd blocked) |
| **Python execution** | Restricted builtins — os/subprocess/socket imports blocked |
| **Web browsing** | Playwright-based browser automation |
| **File editing** | Read/write/edit files scoped to workspace root |
| **API security** | Optional Bearer token auth on all REST endpoints |
| **Fleet integration** | Registered in mcp-central-docs, fleet discovery, glama.json |

## Ports

| Port | Service |
|------|---------|
| 10768 | Backend (FastAPI) |
| 10769 | Frontend (Vite) |

## Quick Start

```powershell
git clone https://github.com/sandraschi/openmanus-mcp
cd openmanus-mcp
just
```

This opens an interactive dashboard showing all available commands. Run `just bootstrap` to install dependencies, then `just serve` or `just dev` to start.

### Manual Setup

If you don't have `just` installed:
# Start everything
.\web_sota\start.ps1
# Or individually:
uv run python -m openmanus_mcp           # MCP server
uv run python -m openmanus_mcp.run_api   # FastAPI backend
cd web_sota && npm run dev               # Frontend
### Configuration
Set `OPENMANUS_MCP_API_KEY` for API authentication:
$env:OPENMANUS_MCP_API_KEY = "your-secret-key"
If not set, a random key is auto-generated and written to `.api_key`.

## Security

See [SECURITY.md](SECURITY.md) and [Upstream SECURITY.md](https://github.com/sandraschi/OpenManus/blob/main/SECURITY.md).

| Tool | Risk | Mitigation |
|------|------|-----------|
| `bash` | Critical | Denylist + obfuscation detection |
| `computer` | High | Confirmation gate (blocked in headless) |
| `python_execute` | High | Restricted builtins |
| `str_replace_editor` | Moderate | Workspace-scoped paths |
| API | High | Optional Bearer auth |

## Requirements

- Python 3.12+
- uv
- OpenManus fork (`sandraschi/OpenManus`)
- Windows (for computer use tool; bash works cross-platform)
