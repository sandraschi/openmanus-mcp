# Contributing

## Setup

```powershell
git clone https://github.com/sandraschi/openmanus-mcp.git
cd openmanus-mcp
uv sync --extra dev
pre-commit install
```

## Checks

```powershell
uv run ruff check src tests
uv run ruff format src tests
uv run pytest
```

Pre-commit runs Ruff on commit (local dev). CI runs `uv run` Ruff + pytest plus `web_sota` `npm ci` / `npm run build`.

## Fleet (Windows + pywinauto-mcp)

See [docs/FLEET.md](docs/FLEET.md) and `.\scripts\Bootstrap-Fleet.ps1`.

## Releases

See [RELEASING.md](RELEASING.md).
