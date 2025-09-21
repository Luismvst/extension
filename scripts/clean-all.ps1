# PowerShell script to clean all build artifacts
Write-Host "🧹 Cleaning all build artifacts..." -ForegroundColor Yellow

# Clean extension dist and out
if (Test-Path "extension/dist") {
    Remove-Item -Recurse -Force "extension/dist"
    Write-Host "✅ Cleaned extension/dist" -ForegroundColor Green
}

if (Test-Path "extension/out") {
    Remove-Item -Recurse -Force "extension/out"
    Write-Host "✅ Cleaned extension/out" -ForegroundColor Green
}

# Clean backend logs
if (Test-Path "backend/logs") {
    Remove-Item -Recurse -Force "backend/logs"
    Write-Host "✅ Cleaned backend/logs" -ForegroundColor Green
}

# Clean artifacts
if (Test-Path "artifacts") {
    Remove-Item -Recurse -Force "artifacts"
    Write-Host "✅ Cleaned artifacts" -ForegroundColor Green
}

# Clean coverage
if (Test-Path "coverage") {
    Remove-Item -Recurse -Force "coverage"
    Write-Host "✅ Cleaned coverage" -ForegroundColor Green
}

Write-Host "🎉 All artifacts cleaned!" -ForegroundColor Green
