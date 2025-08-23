@echo off
setlocal enabledelayedexpansion
REM Comprehensive anti-malware build script for EVE Log Reader
REM This script implements multiple strategies to reduce virus detection

echo ========================================
echo EVE Log Reader - Anti-Malware Build
echo ========================================
echo.

REM Extract APP_VERSION from Python file
echo Extracting version information...
for /f "tokens=3 delims= " %%i in ('findstr /C:"APP_VERSION = " eve_log_reader.py') do (
    set APP_VERSION=%%i
    set APP_VERSION=!APP_VERSION:"=!
)
echo Detected APP_VERSION: !APP_VERSION!
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

REM Create organized distribution structure first
echo Creating organized distribution structure...
mkdir "dist\CRAB Tracker"
echo.

REM Build with enhanced anti-malware settings directly to organized folder
echo Building executable with enhanced anti-malware optimizations...
echo Building directly to: dist\CRAB Tracker\
echo.

REM Use the enhanced spec file with custom distpath
pyinstaller --clean --distpath "dist\CRAB Tracker" EVE_Log_Reader_enhanced.spec

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

REM Copy configuration files to distribution folder
echo Copying configuration files...
copy "google_form_config.json" "dist\CRAB Tracker\"

REM Create README for distribution
echo CRAB Tracker - EVE Online Log Reader > "dist\CRAB Tracker\README.txt"
echo. >> "dist\CRAB Tracker\README.txt"
echo Installation: >> "dist\CRAB Tracker\README.txt"
echo 1. Extract all files to a folder >> "dist\CRAB Tracker\README.txt"
echo 2. Run EVE_Log_Reader_Enhanced.exe >> "dist\CRAB Tracker\README.txt"
echo 3. The app will create logs and data files automatically >> "dist\CRAB Tracker\README.txt"
echo. >> "dist\CRAB Tracker\README.txt"
echo Features: >> "dist\CRAB Tracker\README.txt"
echo - CONCORD Rogue Analysis Beacon tracking >> "dist\CRAB Tracker\README.txt"
echo - CRAB bounty monitoring >> "dist\CRAB Tracker\README.txt"
echo - Google Form integration >> "dist\CRAB Tracker\README.txt"
echo - Session data export >> "dist\CRAB Tracker\README.txt"

echo.
echo Distribution folder created: dist\CRAB Tracker\
echo.

REM Show file information
if exist "dist\CRAB Tracker\EVE_Log_Reader_Enhanced.exe" (
    echo Executable created: dist\CRAB Tracker\EVE_Log_Reader_Enhanced.exe
    
    REM Get file size using PowerShell for better accuracy
    echo.
    echo File size and hash information:
    powershell -Command "$file = 'dist\CRAB Tracker\EVE_Log_Reader_Enhanced.exe'; $size = (Get-Item $file).Length; $sizeMB = [math]::Round($size/1MB, 2); Write-Host \"File size: $sizeMB MB\"; Get-FileHash $file -Algorithm SHA256 | Select-Object Hash, Algorithm | Format-Table -AutoSize"
    
    echo.
    echo ========================================
    echo Creating final distribution package...
    echo ========================================
    
    REM Create ZIP file with app name and version
    set DIST_NAME=CRAB_Tracker_v!APP_VERSION!.zip
    echo Creating: !DIST_NAME!
    
    REM Use PowerShell to create ZIP and move everything from dist into it
    powershell -Command "Compress-Archive -Path 'dist\CRAB Tracker\*' -DestinationPath '!DIST_NAME!' -Force"
    
    if exist "!DIST_NAME!" (
        echo ✓ Successfully created: !DIST_NAME!
        
        REM Get ZIP file size
        for %%A in ("!DIST_NAME!") do (
            set ZIP_SIZE=%%~zA
            set /a ZIP_SIZE_MB=!ZIP_SIZE!/1048576
        )
        echo ✓ ZIP file size: !ZIP_SIZE_MB! MB
        
        REM Clean up the dist folder structure
        echo Cleaning up build artifacts...
        rmdir /s /q "dist"
        rmdir /s /q "build"
        rmdir /s /q "__pycache__"
        
        echo.
        echo ========================================
        echo Distribution package ready!
        echo ========================================
        echo Final package: !DIST_NAME!
        echo Package size: !ZIP_SIZE_MB! MB
        echo.
        echo The dist folder has been cleaned up.
        echo All distribution files are now in: !DIST_NAME!
        echo.
        echo ========================================
        echo Enhanced anti-malware optimizations applied:
        echo ========================================
        echo ✓ UPX compression enabled
        echo ✓ Aggressive library exclusions
        echo ✓ Enhanced file metadata
        echo ✓ Professional company branding
        echo ✓ Clean build environment
        echo ✓ Reduced file size
        echo ✓ Single ZIP distribution package
        echo.
        echo ========================================
        echo Additional anti-malware strategies:
        echo ========================================
        echo 1. Single ZIP file for distribution
        echo 2. Upload to VirusTotal for analysis
        echo 3. Submit to Windows Defender for review
        echo 4. Use code signing certificate (if available)
        echo 5. Distribute through trusted channels
        echo.
        echo ========================================
        echo Build optimization complete!
        echo ========================================
        echo.
        echo Your distribution package is ready: !DIST_NAME!
        echo.
        echo To distribute:
        echo 1. Send the !DIST_NAME! file
        echo 2. Users extract and run EVE_Log_Reader_Enhanced.exe
        echo.
        echo ========================================
        echo Distribution Ready!
        echo ========================================
        echo.
        echo Final package: !DIST_NAME!
        echo.
        echo ========================================
    ) else (
        echo ❌ ERROR: Failed to create ZIP file!
        echo.
        echo Distribution folder remains in: dist\CRAB Tracker\
        echo You can manually create a ZIP file from that folder.
    )
)

echo.
pause
