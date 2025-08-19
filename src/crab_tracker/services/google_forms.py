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
            # Try to find config in resources directory
            current_dir = Path(__file__).parent.parent.parent
            config_path = current_dir / "resources" / "config" / "google_forms.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.logger.info(f"Google Forms config loaded from {config_path}")
            return config
        except FileNotFoundError:
            self.logger.error(f"Google Forms config not found at {config_path}")
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
            return False
        
        form_url = self.config.get('form_url')
        field_mappings = self.config.get('field_mappings', {})
        
        if not form_url:
            self.logger.error("No form URL in configuration")
            return False
        
        # Prepare form data
        form_data = {}
        for field_name, entry_id in field_mappings.items():
            if field_name in session_data:
                form_data[entry_id] = str(session_data[field_name])
        
        try:
            # Submit to Google Forms
            response = requests.post(form_url, data=form_data, timeout=30)
            
            if response.status_code == 200:
                self.logger.info("Beacon session data submitted successfully")
                return True
            else:
                self.logger.error(f"Form submission failed with status {response.status_code}")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"Error submitting to Google Forms: {e}")
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
