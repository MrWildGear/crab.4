"""
Test file for EVELogReader.refresh_eve_client_status method
Tests the EVE client status refresh functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestRefreshEveClientStatus(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    @patch('eve_log_reader.EVELogReader.get_active_eve_clients')
    def test_refresh_eve_client_status_with_clients(self, mock_get_clients):
        """Test refresh when EVE clients are active"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Mock active clients
            mock_clients = [
                {'pid': 1234, 'name': 'Exefile.exe'},
                {'pid': 5678, 'name': 'Exefile.exe'}
            ]
            mock_get_clients.return_value = mock_clients
            
            reader.refresh_eve_client_status()
            
            # Verify cache was updated
            self.assertEqual(reader._active_eve_clients_cache, mock_clients)
            self.assertIsNotNone(reader._eve_clients_cache_time)
            
    @patch('eve_log_reader.EVELogReader.get_active_eve_clients')
    def test_refresh_eve_client_status_no_clients(self, mock_get_clients):
        """Test refresh when no EVE clients are active"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Mock no active clients
            mock_get_clients.return_value = []
            
            reader.refresh_eve_client_status()
            
            # Verify cache was updated
            self.assertEqual(reader._active_eve_clients_cache, [])
            self.assertIsNotNone(reader._eve_clients_cache_time)
            
    @patch('eve_log_reader.EVELogReader.get_active_eve_clients')
    def test_refresh_eve_client_status_exception(self, mock_get_clients):
        """Test refresh handles exceptions gracefully"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Mock exception
            mock_get_clients.side_effect = Exception("Process access denied")
            
            # Should not raise exception
            reader.refresh_eve_client_status()
            
            # Cache should remain unchanged
            self.assertIsNone(reader._active_eve_clients_cache)
            self.assertIsNone(reader._eve_clients_cache_time)

if __name__ == '__main__':
    unittest.main()
