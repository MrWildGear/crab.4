"""
Test file for main function
Tests the main application entry point
"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_log_reader import main

class TestMain(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
    def tearDown(self):
        """Clean up after each test method."""
        self.root.destroy()
        
    def test_main_basic_functionality(self):
        """Test basic functionality of main function"""
        with patch('eve_log_reader.EVELogReader') as mock_eve_log_reader:
            # Mock the EVELogReader class
            mock_instance = Mock()
            mock_eve_log_reader.return_value = mock_instance
            
            # Should not raise exception
            main()
            
            # Verify EVELogReader was instantiated
            mock_eve_log_reader.assert_called_once()
            
    def test_main_handles_exception(self):
        """Test that main function handles exceptions gracefully"""
        with patch('eve_log_reader.EVELogReader') as mock_eve_log_reader:
            # Mock exception during instantiation
            mock_eve_log_reader.side_effect = Exception("Initialization error")
            
            # Should not raise exception
            main()

if __name__ == '__main__':
    unittest.main()
