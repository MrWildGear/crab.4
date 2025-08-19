"""
File monitoring system for CRAB Tracker.

This module handles monitoring of EVE Online log files for changes,
including file size, modification time, and content hash detection.
"""

import os
import hashlib
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from ..utils.eve_paths import find_eve_log_directory, is_eve_log_file


class FileChangeEvent:
    """Represents a file change event."""
    
    def __init__(self, file_path: str, event_type: str, timestamp: datetime):
        self.file_path = file_path
        self.event_type = event_type  # 'modified', 'created', 'deleted'
        self.timestamp = timestamp
    
    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.event_type}: {os.path.basename(self.file_path)}"


class FileMonitor:
    """Monitors EVE Online log files for changes."""
    
    def __init__(self, log_directory: Optional[str] = None):
        """
        Initialize the file monitor.
        
        Args:
            log_directory (str, optional): Directory to monitor
        """
        self.log_directory = log_directory or find_eve_log_directory()
        self.monitoring = False
        self.monitor_thread = None
        self.stop_monitoring_flag = False
        
        # File tracking
        self.file_states: Dict[str, Dict[str, Any]] = {}
        self.change_callbacks: List[Callable[[FileChangeEvent], None]] = []
        
        # Monitoring settings
        self.check_interval = 1.0  # seconds
        self.max_days_old = 1
        self.max_files_to_show = 10
        
        # Log file patterns
        self.log_patterns = ["*.log", "*.txt", "*.xml"]
    
    def start_monitoring(self):
        """Start monitoring log files for changes."""
        if self.monitoring:
            return
        
        if not self.log_directory or not os.path.exists(self.log_directory):
            raise ValueError(f"Invalid log directory: {self.log_directory}")
        
        self.monitoring = True
        self.stop_monitoring_flag = False
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print(f"Started monitoring: {self.log_directory}")
    
    def stop_monitoring(self):
        """Stop monitoring log files."""
        if not self.monitoring:
            return
        
        self.monitoring = False
        self.stop_monitoring_flag = True
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        
        print("Stopped monitoring log files")
    
    def add_change_callback(self, callback: Callable[[FileChangeEvent], None]):
        """
        Add a callback function to be called when files change.
        
        Args:
            callback: Function to call with FileChangeEvent parameter
        """
        self.change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[FileChangeEvent], None]):
        """
        Remove a change callback function.
        
        Args:
            callback: Function to remove
        """
        if callback in self.change_callback:
            self.change_callback.remove(callback)
    
    def get_recent_files(self) -> List[str]:
        """
        Get list of recent log files based on current settings.
        
        Returns:
            List of file paths for recent log files
        """
        if not self.log_directory or not os.path.exists(self.log_directory):
            return []
        
        files = []
        cutoff_time = datetime.now() - timedelta(days=self.max_days_old)
        
        try:
            for file in os.listdir(self.log_directory):
                file_path = os.path.join(self.log_directory, file)
                
                # Check if it's a log file
                if not any(file.endswith(pattern[1:]) for pattern in self.log_patterns):
                    continue
                
                # Check if it's recent enough
                if os.path.isfile(file_path):
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if mtime >= cutoff_time:
                        files.append((file_path, mtime))
            
            # Sort by modification time (newest first) and limit
            files.sort(key=lambda x: x[1], reverse=True)
            files = files[:self.max_files_to_show]
            
            return [file_path for file_path, _ in files]
            
        except Exception as e:
            print(f"Error getting recent files: {e}")
            return []
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring and not self.stop_monitoring_flag:
            try:
                self._check_for_changes()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def _check_for_changes(self):
        """Check for file changes and notify callbacks."""
        current_files = self.get_recent_files()
        
        # Check for new files
        for file_path in current_files:
            if file_path not in self.file_states:
                self._handle_file_created(file_path)
                continue
            
            # Check for modifications
            current_state = self._get_file_state(file_path)
            previous_state = self.file_states[file_path]
            
            if (current_state['size'] != previous_state['size'] or
                current_state['mtime'] != previous_state['mtime'] or
                current_state['hash'] != previous_state['hash']):
                self._handle_file_modified(file_path, previous_state, current_state)
        
        # Check for deleted files
        deleted_files = []
        for file_path in list(self.file_states.keys()):
            if file_path not in current_files:
                deleted_files.append(file_path)
        
        for file_path in deleted_files:
            self._handle_file_deleted(file_path)
    
    def _handle_file_created(self, file_path: str):
        """Handle a newly created file."""
        current_state = self._get_file_state(file_path)
        self.file_states[file_path] = current_state
        
        event = FileChangeEvent(file_path, 'created', datetime.now())
        self._notify_callbacks(event)
    
    def _handle_file_modified(self, file_path: str, previous_state: Dict, current_state: Dict):
        """Handle a modified file."""
        self.file_states[file_path] = current_state
        
        event = FileChangeEvent(file_path, 'modified', datetime.now())
        self._notify_callbacks(event)
    
    def _handle_file_deleted(self, file_path: str):
        """Handle a deleted file."""
        del self.file_states[file_path]
        
        event = FileChangeEvent(file_path, 'deleted', datetime.now())
        self._notify_callbacks(event)
    
    def _get_file_state(self, file_path: str) -> Dict[str, Any]:
        """
        Get the current state of a file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            Dict containing file state information
        """
        try:
            stat = os.stat(file_path)
            file_hash = self._calculate_file_hash(file_path)
            
            return {
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'hash': file_hash,
                'last_check': time.time()
            }
        except Exception as e:
            print(f"Error getting file state for {file_path}: {e}")
            return {
                'size': 0,
                'mtime': 0,
                'hash': '',
                'last_check': time.time()
            }
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            MD5 hash string
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def _notify_callbacks(self, event: FileChangeEvent):
        """Notify all registered callbacks of a file change event."""
        for callback in self.change_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in change callback: {e}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """
        Get the current monitoring status.
        
        Returns:
            Dict containing monitoring status information
        """
        return {
            'monitoring': self.monitoring,
            'log_directory': self.log_directory,
            'check_interval': self.check_interval,
            'max_days_old': self.max_days_old,
            'max_files_to_show': self.max_files_to_show,
            'files_being_monitored': len(self.file_states),
            'recent_files': self.get_recent_files()
        }
    
    def set_monitoring_settings(self, max_days_old: int = None, max_files_to_show: int = None):
        """
        Update monitoring settings.
        
        Args:
            max_days_old (int, optional): Maximum age of files to monitor
            max_files_to_show (int, optional): Maximum number of files to monitor
        """
        if max_days_old is not None:
            self.max_days_old = max(max_days_old, 1)
        
        if max_files_to_show is not None:
            self.max_files_to_show = max(max_files_to_show, 1)
    
    def refresh_file_states(self):
        """Refresh the state of all monitored files."""
        current_files = self.get_recent_files()
        
        # Update states for current files
        for file_path in current_files:
            if file_path in self.file_states:
                self.file_states[file_path] = self._get_file_state(file_path)
            else:
                self.file_states[file_path] = self._get_file_state(file_path)
        
        # Remove deleted files
        deleted_files = [path for path in self.file_states.keys() if path not in current_files]
        for file_path in deleted_files:
            del self.file_states[file_path]
