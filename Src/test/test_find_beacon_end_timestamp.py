"""
Test file for EVELogReader.find_beacon_end_timestamp method
Tests the beacon end timestamp finding functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestFindBeaconEndTimestamp(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    def test_find_beacon_end_timestamp_valid_start(self):
        """Test finding beacon end timestamp with valid start timestamp"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test with valid start timestamp
            start_timestamp = "2024-01-01 12:00:00"
            source_file = "test.log"
            
            result = reader.find_beacon_end_timestamp(start_timestamp, source_file)
            
            # Should return a timestamp (implementation dependent)
            self.assertIsNotNone(result)
            
    def test_find_beacon_end_timestamp_invalid_start(self):
        """Test finding beacon end timestamp with invalid start timestamp"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test with invalid start timestamp
            start_timestamp = "invalid_timestamp"
            source_file = "test.log"
            
            result = reader.find_beacon_end_timestamp(start_timestamp, source_file)
            
            # Should handle invalid timestamp gracefully
            self.assertIsNotNone(result)  # Implementation dependent
            
    def test_find_beacon_end_timestamp_none_source_file(self):
        """Test finding beacon end timestamp with None source file"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test with None source file
            start_timestamp = "2024-01-01 12:00:00"
            source_file = None
            
            result = reader.find_beacon_end_timestamp(start_timestamp, source_file)
            
            # Should handle None source file gracefully
            self.assertIsNotNone(result)  # Implementation dependent

if __name__ == '__main__':
    unittest.main()
