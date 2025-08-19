@echo off
echo Building CRAB Tracker v0.4.0...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run the build script
python src/scripts/build.py

echo.
echo Build completed! Check the dist folder for the executable.
echo.
pause
