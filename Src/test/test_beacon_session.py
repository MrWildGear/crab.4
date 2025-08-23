#!/usr/bin/env python3
"""
Test script to simulate a complete beacon session and test Google Form submission
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path so we can import eve_log_reader
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_beacon_session():
    """Test a complete beacon session with Google Form submission"""
    
    print("🧪 Testing Complete Beacon Session")
    print("=" * 50)
    
    try:
        # Import the EVE log reader class
        from eve_log_reader import EVELogReader
        
        print("✅ EVE Log Reader imported successfully")
        
        # Create a mock session data (similar to what would be created in a real session)
        mock_session_data = {
            'beacon_id': 'TEST_BEACON_001',
            'beacon_start': (datetime.now() - timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S'),
            'beacon_end': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_time': '00:15:00',
            'total_crab_bounty': '2,500,000',
            'rogue_drone_data_amount': 50,
            'rogue_drone_data_value': '500,000',
            'total_loot_value': '3,000,000',
            'loot_details': [
                {
                    'name': 'Rogue Drone Infestation Data',
                    'amount': 50,
                    'category': 'Materials',
                    'volume': '0.01',
                    'value': 500000
                },
                {
                    'name': 'Test Loot Item',
                    'amount': 1,
                    'category': 'Materials',
                    'volume': '0.01',
                    'value': 2500000
                }
            ],
            'source_file': 'test_session.log'
        }
        
        print(f"📊 Mock session data created:")
        for key, value in mock_session_data.items():
            print(f"   • {key}: {value}")
        
        # Create a mock EVE log reader instance (without GUI)
        class MockEVELogReader:
            def __init__(self):
                self.logger = None  # No logger for this test
                
            def submit_to_google_form(self, session_data):
                """Import and call the actual submit_to_google_form function"""
                # Import the function from the module
                import eve_log_reader
                return eve_log_reader.EVELogReader.submit_to_google_form(self, session_data)
        
        # Create mock instance
        mock_reader = MockEVELogReader()
        
        print(f"\n🌐 Testing Google Form submission...")
        
        # Test the submission
        result = mock_reader.submit_to_google_form(mock_session_data)
        
        print(f"\n📡 Submission result: {result}")
        
        if result:
            print("🎉 Google Form submission successful!")
        else:
            print("💥 Google Form submission failed!")
            
        return result
        
    except ImportError as e:
        print(f"❌ Failed to import EVE Log Reader: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    
    print(f"🕐 Test run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_beacon_session()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test completed successfully!")
        print("💡 Google Form submission is working correctly.")
    else:
        print("💥 Test failed!")
        print("💡 Check the error messages above for details.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
