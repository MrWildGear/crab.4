#!/usr/bin/env python3
"""
Test script for CONCORD Rogue Analysis Beacon functionality
"""

import tkinter as tk
from eve_log_reader import EVELogReader

def test_concord_functionality():
    """Test the CONCORD functionality"""
    print("🧪 Testing CONCORD Rogue Analysis Beacon functionality...")
    
    # Create root window
    root = tk.Tk()
    
    # Create EVE Log Reader instance
    app = EVELogReader(root)
    
    print("✅ Application created successfully")
    print("🔗 CONCORD tracking variables initialized:")
    print(f"   - Link start: {app.concord_link_start}")
    print(f"   - Link completed: {app.concord_link_completed}")
    print(f"   - Countdown active: {app.concord_countdown_active}")
    print(f"   - Countdown color: {app.concord_countdown_color}")
    
    # Test the test functions
    print("\n🧪 Testing CONCORD link start...")
    app.test_concord_link_start()
    
    print(f"   - Link start time: {app.concord_link_start}")
    print(f"   - Status: {app.concord_status_var.get()}")
    print(f"   - Countdown active: {app.concord_countdown_active}")
    
    # Wait a moment to see the countdown
    print("\n⏳ Waiting 3 seconds to see countdown in action...")
    root.after(3000, lambda: test_link_complete(app))
    
    # Start the main loop
    root.mainloop()

def test_link_complete(app):
    """Test link completion after delay"""
    print("\n🧪 Testing CONCORD link completion...")
    app.test_concord_link_complete()
    
    print(f"   - Link completed: {app.concord_link_completed}")
    print(f"   - Status: {app.concord_status_var.get()}")
    print(f"   - Countdown active: {app.concord_countdown_active}")
    print(f"   - Link time: {app.concord_time_var.get()}")
    
    print("\n✅ CONCORD functionality test completed!")

if __name__ == "__main__":
    test_concord_functionality()
