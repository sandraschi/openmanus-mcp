set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Display the SOTA Industrial Dashboard
default:
    @$lines = Get-Content '{{justfile()}}'; \
    Write-Host ' [SOTA] Industrial Operations Dashboard v1.3.3' -ForegroundColor White -BackgroundColor Cyan; \
    Write-Host '' ; \
    $currentCategory = ''; \
    foreach ($line in $lines) { \
        if ($line -match '^# ── ([^─]+) ─') { \
            $currentCategory = $matches[1].Trim(); \
            Write-Host "`n  $currentCategory" -ForegroundColor Cyan; \
            Write-Host ('  ' + ('─' * 45)) -ForegroundColor Gray; \
        } elseif ($line -match '^# ([^─].+)') { \
            $desc = $matches[1].Trim(); \
            $idx = [array]::IndexOf($lines, $line); \
            if ($idx -lt $lines.Count - 1) { \
                $nextLine = $lines[$idx + 1]; \
                if ($nextLine -match '^([a-z0-9-]+):') { \
                    $recipe = $matches[1]; \
                    $pad = ' ' * [math]::Max(2, (18 - $recipe.Length)); \
                    Write-Host "    $recipe" -ForegroundColor White -NoNewline; \
                    Write-Host "$pad$desc" -ForegroundColor Gray; \
                } \
            } \
        } \
    } \
    Write-Host "`n  [System State: PROD/INDUSTRIAL]" -ForegroundColor DarkGray; \
    Write-Host ''

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute Ruff linting
lint:
    uv run ruff check .

# Execute Ruff fix and formatting
fix:
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .

# Python dev env sync
install:
    uv sync --extra dev

# Execute unit and integration tests
test:
    uv run pytest

# ── Hardening ─────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    uv run bandit -r src/

# Execute dependency safety audit
audit-deps:
    uv run safety check

# Validate glama.json integrity
check-glama:
    uv run python -c "import json, pathlib; json.load(pathlib.Path('glama.json').open(encoding='utf-8')); print('glama.json: OK')"

# ── Fleet ─────────────────────────────────────────────────────────────────────

# Bootstrap sibling repos and generate snippets (PowerShell)
bootstrap-fleet:
    pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/Bootstrap-Fleet.ps1

# ── MCPB ──────────────────────────────────────────────────────────────────────

# Build the .mcpb standalone bundle (SOTA v2.0)
build-mcpb:
    pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/build_mcpb.ps1

# ── Manus Core ────────────────────────────────────────────────────────────────

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

# ── Webapp ────────────────────────────────────────────────────────────────────

# Build Vite production assets
build-web:
    npm --prefix web_sota ci
    npm --prefix web_sota run build

# Start dashboard with port recovery (PowerShell)
start-web *ARGS:
    pwsh.exe -NoProfile -ExecutionPolicy Bypass -File web_sota/start.ps1 {{ARGS}}

# ── System ────────────────────────────────────────────────────────────────────

# Run the MCP server over stdio (default)
run:
    uv run python -m openmanus_mcp

# Run the FastAPI bridge backend
api:
    uv run python -m openmanus_mcp.run_api

# Repository statistics
stats:
    uv run python tools/repo_stats.py
