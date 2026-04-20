Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# SOTA webapp: FastAPI 10768, Vite 10769. Run from repo root: .\web_sota\start.ps1
# Optional: .\web_sota\start.ps1 -Build  (runs npm run build before dev â€” WEBAPP_STANDARDS lifecycle)
param(
    [switch]$Build,
    [switch]$Engine,
    [int]$BackendPort = 10768,
    [int]$FrontendPort = 10769
)
$ApiHealth = "http://127.0.0.1:$BackendPort/api/v1/health"
$MaxWaitSec = 30

if (Test-Path (Join-Path $PSScriptRoot "package.json")) {
    $WebSotaRoot = $PSScriptRoot
    $RepoRoot = Split-Path -Parent $WebSotaRoot
} else {
    $RepoRoot = $PSScriptRoot
    $WebSotaRoot = Join-Path $RepoRoot "web_sota"
}

# 1. Load OPENMANUS_ROOT from .env if not already set
$envFile = Join-Path $RepoRoot ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | Where-Object { $_ -match "^OPENMANUS_ROOT=(.+)" } | ForEach-Object {
        $val = $matches[1].Trim().Trim('"').Trim("'")
        if (-not $env:OPENMANUS_ROOT) { $env:OPENMANUS_ROOT = $val }
    }
}

# 2. Optionally Start OpenManus Engine (CLI)
if ($Engine) {
    if (-not $env:OPENMANUS_ROOT) {
        Write-Host "WARNING: -Engine requested but OPENMANUS_ROOT is not set in environment or .env" -ForegroundColor Yellow
    } elseif (-not (Test-Path $env:OPENMANUS_ROOT)) {
        Write-Host "ERROR: OPENMANUS_ROOT points to non-existent path: $($env:OPENMANUS_ROOT)" -ForegroundColor Red
    } else {
        Write-Host "Launching OpenManus CLI in new window (Root: $($env:OPENMANUS_ROOT)) ..." -ForegroundColor Cyan
        $engineTitle = "OpenManus Engine (Bridge: $FrontendPort)"
        # Use Start-Process with powershell to keep a persistent window
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$Host.UI.RawUI.WindowTitle = '$engineTitle'; cd '$($env:OPENMANUS_ROOT)'; uv run python main.py"
    }
}


function Stop-PortProcess {
    param([int]$Port)
    $conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($conn) {
        $procId = $conn.OwningProcess | Select-Object -First 1 -Unique
        if ($procId) {
            Write-Host "Stopping process on port $Port (PID: $procId)"
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
        }
    }
}

Write-Host "Clearing ports $BackendPort / $FrontendPort ..."
Stop-PortProcess -Port $BackendPort
Stop-PortProcess -Port $FrontendPort

$env:OPENMANUS_MCP_API_PORT = "$BackendPort"
$env:OPENMANUS_MCP_API_HOST = "127.0.0.1"
$env:OPENMANUS_MCP_UI_PORT = "$FrontendPort"

Write-Host "Starting FastAPI backend on $BackendPort ..."
$backendProc = Start-Process -FilePath "uv" -ArgumentList "run", "python", "-m", "openmanus_mcp.run_api" -WorkingDirectory $RepoRoot -PassThru -NoNewWindow

$waited = 0
$BackendStarted = $false
while ($waited -lt $MaxWaitSec) {
    try {
        $r = Invoke-WebRequest -Uri $ApiHealth -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($r.StatusCode -eq 200) {
            $BackendStarted = $true
            Write-Host "Backend OK: $ApiHealth"
            break
        }
    } catch {
        if (-not $backendProc.HasExited) { Start-Sleep -Seconds 2 }
        $waited += 2
    }
}
if (-not $BackendStarted) {
    Write-Host "WARNING: Backend did not respond within ${MaxWaitSec}s. Check uv run from repo root."
}

Write-Host "Starting Vite on $FrontendPort ..."
Set-Location $WebSotaRoot
if (-not (Test-Path "node_modules")) {
    npm install
}
if ($Build) {
    Write-Host "npm run build (Build switch) ..."
    npm run build
}
$env:VITE_DEV_PORT = "$FrontendPort"
$env:VITE_API_TARGET = "http://127.0.0.1:$BackendPort"
npm run dev -- --port $FrontendPort --host 127.0.0.1

