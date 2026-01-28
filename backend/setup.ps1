# ChemViz Backend Setup and Run Script
Write-Host "================================" -ForegroundColor Cyan
Write-Host "ChemViz Backend Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}
$pythonVersion = python --version
Write-Host "Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}
Write-Host ""

# Install dependencies (using venv python directly)
Write-Host "Installing dependencies..." -ForegroundColor Yellow
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
Write-Host "Dependencies installed successfully!" -ForegroundColor Green
Write-Host ""

# Copy .env.example to .env if .env doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please update .env file with your configuration!" -ForegroundColor Yellow
} else {
    Write-Host ".env file already exists." -ForegroundColor Green
}
Write-Host ""

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
.\venv\Scripts\python.exe manage.py makemigrations
.\venv\Scripts\python.exe manage.py migrate
Write-Host "Database migrations completed!" -ForegroundColor Green
Write-Host ""

# Create superuser prompt
Write-Host "Would you like to create a superuser? (Y/N): " -ForegroundColor Yellow -NoNewline
$createSuperuser = Read-Host
if ($createSuperuser -eq "Y" -or $createSuperuser -eq "y") {
    .\venv\Scripts\python.exe manage.py createsuperuser
}
Write-Host ""

# Collect static files (optional for dev)
Write-Host "Collecting static files..." -ForegroundColor Yellow
.\venv\Scripts\python.exe manage.py collectstatic --noinput
Write-Host ""

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the development server, run:" -ForegroundColor Yellow
Write-Host "  .\run.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Backend will be available at:" -ForegroundColor Yellow
Write-Host "  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  Admin panel: http://127.0.0.1:8000/admin" -ForegroundColor White
Write-Host "  API docs: http://127.0.0.1:8000/api/" -ForegroundColor White
Write-Host ""
