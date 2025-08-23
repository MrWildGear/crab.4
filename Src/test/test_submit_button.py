#!/usr/bin/env python3
"""
Test script to simulate the submit data button functionality
This will help identify where the error might be occurring
"""

import os
import sys
import traceback

def test_submit_button_simulation():
    """Simulate the submit data button click process"""
    print("🔍 Testing Submit Data Button Simulation")
    print("=" * 50)
    
    # Check 1: Working directory and config file
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"📁 Config file exists: {os.path.exists('google_form_config.json')}")
    
    if os.path.exists('google_form_config.json'):
        print("✅ Google Form config found")
        try:
            import json
            with open('google_form_config.json', 'r') as f:
                config = json.load(f)
            print(f"📋 Config loaded: {config.get('form_url', 'NO_URL')}")
        except Exception as e:
            print(f"❌ Error loading config: {e}")
    else:
        print("❌ Google Form config NOT found")
        print(f"📁 Files in current directory: {os.listdir('.')}")
    
    # Check 2: Import the main module
    print("\n🔍 Testing module imports...")
    try:
        from eve_log_reader import EVELogReader
        print("✅ EVELogReader imported successfully")
    except Exception as e:
        print(f"❌ Error importing EVELogReader: {e}")
        traceback.print_exc()
        return False
    
    # Check 3: Create instance with Tkinter root
    print("\n🔍 Testing instance creation...")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        app = EVELogReader(root)
        print("✅ EVELogReader instance created")
        
        # Check 4: Test clipboard access
        print("\n🔍 Testing clipboard access...")
        try:
            # Try to get clipboard data
            try:
                clipboard_data = root.clipboard_get()
                print(f"✅ Clipboard data retrieved: {len(clipboard_data)} characters")
                print(f"📋 First 100 chars: {repr(clipboard_data[:100])}")
            except tk.TclError as e:
                print(f"⚠️ Clipboard error (expected if empty): {e}")
                print("💡 This is normal if clipboard is empty")
        except Exception as e:
            print(f"❌ Error testing clipboard: {e}")
            traceback.print_exc()
        
        # Check 5: Test session data creation
        print("\n🔍 Testing session data creation...")
        try:
            # Mock session data similar to what the button would create
            mock_session_data = {
                'beacon_id': 'TEST_BEACON_123',
                'beacon_start': '2025-01-15 10:00:00',
                'beacon_end': '2025-01-15 11:00:00',
                'total_time': '1:00:00',
                'total_crab_bounty': '1,000,000',
                'rogue_drone_data_amount': 5,
                'rogue_drone_data_value': '500,000',
                'total_loot_value': '1,500,000',
                'loot_details': 'Test loot data',
                'source_file': 'test.log'
            }
            print("✅ Mock session data created")
            print(f"📊 Session data keys: {list(mock_session_data.keys())}")
            
            # Check if submit_to_google_form method exists
            if hasattr(app, 'submit_to_google_form'):
                print("✅ submit_to_google_form method found")
                
                # Test the method
                print("\n🔍 Testing Google Form submission...")
                try:
                    result = app.submit_to_google_form(mock_session_data)
                    print(f"✅ Google Form submission result: {result}")
                except Exception as e:
                    print(f"❌ Error in submit_to_google_form: {e}")
                    traceback.print_exc()
            else:
                print("❌ submit_to_google_form method NOT found")
                
        except Exception as e:
            print(f"❌ Error testing session data: {e}")
            traceback.print_exc()
        
        # Clean up
        root.destroy()
        
    except Exception as e:
        print(f"❌ Error creating instance: {e}")
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("🏁 Submit Button Test Complete")
    return True

if __name__ == "__main__":
    success = test_submit_button_simulation()
    if success:
        print("✅ All tests completed successfully")
    else:
        print("❌ Some tests failed")
        sys.exit(1)
