"""
Log parser for EVE Online log files.

This module handles parsing and processing of EVE Online log files,
including timestamp extraction and log entry parsing.
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..utils.time_utils import parse_eve_timestamp, parse_eve_filename_timestamp


class LogEntry:
    """Represents a single log entry."""
    
    def __init__(self, content: str, timestamp: Optional[datetime] = None, 
                 source_file: str = "", line_number: int = 0):
        self.content = content.strip()
        self.timestamp = timestamp
        self.source_file = source_file
        self.line_number = line_number
        self.parsed_data = {}
    
    def __str__(self):
        timestamp_str = self.timestamp.strftime("%H:%M:%S") if self.timestamp else "??:??:??"
        return f"[{timestamp_str}] {self.content}"
    
    def __repr__(self):
        return f"LogEntry(content='{self.content[:50]}...', timestamp={self.timestamp})"


class LogParser:
    """Parser for EVE Online log files."""
    
    def __init__(self):
        """Initialize the log parser."""
        # Common EVE log patterns
        self.timestamp_patterns = [
            r'^(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})',  # 2025.01.15 16:48:34
            r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',    # 2025-01-15 16:48:34
            r'^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})',    # 15/01/2025 16:48:34
        ]
        
        # Bounty-related patterns
        self.bounty_patterns = {
            'bounty_received': r'bounty.*?(\d+(?:,\d+)*)\s*ISK',
            'bounty_kill': r'You.*?destroyed.*?(\w+).*?bounty.*?(\d+(?:,\d+)*)\s*ISK',
            'loot_dropped': r'(\w+).*?dropped.*?(\w+)',
        }
        
        # Beacon-related patterns
        self.beacon_patterns = {
            'beacon_start': r'CONCORD.*?Rogue.*?Analysis.*?Beacon',
            'beacon_complete': r'Beacon.*?analysis.*?complete',
            'beacon_failed': r'Beacon.*?analysis.*?failed',
        }
    
    def parse_log_file(self, file_path: str, max_lines: Optional[int] = None) -> List[LogEntry]:
        """
        Parse a log file and extract log entries.
        
        Args:
            file_path (str): Path to the log file
            max_lines (int, optional): Maximum number of lines to parse
            
        Returns:
            List of LogEntry objects
        """
        entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
                if max_lines:
                    lines = lines[-max_lines:]  # Get last N lines
                
                for line_num, line in enumerate(lines, 1):
                    entry = self.parse_line(line.strip(), file_path, line_num)
                    if entry:
                        entries.append(entry)
                        
        except Exception as e:
            print(f"Error parsing log file {file_path}: {e}")
        
        return entries
    
    def parse_line(self, line: str, source_file: str = "", line_number: int = 0) -> Optional[LogEntry]:
        """
        Parse a single log line.
        
        Args:
            line (str): Log line to parse
            source_file (str): Source file path
            line_number (int): Line number in source file
            
        Returns:
            LogEntry object or None if line is empty/invalid
        """
        if not line.strip():
            return None
        
        # Extract timestamp
        timestamp = self.extract_timestamp(line)
        
        # Create log entry
        entry = LogEntry(line, timestamp, source_file, line_number)
        
        # Parse additional data
        entry.parsed_data = self.parse_log_data(line)
        
        return entry
    
    def extract_timestamp(self, line: str) -> Optional[datetime]:
        """
        Extract timestamp from a log line.
        
        Args:
            line (str): Log line to extract timestamp from
            
        Returns:
            datetime object or None if no timestamp found
        """
        for pattern in self.timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                timestamp_str = match.group(1)
                return parse_eve_timestamp(timestamp_str)
        
        return None
    
    def parse_log_data(self, line: str) -> Dict[str, Any]:
        """
        Parse additional data from a log line.
        
        Args:
            line (str): Log line to parse
            
        Returns:
            Dict containing parsed data
        """
        data = {}
        
        # Check for bounty information
        for pattern_name, pattern in self.bounty_patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                data[pattern_name] = match.groups()
        
        # Check for beacon information
        for pattern_name, pattern in self.beacon_patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                data[pattern_name] = True
        
        return data
    
    def filter_entries_by_time(self, entries: List[LogEntry], 
                              start_time: Optional[datetime] = None,
                              end_time: Optional[datetime] = None) -> List[LogEntry]:
        """
        Filter log entries by time range.
        
        Args:
            entries (List[LogEntry]): List of log entries to filter
            start_time (datetime, optional): Start time filter
            end_time (datetime, optional): End time filter
            
        Returns:
            Filtered list of LogEntry objects
        """
        if not start_time and not end_time:
            return entries
        
        filtered = []
        for entry in entries:
            if not entry.timestamp:
                continue
            
            if start_time and entry.timestamp < start_time:
                continue
            
            if end_time and entry.timestamp > end_time:
                continue
            
            filtered.append(entry)
        
        return filtered
    
    def sort_entries_by_time(self, entries: List[LogEntry], 
                            reverse: bool = True) -> List[LogEntry]:
        """
        Sort log entries by timestamp.
        
        Args:
            entries (List[LogEntry]): List of log entries to sort
            reverse (bool): If True, sort newest first
            
        Returns:
            Sorted list of LogEntry objects
        """
        return sorted(entries, key=lambda x: x.timestamp or datetime.min, reverse=reverse)
