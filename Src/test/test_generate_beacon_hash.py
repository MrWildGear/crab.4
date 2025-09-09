"""
Test file for EVELogReader.generate_beacon_hash method
Tests the beacon hash generation functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestGenerateBeaconHash(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    def test_generate_beacon_hash_valid_inputs(self):
        """Test generating beacon hash with valid inputs"""
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
            source_file = "test.log"
            timestamp = "2024-01-01 12:00:00"
            line = "Test beacon line"
            
            result = reader.generate_beacon_hash(source_file, timestamp, line)
            
            # Should return a hash string
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
            
    def test_generate_beacon_hash_consistent_output(self):
        """Test that generate_beacon_hash produces consistent output for same inputs"""
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
            timestamp = "2024-01-01 12:00:00"
            line = "Test beacon line"
            
            result1 = reader.generate_beacon_hash(source_file, timestamp, line)
            result2 = reader.generate_beacon_hash(source_file, timestamp, line)
            
            # Results should be identical
            self.assertEqual(result1, result2)
            
    def test_generate_beacon_hash_different_inputs(self):
        """Test that generate_beacon_hash produces different output for different inputs"""
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
            source_file1 = "test1.log"
            timestamp1 = "2024-01-01 12:00:00"
            line1 = "Test beacon line 1"
            
            source_file2 = "test2.log"
            timestamp2 = "2024-01-01 12:00:00"
            line2 = "Test beacon line 2"
            
            result1 = reader.generate_beacon_hash(source_file1, timestamp1, line1)
            result2 = reader.generate_beacon_hash(source_file2, timestamp2, line2)
            
            # Results should be different
            self.assertNotEqual(result1, result2)
            
    def test_generate_beacon_hash_none_inputs(self):
        """Test generating beacon hash with None inputs"""
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
            result = reader.generate_beacon_hash(None, None, None)
            
            # Should handle None inputs gracefully
            self.assertIsInstance(result, str)

if __name__ == '__main__':
    unittest.main()
