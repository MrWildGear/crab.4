"""
Test file for EVELogReader.__init__ method
Tests the initialization of the EVELogReader class
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestInit(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    @patch('eve_log_reader.EVELogReader.find_eve_log_directory')
    @patch('eve_log_reader.EVELogReader.setup_logging')
    @patch('eve_log_reader.EVELogReader.setup_ui')
    @patch('eve_log_reader.EVELogReader.load_log_files')
    @patch('eve_log_reader.EVELogReader.get_utc_now')
    @patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup')
    @patch('eve_log_reader.EVELogReader.refresh_eve_client_status')
    @patch('eve_log_reader.EVELogReader.start_monitoring_only')
    def test_init_basic_initialization(self, mock_start_monitoring, mock_refresh_eve, 
                                     mock_scan_crab, mock_get_utc, mock_load_logs, 
                                     mock_setup_ui, mock_setup_logging, mock_find_dir):
        """Test basic initialization of EVELogReader"""
        # Mock return values
        mock_find_dir.return_value = "C:/test/eve/logs"
        mock_get_utc.return_value = "2024-01-01 12:00:00"
        
        # Create instance
        reader = EVELogReader(self.root)
        
        # Verify basic attributes are set
        self.assertEqual(reader.root, self.root)
        self.assertEqual(reader.eve_log_dir, "C:/test/eve/logs")
        self.assertEqual(reader.max_days_old, 1)
        self.assertEqual(reader.max_files_to_show, 20)
        self.assertFalse(reader.concord_link_completed)
        self.assertFalse(reader.concord_countdown_active)
        self.assertFalse(reader.crab_session_active)
        
        # Verify methods were called
        mock_setup_logging.assert_called_once()
        mock_find_dir.assert_called_once()
        mock_setup_ui.assert_called_once()
        mock_load_logs.assert_called_once()
        mock_get_utc.assert_called()
        mock_scan_crab.assert_called_once()
        mock_refresh_eve.assert_called_once()
        
    def test_init_ui_setup(self):
        """Test that UI is properly configured during initialization"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui') as mock_setup_ui, \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.get_utc_now'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            
            reader = EVELogReader(self.root)
            
            # Verify UI setup was called
            mock_setup_ui.assert_called_once()
            
    def test_init_data_structures(self):
        """Test that all data structures are properly initialized"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.get_utc_now'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            
            reader = EVELogReader(self.root)
            
            # Test list initializations
            self.assertEqual(reader.all_log_entries, [])
            self.assertEqual(reader.bounty_entries, [])
            self.assertEqual(reader.crab_bounty_entries, [])
            
            # Test dictionary initializations
            self.assertEqual(reader.last_file_sizes, {})
            self.assertEqual(reader.last_file_hashes, {})
            
            # Test numeric initializations
            self.assertEqual(reader.total_bounty_isk, 0)
            self.assertEqual(reader.crab_total_bounty_isk, 0)
            
            # Test boolean initializations
            self.assertFalse(reader.concord_link_completed)
            self.assertFalse(reader.concord_countdown_active)
            self.assertFalse(reader.crab_session_active)
            self.assertFalse(reader._expired_beacon_popup_shown)
            self.assertFalse(reader._startup_popup_shown)

if __name__ == '__main__':
    unittest.main()
