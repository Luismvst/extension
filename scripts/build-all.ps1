# PowerShell script to build everything from scratch
Write-Host "Building everything from scratch..." -ForegroundColor Cyan

# Set environment variables
$env:EXT_BUILD_SHA = (git rev-parse --short HEAD)
$env:EXT_BUILD_TIME = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
$env:EXT_VERSION = (Get-Date -Format "yyyyMMddHHmmss")

Write-Host "Build Info:" -ForegroundColor Yellow
Write-Host "  EXT_BUILD_SHA: $env:EXT_BUILD_SHA" -ForegroundColor White
Write-Host "  EXT_BUILD_TIME: $env:EXT_BUILD_TIME" -ForegroundColor White
Write-Host "  EXT_VERSION: $env:EXT_VERSION" -ForegroundColor White

# Clean first
Write-Host "`nCleaning artifacts..." -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File scripts/clean-all.ps1

# Build backend
Write-Host "`nBuilding backend..." -ForegroundColor Yellow
docker compose build --no-cache backend

# Build extension
Write-Host "`nBuilding extension..." -ForegroundColor Yellow
docker compose build --no-cache extension-build

# Run extension build
Write-Host "`nRunning extension build..." -ForegroundColor Yellow
docker compose run --rm extension-build sh -c "npm run clean && npm run typecheck && npm run lint && npm run test:unit && npm run build && npm run package:zip"

# Create artifact
Write-Host "`nCreating extension artifact..." -ForegroundColor Yellow
docker compose run --rm extension-artifact

Write-Host "`nBuild completed!" -ForegroundColor Green
Write-Host "Check extension/dist/ for the built extension" -ForegroundColor White
Write-Host "Check extension/out/ for the packaged zip" -ForegroundColor White