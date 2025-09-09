"""
Test file for EVELogReader.is_log_from_active_client method
Tests the log file to active client matching functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestIsLogFromActiveClient(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    def test_is_log_from_active_client_no_active_clients(self):
        """Test when no active clients are running"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Mock empty active clients
            reader._active_eve_clients_cache = []
            
            result = reader.is_log_from_active_client("test.log")
            self.assertFalse(result)
            
    def test_is_log_from_active_client_matching_client(self):
        """Test when log file matches an active client"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Mock active clients with specific log file patterns
            reader._active_eve_clients_cache = [
                {'log_file_pattern': 'ChatLog_TestChar_*.txt'},
                {'log_file_pattern': 'ChatLog_OtherChar_*.txt'}
            ]
            
            result = reader.is_log_from_active_client("ChatLog_TestChar_20240101.txt")
            self.assertTrue(result)
            
    def test_is_log_from_active_client_no_matching_client(self):
        """Test when log file doesn't match any active client"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Mock active clients with different log file patterns
            reader._active_eve_clients_cache = [
                {'log_file_pattern': 'ChatLog_TestChar_*.txt'},
                {'log_file_pattern': 'ChatLog_OtherChar_*.txt'}
            ]
            
            result = reader.is_log_from_active_client("ChatLog_UnknownChar_20240101.txt")
            self.assertFalse(result)
            
    def test_is_log_from_active_client_cache_expired(self):
        """Test when client cache is expired and needs refresh"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'), \
             patch('eve_log_reader.EVELogReader.get_active_eve_clients') as mock_get_clients:
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Set up expired cache
            reader._active_eve_clients_cache = None
            reader._eve_clients_cache_time = None
            
            # Mock fresh client data
            mock_get_clients.return_value = [
                {'log_file_pattern': 'ChatLog_TestChar_*.txt'}
            ]
            
            result = reader.is_log_from_active_client("ChatLog_TestChar_20240101.txt")
            self.assertTrue(result)
            mock_get_clients.assert_called_once()

if __name__ == '__main__':
    unittest.main()
