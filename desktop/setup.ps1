# Desktop App Setup Script
Write-Host "Setting up ChemViz Desktop Application..." -ForegroundColor Green

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
.\venv\Scripts\pip.exe install --upgrade pip
.\venv\Scripts\pip.exe install -r requirements.txt

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "Run the desktop app with: .\run.ps1" -ForegroundColor Cyan
