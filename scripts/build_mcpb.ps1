# build_mcpb.ps1 - openmanus-mcp SOTA Builder
# Creates the .mcpb bundle for standalone distribution.

$projectName = "openmanus-mcp"
$distDir = Join-Path $PSScriptRoot "..\dist"
$mcpbPath = Join-Path $distDir "$projectName.mcpb"

Write-Host "🚧 Building $projectName MCPB bundle..." -ForegroundColor Cyan

# 1. Clean dist
if (Test-Path $distDir) {
    Remove-Item -Recurse -Force $distDir
}
New-Item -ItemType Directory -Path $distDir | Out-Null

# 2. Sync dependencies
Write-Host "📦 Syncing uv dependencies..." -ForegroundColor Gray
uv lock --upgrade

# 3. Build MCPB Bundle (SOTA v2.0)
# Uses npx to ensure the latest @anthropic-ai/mcpb is used without global install.
# The CLI respects .mcpbignore to exclude .venv, tests, etc.
Write-Host "📦 Bundling into $mcpbPath..." -ForegroundColor Gray

# Ensure dist exists
if (!(Test-Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir | Out-Null
}

npx -y @anthropic-ai/mcpb pack . $mcpbPath

if ($?) {
    Write-Host "✅ SOTA Build Complete: $mcpbPath" -ForegroundColor Green
} else {
    Write-Host "❌ Build Failed: Could not generate .mcpb bundle." -ForegroundColor Red
    exit 1
}
