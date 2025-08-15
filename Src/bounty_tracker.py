"""
Bounty tracking system for EVE Log Reader
"""
from datetime import datetime
from typing import List, Dict, Any

class BountyTracker:
    """Handles bounty tracking and statistics"""
    
    def __init__(self):
        self.bounty_entries: List[Dict[str, Any]] = []
        self.total_bounty_isk: float = 0.0
        self.session_start: datetime = None
        self.session_active: bool = False
    
    def start_session(self):
        """Start a new bounty tracking session"""
        self.session_start = datetime.now()
        self.session_active = True
        print(f"💰 Bounty tracking session started at {self.session_start}")
    
    def end_session(self):
        """End the current bounty tracking session"""
        self.session_active = False
        if self.session_start:
            duration = datetime.now() - self.session_start
            print(f"💰 Bounty tracking session ended. Duration: {duration}")
    
    def add_bounty(self, timestamp: datetime, isk_amount: float, source_file: str):
        """Add a new bounty entry"""
        if not self.session_active:
            print("⚠️ Warning: Adding bounty outside of active session")
        
        bounty_entry = {
            'timestamp': timestamp,
            'isk_amount': isk_amount,
            'source_file': source_file,
            'session_time': timestamp - self.session_start if self.session_start else None
        }
        
        self.bounty_entries.append(bounty_entry)
        self.total_bounty_isk += isk_amount
        
        print(f"💰 Bounty added: {isk_amount:,} ISK from {source_file}")
    
    def reset_tracking(self):
        """Reset all bounty tracking data"""
        self.bounty_entries.clear()
        self.total_bounty_isk = 0.0
        self.session_start = None
        self.session_active = False
        print("💰 Bounty tracking reset")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current bounty statistics"""
        if not self.bounty_entries:
            return {
                'total_bounties': 0,
                'total_isk': 0,
                'average_bounty': 0,
                'largest_bounty': 0,
                'smallest_bounty': 0,
                'session_duration': None
            }
        
        stats = {
            'total_bounties': len(self.bounty_entries),
            'total_isk': self.total_bounty_isk,
            'average_bounty': self.total_bounty_isk / len(self.bounty_entries),
            'largest_bounty': max(entry['isk_amount'] for entry in self.bounty_entries),
            'smallest_bounty': min(entry['isk_amount'] for entry in self.bounty_entries),
            'session_duration': datetime.now() - self.session_start if self.session_start else None
        }
        
        return stats
    
    def export_bounties(self, filename: str = None) -> str:
        """Export bounty data to a file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bounty_export_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("EVE Online Bounty Export\n")
                f.write("=" * 50 + "\n\n")
                
                stats = self.get_statistics()
                f.write(f"Session Start: {self.session_start}\n")
                f.write(f"Session Duration: {stats['session_duration']}\n")
                f.write(f"Total Bounties: {stats['total_bounties']}\n")
                f.write(f"Total ISK: {stats['total_isk']:,} ISK\n")
                f.write(f"Average Bounty: {stats['average_bounty']:,.0f} ISK\n")
                f.write(f"Largest Bounty: {stats['largest_bounty']:,} ISK\n")
                f.write(f"Smallest Bounty: {stats['smallest_bounty']:,} ISK\n\n")
                
                f.write("Individual Bounties:\n")
                f.write("-" * 30 + "\n")
                
                for i, entry in enumerate(self.bounty_entries, 1):
                    f.write(f"{i}. {entry['timestamp']} - {entry['isk_amount']:,} ISK")
                    if entry['session_time']:
                        f.write(f" (Session: {entry['session_time']})")
                    f.write(f" - {entry['source_file']}\n")
            
            print(f"💰 Bounty data exported to {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error exporting bounty data: {e}")
            return None

class CRABBountyTracker(BountyTracker):
    """Specialized bounty tracker for CRAB operations"""
    
    def __init__(self):
        super().__init__()
        self.crab_session_active = False
    
    def start_crab_session(self):
        """Start a CRAB bounty tracking session"""
        self.crab_session_active = True
        self.start_session()
        print("🦀 CRAB bounty tracking session started")
    
    def end_crab_session(self, status: str = "Completed"):
        """End the CRAB bounty tracking session"""
        self.crab_session_active = False
        self.end_session()
        print(f"🦀 CRAB bounty tracking session ended: {status}")
    
    def add_crab_bounty(self, timestamp: datetime, isk_amount: float, source_file: str):
        """Add a CRAB bounty entry"""
        if not self.crab_session_active:
            print("⚠️ Warning: Adding CRAB bounty outside of active CRAB session")
        
        self.add_bounty(timestamp, isk_amount, source_file)
    
    def get_crab_statistics(self) -> Dict[str, Any]:
        """Get CRAB-specific bounty statistics"""
        stats = self.get_statistics()
        stats['crab_session_active'] = self.crab_session_active
        return stats
