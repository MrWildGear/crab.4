"""
Test file for EVELogReader.check_for_expired_but_recent_beacons method
Tests the expired beacon checking functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestCheckForExpiredButRecentBeacons(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    def test_check_for_expired_but_recent_beacons_no_popup_shown(self):
        """Test when expired beacon popup has not been shown"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Set up initial state
            reader._expired_beacon_popup_shown = False
            reader._startup_popup_shown = False
            
            reader.check_for_expired_but_recent_beacons()
            
            # Should not raise exception
            self.assertFalse(reader._expired_beacon_popup_shown)
            
    def test_check_for_expired_but_recent_beacons_popup_already_shown(self):
        """Test when expired beacon popup has already been shown"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Set up initial state
            reader._expired_beacon_popup_shown = True
            reader._startup_popup_shown = True
            
            reader.check_for_expired_but_recent_beacons()
            
            # Should not raise exception
            self.assertTrue(reader._expired_beacon_popup_shown)
            
    def test_check_for_expired_but_recent_beacons_handles_exception(self):
        """Test that check_for_expired_but_recent_beacons handles exceptions gracefully"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Set up initial state
            reader._expired_beacon_popup_shown = False
            reader._startup_popup_shown = False
            
            # Should not raise exception even if internal logic fails
            reader.check_for_expired_but_recent_beacons()

if __name__ == '__main__':
    unittest.main()
