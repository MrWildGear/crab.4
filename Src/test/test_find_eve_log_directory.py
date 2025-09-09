"""
Test file for EVELogReader.find_eve_log_directory method
Tests the EVE log directory detection functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestFindEveLogDirectory(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    @patch('eve_log_reader.os.path.exists')
    def test_find_eve_log_directory_default_path_exists(self, mock_exists):
        """Test finding EVE log directory at default location"""
        with patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            # Mock only the first path (Gamelogs) exists
            def mock_exists_side_effect(path):
                return path == os.path.expanduser("~/Documents/EVE/logs/Gamelogs")
            mock_exists.side_effect = mock_exists_side_effect
            
            reader = EVELogReader(self.root)
            result = reader.find_eve_log_directory()
            
            # Should return the Gamelogs path (first one that exists)
            expected_path = os.path.expanduser("~/Documents/EVE/logs/Gamelogs")
            self.assertEqual(result, expected_path)
            
    @patch('eve_log_reader.os.path.exists')
    def test_find_eve_log_directory_default_path_not_exists(self, mock_exists):
        """Test when default EVE log directory doesn't exist"""
        with patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            # Mock no EVE paths exist
            mock_exists.return_value = False
            
            reader = EVELogReader(self.root)
            result = reader.find_eve_log_directory()
            
            # Should return Documents folder as fallback
            expected_path = os.path.expanduser("~/Documents")
            self.assertEqual(result, expected_path)
            
    @patch('eve_log_reader.os.path.exists')
    def test_find_eve_log_directory_alternative_paths(self, mock_exists):
        """Test finding EVE log directory at alternative locations"""
        with patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            # Mock first path doesn't exist, second does (Gamelogs)
            def side_effect(path):
                if "Documents/EVE/logs" in path:
                    return False
                elif "AppData/Local/CCP/EVE/logs/Gamelogs" in path:
                    return True
                return False
                
            mock_exists.side_effect = side_effect
            
            reader = EVELogReader(self.root)
            result = reader.find_eve_log_directory()
            
            # Should return the alternative Gamelogs path
            expected_path = os.path.expanduser("~/AppData/Local/CCP/EVE/logs/Gamelogs")
            self.assertEqual(result, expected_path)
            
    @patch('eve_log_reader.os.path.exists')
    def test_find_eve_log_directory_no_paths_exist(self, mock_exists):
        """Test when no EVE log directories exist"""
        with patch('eve_log_reader.EVELogReader.setup_logging'), \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            # Mock no paths exist
            mock_exists.return_value = False
            
            reader = EVELogReader(self.root)
            result = reader.find_eve_log_directory()
            
            # Should return Documents folder as fallback
            expected_path = os.path.expanduser("~/Documents")
            self.assertEqual(result, expected_path)

if __name__ == '__main__':
    unittest.main()
