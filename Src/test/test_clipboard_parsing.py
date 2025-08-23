#!/usr/bin/env python3
"""
Test script to check clipboard parsing functionality
This will help identify if the clipboard content is causing issues
"""

import os
import sys
import traceback

def test_clipboard_parsing():
    """Test the clipboard parsing functionality"""
    print("🔍 Testing Clipboard Parsing")
    print("=" * 50)
    
    # Check 1: Import the main module
    print("🔍 Testing module imports...")
    try:
        from eve_log_reader import EVELogReader
        print("✅ EVELogReader imported successfully")
    except Exception as e:
        print(f"❌ Error importing EVELogReader: {e}")
        traceback.print_exc()
        return False
    
    # Check 2: Create instance and test clipboard
    print("\n🔍 Testing clipboard access and parsing...")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        app = EVELogReader(root)
        print("✅ EVELogReader instance created")
        
        # Get clipboard data
        try:
            clipboard_data = root.clipboard_get()
            print(f"📋 Clipboard data retrieved: {len(clipboard_data)} characters")
            print(f"📋 First 200 chars: {repr(clipboard_data[:200])}")
            
            # Check if it looks like HTML
            if '<!DOCTYPE html>' in clipboard_data or '<html' in clipboard_data:
                print("⚠️ WARNING: Clipboard contains HTML content instead of EVE loot data!")
                print("💡 This suggests the clipboard was copied from a web page, not from EVE Online")
                print("💡 The user needs to copy the loot data from EVE Online before clicking Submit Data")
                
                # Try to parse it anyway to see what happens
                print("\n🔍 Attempting to parse HTML clipboard data...")
                loot_data = app.parse_clipboard_loot(clipboard_data)
                print(f"📊 Parse result: {loot_data}")
                
                # Check if we got any meaningful loot data
                if loot_data['all_loot'] and len(loot_data['all_loot']) > 0:
                    print("✅ Surprisingly, some loot data was parsed!")
                else:
                    print("❌ No loot data could be parsed from HTML content")
                    print("💡 This explains why the Google Form submission might fail")
                
            else:
                print("✅ Clipboard data appears to be non-HTML (possibly EVE loot data)")
                # Try to parse it
                loot_data = app.parse_clipboard_loot(clipboard_data)
                print(f"📊 Parse result: {loot_data}")
                
        except tk.TclError as e:
            print(f"⚠️ Clipboard error: {e}")
            print("💡 This is normal if clipboard is empty")
        except Exception as e:
            print(f"❌ Error testing clipboard: {e}")
            traceback.print_exc()
        
        # Clean up
        root.destroy()
        
    except Exception as e:
        print(f"❌ Error creating instance: {e}")
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("🏁 Clipboard Parsing Test Complete")
    return True

if __name__ == "__main__":
    success = test_clipboard_parsing()
    if success:
        print("✅ All tests completed successfully")
    else:
        print("❌ Some tests failed")
        sys.exit(1)
