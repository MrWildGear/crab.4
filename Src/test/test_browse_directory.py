"""
Test file for EVELogReader.browse_directory method
Tests the directory browsing functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestBrowseDirectory(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    @patch('eve_log_reader.filedialog.askdirectory')
    def test_browse_directory_user_selects_directory(self, mock_askdirectory):
        """Test browse_directory when user selects a directory"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files') as mock_load_logs, \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            mock_askdirectory.return_value = "C:/new/eve/logs"
            
            reader = EVELogReader(self.root)
            reader.browse_directory()
            
            # Verify directory was updated
            self.assertEqual(reader.eve_log_dir, "C:/new/eve/logs")
            # Verify load_log_files was called
            mock_load_logs.assert_called()
            
    @patch('eve_log_reader.filedialog.askdirectory')
    def test_browse_directory_user_cancels(self, mock_askdirectory):
        """Test browse_directory when user cancels dialog"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files') as mock_load_logs, \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            mock_askdirectory.return_value = ""  # User cancelled
            
            reader = EVELogReader(self.root)
            original_dir = reader.eve_log_dir
            reader.browse_directory()
            
            # Verify directory was not changed
            self.assertEqual(reader.eve_log_dir, original_dir)
            # Verify load_log_files was not called
            mock_load_logs.assert_not_called()
            
    @patch('eve_log_reader.filedialog.askdirectory')
    def test_browse_directory_handles_exception(self, mock_askdirectory):
        """Test browse_directory handles exceptions gracefully"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            mock_askdirectory.side_effect = Exception("Dialog error")
            
            reader = EVELogReader(self.root)
            original_dir = reader.eve_log_dir
            
            # Should not raise exception
            reader.browse_directory()
            
            # Verify directory was not changed
            self.assertEqual(reader.eve_log_dir, original_dir)

if __name__ == '__main__':
    unittest.main()
