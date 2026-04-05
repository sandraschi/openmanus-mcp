set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Display the SOTA Industrial Dashboard
default:
    @powershell -NoLogo -Command " \
        $lines = Get-Content '{{justfile()}}'; \
        Write-Host ' [SOTA] Industrial Operations Dashboard v1.3.1' -ForegroundColor White -BackgroundColor Cyan; \
        Write-Host '' ; \
        $currentCategory = ''; \
        foreach ($line in $lines) { \
            if ($line -match '^# ── ([^─]+) ─') { \
                $currentCategory = $matches[1].Trim(); \
                Write-Host \"`n  $currentCategory\" -ForegroundColor Cyan; \
                Write-Host '  ' + ('─' * 45) -ForegroundColor Gray; \
            } elseif ($line -match '^# ([^─].+)') { \
                $desc = $matches[1].Trim(); \
                $idx = [array]::IndexOf($lines, $line); \
                if ($idx -lt $lines.Count - 1) { \
                    $nextLine = $lines[$idx + 1]; \
                    if ($nextLine -match '^([a-z0-9-]+):') { \
                        $recipe = $matches[1]; \
                        $pad = ' ' * [math]::Max(2, (18 - $recipe.Length)); \
                        Write-Host \"    $recipe\" -ForegroundColor White -NoNewline; \
                        Write-Host \"$pad$desc\" -ForegroundColor Gray; \
                    } \
                } \
            } \
        } \
        Write-Host \"`n  [System State: PROD/HARDENED]\" -ForegroundColor DarkGray; \
        Write-Host ''"

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute Ruff SOTA v13.1 linting
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check .

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .

# ── Hardening ─────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run safety check

# openmanus-mcp — https://github.com/casey/just
# Install: https://just.systems/  (Windows: scoop install just  |  choco install just)
# Uses uv; web build needs Node/npm in PATH.

stats:
    uv run python tools/repo_stats.py

# Default: MCP stdio (Cursor, Glama, etc.)
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
