"""
Test file for EVELogReader.parse_filename_timestamp method
Tests the filename timestamp parsing functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestParseFilenameTimestamp(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    def test_parse_filename_timestamp_valid_format(self):
        """Test parsing valid timestamp from filename"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test valid timestamp format
            filename = "20240101_120000_12345678.txt"
            result = reader.parse_filename_timestamp(filename)
            
            # Should return a tuple (timestamp, character_id)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            
            timestamp, char_id = result
            self.assertIsNotNone(timestamp)
            self.assertEqual(timestamp.year, 2024)
            self.assertEqual(timestamp.month, 1)
            self.assertEqual(timestamp.day, 1)
            self.assertEqual(timestamp.hour, 12)
            self.assertEqual(timestamp.minute, 0)
            self.assertEqual(timestamp.second, 0)
            
    def test_parse_filename_timestamp_invalid_format(self):
        """Test parsing invalid timestamp from filename"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test invalid timestamp format
            filename = "invalid_filename.txt"
            result = reader.parse_filename_timestamp(filename)
            
            # Should return (None, None) for invalid format
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(result, (None, None))
            
    def test_parse_filename_timestamp_no_timestamp(self):
        """Test parsing filename without timestamp"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test filename without timestamp
            filename = "ChatLog.txt"
            result = reader.parse_filename_timestamp(filename)
            
            # Should return (None, None) for filename without timestamp
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(result, (None, None))
            
    def test_parse_filename_timestamp_different_formats(self):
        """Test parsing different timestamp formats"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test different valid formats
            test_cases = [
                ("20240101_120000_12345678.txt", 2024, 1, 1, 12, 0, 0),
                ("20231225_235959_87654321.txt", 2023, 12, 25, 23, 59, 59),
                ("20240229_000000_11111111.txt", 2024, 2, 29, 0, 0, 0),  # Leap year
            ]
            
            for filename, year, month, day, hour, minute, second in test_cases:
                with self.subTest(filename=filename):
                    result = reader.parse_filename_timestamp(filename)
                    self.assertIsNotNone(result)
                    self.assertIsInstance(result, tuple)
                    self.assertEqual(len(result), 2)
                    
                    timestamp, char_id = result
                    self.assertIsNotNone(timestamp)
                    self.assertEqual(timestamp.year, year)
                    self.assertEqual(timestamp.month, month)
                    self.assertEqual(timestamp.day, day)
                    self.assertEqual(timestamp.hour, hour)
                    self.assertEqual(timestamp.minute, minute)
                    self.assertEqual(timestamp.second, second)

if __name__ == '__main__':
    unittest.main()
