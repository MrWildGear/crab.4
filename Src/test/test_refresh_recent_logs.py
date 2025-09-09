"""
Test file for EVELogReader.refresh_recent_logs method
Tests the recent logs refresh functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestRefreshRecentLogs(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    @patch('eve_log_reader.EVELogReader.load_log_files')
    def test_refresh_recent_logs_calls_load_log_files(self, mock_load_logs):
        """Test that refresh_recent_logs calls load_log_files"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            reader.refresh_recent_logs()
            
            # Verify load_log_files was called
            mock_load_logs.assert_called_once()
            
    def test_refresh_recent_logs_handles_exception(self):
        """Test that refresh_recent_logs handles exceptions gracefully"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'), \
             patch('eve_log_reader.EVELogReader.load_log_files') as mock_load_logs:
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            mock_load_logs.side_effect = Exception("Load error")
            
            reader = EVELogReader(self.root)
            
            # Should not raise exception
            reader.refresh_recent_logs()

if __name__ == '__main__':
    unittest.main()
