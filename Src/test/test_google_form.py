#!/usr/bin/env python3
"""
Test script for Google Form submission functionality
"""

import requests
import json
import os

def test_google_form_submission():
    """Test the Google Form submission with sample data"""
    
    # Load configuration
    config_file = "google_form_config.json"
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        form_url = config.get('form_url')
        field_mappings = config.get('field_mappings', {})
        
        print(f"✅ Configuration loaded:")
        print(f"   Form URL: {form_url}")
        print(f"   Field mappings: {len(field_mappings)} fields")
        
        # Sample session data (matching the structure from EVE log reader)
        session_data = {
            'beacon_id': 'TEST_BEACON_001',
            'total_time': '00:15:30',
            'total_crab_bounty': '1,500,000',
            'rogue_drone_data_amount': 25,
            'loot_details': 'Test loot item x1 (Materials) - 0.01 = 50,000.00 ISK'
        }
        
        print(f"\n📊 Sample session data:")
        for key, value in session_data.items():
            print(f"   {key}: {value}")
        
        # Map to form fields
        form_fields = {}
        field_to_data_mapping = {
            "Beacon ID": "beacon_id",
            "Total Duration": "total_time", 
            "Total CRAB Bounty": "total_crab_bounty",
            "Rogue Drone Data Amount": "rogue_drone_data_amount",
            "Loot Details": "loot_details"
        }
        
        print(f"\n🔗 Field mapping:")
        for field_name, entry_id in field_mappings.items():
            data_key = field_to_data_mapping.get(field_name)
            if data_key and data_key in session_data:
                form_fields[entry_id] = session_data[data_key]
                print(f"   ✅ {field_name} -> {entry_id} = {session_data[data_key]}")
            else:
                print(f"   ❌ {field_name} -> {entry_id} (data key '{data_key}' not found)")
        
        if not form_fields:
            print("❌ No valid field mappings found")
            return False
        
        print(f"\n🌐 Submitting to Google Form...")
        print(f"   URL: {form_url}")
        print(f"   Data: {form_fields}")
        
        # Submit the form
        response = requests.post(form_url, data=form_fields, timeout=30)
        
        print(f"\n📡 Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            print("✅ Form submission successful!")
            return True
        else:
            print(f"❌ Form submission failed: HTTP {response.status_code}")
            print(f"   Response content: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Google Form Submission...")
    print("=" * 50)
    
    success = test_google_form_submission()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test completed successfully!")
    else:
        print("💥 Test failed!")
    
    input("\nPress Enter to exit...")
