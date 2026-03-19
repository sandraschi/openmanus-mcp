# web_sota — openmanus-mcp dashboard

Vite + React UI proxied to the FastAPI backend.

## Ports

| | Port |
|--|------|
| Dev server | **10769** |
| API (see repo root) | **10768** |

## Features (high level)

- **Fleet** — curated MCP onboarding
- **Run** — OpenManus sync/async + **activity** presets (build, ops, research, debug, **comms**, **robots**, **media**)
- **SOTA Chat** — local Ollama / LM Studio; **OpenClaw-style skills** (compact index + optional full `SKILL.md` per checkbox)
- **Logger**, **Help**, **Settings**, **Dashboard**

## Run

From repo root:

```powershell
Set-Location .\web_sota
npm install
Set-Location ..
.\web_sota\start.ps1
```

Canonical docs: [../docs/INSTALL.md](../docs/INSTALL.md) · [../docs/TECH.md](../docs/TECH.md) · [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
