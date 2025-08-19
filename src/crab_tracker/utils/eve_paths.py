"""
EVE Online path detection utilities.

This module provides functions to locate EVE Online log directories
and other game-related paths on the system.
"""

import os
from pathlib import Path


def find_eve_log_directory():
    """
    Find the EVE Online log directory on the system.
    
    Returns:
        str: Path to the EVE Online log directory, or None if not found.
    """
    # Common EVE Online log directory locations
    possible_paths = [
        # Primary location
        os.path.expanduser("~/Documents/EVE/logs/Gamelogs/"),
        # Fallback locations
        os.path.expanduser("~/Documents/EVE/logs/"),
        os.path.expanduser("~/AppData/Local/CCP/EVE/logs/"),
        # Alternative locations
        "C:/Users/Public/Documents/EVE/logs/",
        "C:/Program Files/CCP/EVE/logs/",
        # Windows specific
        os.path.expanduser("~/Documents/EVE/logs/"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            return path
    
    return None


def get_eve_character_logs(log_dir, character_id=None):
    """
    Get log files for a specific character or all characters.
    
    Args:
        log_dir (str): Base EVE log directory
        character_id (str, optional): Specific character ID to filter by
        
    Returns:
        list: List of log file paths
    """
    if not log_dir or not os.path.exists(log_dir):
        return []
    
    log_files = []
    for file in os.listdir(log_dir):
        if file.endswith(('.txt', '.log', '.xml')):
            if character_id is None or character_id in file:
                log_files.append(os.path.join(log_dir, file))
    
    return sorted(log_files, reverse=True)


def is_eve_log_file(filename):
    """
    Check if a filename follows EVE Online log naming convention.
    
    Args:
        filename (str): Filename to check
        
    Returns:
        bool: True if it's an EVE log file, False otherwise
    """
    # EVE log format: YYYYMMDD_HHMMSS_characterID.txt
    import re
    pattern = r'^\d{8}_\d{6}_\d+\.(txt|log|xml)$'
    return bool(re.match(pattern, filename))
