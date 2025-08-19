"""
Beacon tracking system for CRAB Tracker.

This module handles tracking of CONCORD Rogue Analysis Beacon sessions,
including session timing, completion status, and data collection.
"""

import re
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class BeaconSession:
    """Represents a CONCORD Rogue Analysis Beacon session."""
    beacon_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    completed: bool = False
    failed: bool = False
    duration: Optional[timedelta] = None
    source_file: str = ""
    rogue_drone_data: int = 0
    loot_details: List[str] = None
    
    def __post_init__(self):
        if self.loot_details is None:
            self.loot_details = []
    
    def end_session(self, completed: bool = True, failed: bool = False):
        """
        End the beacon session.
        
        Args:
            completed (bool): Whether the beacon was completed successfully
            failed (bool): Whether the beacon failed
        """
        self.end_time = datetime.now()
        self.completed = completed
        self.failed = failed
        self.duration = self.end_time - self.start_time
    
    def get_duration(self) -> timedelta:
        """Get the current duration of the session."""
        if self.duration:
            return self.duration
        elif self.start_time:
            return datetime.now() - self.start_time
        return timedelta(0)
    
    def is_active(self) -> bool:
        """Check if the beacon session is currently active."""
        return self.start_time and not self.end_time
    
    def __str__(self):
        status = "Active" if self.is_active() else "Completed" if self.completed else "Failed"
        duration = self.get_duration()
        return f"Beacon {self.beacon_id[:8]}... - {status} - Duration: {duration}"


class BeaconTracker:
    """Tracks CONCORD Rogue Analysis Beacon sessions."""
    
    def __init__(self):
        """Initialize the beacon tracker."""
        self.active_sessions: List[BeaconSession] = []
        self.completed_sessions: List[BeaconSession] = []
        self.failed_sessions: List[BeaconSession] = []
        self.current_beacon_id: Optional[str] = None
        
        # Beacon-related patterns
        self.beacon_patterns = {
            'beacon_start': r'CONCORD.*?Rogue.*?Analysis.*?Beacon',
            'beacon_complete': r'Beacon.*?analysis.*?complete',
            'beacon_failed': r'Beacon.*?analysis.*?failed',
            'rogue_drone_data': r'Rogue.*?drone.*?data.*?(\d+)',
            'loot_dropped': r'(\w+).*?dropped.*?(\w+)',
        }
    
    def start_beacon_session(self, source_file: str = "") -> str:
        """
        Start a new beacon session.
        
        Args:
            source_file (str): Source log file for the beacon
            
        Returns:
            str: Generated beacon ID
        """
        # Generate unique beacon ID
        beacon_id = str(uuid.uuid4())
        
        # Create new session
        session = BeaconSession(
            beacon_id=beacon_id,
            start_time=datetime.now(),
            source_file=source_file
        )
        
        self.active_sessions.append(session)
        self.current_beacon_id = beacon_id
        
        return beacon_id
    
    def end_beacon_session(self, beacon_id: str, completed: bool = True, 
                          failed: bool = False) -> Optional[BeaconSession]:
        """
        End a beacon session.
        
        Args:
            beacon_id (str): ID of the beacon session to end
            completed (bool): Whether the beacon was completed successfully
            failed (bool): Whether the beacon failed
            
        Returns:
            BeaconSession if found, None otherwise
        """
        # Find the session
        session = self._find_session_by_id(beacon_id)
        if not session:
            return None
        
        # End the session
        session.end_session(completed, failed)
        
        # Move to appropriate list
        self.active_sessions.remove(session)
        
        if failed:
            self.failed_sessions.append(session)
        else:
            self.completed_sessions.append(session)
        
        # Clear current beacon ID if this was the current one
        if self.current_beacon_id == beacon_id:
            self.current_beacon_id = None
        
        return session
    
    def parse_beacon_log(self, log_content: str, timestamp: datetime, 
                        source_file: str = "") -> Dict[str, Any]:
        """
        Parse beacon-related information from a log entry.
        
        Args:
            log_content (str): Log content to parse
            timestamp (datetime): Timestamp of the log entry
            source_file (str): Source file of the log entry
            
        Returns:
            Dict containing parsed beacon information
        """
        result = {}
        
        # Check for beacon start
        if re.search(self.beacon_patterns['beacon_start'], log_content, re.IGNORECASE):
            beacon_id = self.start_beacon_session(source_file)
            result['beacon_started'] = True
            result['beacon_id'] = beacon_id
        
        # Check for beacon completion
        if re.search(self.beacon_patterns['beacon_complete'], log_content, re.IGNORECASE):
            if self.current_beacon_id:
                session = self.end_beacon_session(self.current_beacon_id, completed=True)
                result['beacon_completed'] = True
                result['beacon_id'] = self.current_beacon_id
        
        # Check for beacon failure
        if re.search(self.beacon_patterns['beacon_failed'], log_content, re.IGNORECASE):
            if self.current_beacon_id:
                session = self.end_beacon_session(self.current_beacon_id, completed=False, failed=True)
                result['beacon_failed'] = True
                result['beacon_id'] = self.current_beacon_id
        
        # Check for rogue drone data
        match = re.search(self.beacon_patterns['rogue_drone_data'], log_content, re.IGNORECASE)
        if match and self.current_beacon_id:
            data_amount = int(match.group(1))
            session = self._find_session_by_id(self.current_beacon_id)
            if session:
                session.rogue_drone_data = data_amount
                result['rogue_drone_data'] = data_amount
        
        # Check for loot drops
        match = re.search(self.beacon_patterns['loot_dropped'], log_content, re.IGNORECASE)
        if match and self.current_beacon_id:
            loot_item = match.group(2)
            session = self._find_session_by_id(self.current_beacon_id)
            if session:
                session.loot_details.append(loot_item)
                result['loot_dropped'] = loot_item
        
        return result
    
    def get_active_session(self) -> Optional[BeaconSession]:
        """Get the currently active beacon session."""
        if self.current_beacon_id:
            return self._find_session_by_id(self.current_beacon_id)
        return None
    
    def get_session_by_id(self, beacon_id: str) -> Optional[BeaconSession]:
        """Get a beacon session by ID."""
        return self._find_session_by_id(beacon_id)
    
    def get_all_sessions(self) -> List[BeaconSession]:
        """Get all beacon sessions (active, completed, and failed)."""
        return (self.active_sessions + 
                self.completed_sessions + 
                self.failed_sessions)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all beacon sessions.
        
        Returns:
            Dict containing session summary information
        """
        total_sessions = len(self.get_all_sessions())
        completed_count = len(self.completed_sessions)
        failed_count = len(self.failed_sessions)
        active_count = len(self.active_sessions)
        
        total_duration = timedelta(0)
        total_rogue_data = 0
        
        for session in self.completed_sessions:
            if session.duration:
                total_duration += session.duration
            total_rogue_data += session.rogue_drone_data
        
        return {
            'total_sessions': total_sessions,
            'completed_sessions': completed_count,
            'failed_sessions': failed_count,
            'active_sessions': active_count,
            'total_duration': total_duration,
            'total_rogue_drone_data': total_rogue_data,
            'current_beacon_id': self.current_beacon_id,
            'has_active_session': self.current_beacon_id is not None
        }
    
    def export_session_data(self, format: str = 'csv') -> str:
        """
        Export beacon session data to a file.
        
        Args:
            format (str): Export format ('csv' or 'txt')
            
        Returns:
            Path to exported file
        """
        if format == 'csv':
            return self._export_to_csv()
        else:
            return self._export_to_txt()
    
    def _export_to_csv(self) -> str:
        """Export beacon session data to CSV format."""
        import csv
        from pathlib import Path
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"beacon_sessions_{timestamp}.csv"
        filepath = Path('exports') / filename
        
        # Create exports directory if it doesn't exist
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Beacon ID', 'Start Time', 'End Time', 'Duration', 'Status',
                'Rogue Drone Data', 'Loot Details', 'Source File'
            ])
            
            for session in self.get_all_sessions():
                status = "Active" if session.is_active() else "Completed" if session.completed else "Failed"
                end_time = session.end_time.strftime('%Y-%m-%d %H:%M:%S') if session.end_time else ""
                duration = str(session.get_duration()) if session.get_duration() else ""
                loot_str = ", ".join(session.loot_details) if session.loot_details else ""
                
                writer.writerow([
                    session.beacon_id,
                    session.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    end_time,
                    duration,
                    status,
                    session.rogue_drone_data,
                    loot_str,
                    session.source_file
                ])
        
        return str(filepath)
    
    def _export_to_txt(self) -> str:
        """Export beacon session data to text format."""
        from pathlib import Path
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"beacon_sessions_{timestamp}.txt"
        filepath = Path('exports') / filename
        
        # Create exports directory if it doesn't exist
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("CRAB Tracker - Beacon Sessions Export\n")
            f.write("=" * 50 + "\n\n")
            
            for session in self.get_all_sessions():
                f.write(f"Beacon ID: {session.beacon_id}\n")
                f.write(f"Start Time: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                if session.end_time:
                    f.write(f"End Time: {session.end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duration: {session.get_duration()}\n")
                f.write(f"Status: {'Active' if session.is_active() else 'Completed' if session.completed else 'Failed'}\n")
                f.write(f"Rogue Drone Data: {session.rogue_drone_data}\n")
                if session.loot_details:
                    f.write(f"Loot: {', '.join(session.loot_details)}\n")
                f.write(f"Source: {session.source_file}\n")
                f.write("-" * 30 + "\n\n")
        
        return str(filepath)
    
    def _find_session_by_id(self, beacon_id: str) -> Optional[BeaconSession]:
        """Find a beacon session by ID."""
        # Check active sessions first
        for session in self.active_sessions:
            if session.beacon_id == beacon_id:
                return session
        
        # Check completed sessions
        for session in self.completed_sessions:
            if session.beacon_id == beacon_id:
                return session
        
        # Check failed sessions
        for session in self.failed_sessions:
            if session.beacon_id == beacon_id:
                return session
        
        return None
