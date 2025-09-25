# Setup Frontend Environment Script
# This script sets up and activates the frontend virtual environment

Write-Host "Setting up Frontend Environment..." -ForegroundColor Green

# Check if virtual environment exists
if (Test-Path "frontend-env") {
    Write-Host "Virtual environment already exists" -ForegroundColor Yellow
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Blue
    python -m venv frontend-env
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Blue
& "frontend-env\Scripts\Activate.ps1"

# Install requirements
Write-Host "Installing Python requirements..." -ForegroundColor Blue
pip install -r requirements-frontend.txt

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Blue
npm install

Write-Host "Frontend environment setup complete!" -ForegroundColor Green
Write-Host "To activate the environment in the future, run: frontend-env\Scripts\Activate.ps1" -ForegroundColor Cyan
