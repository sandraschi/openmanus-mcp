param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$Build,
    [switch]$Engine,
    [switch]$NoBrowser,
    [int]$BackendPort = 10768,
    [int]$FrontendPort = 10769
)

$RepoRoot = Split-Path -Parent $PSScriptRoot
$FleetStartPath = Join-Path $RepoRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath
$FleetStart = Initialize-FleetStartMode @PSBoundParameters
Enter-FleetHeadlessConsole -Headless:$Headless -BackendOnly:$BackendOnly
Stop-FleetPortSquatters -Ports @($BackendPort, $FrontendPort) -Label "openmanus-mcp"

if (-not (Assert-FleetPortsAvailable -Ports @($BackendPort, $FrontendPort) -Label "openmanus-mcp")) { exit 1 }

# SOTA webapp: FastAPI 10768, Vite 10769. Run from repo root: .\web_sota\start.ps1
# Optional: .\web_sota\start.ps1 -Build  (runs npm run build before dev - WEBAPP_STANDARDS lifecycle)
$ApiHealth = "http://127.0.0.1:$BackendPort/api/v1/health"
$MaxWaitSec = 90

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


$env:OPENMANUS_MCP_API_PORT = "$BackendPort"
$env:OPENMANUS_MCP_API_HOST = "127.0.0.1"
$env:OPENMANUS_MCP_UI_PORT = "$FrontendPort"

Write-Host "Starting FastAPI backend on $BackendPort ..."
$backendCmd = "Set-Location '$RepoRoot'; `$env:OPENMANUS_MCP_API_PORT='$BackendPort'; `$env:OPENMANUS_MCP_API_HOST='127.0.0.1'; uv run --project '$RepoRoot' python -m openmanus_mcp.run_api"
$backendProc = Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Normal", "-Command", $backendCmd -PassThru

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

if (-not $FleetStart.RunFrontend) {
    while ($true) { Start-Sleep -Seconds 60 }
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



