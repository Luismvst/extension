# Activate Frontend Environment Script
# This script activates the frontend virtual environment

Write-Host "Activating Frontend Environment..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "frontend-env")) {
    Write-Host "Virtual environment not found. Please run setup-frontend-env.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
& "frontend-env\Scripts\Activate.ps1"

Write-Host "Frontend environment activated!" -ForegroundColor Green
Write-Host "You can now run npm commands and Python scripts." -ForegroundColor Cyan
