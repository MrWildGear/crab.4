"""
Test file for EVELogReader.is_recent_file method
Tests the recent file detection functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os
from datetime import datetime, timedelta, timezone

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestIsRecentFile(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    @patch('eve_log_reader.os.path.getmtime')
    @patch('builtins.open', create=True)
    def test_is_recent_file_recent_file(self, mock_open, mock_getmtime):
        """Test is_recent_file with a recent file"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Mock recent file (modified 1 hour ago)
            recent_time = datetime.now().timestamp() - 3600  # 1 hour ago
            mock_getmtime.return_value = recent_time
            
            # Mock file content to look like EVE log
            mock_file = mock_open.return_value.__enter__.return_value
            mock_file.readline.return_value = "[2024-01-01 12:00:00] Test EVE log line"
            
            # Use a recent date (today)
            today = datetime.now(timezone.utc)
            recent_filename = f"{today.strftime('%Y%m%d')}_120000_12345678.txt"
            result = reader.is_recent_file(recent_filename)
            self.assertTrue(result)
            
    @patch('eve_log_reader.os.path.getmtime')
    def test_is_recent_file_old_file(self, mock_getmtime):
        """Test is_recent_file with an old file"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Mock old file (modified 2 days ago)
            old_time = datetime.now().timestamp() - (2 * 24 * 3600)  # 2 days ago
            mock_getmtime.return_value = old_time
            
            result = reader.is_recent_file("test.log")
            self.assertFalse(result)
            
    @patch('eve_log_reader.os.path.getmtime')
    def test_is_recent_file_exception_handling(self, mock_getmtime):
        """Test is_recent_file handles exceptions gracefully"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Mock exception
            mock_getmtime.side_effect = OSError("File not found")
            
            result = reader.is_recent_file("nonexistent.log")
            self.assertFalse(result)
            
    @patch('eve_log_reader.os.path.getmtime')
    @patch('builtins.open', create=True)
    def test_is_recent_file_boundary_conditions(self, mock_open, mock_getmtime):
        """Test is_recent_file with boundary conditions"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test file exactly at the boundary (1 day old)
            boundary_time = datetime.now().timestamp() - (24 * 3600)  # Exactly 1 day ago
            mock_getmtime.return_value = boundary_time
            
            # Mock file content to look like EVE log
            mock_file = mock_open.return_value.__enter__.return_value
            mock_file.readline.return_value = "[2024-01-01 12:00:00] Test EVE log line"
            
            # Use a recent date (today)
            today = datetime.now(timezone.utc)
            recent_filename = f"{today.strftime('%Y%m%d')}_120000_12345678.txt"
            result = reader.is_recent_file(recent_filename)
            # Should be True since it's exactly at the boundary
            self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
