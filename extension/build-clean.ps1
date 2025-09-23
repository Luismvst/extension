# Clean build script for Chrome Extension
Write-Host "=== CLEAN BUILD CHROME EXTENSION ===" -ForegroundColor Cyan

# Clean previous builds
Write-Host "`n1. Cleaning previous builds..." -ForegroundColor Yellow
Remove-Item -Recurse -Force dist, out, .vite, .turbo, coverage, artifacts -ErrorAction SilentlyContinue
Write-Host "✅ Cleaned build directories" -ForegroundColor Green

# Check if Node.js is available
Write-Host "`n2. Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not available. Please install Node.js to build the extension." -ForegroundColor Red
    exit 1
}

# Check if npm is available
Write-Host "`n3. Checking npm..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version
    Write-Host "✅ npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not available. Please install npm to build the extension." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`n4. Installing dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Type check
Write-Host "`n5. Running type check..." -ForegroundColor Yellow
npm run typecheck
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Type check passed" -ForegroundColor Green
} else {
    Write-Host "❌ Type check failed" -ForegroundColor Red
    exit 1
}

# Lint check
Write-Host "`n6. Running lint check..." -ForegroundColor Yellow
npm run lint
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Lint check passed" -ForegroundColor Green
} else {
    Write-Host "❌ Lint check failed" -ForegroundColor Red
    exit 1
}

# Build extension
Write-Host "`n7. Building extension..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Extension built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Extension build failed" -ForegroundColor Red
    exit 1
}

# Verify build
Write-Host "`n8. Verifying build..." -ForegroundColor Yellow
if (Test-Path "dist/manifest.json") {
    $manifest = Get-Content "dist/manifest.json" | ConvertFrom-Json
    Write-Host "✅ Manifest v$($manifest.manifest_version) - Version $($manifest.version)" -ForegroundColor Green
    
    Write-Host "`nGenerated files:" -ForegroundColor Gray
    Get-ChildItem "dist" | ForEach-Object { 
        Write-Host "  - $($_.Name)" -ForegroundColor Gray 
    }
} else {
    Write-Host "❌ Extension not built correctly" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== BUILD COMPLETE ===" -ForegroundColor Cyan
Write-Host "Extension ready to load in Chrome:" -ForegroundColor Green
Write-Host "- Go to chrome://extensions/" -ForegroundColor White
Write-Host "- Enable 'Developer mode'" -ForegroundColor White
Write-Host "- Click 'Load unpacked'" -ForegroundColor White
Write-Host "- Select the 'dist' folder" -ForegroundColor White
Write-Host "`nExtension location: $((Get-Location).Path)\dist" -ForegroundColor Cyan
