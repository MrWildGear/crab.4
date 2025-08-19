"""
Google Forms integration service for CRAB Tracker.

This module handles submission of beacon session data to Google Forms
for data collection and analysis.
"""

import json
import requests
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import sys


class GoogleFormsService:
    """Service for Google Forms integration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Google Forms service.
        
        Args:
            config_path (str, optional): Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load Google Forms configuration.
        
        Args:
            config_path (str, optional): Path to configuration file
            
        Returns:
            Dict containing configuration data
        """
        if config_path is None:
            # Try multiple possible config locations for different environments
            possible_paths = []
            
            # 1. Try current working directory (for PyInstaller executable)
            possible_paths.append(Path.cwd() / "config" / "google_forms.json")
            
            # 2. Try executable directory (for PyInstaller executable)
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller executable
                exe_dir = Path(sys.executable).parent
                possible_paths.append(exe_dir / "config" / "google_forms.json")
            
            # 3. Try development path (for running from source)
            current_dir = Path(__file__).parent.parent.parent
            possible_paths.append(current_dir / "resources" / "config" / "google_forms.json")
            
            # 4. Try parent directory of executable (fallback)
            if getattr(sys, 'frozen', False):
                exe_dir = Path(sys.executable).parent
                possible_paths.append(exe_dir.parent / "config" / "google_forms.json")
            
            # Try each possible path
            for path in possible_paths:
                if path.exists():
                    config_path = path
                    break
            else:
                # If no path found, use the first one for error reporting
                config_path = possible_paths[0] if possible_paths else Path("config/google_forms.json")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.logger.info(f"Google Forms config loaded from {config_path}")
            return config
        except FileNotFoundError:
            self.logger.error(f"Google Forms config not found at {config_path}")
            self.logger.error(f"Tried paths: {[str(p) for p in possible_paths] if 'possible_paths' in locals() else 'N/A'}")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            return {}
    
    def submit_beacon_session(self, session_data: Dict[str, Any]) -> bool:
        """
        Submit beacon session data to Google Forms.
        
        Args:
            session_data (Dict): Session data to submit
            
        Returns:
            bool: True if submission successful, False otherwise
        """
        if not self.config:
            self.logger.error("No Google Forms configuration available")
            self.logger.error(f"Config object: {self.config}")
            return False
        
        form_url = self.config.get('form_url')
        field_mappings = self.config.get('field_mappings', {})
        
        if not form_url:
            self.logger.error("No form URL in configuration")
            self.logger.error(f"Available config keys: {list(self.config.keys())}")
            return False
        
        self.logger.info(f"Submitting to Google Forms URL: {form_url}")
        self.logger.info(f"Field mappings: {field_mappings}")
        self.logger.info(f"Session data keys: {list(session_data.keys())}")
        
        # Prepare form data
        form_data = {}
        for field_name, entry_id in field_mappings.items():
            if field_name in session_data:
                form_data[entry_id] = str(session_data[field_name])
                self.logger.info(f"Mapped field '{field_name}' -> '{entry_id}' = '{session_data[field_name]}'")
            else:
                self.logger.warning(f"Field '{field_name}' not found in session data")
        
        self.logger.info(f"Final form data to submit: {form_data}")
        
        try:
            # Submit to Google Forms
            self.logger.info(f"Submitting POST request to {form_url}")
            response = requests.post(form_url, data=form_data, timeout=30)
            
            self.logger.info(f"Response status: {response.status_code}")
            self.logger.info(f"Response headers: {dict(response.headers)}")
            self.logger.info(f"Response content: {response.text[:500]}...")  # First 500 chars
            
            if response.status_code == 200:
                self.logger.info("Beacon session data submitted successfully")
                return True
            else:
                self.logger.error(f"Form submission failed with status {response.status_code}")
                self.logger.error(f"Response content: {response.text}")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"Error submitting to Google Forms: {e}")
            self.logger.error(f"Exception type: {type(e).__name__}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        Get configuration information.
        
        Returns:
            Dict containing configuration details
        """
        return {
            'form_url': self.config.get('form_url', 'Not configured'),
            'field_mappings': self.config.get('field_mappings', {}),
            'version': self.config.get('version', 'Unknown'),
            'last_updated': self.config.get('last_updated', 'Unknown')
        }
    
    def test_connection(self) -> bool:
        """
        Test connection to Google Forms.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not self.config.get('form_url'):
            return False
        
        try:
            response = requests.get(self.config['form_url'], timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def test_config_loading(self) -> Dict[str, Any]:
        """
        Test configuration loading and return debug information.
        
        Returns:
            Dict containing debug information about config loading
        """
        debug_info = {
            'config_loaded': bool(self.config),
            'config_keys': list(self.config.keys()) if self.config else [],
            'form_url': self.config.get('form_url') if self.config else None,
            'field_mappings_count': len(self.config.get('field_mappings', {})) if self.config else 0,
            'field_mappings': self.config.get('field_mappings', {}) if self.config else {},
            'version': self.config.get('version') if self.config else None,
            'last_updated': self.config.get('last_updated') if self.config else None
        }
        
        # Test config file paths
        if getattr(sys, 'frozen', False):
            debug_info['environment'] = 'PyInstaller Executable'
            debug_info['executable_dir'] = str(Path(sys.executable).parent)
            debug_info['working_dir'] = str(Path.cwd())
            
            # Check if config file exists in expected locations
            exe_dir = Path(sys.executable).parent
            possible_config_paths = [
                exe_dir / "config" / "google_forms.json",
                Path.cwd() / "config" / "google_forms.json",
                exe_dir.parent / "config" / "google_forms.json"
            ]
            
            debug_info['config_file_exists'] = {}
            for path in possible_config_paths:
                debug_info['config_file_exists'][str(path)] = path.exists()
        else:
            debug_info['environment'] = 'Development'
            debug_info['current_dir'] = str(Path(__file__).parent.parent.parent)
        
        return debug_info
