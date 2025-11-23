# start_app.ps1
Write-Host "Starting Face Recognition Application..." -ForegroundColor Cyan

# Check if venv exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Check activation
if ($env:VIRTUAL_ENV) {
    Write-Host " Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Start Flask app
Write-Host "`nStarting Flask application..." -ForegroundColor Yellow
python .\backend\app.py
