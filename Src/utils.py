"""
Utility functions for EVE Log Reader
"""
import os
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from config import EVE_LOG_PATHS, HASH_BUFFER_SIZE

def find_eve_log_directory():
    """Find the EVE Online log directory"""
    for path in EVE_LOG_PATHS:
        if os.path.exists(path):
            return path
    
    # If not found, return user's Documents folder
    return os.path.expanduser("~/Documents")

def parse_filename_timestamp(filename):
    """Parse timestamp from EVE log filename"""
    # EVE log files typically have format: YYYYMMDD_HHMMSS_*.log
    timestamp_pattern = r'(\d{8})_(\d{6})'
    match = re.search(timestamp_pattern, filename)
    
    if match:
        date_str, time_str = match.groups()
        try:
            # Parse YYYYMMDD_HHMMSS format
            timestamp = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
            return timestamp
        except ValueError:
            pass
    
    # Fallback: try to get file modification time
    try:
        file_path = Path(filename)
        if file_path.exists():
            return datetime.fromtimestamp(file_path.stat().st_mtime)
    except (OSError, ValueError):
        pass
    
    return None

def is_recent_file(file_path, max_days_old=1):
    """Check if a file is recent enough to include"""
    try:
        # First try to parse timestamp from filename
        filename = os.path.basename(file_path)
        timestamp = parse_filename_timestamp(filename)
        
        if timestamp:
            # Check if timestamp is within the specified days
            cutoff_time = datetime.now() - timedelta(days=max_days_old)
            return timestamp >= cutoff_time
        
        # Fallback: check file modification time
        file_stat = os.stat(file_path)
        mod_time = datetime.fromtimestamp(file_stat.st_mtime)
        cutoff_time = datetime.now() - timedelta(days=max_days_old)
        return mod_time >= cutoff_time
        
    except (OSError, ValueError):
        return False

def calculate_file_hash(file_path):
    """Calculate MD5 hash of a file"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(HASH_BUFFER_SIZE), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (OSError, IOError):
        return None

def extract_timestamp(line):
    """Extract timestamp from a log line"""
    # Common EVE log timestamp patterns
    timestamp_patterns = [
        r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]',  # [2024-01-01 12:00:00]
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',      # 2024-01-01 12:00:00
        r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})',      # 01/01/2024 12:00:00
    ]
    
    for pattern in timestamp_patterns:
        match = re.search(pattern, line)
        if match:
            try:
                timestamp_str = match.group(1)
                # Try different date formats
                for fmt in ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"]:
                    try:
                        return datetime.strptime(timestamp_str, fmt)
                    except ValueError:
                        continue
            except (ValueError, IndexError):
                continue
    
    return None

def extract_bounty(line):
    """Extract bounty information from a log line"""
    # Common bounty patterns in EVE logs
    bounty_patterns = [
        r'bounty.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*ISK',  # bounty 1,234 ISK
        r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*ISK.*?bounty',  # 1,234 ISK bounty
        r'earned.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*ISK',  # earned 1,234 ISK
        r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*ISK.*?earned',  # 1,234 ISK earned
    ]
    
    for pattern in bounty_patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            try:
                # Remove commas and convert to float
                isk_str = match.group(1).replace(',', '')
                isk_amount = float(isk_str)
                return isk_amount
            except (ValueError, IndexError):
                continue
    
    return None

def detect_concord_message(line):
    """Detect CONCORD-related messages in log lines"""
    concord_keywords = [
        'concord', 'rogue', 'analysis', 'beacon', 'link', 'connecting',
        'connection', 'established', 'failed', 'timeout', 'countdown'
    ]
    
    line_lower = line.lower()
    return any(keyword in line_lower for keyword in concord_keywords)
