"""
Test file for EVELogReader.get_utc_now method
Tests the UTC timestamp generation functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os
from datetime import datetime, timezone

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestGetUtcNow(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    def test_get_utc_now_returns_datetime(self):
        """Test that get_utc_now returns a datetime object"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            result = reader.get_utc_now()
            from datetime import datetime
            self.assertIsInstance(result, datetime)
            
    def test_get_utc_now_format(self):
        """Test that get_utc_now returns properly formatted timestamp"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            result = reader.get_utc_now()
            
            # Test that the result can be formatted as a string
            formatted = result.strftime('%Y-%m-%d %H:%M:%S')
            self.assertRegex(formatted, r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')
            
    def test_get_utc_now_utc_timezone(self):
        """Test that get_utc_now returns UTC time"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            result = reader.get_utc_now()
            
            # Verify it's a datetime object with UTC timezone
            from datetime import timezone
            self.assertEqual(result.tzinfo, timezone.utc)
            
    def test_get_utc_now_consistency(self):
        """Test that get_utc_now returns consistent results within a short time"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            result1 = reader.get_utc_now()
            result2 = reader.get_utc_now()
            
            # Results should be the same or very close (calls happen very quickly)
            # Difference should be very small (less than 1 second)
            diff = abs((result2 - result1).total_seconds())
            self.assertLessEqual(diff, 1.0)
            
            # Both results should be valid datetime objects
            from datetime import datetime
            self.assertIsInstance(result1, datetime)
            self.assertIsInstance(result2, datetime)

if __name__ == '__main__':
    unittest.main()
