# PowerShell script to verify build artifacts
Write-Host "🔍 Verifying build artifacts..." -ForegroundColor Cyan

# Check if extension/dist exists
if (Test-Path "extension/dist") {
    Write-Host "✅ extension/dist exists" -ForegroundColor Green
    
    # Check manifest.json
    if (Test-Path "extension/dist/manifest.json") {
        Write-Host "✅ manifest.json exists" -ForegroundColor Green
        
        # Read and display manifest info
        $manifest = Get-Content "extension/dist/manifest.json" | ConvertFrom-Json
        Write-Host "  Name: $($manifest.name)" -ForegroundColor White
        Write-Host "  Version: $($manifest.version)" -ForegroundColor White
        Write-Host "  Manifest Version: $($manifest.manifest_version)" -ForegroundColor White
    } else {
        Write-Host "❌ manifest.json missing" -ForegroundColor Red
    }
    
    # Check background.js
    if (Test-Path "extension/dist/background.js") {
        Write-Host "✅ background.js exists" -ForegroundColor Green
        
        # Check for BG SENTINEL
        $backgroundContent = Get-Content "extension/dist/background.js" -Raw
        if ($backgroundContent -match "BG SENTINEL") {
            Write-Host "✅ BG SENTINEL found in background.js" -ForegroundColor Green
        } else {
            Write-Host "❌ BG SENTINEL missing in background.js" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ background.js missing" -ForegroundColor Red
    }
    
    # Check popup files
    if (Test-Path "extension/dist/popup.html") {
        Write-Host "✅ popup.html exists" -ForegroundColor Green
        
        # Check for POPUP SENTINEL
        $popupContent = Get-Content "extension/dist/popup.html" -Raw
        if ($popupContent -match "data-sentinel") {
            Write-Host "✅ POPUP SENTINEL found in popup.html" -ForegroundColor Green
        } else {
            Write-Host "❌ POPUP SENTINEL missing in popup.html" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ popup.html missing" -ForegroundColor Red
    }
    
    if (Test-Path "extension/dist/popup.js") {
        Write-Host "✅ popup.js exists" -ForegroundColor Green
    } else {
        Write-Host "❌ popup.js missing" -ForegroundColor Red
    }
    
    # Check content files
    if (Test-Path "extension/dist/content/index.js") {
        Write-Host "✅ content/index.js exists" -ForegroundColor Green
        
        # Check for CONTENT SENTINEL
        $contentContent = Get-Content "extension/dist/content/index.js" -Raw
        if ($contentContent -match "CONTENT SENTINEL") {
            Write-Host "✅ CONTENT SENTINEL found in content/index.js" -ForegroundColor Green
        } else {
            Write-Host "❌ CONTENT SENTINEL missing in content/index.js" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ content/index.js missing" -ForegroundColor Red
    }
    
} else {
    Write-Host "❌ extension/dist does not exist" -ForegroundColor Red
    Write-Host "Run the build process first" -ForegroundColor Yellow
}

# Check backend logs
if (Test-Path "backend/logs") {
    Write-Host "✅ backend/logs exists" -ForegroundColor Green
    
    if (Test-Path "backend/logs/operations.csv") {
        Write-Host "✅ operations.csv exists" -ForegroundColor Green
    } else {
        Write-Host "⚠️ operations.csv missing (will be created on first run)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ backend/logs missing (will be created on first run)" -ForegroundColor Yellow
}

Write-Host "`n🎯 Verification completed!" -ForegroundColor Cyan
