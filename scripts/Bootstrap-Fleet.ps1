#Requires -Version 5.1
<#
.SYNOPSIS
  Clone pywinauto-mcp (sibling of this repo), install deps, sync openmanus-mcp + web_sota, emit Cursor MCP snippet.

.DESCRIPTION
  Run from the openmanus-mcp repository root, or any path (script resolves repo root).

.PARAMETER SiblingRoot
  Directory that should contain pywinauto-mcp next to openmanus-mcp. Default: parent of this repo.

.PARAMETER SkipNpm
  Skip npm install in web_sota.

.PARAMETER SkipPyWinAuto
  Skip clone + venv + pip install for pywinauto-mcp (still writes snippet if that repo exists).

.PARAMETER Face
  Install pywinauto-mcp with optional [face] extra (heavier dependencies).

.EXAMPLE
  .\scripts\Bootstrap-Fleet.ps1
#>
param(
    [string] $SiblingRoot = "",
    [switch] $SkipNpm,
    [switch] $SkipPyWinAuto,
    [switch] $Face
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")
if (-not $SiblingRoot) {
    $SiblingRoot = Split-Path -Parent $RepoRoot.Path
}
else {
    $SiblingRoot = (Resolve-Path $SiblingRoot).Path
}

$PyWinAutoRoot = Join-Path $SiblingRoot "pywinauto-mcp"
$PyWinAutoUrl = "https://github.com/sandraschi/pywinauto-mcp.git"
$GeneratedSnippet = Join-Path $RepoRoot "examples\cursor-fleet.generated.json"

Write-Host "openmanus-mcp root: $($RepoRoot.Path)"
Write-Host "Sibling root:       $SiblingRoot"
Write-Host "pywinauto-mcp path: $PyWinAutoRoot"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "git is not on PATH."
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv is not on PATH. Install from https://docs.astral.sh/uv/"
}

Push-Location $RepoRoot.Path
try {
    Write-Host "`n[openmanus-mcp] uv sync --extra dev"
    uv sync --extra dev

    if (-not $SkipNpm) {
        $WebSota = Join-Path $RepoRoot.Path "web_sota"
        if (Test-Path $WebSota) {
            Push-Location $WebSota
            try {
                Write-Host "`n[web_sota] npm install"
                npm install
            }
            finally {
                Pop-Location
            }
        }
    }
}
finally {
    Pop-Location
}

if (-not $SkipPyWinAuto) {
    if (-not (Test-Path $PyWinAutoRoot)) {
        Write-Host "`n[pywinauto-mcp] git clone -> $PyWinAutoRoot"
        git clone $PyWinAutoUrl $PyWinAutoRoot
    }
    else {
        Write-Host "`n[pywinauto-mcp] already present: $PyWinAutoRoot"
    }

    Push-Location $PyWinAutoRoot
    try {
        if (-not (Test-Path (Join-Path $PyWinAutoRoot ".venv"))) {
            Write-Host "[pywinauto-mcp] uv venv"
            uv venv
        }
        $pyExe = Join-Path $PyWinAutoRoot ".venv\Scripts\python.exe"
        if (-not (Test-Path $pyExe)) {
            Write-Error "Expected venv python at $pyExe"
        }
        if ($Face) {
            Write-Host "[pywinauto-mcp] uv pip install -e .[face]"
            uv pip install -e ".[face]"
        }
        else {
            Write-Host "[pywinauto-mcp] uv pip install -e ."
            uv pip install -e .
        }
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Host "`n[pywinauto-mcp] skipped (-SkipPyWinAuto)"
}

if (-not (Test-Path (Join-Path $RepoRoot.Path "examples"))) {
    New-Item -ItemType Directory -Path (Join-Path $RepoRoot.Path "examples") | Out-Null
}

$pywinPy = Join-Path $PyWinAutoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pywinPy)) {
    Write-Warning "pywinauto venv python not found at $pywinPy - edit generated snippet manually."
    $pywinPy = "REPLACE_WITH_ABSOLUTE_PATH_TO_PYWINAUTO_VENV_PYTHON"
}

$snippet = [ordered]@{
    mcpServers = [ordered]@{
        "openmanus-mcp" = [ordered]@{
            command = "uv"
            args      = @("run", "python", "-m", "openmanus_mcp")
            cwd       = $RepoRoot.Path
        }
        "pywinauto-mcp" = [ordered]@{
            command = $pywinPy
            args    = @("-m", "pywinauto_mcp")
            cwd     = $pywinCwd
        }
    }
}

$json = $snippet | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($GeneratedSnippet, $json, [System.Text.UTF8Encoding]::new($false))
Write-Host "`nWrote: $GeneratedSnippet"
Write-Host "Merge mcpServers into your Cursor MCP JSON (User or Project)."
Write-Host "Start openmanus dashboard: .\web_sota\start.ps1"
Write-Host "pywinauto-mcp: no upstream webapp in repo today - MCP tools only."
