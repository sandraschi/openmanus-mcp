# Changelog

## [Unreleased]

### Fixed
- **`openmanus_sample_relay`**: Implemented real FastMCP 3.2 sampling via `ctx.sample()` — delegates sub-task reasoning to the host LLM (Claude Desktop, Cursor, etc.) with a planning-focused system prompt. Gracefully degrades with an explanatory string when the client doesn't support sampling rather than raising.
- **`openmanus_bridge`**: Eliminated redundant `get_settings()` double-call — `Settings` is now instantiated once per request and passed via `BridgeContext`, avoiding double env/file reads.
- **Startup log key collision**: Renamed warning-branch log events to `openmanus_mcp_startup_warn` so `openmanus_mcp_startup` is no longer emitted twice with different severities, which broke log filtering.
- **`list_skills_resources` inline import**: Removed `from fastmcp import Resource` inside the function body — `Resource` and `Context` are now imported at module level alongside `FastMCP`.
- **`pyproject.toml`**: Pinned `fastmcp>=3.2.4,<4` (was `>=3.2.0`) to track current release.

### Added
- **Subprocess runner:** `runner.py` — `main.py` uses **`--prompt`** when the prompt is a single line; multiline → stdin. **`run_flow.py`** via stdin. REST **`POST /api/v1/run`**, **`/run/async`**, **`GET /api/v1/run/jobs/{id}`**.
- **`job_store.py`:** bounded **FIFO eviction** for completed async jobs (`OPENMANUS_JOB_STORE_MAX_COMPLETED`); separate stores for **MCP** vs **API** process.
- **web_sota (WEBAPP_STANDARDS):** **Iron Shell** topbar + sidebar, **Run** page (sync/async + poll), **Logger** panel (auto-scroll pause), **AutoResizeTextarea**, **Help** stub.
- **`tests/conftest.py`** — reset job stores between tests; **`test_job_store.py`**, extended **`test_runner`** fakes for `--prompt`.
- **[docs/REPO_HYGIENE.md](docs/REPO_HYGIENE.md)** — authenticity / anti-slop signals, AI-assisted transparency, spam stance; **GitHub-scale noise** (AI PR/issue floods, poisoning/sabotage, **centaur** accountability gaps, **agent-fleet** trolling); **plain-English** gloss for **Sybil** / poisoning / centaur; **2026 arms-race** note (**DTU** / public **dark-app-factory** on GitHub; **Bastio** / bastio.com gateway pointer, threat landscape); **ORB** roadmap pointer
- **[.github/pull_request_template.md](.github/pull_request_template.md)** — review checklist (tests, docs, optional LLM note)

## [0.1.0b1] - 2026-03-19

### Changed
- **Beta** channel (was alpha): `pyproject` **0.1.0b1**, Trove `Development Status :: 4 - Beta`, **`glama.json`** `status` + versions, **`web_sota`** `0.1.0-beta.1`
- **README:** centered **SVG banner**, badge row, snappy pitch, **Honest visibility** section (demo, topics, Glama, 1k-star realism vs OpenClaw/OpenFang lighthouse)
- **[.github/TOPICS.md](.github/TOPICS.md):** paste-ready **GitHub description** + **20 topic** `gh` recipe for search discovery
- **[docs/assets/](docs/assets/):** `banner.svg` + README for optional **Nano Banana / Veo** hero + demo files
- **Docs:** [RELEASING.md](RELEASING.md) examples use **beta** tags; [TECH.md](docs/TECH.md) / [OPENMANUS.md](docs/OPENMANUS.md) wording **beta** (was alpha)

## [0.1.0a1] - 2026-03-19

### Added
- **[docs/HOW_WE_BUILD.md](docs/HOW_WE_BUILD.md)** — how building works: **§1** Karpathy-linked vibe coding / agentic engineering (vibeCODING-as-typist outdated; ship sailed); **§2** repo basics; Cursor & Antigravity; free/local LLMs; daily FOSS trawl; Opus 4.6-style integration pass; fleet; **zeropaid**
- Roadmap: **OpenClaw- / OpenFang-class** stepwise plan (heartbeat, comms connectors, skills, multi-agentic) + **hierarchical local agent fleet** (arXiv-informed); [ARCHITECTURE.md](docs/ARCHITECTURE.md) section + README [Planned / TODO](README.md#planned--todo)
- **[docs/FLEET_CONTEXT.md](docs/FLEET_CONTEXT.md)** + README blurb: sandraschi MCP fleet (months, mostly private), MCP + React pattern, OpenManus / robotics / Resonite / World Labs examples
- README **Planned / TODO:** **My robots** roadmap (Yahboom-class → Dreame/Xiaomi hoovers → Noetix/Bumi-class Androids; virtual + real parallel handling); expanded in [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Staggered docs:** [docs/README.md](docs/README.md) hub + [INSTALL](docs/INSTALL.md), [TECH](docs/TECH.md), [MANUS](docs/MANUS.md), [OPENMANUS](docs/OPENMANUS.md), [ARCHITECTURE](docs/ARCHITECTURE.md), [SAFETY](docs/SAFETY.md); root [README.md](README.md) shortened; [SECURITY.md](SECURITY.md)
- **Fleet automation:** `scripts/Bootstrap-Fleet.ps1`, `docs/FLEET.md`, `examples/cursor-fleet.template.json` — documents pywinauto-mcp requirement and generates Cursor MCP snippet (generated file gitignored)
- **Fleet onboarding UI:** webapp **Fleet** page + REST `GET/POST /api/v1/fleet/*` — curated catalog in `data/fleet_catalog.json`, clones to `fleet/`, `.fleet_state.json`, optional PowerShell webapp launch (Windows)
- **`justfile`** (run, api, install, lint, format, test, precommit, build, build-web, start-web, check-glama)
- **Glama:** expanded **`glama.json`** (metadata + `mcpServers` webapp URLs) and **`docs/GLAMA.md`**
- **Alpha** release channel; PyPI classifiers and README status badges
- CI (Ruff + pytest + `web_sota` build), pre-commit (Ruff check + format), release workflow on `v*` tags
- `__version__` from installed package metadata (`importlib.metadata`)

### Changed
- README / `.env.example` / `.cursorrules`: removed machine-specific paths; portable clone + `cwd` guidance

## [0.1.0] - 2026-03-19

Superseded by **0.1.0a1** / **0.1.0b1** pre-releases; kept for history.

### Added
- FastMCP 3.1 server: `openmanus_bridge` (status, validate, run_prompt stub)
- FastAPI backend (10768): `/api/v1/health`, `/api/v1/status`
- SOTA web shell (10769): Vite + React, glass sidebar, dashboard cards
- `start.ps1` / `start.bat`, `glama.json`, `.cursorrules`
- `OPENMANUS_ROOT` detection for upstream clone
