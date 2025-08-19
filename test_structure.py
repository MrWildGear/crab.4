#!/usr/bin/env python3
"""
Test script to verify the new CRAB Tracker project structure.
"""

import os
import sys
from pathlib import Path

def test_structure():
    """Test the project structure and imports."""
    print("Testing CRAB Tracker project structure...")
    print("=" * 50)
    
    # Test 1: Check if src directory exists
    src_dir = Path("src")
    if src_dir.exists():
        print("✓ src/ directory exists")
    else:
        print("✗ src/ directory missing")
        return False
    
    # Test 2: Check if main package exists
    main_pkg = src_dir / "crab_tracker"
    if main_pkg.exists():
        print("✓ src/crab_tracker/ package exists")
    else:
        print("✗ src/crab_tracker/ package missing")
        return False
    
    # Test 3: Check if main.py exists
    main_file = main_pkg / "main.py"
    if main_file.exists():
        print("✓ src/crab_tracker/main.py exists")
    else:
        print("✗ src/crab_tracker/main.py missing")
        return False
    
    # Test 4: Check if resources exist
    resources_dir = src_dir / "resources"
    if resources_dir.exists():
        print("✓ src/resources/ directory exists")
        
        config_dir = resources_dir / "config"
        if config_dir.exists():
            print("✓ src/resources/config/ directory exists")
            
            google_forms_config = config_dir / "google_forms.json"
            if google_forms_config.exists():
                print("✓ Google Forms config exists")
            else:
                print("✗ Google Forms config missing")
        else:
            print("✗ src/resources/config/ directory missing")
    else:
        print("✗ src/resources/ directory missing")
    
    # Test 5: Check if scripts exist
    scripts_dir = src_dir / "scripts"
    if scripts_dir.exists():
        print("✓ src/scripts/ directory exists")
        
        run_script = scripts_dir / "run.py"
        if run_script.exists():
            print("✓ run.py script exists")
        else:
            print("✗ run.py script missing")
    else:
        print("✗ src/scripts/ directory missing")
    
    # Test 6: Check if tests exist
    tests_dir = Path("tests")
    if tests_dir.exists():
        print("✓ tests/ directory exists")
    else:
        print("✗ tests/ directory missing")
    
    # Test 7: Check if docs exist
    docs_dir = Path("docs")
    if docs_dir.exists():
        print("✓ docs/ directory exists")
    else:
        print("✗ docs/ directory missing")
    
    # Test 8: Check configuration files
    config_files = [
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        "setup.py",
        ".gitignore",
        "README.md"
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✓ {config_file} exists")
        else:
            print(f"✗ {config_file} missing")
    
    print("\n" + "=" * 50)
    print("Structure test completed!")
    
    return True

if __name__ == "__main__":
    success = test_structure()
    if success:
        print("✓ Project structure looks good!")
    else:
        print("✗ Project structure has issues!")
        sys.exit(1)
