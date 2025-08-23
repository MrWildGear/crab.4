#!/usr/bin/env python3
"""
Test Individual Functions Without Full Class Initialization
This approach avoids the Tkinter UI setup issues
"""

import os
import sys
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, MagicMock

# Add the current directory to the path so we can import eve_log_reader
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_parse_clipboard_loot_function():
    """Test the parse_clipboard_loot function directly"""
    print("🔍 Testing parse_clipboard_loot function")
    print("=" * 50)
    
    try:
        # Import the function directly from the module
        import eve_log_reader
        
        # Create a minimal instance without UI
        class MinimalReader:
            def __init__(self):
                pass
        
        # Copy the function to our minimal class
        minimal_reader = MinimalReader()
        minimal_reader.parse_clipboard_loot = eve_log_reader.EVELogReader.parse_clipboard_loot.__get__(minimal_reader)
        
        # Test 1: Valid loot data
        print("Test 1: Valid loot data")
        test_loot = """Exigent Heavy Drone Projection Mutaplasmid        1        Mutaplasmids                        1 m3        1 588 605,26 ISK
Rogue Drone Infestation Data        1229        Rogue Drone Analysis Data                        12,29 m3        122 900 000,00 ISK"""
        
        result = minimal_reader.parse_clipboard_loot(test_loot)
        print(f"✅ Result: {result}")
        
        # Verify structure
        assert 'rogue_drone_data' in result, "Missing rogue_drone_data field"
        assert 'total_value' in result, "Missing total_value field"
        assert 'all_loot' in result, "Missing all_loot field"
        
        # Verify values
        assert result['rogue_drone_data'] == 1229, f"Expected 1229, got {result['rogue_drone_data']}"
        expected_total = 1588605.26 + 122900000.00
        assert abs(result['total_value'] - expected_total) < 0.01, f"Expected {expected_total}, got {result['total_value']}"
        assert len(result['all_loot']) == 2, f"Expected 2 loot items, got {len(result['all_loot'])}"
        
        print("✅ Test 1 passed!")
        
        # Test 2: Empty data
        print("\nTest 2: Empty data")
        result = minimal_reader.parse_clipboard_loot("")
        print(f"✅ Result: {result}")
        
        assert result['rogue_drone_data'] == 0, f"Expected 0, got {result['rogue_drone_data']}"
        assert result['total_value'] == 0, f"Expected 0, got {result['total_value']}"
        assert len(result['all_loot']) == 0, f"Expected 0 loot items, got {len(result['all_loot'])}"
        
        print("✅ Test 2 passed!")
        
        # Test 3: HTML data
        print("\nTest 3: HTML data")
        html_data = "<!DOCTYPE html><html><body><div>Test</div></body></html>"
        result = minimal_reader.parse_clipboard_loot(html_data)
        print(f"✅ Result: {result}")
        
        assert isinstance(result, dict), "Should return a dictionary"
        assert 'all_loot' in result, "Should have all_loot field"
        
        print("✅ Test 3 passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing parse_clipboard_loot: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_google_form_submission_function():
    """Test the submit_to_google_form function directly"""
    print("\n🔍 Testing submit_to_google_form function")
    print("=" * 50)
    
    try:
        # Create a test directory
        test_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(test_dir)
        
        # Create mock config
        config = {
            "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSeQPdllLwJZjkf0AmWJRb201ctCuEoT9FcNmnfeqXBt80grJg/formResponse",
            "field_mappings": {
                "Beacon ID": "entry.1520906809",
                "Total Duration": "entry.66008066",
                "Total CRAB Bounty": "entry.257705337",
                "Rogue Drone Data Amount": "entry.1906365497",
                "Loot Details": "entry.1769084685"
            }
        }
        
        with open('google_form_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Import the function
        import eve_log_reader
        
        # Create minimal instance
        class MinimalReader:
            def __init__(self):
                self.logger = None
        
        minimal_reader = MinimalReader()
        minimal_reader.submit_to_google_form = eve_log_reader.EVELogReader.submit_to_google_form.__get__(minimal_reader)
        
        # Test data
        session_data = {
            'beacon_id': 'TEST_123',
            'total_time': '1:00:00',
            'total_crab_bounty': '1,000,000',
            'rogue_drone_data_amount': 5,
            'loot_details': 'Test loot'
        }
        
        # Test with mocked requests
        with patch('requests.post') as mock_post:
            # Test success
            print("Test 1: Successful submission")
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "Success"
            mock_post.return_value = mock_response
            
            result = minimal_reader.submit_to_google_form(session_data)
            assert result == True, f"Expected True, got {result}"
            print("✅ Success test passed!")
            
            # Test failure
            print("\nTest 2: Failed submission")
            mock_response.status_code = 500
            mock_response.text = "Error"
            
            result = minimal_reader.submit_to_google_form(session_data)
            assert result == False, f"Expected False, got {result}"
            print("✅ Failure test passed!")
        
        # Test without config file
        print("\nTest 3: No config file")
        os.remove('google_form_config.json')
        
        result = minimal_reader.submit_to_google_form(session_data)
        assert result == False, f"Expected False when no config, got {result}"
        print("✅ No config test passed!")
        
        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(test_dir, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing submit_to_google_form: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_operations():
    """Test CSV file operations"""
    print("\n🔍 Testing CSV operations")
    print("=" * 50)
    
    try:
        # Create test directory
        test_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(test_dir)
        
        # Import the function
        import eve_log_reader
        
        # Create minimal instance
        class MinimalReader:
            def __init__(self):
                pass
        
        minimal_reader = MinimalReader()
        minimal_reader.save_beacon_session_to_csv = eve_log_reader.EVELogReader.save_beacon_session_to_csv.__get__(minimal_reader)
        
        # Test data
        session_data = {
            'beacon_id': 'TEST_123',
            'beacon_start': '2025-01-15 10:00:00',
            'beacon_end': '2025-01-15 11:00:00',
            'total_time': '1:00:00',
            'total_crab_bounty': '1,000,000',
            'rogue_drone_data_amount': 5,
            'rogue_drone_data_value': '500,000',
            'total_loot_value': '1,500,000',
            'loot_details': 'Test loot',
            'source_file': 'test.log'
        }
        
        # Test saving
        print("Test: Save to CSV")
        result = minimal_reader.save_beacon_session_to_csv(session_data)
        assert result == True, f"Expected True, got {result}"
        
        # Check file exists
        assert os.path.exists('beacon_sessions.csv'), "CSV file not created"
        
        # Check content
        with open('beacon_sessions.csv', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'TEST_123' in content, "Beacon ID not in CSV"
            assert '1,000,000' in content, "Bounty not in CSV"
        
        print("✅ CSV test passed!")
        
        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(test_dir, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing CSV operations: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_concord_message_detection():
    """Test CONCORD message detection"""
    print("\n🔍 Testing CONCORD message detection")
    print("=" * 50)
    
    try:
        # Import the function
        import eve_log_reader
        
        # Create minimal instance
        class MinimalReader:
            def __init__(self):
                pass
        
        minimal_reader = MinimalReader()
        minimal_reader.detect_concord_message = eve_log_reader.EVELogReader.detect_concord_message.__get__(minimal_reader)
        
        # Test messages - only CONCORD beacon messages, not bounty messages
        test_cases = [
            ("[CONCORD] Rogue Analysis Beacon link established", "link_start"),
            ("[CONCORD] Rogue Analysis Beacon link completed", "link_complete"),
            ("[Random] Some other message", None)
        ]
        
        for message, expected in test_cases:
            print(f"Testing: {message[:50]}...")
            result = minimal_reader.detect_concord_message(message)
            assert result == expected, f"Expected {expected}, got {result} for message: {message}"
            print(f"✅ {expected or 'None'} - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing CONCORD detection: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_function_tests():
    """Run all function tests"""
    print("🧪 Running Individual Function Tests")
    print("=" * 60)
    
    tests = [
        ("parse_clipboard_loot", test_parse_clipboard_loot_function),
        ("submit_to_google_form", test_google_form_submission_function),
        ("CSV operations", test_csv_operations),
        ("CONCORD detection", test_concord_message_detection)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Function Test Results Summary")
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    
    if failed == 0:
        print("\n✅ All function tests passed!")
    else:
        print(f"\n❌ {failed} function test(s) failed")
    
    return passed, failed

if __name__ == "__main__":
    # Run all function tests
    passed, failed = run_all_function_tests()
    
    # Exit with appropriate code
    if failed == 0:
        sys.exit(0)
    else:
        sys.exit(1)
