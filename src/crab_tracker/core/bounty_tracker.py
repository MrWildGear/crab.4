"""
Bounty tracking system for CRAB Tracker.

This module handles tracking of bounty earnings from EVE Online,
including CRAB-specific bounty tracking and session management.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class BountyEntry:
    """Represents a single bounty entry."""
    timestamp: datetime
    amount: int
    source: str
    target: str
    location: str = ""
    session_id: str = ""
    beacon_id: str = ""
    character_name: str = ""
    
    def __str__(self):
        beacon_info = f" (Beacon: {self.beacon_id})" if self.beacon_id else ""
        char_info = f" [{self.character_name}]" if self.character_name else ""
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.amount:,} ISK from {self.target}{beacon_info}{char_info}"


class BountyTracker:
    """Tracks bounty earnings and sessions."""
    
    def __init__(self):
        """Initialize the bounty tracker."""
        import logging
        self.logger = logging.getLogger(__name__)
        
        self.bounty_entries: List[BountyEntry] = []
        self.crab_bounty_entries: List[BountyEntry] = []
        self.session_start: Optional[datetime] = None
        self.crab_session_active: bool = False
        
        # Bounty patterns
        self.bounty_patterns = {
            'standard_bounty': r'bounty.*?(\d+(?:,\d+)*)\s*ISK',
            'kill_bounty': r'You.*?destroyed.*?(\w+).*?bounty.*?(\d+(?:,\d+)*)\s*ISK',
            'mission_bounty': r'mission.*?reward.*?(\d+(?:,\d+)*)\s*ISK',
        }
    
    def start_session(self, session_id: str = None):
        """
        Start a new bounty tracking session.
        
        Args:
            session_id (str, optional): Custom session ID
        """
        self.session_start = datetime.now()
        if session_id is None:
            session_id = f"session_{self.session_start.strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"Bounty session started: {session_id}")
    
    def end_session(self):
        """End the current bounty tracking session."""
        if self.session_start:
            duration = datetime.now() - self.session_start
            total_bounty = self.get_total_bounty()
            self.logger.info(f"Bounty session ended. Duration: {duration}, Total: {total_bounty:,} ISK")
            
            self.session_start = None
            return {
                'duration': duration,
                'total_bounty': total_bounty,
                'entry_count': len(self.bounty_entries)
            }
        return None
    
    def add_bounty_entry(self, entry: BountyEntry):
        """
        Add a new bounty entry.
        
        Args:
            entry (BountyEntry): Bounty entry to add
        """
        self.bounty_entries.append(entry)
        
        # If CRAB session is active, also add to CRAB entries
        if self.crab_session_active:
            self.crab_bounty_entries.append(entry)
        
        self.logger.info(f"Bounty entry added: {entry}")
    
    def add_bounty_with_beacon(self, timestamp: datetime, amount: int, source: str, 
                              target: str = "", location: str = "", beacon_id: str = "", 
                              character_name: str = ""):
        """
        Add a new bounty entry with beacon tracking.
        
        Args:
            timestamp (datetime): When the bounty was received
            amount (int): Bounty amount in ISK
            source (str): Source of the bounty (e.g., rat type, mission name)
            target (str): Target that was killed
            location (str): Location where bounty was received
            beacon_id (str): Beacon ID to associate with this bounty
            character_name (str): Character name that received the bounty
        """
        entry = BountyEntry(
            timestamp=timestamp,
            amount=amount,
            source=source,
            target=target,
            location=location,
            session_id=self._get_current_session_id(),
            beacon_id=beacon_id,
            character_name=character_name
        )
        
        self.add_bounty_entry(entry)
        return entry
    
    def parse_bounty_from_log(self, log_content: str, timestamp: datetime, source: str = "") -> Optional[BountyEntry]:
        """
        Parse bounty information from a log entry.
        
        Args:
            log_content (str): Log content to parse
            timestamp (datetime): Timestamp of the log entry
            source (str): Source of the bounty
            
        Returns:
            BountyEntry if bounty found, None otherwise
        """
        # Check for bounty patterns
        for pattern_name, pattern in self.bounty_patterns.items():
            match = re.search(pattern, log_content, re.IGNORECASE)
            if match:
                if pattern_name == 'kill_bounty':
                    target = match.group(1)
                    amount = int(match.group(2).replace(',', ''))
                else:
                    target = "Unknown"
                    amount = int(match.group(1).replace(',', ''))
                
                entry = BountyEntry(
                    timestamp=timestamp,
                    amount=amount,
                    source=source,
                    target=target,
                    session_id=self._get_current_session_id()
                )
                
                return entry
        
        return None
    
    def get_total_bounty(self, session_only: bool = False) -> int:
        """
        Get total bounty earned.
        
        Args:
            session_only (bool): If True, only count current session
            
        Returns:
            Total bounty amount in ISK
        """
        if session_only and self.session_start:
            # Only count entries from current session
            session_entries = [
                entry for entry in self.bounty_entries
                if entry.timestamp >= self.session_start
            ]
            return sum(entry.amount for entry in session_entries)
        
        return sum(entry.amount for entry in self.bounty_entries)
    
    def get_crab_total_bounty(self) -> int:
        """
        Get total bounty earned during CRAB sessions.
        
        Returns:
            Total CRAB bounty amount in ISK
        """
        return sum(entry.amount for entry in self.crab_bounty_entries)
    
    def get_bounties_by_beacon(self, beacon_id: str) -> List[BountyEntry]:
        """
        Get all bounty entries associated with a specific beacon.
        
        Args:
            beacon_id (str): Beacon ID to filter by
            
        Returns:
            List of bounty entries for the specified beacon
        """
        return [entry for entry in self.bounty_entries if entry.beacon_id == beacon_id]
    
    def get_beacon_bounty_total(self, beacon_id: str) -> int:
        """
        Get total bounty earned for a specific beacon.
        
        Args:
            beacon_id (str): Beacon ID to get total for
            
        Returns:
            Total bounty amount in ISK for the specified beacon
        """
        beacon_entries = self.get_bounties_by_beacon(beacon_id)
        return sum(entry.amount for entry in beacon_entries)
    
    def get_beacon_summary(self, beacon_id: str) -> Dict[str, Any]:
        """
        Get summary of bounty data for a specific beacon.
        
        Args:
            beacon_id (str): Beacon ID to get summary for
            
        Returns:
            Dict containing beacon bounty summary
        """
        beacon_entries = self.get_bounties_by_beacon(beacon_id)
        if not beacon_entries:
            return {
                'beacon_id': beacon_id,
                'total_bounty': 0,
                'entry_count': 0,
                'characters': [],
                'sources': []
            }
        
        total_bounty = sum(entry.amount for entry in beacon_entries)
        characters = list(set(entry.character_name for entry in beacon_entries if entry.character_name))
        sources = list(set(entry.source for entry in beacon_entries))
        
        return {
            'beacon_id': beacon_id,
            'total_bounty': total_bounty,
            'entry_count': len(beacon_entries),
            'characters': characters,
            'sources': sources,
            'first_bounty': min(entry.timestamp for entry in beacon_entries),
            'last_bounty': max(entry.timestamp for entry in beacon_entries)
        }
    
    def start_crab_session(self):
        """Start a CRAB-specific bounty session."""
        self.crab_session_active = True
        self.logger.info("CRAB bounty session started")
    
    def end_crab_session(self):
        """End the CRAB bounty session."""
        if self.crab_session_active:
            total_crab_bounty = self.get_crab_total_bounty()
            self.logger.info(f"CRAB session ended. Total bounty: {total_crab_bounty:,} ISK")
            self.crab_session_active = False
    
    def get_session_duration(self) -> timedelta:
        """
        Get the duration of the current session.
        
        Returns:
            Session duration as timedelta
        """
        if self.session_start:
            return datetime.now() - self.session_start
        return timedelta(0)
    
    def get_bounty_summary(self) -> Dict[str, Any]:
        """
        Get a summary of bounty tracking.
        
        Returns:
            Dict containing bounty summary information
        """
        return {
            'total_bounty': self.get_total_bounty(),
            'session_bounty': self.get_total_bounty(session_only=True),
            'crab_bounty': self.get_crab_total_bounty(),
            'entry_count': len(self.bounty_entries),
            'crab_entry_count': len(self.crab_bounty_entries),
            'session_active': self.session_start is not None,
            'crab_session_active': self.crab_session_active,
            'session_duration': self.get_session_duration(),
            'session_start': self.session_start
        }
    
    def export_bounty_data(self, format: str = 'csv') -> str:
        """
        Export bounty data to a file.
        
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
        """Export bounty data to CSV format."""
        import csv
        from pathlib import Path
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"bounty_export_{timestamp}.csv"
        filepath = Path('exports') / filename
        
        # Create exports directory if it doesn't exist
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Amount', 'Source', 'Target', 'Location', 'Session ID', 'Beacon ID', 'Character'])
            
            for entry in self.bounty_entries:
                writer.writerow([
                    entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    entry.amount,
                    entry.source,
                    entry.target,
                    entry.location,
                    entry.session_id,
                    entry.beacon_id,
                    entry.character_name
                ])
        
        return str(filepath)
    
    def _export_to_txt(self) -> str:
        """Export bounty data to text format."""
        from pathlib import Path
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"bounty_export_{timestamp}.txt"
        filepath = Path('exports') / filename
        
        # Create exports directory if it doesn't exist
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("CRAB Tracker - Bounty Export\n")
            f.write("=" * 50 + "\n\n")
            
            for entry in self.bounty_entries:
                f.write(f"{entry}\n")
            
            f.write(f"\nTotal Bounty: {self.get_total_bounty():,} ISK\n")
            f.write(f"Total CRAB Bounty: {self.get_crab_total_bounty():,} ISK\n")
        
        return str(filepath)
    
    def _get_current_session_id(self) -> str:
        """Get the current session ID."""
        if self.session_start:
            return f"session_{self.session_start.strftime('%Y%m%d_%H%M%S')}"
        return "no_session"
