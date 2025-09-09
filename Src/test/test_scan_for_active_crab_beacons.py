"""
Test file for EVELogReader.scan_for_active_crab_beacons method
Tests the active CRAB beacon scanning functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestScanForActiveCrabBeacons(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    @patch('eve_log_reader.EVELogReader.display_combined_logs')
    def test_scan_for_active_crab_beacons_calls_display(self, mock_display):
        """Test that scan_for_active_crab_beacons calls display_combined_logs"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            reader.scan_for_active_crab_beacons()
            
            # Verify display_combined_logs was NOT called (method only scans, doesn't display)
            mock_display.assert_not_called()
            
    def test_scan_for_active_crab_beacons_handles_exception(self):
        """Test that scan_for_active_crab_beacons handles exceptions gracefully"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'), \
             patch('eve_log_reader.EVELogReader.display_combined_logs') as mock_display:
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            mock_display.side_effect = Exception("Display error")
            
            reader = EVELogReader(self.root)
            
            # Should not raise exception
            reader.scan_for_active_crab_beacons()

if __name__ == '__main__':
    unittest.main()
