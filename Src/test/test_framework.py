#!/usr/bin/env python3
"""
Comprehensive Test Framework for EVELogReader
Tests each component individually to identify bugs and issues
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk

# Add the current directory to the path so we can import eve_log_reader
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestEVELogReader(unittest.TestCase):
    """Base test class with common setup and teardown"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create a mock root window
        self.root = Mock()
        self.root.title = Mock()
        self.root.geometry = Mock()
        self.root.columnconfigure = Mock()
        self.root.rowconfigure = Mock()
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Create a mock google_form_config.json for testing
        self.create_mock_config()
        
    def tearDown(self):
        """Clean up after each test"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def create_mock_config(self):
        """Create a mock Google Form configuration file"""
        config = {
            "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSeQPdllLwJZjkf0AmWJRb201ctCuEoT9FcNmnfeqXBt80grJg/formResponse",
            "field_mappings": {
                "Beacon ID": "entry.1520906809",
                "Total Duration": "entry.66008066",
                "Total CRAB Bounty": "entry.257705337",
                "Rogue Drone Data Amount": "entry.1906365497",
                "Loot Details": "entry.1769084685"
            },
            "description": "Test configuration",
            "version": "2.0",
            "last_updated": "2025-01-15"
        }
        
        with open('google_form_config.json', 'w') as f:
            json.dump(config, f, indent=2)
            
    def create_test_log_file(self, filename, content):
        """Create a test log file with specified content"""
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath

class TestCoreFunctionality(TestEVELogReader):
    """Test core functionality methods"""
    
    def test_get_utc_now(self):
        """Test UTC time retrieval"""
        from eve_log_reader import EVELogReader
        
        app = EVELogReader(self.root)
        utc_time = app.get_utc_now()
        
        self.assertIsNotNone(utc_time)
        self.assertEqual(utc_time.tzinfo, timezone.utc)
        
    def test_find_eve_log_directory(self):
        """Test EVE log directory detection"""
        from eve_log_reader import EVELogReader
        
        app = EVELogReader(self.root)
        log_dir = app.find_eve_log_directory()
        
        # Should return a valid directory path
        self.assertIsInstance(log_dir, str)
        self.assertTrue(len(log_dir) > 0)

class TestLogParsing(TestEVELogReader):
    """Test log parsing functionality"""
    
    def test_parse_clipboard_loot_valid_data(self):
        """Test parsing valid loot data"""
        from eve_log_reader import EVELogReader
        
        app = EVELogReader(self.root)
        
        # Test with valid loot data
        test_loot = """Exigent Heavy Drone Projection Mutaplasmid        1        Mutaplasmids                        1 m3        1 588 605,26 ISK
Rogue Drone Infestation Data        1229        Rogue Drone Analysis Data                        12,29 m3        122 900 000,00 ISK"""
        
        result = app.parse_clipboard_loot(test_loot)
        
        # Check that we got the expected structure
        self.assertIn('rogue_drone_data', result)
        self.assertIn('rogue_drone_data_value', result)
        self.assertIn('total_value', result)
        self.assertIn('all_loot', result)
        
        # Check specific values
        self.assertEqual(result['rogue_drone_data'], 1229)
        self.assertEqual(result['total_value'], 1588605.26 + 122900000.00)
        self.assertEqual(len(result['all_loot']), 2)
        
    def test_parse_clipboard_loot_empty_data(self):
        """Test parsing empty clipboard data"""
        from eve_log_reader import EVELogReader
        
        app = EVELogReader(self.root)
        
        result = app.parse_clipboard_loot("")
        
        # Should return default structure
        self.assertEqual(result['rogue_drone_data'], 0)
        self.assertEqual(result['total_value'], 0)
        self.assertEqual(len(result['all_loot']), 0)
        
    def test_parse_clipboard_loot_html_data(self):
        """Test parsing HTML data (should handle gracefully)"""
        from eve_log_reader import EVELogReader
        
        app = EVELogReader(self.root)
        
        html_data = "<!DOCTYPE html><html><body><div>Test</div></body></html>"
        result = app.parse_clipboard_loot(html_data)
        
        # Should handle HTML gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('all_loot', result)

class TestGoogleFormSubmission(TestEVELogReader):
    """Test Google Form submission functionality"""
    
    @patch('requests.post')
    def test_submit_to_google_form_success(self, mock_post):
        """Test successful Google Form submission"""
        from eve_log_reader import EVELogReader
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_post.return_value = mock_response
        
        app = EVELogReader(self.root)
        
        # Test data
        session_data = {
            'beacon_id': 'TEST_123',
            'total_time': '1:00:00',
            'total_crab_bounty': '1,000,000',
            'rogue_drone_data_amount': 5,
            'loot_details': 'Test loot'
        }
        
        result = app.submit_to_google_form(session_data)
        
        # Should return True for success
        self.assertTrue(result)
        mock_post.assert_called_once()
        
    @patch('requests.post')
    def test_submit_to_google_form_failure(self, mock_post):
        """Test failed Google Form submission"""
        from eve_log_reader import EVELogReader
        
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Error"
        mock_post.return_value = mock_response
        
        app = EVELogReader(self.root)
        
        session_data = {
            'beacon_id': 'TEST_123',
            'total_time': '1:00:00',
            'total_crab_bounty': '1,000,000',
            'rogue_drone_data_amount': 5,
            'loot_details': 'Test loot'
        }
        
        result = app.submit_to_google_form(session_data)
        
        # Should return False for failure
        self.assertFalse(result)
        
    def test_submit_to_google_form_no_config(self):
        """Test Google Form submission without config file"""
        from eve_log_reader import EVELogReader
        
        # Remove config file
        if os.path.exists('google_form_config.json'):
            os.remove('google_form_config.json')
        
        app = EVELogReader(self.root)
        
        session_data = {
            'beacon_id': 'TEST_123',
            'total_time': '1:00:00',
            'total_crab_bounty': '1,000,000',
            'rogue_drone_data_amount': 5,
            'loot_details': 'Test loot'
        }
        
        result = app.submit_to_google_form(session_data)
        
        # Should return False when no config
        self.assertFalse(result)

class TestBeaconSessionManagement(TestEVELogReader):
    """Test beacon session management"""
    
    def test_end_crab_submit_no_session(self):
        """Test submit data button with no active session"""
        from eve_log_reader import EVELogReader
        
        app = EVELogReader(self.root)
        
        # Ensure no active session
        app.concord_link_start = None
        
        # Mock messagebox to capture calls
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            app.end_crab_submit()
            
            # Should show warning about no active session
            mock_warning.assert_called_once()
            
    def test_end_crab_submit_with_session(self):
        """Test submit data button with active session"""
        from eve_log_reader import EVELogReader
        
        app = EVELogReader(self.root)
        
        # Setup active session
        app.concord_link_start = app.get_utc_now()
        app.current_beacon_id = "TEST_BEACON_123"
        app.beacon_source_file = "test.log"
        app.crab_total_bounty_isk = 1000000
        
        # Mock clipboard data
        test_loot = "Rogue Drone Infestation Data        5        Data        0.05 m3        500,000.00 ISK"
        
        with patch.object(app.root, 'clipboard_get', return_value=test_loot), \
             patch('tkinter.messagebox.askyesno', return_value=True), \
             patch('tkinter.messagebox.showinfo') as mock_info:
            
            app.end_crab_submit()
            
            # Should show success message
            mock_info.assert_called()

class TestCSVOperations(TestEVELogReader):
    """Test CSV file operations"""
    
    def test_save_beacon_session_to_csv(self):
        """Test saving beacon session data to CSV"""
        from eve_log_reader import EVELogReader
        
        app = EVELogReader(self.root)
        
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
        
        result = app.save_beacon_session_to_csv(session_data)
        
        # Should return True for success
        self.assertTrue(result)
        
        # Check that file was created
        self.assertTrue(os.path.exists('beacon_sessions.csv'))
        
        # Check file content
        with open('beacon_sessions.csv', 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('TEST_123', content)
            self.assertIn('1,000,000', content)

class TestLogFileOperations(TestEVELogReader):
    """Test log file operations"""
    
    def test_load_log_files(self):
        """Test loading log files"""
        from eve_log_reader import EVELogReader
        
        # Create test log files
        self.create_test_log_file('test1.log', '2025-01-15 10:00:00 Test log entry 1')
        self.create_test_log_file('test2.log', '2025-01-15 11:00:00 Test log entry 2')
        
        app = EVELogReader(self.root)
        
        # Should have loaded log files
        self.assertGreater(len(app.all_log_entries), 0)
        
    def test_detect_concord_message(self):
        """Test CONCORD message detection"""
        from eve_log_reader import EVELogReader
        
        app = EVELogReader(self.root)
        
        # Test different message types
        link_start_msg = "2025-01-15 10:00:00 [CONCORD] Rogue Analysis Beacon link established"
        link_complete_msg = "2025-01-15 11:00:00 [CONCORD] Rogue Analysis Beacon link completed"
        bounty_msg = "2025-01-15 10:30:00 [Bounty] You received 100,000 ISK"
        
        self.assertEqual(app.detect_concord_message(link_start_msg), "link_start")
        self.assertEqual(app.detect_concord_message(link_complete_msg), "link_complete")
        self.assertEqual(app.detect_concord_message(bounty_msg), "bounty")

def run_all_tests():
    """Run all tests and report results"""
    print("🧪 Running Comprehensive EVELogReader Test Suite")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCoreFunctionality)
    suite.addTests(loader.loadTestsFromTestCase(TestLogParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestGoogleFormSubmission))
    suite.addTests(loader.loadTestsFromTestCase(TestBeaconSessionManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestCSVOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestLogFileOperations))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🏁 Test Results Summary")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
            
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
            
    if not result.failures and not result.errors:
        print("\n✅ All tests passed!")
        
    return result

if __name__ == "__main__":
    # Import timezone here to avoid import issues
    from datetime import timezone
    
    # Run all tests
    test_result = run_all_tests()
    
    # Exit with appropriate code
    if test_result.failures or test_result.errors:
        sys.exit(1)
    else:
        sys.exit(0)
