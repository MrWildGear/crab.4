"""
Log monitoring and file change detection for EVE Log Reader
"""
import os
import glob
import threading
import time
from datetime import datetime
from typing import List, Dict, Set, Callable, Optional
from pathlib import Path

from config import LOG_PATTERNS, MAX_DAYS_OLD, MAX_FILES_TO_SHOW, MONITORING_INTERVAL
from utils import is_recent_file, calculate_file_hash, extract_timestamp, extract_bounty, detect_concord_message

class LogMonitor:
    """Handles log file monitoring and change detection"""
    
    def __init__(self, log_directory: str):
        self.log_directory = log_directory
        self.log_patterns = LOG_PATTERNS
        self.max_days_old = MAX_DAYS_OLD
        self.max_files_to_show = MAX_FILES_TO_SHOW
        
        # File tracking
        self.last_file_sizes: Dict[str, int] = {}
        self.last_file_hashes: Dict[str, str] = {}
        self.monitored_files: Set[str] = set()
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.stop_monitoring = False
        
        # Callbacks
        self.file_change_callback: Optional[Callable] = None
        self.bounty_detected_callback: Optional[Callable] = None
        self.concord_detected_callback: Optional[Callable] = None
        
    def set_callbacks(self, 
                     file_change: Optional[Callable] = None,
                     bounty_detected: Optional[Callable] = None,
                     concord_detected: Optional[Callable] = None):
        """Set callback functions for various events"""
        self.file_change_callback = file_change
        self.bounty_detected_callback = bounty_detected
        self.concord_detected_callback = concord_detected
    
    def get_recent_log_files(self) -> List[str]:
        """Get list of recent log files"""
        all_files = []
        
        for pattern in self.log_patterns:
            pattern_path = os.path.join(self.log_directory, pattern)
            files = glob.glob(pattern_path)
            all_files.extend(files)
        
        # Filter by recency and sort by modification time
        recent_files = [
            f for f in all_files 
            if is_recent_file(f, self.max_days_old)
        ]
        
        # Sort by modification time (newest first)
        recent_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Limit number of files
        return recent_files[:self.max_files_to_show]
    
    def scan_existing_bounties(self) -> List[Dict]:
        """Scan existing log files for bounty entries"""
        bounty_entries = []
        recent_files = self.get_recent_log_files()
        
        for file_path in recent_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Check for bounty
                        isk_amount = extract_bounty(line)
                        if isk_amount:
                            timestamp = extract_timestamp(line) or datetime.now()
                            bounty_entries.append({
                                'timestamp': timestamp,
                                'isk_amount': isk_amount,
                                'source_file': os.path.basename(file_path),
                                'line_number': line_num
                            })
                        
                        # Check for CONCORD messages
                        if detect_concord_message(line):
                            if self.concord_detected_callback:
                                self.concord_detected_callback(line, file_path)
                
                # Update file tracking
                self._update_file_tracking(file_path)
                
            except Exception as e:
                print(f"Error scanning file {file_path}: {e}")
        
        return bounty_entries
    
    def start_monitoring(self):
        """Start file monitoring"""
        if self.monitoring_active:
            print("⚠️ Monitoring already active")
            return
        
        self.monitoring_active = True
        self.stop_monitoring = False
        
        # Start monitoring in separate thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        print(f"📁 Started monitoring log directory: {self.log_directory}")
    
    def stop_monitoring(self):
        """Stop file monitoring"""
        self.monitoring_active = False
        self.stop_monitoring = True
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1.0)
        
        print("📁 Stopped monitoring log directory")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active and not self.stop_monitoring:
            try:
                self._check_for_changes()
                time.sleep(MONITORING_INTERVAL)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(MONITORING_INTERVAL)
    
    def _check_for_changes(self):
        """Check for changes in monitored files"""
        recent_files = self.get_recent_log_files()
        
        for file_path in recent_files:
            if self._has_file_changed(file_path):
                self._handle_file_change(file_path)
    
    def _has_file_changed(self, file_path: str) -> bool:
        """Check if a file has changed since last check"""
        try:
            current_size = os.path.getsize(file_path)
            current_hash = calculate_file_hash(file_path)
            
            # Check if file is new or has changed
            if file_path not in self.last_file_sizes:
                return True
            
            if (current_size != self.last_file_sizes[file_path] or 
                current_hash != self.last_file_hashes[file_path]):
                return True
            
            return False
            
        except (OSError, IOError):
            return False
    
    def _handle_file_change(self, file_path: str):
        """Handle a detected file change"""
        try:
            # Read new content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Check for new bounty entries
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Check for bounty
                isk_amount = extract_bounty(line)
                if isk_amount and self.bounty_detected_callback:
                    timestamp = extract_timestamp(line) or datetime.now()
                    self.bounty_detected_callback(timestamp, isk_amount, os.path.basename(file_path))
                
                # Check for CONCORD messages
                if detect_concord_message(line) and self.concord_detected_callback:
                    self.concord_detected_callback(line, file_path)
            
            # Update file tracking
            self._update_file_tracking(file_path)
            
            # Notify about file change
            if self.file_change_callback:
                self.file_change_callback(file_path)
                
        except Exception as e:
            print(f"Error handling file change in {file_path}: {e}")
    
    def _update_file_tracking(self, file_path: str):
        """Update file tracking information"""
        try:
            self.last_file_sizes[file_path] = os.path.getsize(file_path)
            self.last_file_hashes[file_path] = calculate_file_hash(file_path) or ""
            self.monitored_files.add(file_path)
        except (OSError, IOError) as e:
            print(f"Error updating file tracking for {file_path}: {e}")
    
    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status"""
        return {
            'monitoring_active': self.monitoring_active,
            'log_directory': self.log_directory,
            'monitored_files_count': len(self.monitored_files),
            'recent_files_count': len(self.get_recent_log_files())
        }
    
    def refresh_monitoring(self):
        """Refresh monitoring state and rescan files"""
        recent_files = self.get_recent_log_files()
        
        # Update tracking for all recent files
        for file_path in recent_files:
            self._update_file_tracking(file_path)
        
        print(f"📁 Refreshed monitoring: {len(recent_files)} recent files")
