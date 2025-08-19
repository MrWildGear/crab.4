#!/usr/bin/env python3
"""
CRAB Tracker - Simple Launcher Script

This script launches the CRAB Tracker application from the Python source.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

def main():
    """Main launcher function."""
    try:
        print("Starting CRAB Tracker...")
        print(f"Source directory: {src_dir}")
        
        # Import and run the main application
        from crab_tracker.main import main as app_main
        app_main()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
