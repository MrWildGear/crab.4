"""
Test file for EVELogReader.scan_for_active_crab_beacons_on_startup method
Tests the startup CRAB beacon scanning functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestScanForActiveCrabBeaconsOnStartup(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    @patch('eve_log_reader.EVELogReader.perform_startup_crab_scan')
    def test_scan_for_active_crab_beacons_on_startup_calls_perform_scan(self, mock_perform_scan):
        """Test that scan_for_active_crab_beacons_on_startup calls perform_startup_crab_scan"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            reader.scan_for_active_crab_beacons_on_startup()
            
            # Verify perform_startup_crab_scan was called
            mock_perform_scan.assert_called_once()
            
    def test_scan_for_active_crab_beacons_on_startup_handles_exception(self):
        """Test that scan_for_active_crab_beacons_on_startup handles exceptions gracefully"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'), \
             patch('eve_log_reader.EVELogReader.perform_startup_crab_scan') as mock_perform_scan:
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            mock_perform_scan.side_effect = Exception("Scan error")
            
            reader = EVELogReader(self.root)
            
            # Should not raise exception
            reader.scan_for_active_crab_beacons_on_startup()

if __name__ == '__main__':
    unittest.main()
