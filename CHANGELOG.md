# Changelog

## [Unreleased]

### Added
- **Fleet automation:** `scripts/Bootstrap-Fleet.ps1`, `docs/FLEET.md`, `examples/cursor-fleet.template.json` — documents pywinauto-mcp requirement and generates Cursor MCP snippet (generated file gitignored)
- **Fleet onboarding UI:** webapp **Fleet** page + REST `GET/POST /api/v1/fleet/*` — curated catalog in `data/fleet_catalog.json`, clones to `fleet/`, `.fleet_state.json`, optional PowerShell webapp launch (Windows)
- **`justfile`** (run, api, install, lint, format, test, precommit, build, build-web, start-web, check-glama)
- **Glama:** expanded **`glama.json`** (metadata + `mcpServers` webapp URLs) and **`docs/GLAMA.md`**

## [0.1.0a1] - 2026-03-19

### Added
- **Alpha** release channel; PyPI classifiers and README status badges
- CI (Ruff + pytest + `web_sota` build), pre-commit (Ruff check + format), release workflow on `v*` tags
- `__version__` from installed package metadata (`importlib.metadata`)

### Changed
- README / `.env.example` / `.cursorrules`: removed machine-specific paths; portable clone + `cwd` guidance

## [0.1.0] - 2026-03-19

Superseded by **0.1.0a1** (alpha); kept for history.

### Added
- FastMCP 3.1 server: `openmanus_bridge` (status, validate, run_prompt stub)
- FastAPI backend (10768): `/api/v1/health`, `/api/v1/status`
- SOTA web shell (10769): Vite + React, glass sidebar, dashboard cards
- `start.ps1` / `start.bat`, `glama.json`, `.cursorrules`
- `OPENMANUS_ROOT` detection for upstream clone
