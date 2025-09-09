"""
Test file for EVELogReader.add_bounty_entry method
Tests the bounty entry addition functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestAddBountyEntry(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    def test_add_bounty_entry_valid_data(self):
        """Test adding valid bounty entry"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test with valid bounty data
            timestamp = "2024-01-01 12:00:00"
            isk_amount = 1000000
            source_file = "test.log"
            
            reader.add_bounty_entry(timestamp, isk_amount, source_file)
            
            # Verify bounty was added
            self.assertEqual(len(reader.bounty_entries), 1)
            self.assertEqual(reader.total_bounty_isk, isk_amount)
            
    def test_add_bounty_entry_multiple_entries(self):
        """Test adding multiple bounty entries"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Add multiple bounty entries
            reader.add_bounty_entry("2024-01-01 12:00:00", 1000000, "test1.log")
            reader.add_bounty_entry("2024-01-01 12:01:00", 500000, "test2.log")
            
            # Verify both bounties were added
            self.assertEqual(len(reader.bounty_entries), 2)
            self.assertEqual(reader.total_bounty_isk, 1500000)
            
    def test_add_bounty_entry_zero_amount(self):
        """Test adding bounty entry with zero amount"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test with zero bounty amount
            reader.add_bounty_entry("2024-01-01 12:00:00", 0, "test.log")
            
            # Verify bounty was added but total remains 0
            self.assertEqual(len(reader.bounty_entries), 1)
            self.assertEqual(reader.total_bounty_isk, 0)
            
    def test_add_bounty_entry_negative_amount(self):
        """Test adding bounty entry with negative amount"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Test with negative bounty amount
            reader.add_bounty_entry("2024-01-01 12:00:00", -1000000, "test.log")
            
            # Verify bounty was added but total is negative
            self.assertEqual(len(reader.bounty_entries), 1)
            self.assertEqual(reader.total_bounty_isk, -1000000)

if __name__ == '__main__':
    unittest.main()
