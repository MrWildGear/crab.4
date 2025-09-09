"""
Test file for EVELogReader.get_active_eve_clients method
Tests the EVE client detection functionality
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestGetActiveEveClients(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    @patch('eve_log_reader.psutil.process_iter')
    def test_get_active_eve_clients_no_processes(self, mock_process_iter):
        """Test get_active_eve_clients when no EVE processes are running"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            mock_process_iter.return_value = []
            
            reader = EVELogReader(self.root)
            result = reader.get_active_eve_clients()
            
            self.assertEqual(result, [])
            
    @patch('eve_log_reader.psutil.process_iter')
    def test_get_active_eve_clients_with_eve_processes(self, mock_process_iter):
        """Test get_active_eve_clients when EVE processes are running"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            
            # Mock EVE processes
            mock_process1 = Mock()
            mock_process1.name.return_value = "Exefile.exe"
            mock_process1.pid = 1234
            mock_process1.cmdline.return_value = ["Exefile.exe", "--character", "TestChar"]
            
            mock_process2 = Mock()
            mock_process2.name.return_value = "Exefile.exe"
            mock_process2.pid = 5678
            mock_process2.cmdline.return_value = ["Exefile.exe", "--character", "TestChar2"]
            
            mock_process_iter.return_value = [mock_process1, mock_process2]
            
            reader = EVELogReader(self.root)
            result = reader.get_active_eve_clients()
            
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['pid'], 1234)
            self.assertEqual(result[1]['pid'], 5678)
            
    @patch('eve_log_reader.psutil.process_iter')
    def test_get_active_eve_clients_non_eve_processes(self, mock_process_iter):
        """Test get_active_eve_clients when non-EVE processes are running"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            
            # Mock non-EVE processes
            mock_process1 = Mock()
            mock_process1.name.return_value = "notepad.exe"
            mock_process1.pid = 1234
            
            mock_process2 = Mock()
            mock_process2.name.return_value = "chrome.exe"
            mock_process2.pid = 5678
            
            mock_process_iter.return_value = [mock_process1, mock_process2]
            
            reader = EVELogReader(self.root)
            result = reader.get_active_eve_clients()
            
            self.assertEqual(result, [])
            
    @patch('eve_log_reader.psutil.process_iter')
    def test_get_active_eve_clients_exception_handling(self, mock_process_iter):
        """Test get_active_eve_clients handles exceptions gracefully"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            mock_process_iter.side_effect = Exception("Process access denied")
            
            reader = EVELogReader(self.root)
            result = reader.get_active_eve_clients()
            
            # Should return empty list on exception
            self.assertEqual(result, [])
            
    @patch('eve_log_reader.psutil.process_iter')
    def test_get_active_eve_clients_process_access_error(self, mock_process_iter):
        """Test get_active_eve_clients handles process access errors"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            
            # Mock process that raises exception when accessing name
            mock_process = Mock()
            mock_process.name.side_effect = Exception("Access denied")
            mock_process_iter.return_value = [mock_process]
            
            reader = EVELogReader(self.root)
            result = reader.get_active_eve_clients()
            
            # Should return empty list when process access fails
            self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
