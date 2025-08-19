#!/usr/bin/env python3
"""
CRAB Tracker - Main Entry Point

This is the main entry point for the CRAB Tracker application.
It initializes the GUI and starts the main application loop.
"""

import tkinter as tk
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from crab_tracker.gui.main_window import MainWindow
from crab_tracker.services.logging_service import LoggingService


def main():
    """Main entry point for the CRAB Tracker application."""
    try:
        # Create the main window (logging will be initialized there)
        root = tk.Tk()
        app = MainWindow(root)
        
        # Start the main event loop
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting CRAB Tracker: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
