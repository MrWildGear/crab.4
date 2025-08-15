@echo off
REM Optimized build script for EVE Log Reader with anti-malware detection optimizations
REM This script helps reduce the likelihood of Windows Defender flagging the executable

echo ========================================
echo EVE Log Reader - Optimized Build Script
echo ========================================
echo.

REM Check if virtual environment exists and activate it
if exist "..\.venv\Scripts\activate.bat" (
    echo Found virtual environment, activating...
    call "..\.venv\Scripts\activate.bat"
    echo Virtual environment activated: %VIRTUAL_ENV%
) else (
    echo No virtual environment found, using system Python
    echo Make sure PyInstaller is installed: pip install pyinstaller
)

echo.

REM Install/upgrade required packages
echo Installing/upgrading required packages...
python -m pip install --upgrade pip
python -m pip install --upgrade pyinstaller
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
echo.

REM Build with optimized settings
echo Building executable with anti-malware optimizations...
echo.

REM Use the optimized spec file
pyinstaller --clean EVE_Log_Reader.spec

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.

REM Show file information
if exist "dist\EVE_Log_Reader.exe" (
    echo Executable created: dist\EVE_Log_Reader.exe
    
    REM Get file size
    for %%A in ("dist\EVE_Log_Reader.exe") do set "size=%%~zA"
    set /a "size_mb=%size%/1024/1024"
    echo File size: %size_mb% MB
    
    REM Get file hash for verification
    echo.
    echo Calculating file hash for verification...
    powershell -Command "Get-FileHash 'dist\EVE_Log_Reader.exe' -Algorithm SHA256 | Select-Object Hash, Algorithm | Format-Table -AutoSize"
    
    echo.
    echo ========================================
    echo Anti-malware detection optimizations applied:
    echo ========================================
    echo ✓ UPX compression enabled
    echo ✓ Excluded unnecessary libraries
    echo ✓ Added proper file metadata
    echo ✓ Clean build environment
    echo.
    echo ========================================
    echo Build optimization complete!
    echo ========================================
    echo.
    echo The executable has been built with optimizations
    echo that should reduce false positive malware detections.
    echo.
    echo If Windows Defender still flags the file:
    echo 1. Right-click the exe → Properties → Security
    echo 2. Check "Unblock" if available
    echo 3. Add to Windows Defender exclusions if needed
    echo.
) else (
    echo ERROR: Executable not found in dist folder!
)

echo.
pause
