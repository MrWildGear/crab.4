# EVE Log Reader - Optimized Build Script (PowerShell)

Write-Host "EVE Log Reader - Optimized Build Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists and activate it
$venvPath = "..\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Found virtual environment, activating..." -ForegroundColor Yellow
    & $venvPath
    Write-Host "Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green
}
else {
    Write-Host "No virtual environment found, using system Python" -ForegroundColor Yellow
    Write-Host "Make sure PyInstaller is installed: pip install pyinstaller" -ForegroundColor White
}

Write-Host ""

# Install/upgrade required packages
Write-Host "Installing/upgrading required packages..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install --upgrade pyinstaller
Write-Host ""

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "__pycache__") { Remove-Item -Recurse -Force "__pycache__" }
Write-Host ""

# Build with optimized settings
Write-Host "Building executable with anti-malware optimizations..." -ForegroundColor Yellow
Write-Host ""

# Use the optimized spec file
pyinstaller --clean EVE_Log_Reader.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host ""
    
    if (Test-Path "dist\EVE_Log_Reader.exe") {
        $exePath = "dist\EVE_Log_Reader.exe"
        Write-Host "Executable created: $exePath" -ForegroundColor Green
        
        # Get file size
        $fileInfo = Get-Item $exePath
        $sizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
        Write-Host "File size: $sizeMB MB" -ForegroundColor White
        
        Write-Host ""
        Write-Host "Anti-malware optimizations applied:" -ForegroundColor Green
        Write-Host "✓ UPX compression enabled" -ForegroundColor White
        Write-Host "✓ Excluded unnecessary libraries" -ForegroundColor White
        Write-Host "✓ Added proper file metadata" -ForegroundColor White
        Write-Host "✓ Clean build environment" -ForegroundColor White
    }
    else {
        Write-Host "ERROR: Executable not found in dist folder!" -ForegroundColor Red
    }
}
else {
    Write-Host ""
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit" 
