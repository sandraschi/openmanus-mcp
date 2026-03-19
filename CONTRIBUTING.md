# Contributing

**Documentation index:** [docs/README.md](docs/README.md) · **How we build:** [docs/HOW_WE_BUILD.md](docs/HOW_WE_BUILD.md)

## Authenticity & quality bar

This repo is **agent-adjacent**; we still ship **reviewed, tested** code. Read **[docs/REPO_HYGIENE.md](docs/REPO_HYGIENE.md)** — what we commit to, what we reject (slop / spam PRs), and how we talk about **AI-assisted** work **without** hiding behind it.

Opening a PR fills **[.github/pull_request_template.md](.github/pull_request_template.md)** automatically.

## Setup

```powershell
git clone https://github.com/sandraschi/openmanus-mcp.git
cd openmanus-mcp
uv sync --extra dev
pre-commit install
```

Optional: install [just](https://just.systems/) and use `just install`, `just test`, `just lint`, `just check-glama`. See [docs/GLAMA.md](docs/GLAMA.md) for `glama.json`.

## Checks

```powershell
uv run ruff check src tests
uv run ruff format src tests
uv run pytest
```

Pre-commit runs Ruff on commit (local dev). CI runs `uv run` Ruff + pytest plus `web_sota` `npm ci` / `npm run build`.

## Fleet (Windows + pywinauto-mcp)

See [docs/FLEET.md](docs/FLEET.md) and `.\scripts\Bootstrap-Fleet.ps1`.

## Supervisor, connectors, skills

New REST surface and chat behavior: [docs/SUPERVISOR.md](docs/SUPERVISOR.md), [docs/SKILLS_OPENCLAW.md](docs/SKILLS_OPENCLAW.md). Bundled skills live under `src/openmanus_mcp/skills/`; extend [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) when you change behavior.

## Releases

See [RELEASING.md](RELEASING.md).
