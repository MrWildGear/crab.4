"""
Test file for EVELogReader.load_log_files method
Tests the log file loading functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestLoadLogFiles(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    @patch('eve_log_reader.glob.glob')
    @patch('eve_log_reader.EVELogReader.is_recent_file')
    def test_load_log_files_finds_recent_files(self, mock_is_recent, mock_glob):
        """Test load_log_files finds and loads recent files"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            mock_glob.return_value = ["test1.log", "test2.log", "test3.log"]
            mock_is_recent.return_value = True
            
            reader = EVELogReader(self.root)
            reader.load_log_files()
            
            # Verify glob was called for each pattern
            expected_calls = [
                unittest.mock.call("C:/test/eve/logs/*.log"),
                unittest.mock.call("C:/test/eve/logs/*.txt"),
                unittest.mock.call("C:/test/eve/logs/*.xml")
            ]
            mock_glob.assert_has_calls(expected_calls, any_order=True)
            
    @patch('eve_log_reader.glob.glob')
    @patch('eve_log_reader.EVELogReader.is_recent_file')
    def test_load_log_files_filters_old_files(self, mock_is_recent, mock_glob):
        """Test load_log_files filters out old files"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            mock_glob.return_value = ["recent.log", "old.log"]
            
            # Mock is_recent_file to return different values
            def is_recent_side_effect(filename):
                return filename == "recent.log"
            mock_is_recent.side_effect = is_recent_side_effect
            
            reader = EVELogReader(self.root)
            reader.load_log_files()
            
            # Verify is_recent_file was called for each file
            self.assertEqual(mock_is_recent.call_count, 2)
            
    @patch('eve_log_reader.glob.glob')
    def test_load_log_files_no_directory(self, mock_glob):
        """Test load_log_files when no log directory is set"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = None
            reader = EVELogReader(self.root)
            
            reader.load_log_files()
            
            # Verify glob was not called
            mock_glob.assert_not_called()
            
    @patch('eve_log_reader.glob.glob')
    def test_load_log_files_handles_exception(self, mock_glob):
        """Test load_log_files handles exceptions gracefully"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            mock_glob.side_effect = Exception("Glob error")
            
            reader = EVELogReader(self.root)
            
            # Should not raise exception
            reader.load_log_files()

if __name__ == '__main__':
    unittest.main()
