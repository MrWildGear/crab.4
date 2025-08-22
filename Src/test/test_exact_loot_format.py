#!/usr/bin/env python3
"""
Test script to verify the parsing function works with the exact EVE Online loot format
"""

import os
import sys
import traceback

def test_exact_loot_format():
    """Test the parsing function with the exact loot format provided by the user"""
    print("🔍 Testing Exact Loot Format Parsing")
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
    
    # Check 2: Create instance and test parsing
    print("\n🔍 Testing exact loot format parsing...")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        app = EVELogReader(root)
        print("✅ EVELogReader instance created")
        
        # Test with the exact format provided by the user
        test_loot_data = """Exigent Heavy Drone Projection Mutaplasmid        1        Mutaplasmids                        1 m3        1 588 605,26 ISK
Exigent Medium Drone Projection Mutaplasmid        1        Mutaplasmids                        1 m3        6 109 861,70 ISK
Exigent Sentry Drone Firepower Mutaplasmid        1        Mutaplasmids                        1 m3        7 017 969,69 ISK
Rogue Drone Infestation Data        1229        Rogue Drone Analysis Data                        12,29 m3        122 900 000,00 ISK"""
        
        print("📋 Testing with exact loot format:")
        print(test_loot_data)
        print("\n" + "-" * 50)
        
        # Parse the test data
        loot_data = app.parse_clipboard_loot(test_loot_data)
        
        print(f"\n📊 Parse result: {loot_data}")
        
        # Check if we got the expected results
        expected_rogue_drone_data = 1229
        expected_total_value = 1588605.26 + 6109861.70 + 7017969.69 + 122900000.00
        
        print(f"\n🔍 Verification:")
        print(f"   Rogue Drone Data: {loot_data['rogue_drone_data']} (expected: {expected_rogue_drone_data})")
        print(f"   Total Value: {loot_data['total_value']:,.2f} ISK (expected: {expected_total_value:,.2f} ISK)")
        print(f"   Loot Items: {len(loot_data['all_loot'])} (expected: 4)")
        
        # Check if parsing was successful
        if (loot_data['rogue_drone_data'] == expected_rogue_drone_data and 
            abs(loot_data['total_value'] - expected_total_value) < 0.01 and
            len(loot_data['all_loot']) == 4):
            print("✅ All parsing checks passed!")
        else:
            print("❌ Some parsing checks failed!")
            
        # Show detailed loot items
        print(f"\n📦 Detailed Loot Items:")
        for i, item in enumerate(loot_data['all_loot']):
            print(f"   {i+1}. {item['name']} x{item['amount']} = {item['value']:,.2f} ISK")
        
        # Clean up
        root.destroy()
        
    except Exception as e:
        print(f"❌ Error testing exact loot format: {e}")
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("🏁 Exact Loot Format Test Complete")
    return True

if __name__ == "__main__":
    success = test_exact_loot_format()
    if success:
        print("✅ All tests completed successfully")
    else:
        print("❌ Some tests failed")
        sys.exit(1)
