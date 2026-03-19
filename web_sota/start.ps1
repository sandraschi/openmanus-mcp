# SOTA webapp: FastAPI 10768, Vite 10769. Run from repo root: .\web_sota\start.ps1
# Optional: .\web_sota\start.ps1 -Build  (runs npm run build before dev — WEBAPP_STANDARDS lifecycle)
param(
    [switch]$Build
)
$BackendPort = 10768
$FrontendPort = 10769
$ApiHealth = "http://127.0.0.1:$BackendPort/api/v1/health"
$MaxWaitSec = 30

if (Test-Path (Join-Path $PSScriptRoot "package.json")) {
    $WebSotaRoot = $PSScriptRoot
    $RepoRoot = Split-Path -Parent $WebSotaRoot
} else {
    $RepoRoot = $PSScriptRoot
    $WebSotaRoot = Join-Path $RepoRoot "web_sota"
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
npm run dev
