# openmanus-mcp — https://github.com/casey/just
# Install: https://just.systems/  (Windows: scoop install just  |  choco install just)
# Uses uv; web build needs Node/npm in PATH.

# Default: MCP stdio (Cursor, Glama, etc.)
default: run

# MCP server over stdio
run:
    uv run python -m openmanus_mcp

# FastAPI backend (webapp proxy target), default 127.0.0.1:10768
api:
    uv run python -m openmanus_mcp.run_api

# Python dev env
install:
    uv sync --extra dev

lint:
    uv run ruff check src tests

format:
    uv run ruff format src tests

test:
    uv run pytest

precommit:
    uv run pre-commit run --all-files

build:
    uv build

# Vite production build (from repo root; no cd — works on older `just`)
build-web:
    npm --prefix web_sota ci
    npm --prefix web_sota run build

# Full stack with port clear: PowerShell only (see web_sota/start.ps1)
start-web *ARGS:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File web_sota/start.ps1 {{ARGS}}

# Validate glama.json is parseable JSON (Python, no jq dependency on Windows)
check-glama:
    uv run python -c "import json, pathlib; json.load(pathlib.Path('glama.json').open(encoding='utf-8')); print('glama.json: OK')"
