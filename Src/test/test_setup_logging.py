"""
Test file for EVELogReader.setup_logging method
Tests the logging configuration functionality
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os
import logging

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import EVELogReader

class TestSetupLogging(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    @patch('eve_log_reader.logging.basicConfig')
    def test_setup_logging_configures_logging(self, mock_basic_config):
        """Test that setup_logging configures logging properly"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'):
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Verify logging was configured
            mock_basic_config.assert_called_once()
            
            # Check the call arguments
            call_args = mock_basic_config.call_args
            self.assertEqual(call_args[1]['level'], logging.DEBUG)
            self.assertIn('logs/google_form_debug.log', call_args[1]['filename'])
            self.assertIn('%(asctime)s - %(levelname)s - %(message)s', call_args[1]['format'])
            
    @patch('eve_log_reader.logging.basicConfig')
    def test_setup_logging_creates_log_directory(self, mock_basic_config):
        """Test that setup_logging creates log directory if it doesn't exist"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'), \
             patch('os.makedirs') as mock_makedirs:
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            reader = EVELogReader(self.root)
            
            # Verify makedirs was called to create logs directory
            mock_makedirs.assert_called_once_with('logs', exist_ok=True)
            
    @patch('eve_log_reader.logging.basicConfig')
    def test_setup_logging_handles_exception(self, mock_basic_config):
        """Test that setup_logging handles exceptions gracefully"""
        with patch('eve_log_reader.EVELogReader.find_eve_log_directory') as mock_find_dir, \
             patch('eve_log_reader.EVELogReader.setup_ui'), \
             patch('eve_log_reader.EVELogReader.load_log_files'), \
             patch('eve_log_reader.EVELogReader.scan_for_active_crab_beacons_on_startup'), \
             patch('eve_log_reader.EVELogReader.refresh_eve_client_status'), \
             patch('eve_log_reader.EVELogReader.start_monitoring_only'), \
             patch('os.makedirs') as mock_makedirs:
            
            mock_find_dir.return_value = "C:/test/eve/logs"
            mock_makedirs.side_effect = Exception("Permission denied")
            
            # Should not raise exception
            reader = EVELogReader(self.root)
            
            # Verify basic config was still called
            mock_basic_config.assert_called_once()

if __name__ == '__main__':
    unittest.main()
