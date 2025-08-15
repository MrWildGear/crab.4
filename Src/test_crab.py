#!/usr/bin/env python3
"""
Test script for CRAB Bounty Tracking functionality
"""

import tkinter as tk
from eve_log_reader import EVELogReader

def test_crab_functionality():
    """Test the CRAB bounty tracking functionality"""
    print("🧪 Testing CRAB Bounty Tracking functionality...")
    
    # Create root window
    root = tk.Tk()
    
    # Create EVE Log Reader instance
    app = EVELogReader(root)
    
    print("✅ Application created successfully")
    print("🦀 CRAB tracking variables initialized:")
    print(f"   - CRAB bounty entries: {len(app.crab_bounty_entries)}")
    print(f"   - CRAB total ISK: {app.crab_total_bounty_isk:,} ISK")
    print(f"   - CRAB session active: {app.crab_session_active}")
    
    # Test CRAB session start
    print("\n🧪 Testing CRAB session start...")
    app.start_crab_session()
    print(f"   - CRAB session active: {app.crab_session_active}")
    
    # Test adding CRAB bounties
    print("\n🧪 Testing CRAB bounty addition...")
    test_timestamp = app.concord_link_start or app.bounty_session_start
    if test_timestamp:
        app.add_crab_bounty_entry(test_timestamp, 100000, "test_file.txt")
        app.add_crab_bounty_entry(test_timestamp, 250000, "test_file.txt")
        app.add_crab_bounty_entry(test_timestamp, 75000, "test_file.txt")
        print(f"   - CRAB bounties added: {len(app.crab_bounty_entries)}")
        print(f"   - CRAB total ISK: {app.crab_total_bounty_isk:,} ISK")
    
    # Test CRAB session end
    print("\n🧪 Testing CRAB session end...")
    app.end_crab_session()
    print(f"   - CRAB session active: {app.crab_session_active}")
    
    # Test reset
    print("\n🧪 Testing CRAB reset...")
    app.reset_crab_bounty_tracking()
    print(f"   - CRAB bounty entries: {len(app.crab_bounty_entries)}")
    print(f"   - CRAB total ISK: {app.crab_total_bounty_isk:,} ISK")
    
    print("\n✅ CRAB functionality test completed!")
    
    # Close the application
    root.destroy()

if __name__ == "__main__":
    test_crab_functionality()
