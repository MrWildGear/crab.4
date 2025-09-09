"""
Test file for EVELogReader.reset_bounty_tracking method
Tests the bounty tracking reset functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestResetBountyTracking(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    def test_reset_bounty_tracking_clears_data(self):
        """Test that reset_bounty_tracking clears all bounty data"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Add some bounty data first
            reader.add_bounty_entry("2024-01-01 12:00:00", 1000000, "test.log")
            reader.add_bounty_entry("2024-01-01 12:01:00", 500000, "test.log")
            
            # Verify data exists
            self.assertEqual(len(reader.bounty_entries), 2)
            self.assertEqual(reader.total_bounty_isk, 1500000)
            
            # Reset bounty tracking
            reader.reset_bounty_tracking()
            
            # Verify data was cleared
            self.assertEqual(len(reader.bounty_entries), 0)
            self.assertEqual(reader.total_bounty_isk, 0)
            
    def test_reset_bounty_tracking_empty_data(self):
        """Test reset_bounty_tracking with empty data"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Reset with empty data
            reader.reset_bounty_tracking()
            
            # Verify data remains empty
            self.assertEqual(len(reader.bounty_entries), 0)
            self.assertEqual(reader.total_bounty_isk, 0)
            
    def test_reset_bounty_tracking_handles_exception(self):
        """Test that reset_bounty_tracking handles exceptions gracefully"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Should not raise exception even if internal logic fails
            reader.reset_bounty_tracking()

if __name__ == '__main__':
    unittest.main()
