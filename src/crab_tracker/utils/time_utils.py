"""
Time utility functions for CRAB Tracker.

This module provides functions for formatting time durations and
parsing EVE Online log timestamps.
"""

from datetime import datetime, timedelta
import re


def format_duration(seconds):
    """
    Format duration in seconds to human-readable format.
    
    Args:
        seconds (int): Duration in seconds
        
    Returns:
        str: Formatted duration string (e.g., "2h 15m 30s")
    """
    if seconds < 0:
        return "0s"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes:02d}m")
    if seconds > 0 or not parts:
        parts.append(f"{int(seconds):02d}s")
    
    return " ".join(parts)


def parse_eve_timestamp(timestamp_str):
    """
    Parse EVE Online log timestamp.
    
    Args:
        timestamp_str (str): Timestamp string from EVE logs
        
    Returns:
        datetime: Parsed datetime object, or None if parsing fails
    """
    # Common EVE timestamp formats
    formats = [
        "%Y.%m.%d %H:%M:%S",  # 2025.08.19 07:37:05 (most common EVE format)
        "%Y-%m-%d %H:%M:%S",  # 2025-01-15 16:48:34
        "%d/%m/%Y %H:%M:%S",  # 15/01/2025 16:48:34
        "%m/%d/%Y %H:%M:%S",  # 01/15/2025 16:48:34
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    return None


def parse_eve_filename_timestamp(filename):
    """
    Parse timestamp from EVE log filename.
    
    Args:
        filename (str): EVE log filename (e.g., "20250115_164834_94266210.txt")
        
    Returns:
        datetime: Parsed datetime object, or None if parsing fails
    """
    # EVE filename format: YYYYMMDD_HHMMSS_characterID.txt
    pattern = r'^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})_\d+\.(txt|log|xml)$'
    match = re.match(pattern, filename)
    
    if match:
        try:
            year, month, day, hour, minute, second = map(int, match.groups()[:6])
            return datetime(year, month, day, hour, minute, second)
        except ValueError:
            pass
    
    return None


def get_time_difference(timestamp1, timestamp2):
    """
    Calculate time difference between two timestamps.
    
    Args:
        timestamp1 (datetime): First timestamp
        timestamp2 (datetime): Second timestamp
        
    Returns:
        timedelta: Time difference
    """
    if isinstance(timestamp1, str):
        timestamp1 = parse_eve_timestamp(timestamp1)
    if isinstance(timestamp2, str):
        timestamp2 = parse_eve_timestamp(timestamp2)
    
    if timestamp1 and timestamp2:
        return abs(timestamp2 - timestamp1)
    
    return timedelta(0)


def is_recent_timestamp(timestamp, max_days=1):
    """
    Check if a timestamp is within the specified number of days.
    
    Args:
        timestamp (datetime): Timestamp to check
        max_days (int): Maximum number of days to consider "recent"
        
    Returns:
        bool: True if timestamp is recent, False otherwise
    """
    if isinstance(timestamp, str):
        timestamp = parse_eve_timestamp(timestamp)
    
    if not timestamp:
        return False
    
    cutoff_date = datetime.now() - timedelta(days=max_days)
    return timestamp >= cutoff_date
