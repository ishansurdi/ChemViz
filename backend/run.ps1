# ChemViz Backend - Quick Start
Write-Host "Starting ChemViz Backend Server..." -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "Using virtual environment Python..." -ForegroundColor Green
} else {
    Write-Host "ERROR: Virtual environment not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Start Django server
Write-Host "Starting Django development server..." -ForegroundColor Yellow
Write-Host "Server available at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""
.\venv\Scripts\python.exe manage.py runserver
