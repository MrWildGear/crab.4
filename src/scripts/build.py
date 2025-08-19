#!/usr/bin/env python3
"""
CRAB Tracker - Python Build Script

This script builds the CRAB Tracker application into an executable
using PyInstaller with anti-malware optimizations.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("✗ PyInstaller not found")
        print("Install with: pip install pyinstaller")
        return False
    
    try:
        import requests
        print("✓ Requests library found")
    except ImportError:
        print("✗ Requests library not found")
        print("Install with: pip install requests")
        return False
    
    return True

def clean_build_directories():
    """Clean previous build artifacts."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)

def create_dist_structure():
    """Create the distribution directory structure."""
    dist_dir = Path("dist/CRAB Tracker")
    dist_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created distribution directory: {dist_dir}")
    return dist_dir

def build_executable(dist_dir):
    """Build the executable using PyInstaller."""
    print("Building executable...")
    
    # PyInstaller command with anti-malware optimizations
    cmd = [
        'pyinstaller',
        '--clean',
        '--onefile',
        '--windowed',
        '--name=CRAB_Tracker',
        '--distpath', str(dist_dir),
        '--add-data', f'src/resources/config{os.pathsep}config',
        '--add-data', f'src/resources/build{os.pathsep}build',
        '--hidden-import=tkinter',
        '--hidden-import=requests',
        '--hidden-import=logging',
        '--hidden-import=hashlib',
        '--hidden-import=threading',
        '--hidden-import=datetime',
        '--hidden-import=pathlib',
        '--hidden-import=re',
        '--hidden-import=json',
        '--hidden-import=csv',
        '--hidden-import=uuid',
        '--hidden-import=dataclasses',
        '--hidden-import=typing',
        '--hidden-import=sys',
        'src/crab_tracker/main.py'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Build completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed with error code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False

def copy_resources(dist_dir):
    """Copy configuration and resource files to distribution."""
    print("Copying resources...")
    
    # Copy configuration files
    config_src = Path("src/resources/config")
    config_dst = dist_dir / "config"
    
    if config_src.exists():
        shutil.copytree(config_src, config_dst, dirs_exist_ok=True)
        print(f"✓ Copied config files to {config_dst}")
    
    # Copy build resources
    build_src = Path("src/resources/build")
    build_dst = dist_dir / "build"
    
    if build_src.exists():
        shutil.copytree(build_src, build_dst, dirs_exist_ok=True)
        print(f"✓ Copied build resources to {build_dst}")

def create_readme(dist_dir):
    """Create a README file for the distribution."""
    readme_content = """CRAB Tracker - EVE Online Log Reader & Beacon Analysis

Installation:
1. Extract all files to a folder
2. Run CRAB_Tracker.exe
3. The app will create logs and data files automatically

Features:
- CONCORD Rogue Analysis Beacon tracking
- CRAB bounty monitoring
- Google Form integration
- Session data export
- Real-time log monitoring

Requirements:
- Windows 10/11
- No additional software required

Support:
- Check the logs folder for application logs
- Use the export functions to save data
- Submit beacon data to Google Forms for analysis
"""
    
    readme_path = dist_dir / "README.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✓ Created README.txt")

def main():
    """Main build function."""
    print("CRAB Tracker - Build Script")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("Build cannot continue due to missing dependencies.")
        sys.exit(1)
    
    # Clean previous builds
    clean_build_directories()
    
    # Create distribution structure
    dist_dir = create_dist_structure()
    
    # Build executable
    if not build_executable(dist_dir):
        print("Build failed!")
        sys.exit(1)
    
    # Copy resources
    copy_resources(dist_dir)
    
    # Create README
    create_readme(dist_dir)
    
    print("\n" + "=" * 40)
    print("Build completed successfully!")
    print(f"Executable location: {dist_dir / 'CRAB_Tracker.exe'}")
    print(f"Distribution folder: {dist_dir}")
    
    # Show file information
    exe_path = dist_dir / "CRAB_Tracker.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"Executable size: {size_mb:.1f} MB")

if __name__ == "__main__":
    main()
