"""
Test file for EVELogReader.save_beacon_session_to_csv method
Tests the beacon session CSV saving functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestSaveBeaconSessionToCsv(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    def test_save_beacon_session_to_csv_valid_data(self):
        """Test saving valid beacon session data to CSV"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test with valid session data
            session_data = {
                'beacon_id': 'test_beacon_123',
                'start_time': '2024-01-01 12:00:00',
                'end_time': '2024-01-01 12:30:00',
                'total_isk': 1000000
            }
            
            # Should not raise exception
            reader.save_beacon_session_to_csv(session_data)
            
    def test_save_beacon_session_to_csv_empty_data(self):
        """Test saving empty beacon session data to CSV"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test with empty session data
            session_data = {}
            
            # Should not raise exception
            reader.save_beacon_session_to_csv(session_data)
            
    def test_save_beacon_session_to_csv_none_data(self):
        """Test saving None beacon session data to CSV"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test with None session data
            reader.save_beacon_session_to_csv(None)
            
            # Should handle None data gracefully
            
    def test_save_beacon_session_to_csv_handles_exception(self):
        """Test that save_beacon_session_to_csv handles exceptions gracefully"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Should not raise exception even if internal logic fails
            reader.save_beacon_session_to_csv({})

if __name__ == '__main__':
    unittest.main()
