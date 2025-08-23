#!/usr/bin/env python3
"""
Diagnostic script for Google Form submission issues
"""

import json
import os
import requests
from datetime import datetime

def diagnose_google_form():
    """Run comprehensive diagnostics on Google Form setup"""
    
    print("🔍 Google Form Submission Diagnostics")
    print("=" * 50)
    
    # Check 1: Configuration file
    print("\n1️⃣ Checking configuration file...")
    config_file = "google_form_config.json"
    if os.path.exists(config_file):
        print(f"   ✅ Config file found: {config_file}")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"   ✅ Config file is valid JSON")
        except json.JSONDecodeError as e:
            print(f"   ❌ Config file has invalid JSON: {e}")
            return False
    else:
        print(f"   ❌ Config file not found: {config_file}")
        return False
    
    # Check 2: Configuration content
    print("\n2️⃣ Checking configuration content...")
    form_url = config.get('form_url', '')
    field_mappings = config.get('field_mappings', {})
    
    if not form_url:
        print("   ❌ Form URL is empty")
        return False
    elif "YOUR_FORM_ID" in form_url:
        print("   ❌ Form URL contains placeholder 'YOUR_FORM_ID'")
        return False
    else:
        print(f"   ✅ Form URL: {form_url}")
    
    if not field_mappings:
        print("   ❌ No field mappings configured")
        return False
    else:
        print(f"   ✅ Field mappings: {len(field_mappings)} fields")
        for field_name, entry_id in field_mappings.items():
            print(f"      • {field_name} -> {entry_id}")
    
    # Check 3: Test form accessibility
    print("\n3️⃣ Testing form accessibility...")
    try:
        # Try to access the form (not submit, just check if it's reachable)
        test_url = form_url.replace('/formResponse', '/viewform')
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Form is accessible (HTTP {response.status_code})")
        else:
            print(f"   ⚠️ Form returned HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Cannot access form: {e}")
        return False
    
    # Check 4: Test form submission
    print("\n4️⃣ Testing form submission...")
    
    # Create test data
    test_data = {
        'beacon_id': 'DIAGNOSTIC_TEST',
        'total_time': '00:00:01',
        'total_crab_bounty': '0',
        'rogue_drone_data_amount': 0,
        'loot_details': 'Diagnostic test - no actual data'
    }
    
    # Map to form fields
    field_to_data_mapping = {
        "Beacon ID": "beacon_id",
        "Total Duration": "total_time", 
        "Total CRAB Bounty": "total_crab_bounty",
        "Rogue Drone Data Amount": "rogue_drone_data_amount",
        "Loot Details": "loot_details"
    }
    
    form_fields = {}
    for field_name, entry_id in field_mappings.items():
        data_key = field_to_data_mapping.get(field_name)
        if data_key and data_key in test_data:
            form_fields[entry_id] = test_data[data_key]
    
    if not form_fields:
        print("   ❌ No valid field mappings found")
        return False
    
    print(f"   📊 Test data prepared: {form_fields}")
    
    try:
        response = requests.post(form_url, data=form_fields, timeout=30)
        print(f"   📡 Submission response: HTTP {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Form submission successful!")
            return True
        else:
            print(f"   ❌ Form submission failed")
            print(f"      Response content: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Form submission error: {e}")
        return False

def check_session_data_structure():
    """Check if session data structure matches expected format"""
    
    print("\n5️⃣ Checking session data structure...")
    
    # Expected session data structure
    expected_keys = [
        'beacon_id',
        'beacon_start', 
        'beacon_end',
        'total_time',
        'total_crab_bounty',
        'rogue_drone_data_amount',
        'rogue_drone_data_value',
        'total_loot_value',
        'loot_details',
        'source_file'
    ]
    
    print(f"   📋 Expected session data keys: {len(expected_keys)}")
    for key in expected_keys:
        print(f"      • {key}")
    
    # Check field mapping compatibility
    print(f"\n   🔗 Field mapping compatibility:")
    field_mappings = {
        "Beacon ID": "beacon_id",
        "Total Duration": "total_time", 
        "Total CRAB Bounty": "total_crab_bounty",
        "Rogue Drone Data Amount": "rogue_drone_data_amount",
        "Loot Details": "loot_details"
    }
    
    for field_name, data_key in field_mappings.items():
        if data_key in expected_keys:
            print(f"      ✅ {field_name} -> {data_key}")
        else:
            print(f"      ❌ {field_name} -> {data_key} (missing)")
    
    return True

def main():
    """Main diagnostic function"""
    
    print(f"🕐 Diagnostic run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run diagnostics
    config_ok = diagnose_google_form()
    structure_ok = check_session_data_structure()
    
    print("\n" + "=" * 50)
    print("📊 Diagnostic Summary:")
    
    if config_ok and structure_ok:
        print("🎉 All checks passed! Google Form should be working.")
        print("\n💡 If you're still having issues:")
        print("   • Check the console output for error messages")
        print("   • Verify the form is accepting submissions")
        print("   • Check network connectivity")
    else:
        print("💥 Some checks failed. Please fix the issues above.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
