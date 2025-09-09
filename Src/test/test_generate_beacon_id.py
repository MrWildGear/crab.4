"""
Test file for EVELogReader.generate_beacon_id method
Tests the beacon ID generation functionality
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

class TestGenerateBeaconId(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    def test_generate_beacon_id_valid_inputs(self):
        """Test generating beacon ID with valid inputs"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test with valid inputs
            source_file = "20240101_120000_12345678.txt"
            beacon_timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            
            result = reader.generate_beacon_id(source_file, beacon_timestamp)
            
            # Should return a beacon ID string
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
            
    def test_generate_beacon_id_consistent_output(self):
        """Test that generate_beacon_id produces consistent output for same inputs"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test with same inputs multiple times
            source_file = "test.log"
            beacon_timestamp = "2024-01-01 12:00:00"
            
            result1 = reader.generate_beacon_id(source_file, beacon_timestamp)
            result2 = reader.generate_beacon_id(source_file, beacon_timestamp)
            
            # Results should be identical
            self.assertEqual(result1, result2)
            
    def test_generate_beacon_id_different_inputs(self):
        """Test that generate_beacon_id produces different output for different inputs"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test with different inputs
            source_file1 = "20240101_120000_12345678.txt"
            beacon_timestamp1 = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            
            source_file2 = "20240102_120000_87654321.txt"
            beacon_timestamp2 = datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
            
            result1 = reader.generate_beacon_id(source_file1, beacon_timestamp1)
            result2 = reader.generate_beacon_id(source_file2, beacon_timestamp2)
            
            # Results should be different
            self.assertNotEqual(result1, result2)
            
    def test_generate_beacon_id_none_inputs(self):
        """Test generating beacon ID with None inputs"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test with None inputs
            result = reader.generate_beacon_id(None, None)
            
            # Should return None for invalid inputs
            self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
