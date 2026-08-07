set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
import 'scripts/just/fleet.just'

# --- Dashboard ---

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# --- Quality ---

# Execute Ruff linting
lint:
    uv run ruff check .
    Set-Location '{{justfile_directory()}}\web_sota'
    npx @biomejs/biome ci .

# Execute Ruff fix and formatting
fix:
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .
    Set-Location '{{justfile_directory()}}\web_sota'
    npx @biomejs/biome check --write .

# Python dev env sync
install:
    uv sync --extra dev

# Execute unit and integration tests
test:
    uv run pytest

# --- Hardening ---

# Execute Bandit security audit
check-sec:
    uv run bandit -r src/

# Execute dependency safety audit
audit-deps:
    uv run safety check

# Validate glama.json integrity
check-glama:
    uv run python -c "import json, pathlib; json.load(pathlib.Path('glama.json').open(encoding='utf-8')); print('glama.json: OK')"

# --- Fleet ---

# Bootstrap sibling repos and generate snippets (PowerShell)
bootstrap-fleet:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/Bootstrap-Fleet.ps1

# --- MCPB ---

# Build the .mcpb standalone bundle (SOTA v2.0)
build-mcpb:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/build_mcpb.ps1

# --- Manus Core ---

# Detect OpenManus local installation
detect:
    uv run python -m openmanus_mcp.openmanus_detect

# List discovered OpenClaw-style skills
skills:
    uv run python -m openmanus_mcp.skills_catalog

# Dry-run validation of the bridge (no subprocess)
bridge-test op="validate":
    uv run python -m openmanus_mcp.bridge_dry_run {{op}}

# System diagnostic and GPU info
diag:
    uv run python -m openmanus_mcp.system_info

# --- Webapp ---

# Build Vite production assets
build-web:
    npm --prefix web_sota ci
    npm --prefix web_sota run build

# Start dashboard with port recovery (PowerShell)
start-web *ARGS:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File web_sota/start.ps1 {{ARGS}}

# --- System ---

# Run the MCP server over stdio (default)
run:
    uv run python -m openmanus_mcp

# Run the FastAPI bridge backend
api:
    uv run python -m openmanus_mcp.run_api

# Repository statistics
stats:
    uv run python tools/repo_stats.py

# Bootstrap: install dev deps + pre-commit hook
bootstrap:
    uv sync --group dev
    uv run pre-commit install
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green