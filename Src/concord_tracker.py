"""
CONCORD tracking system for EVE Log Reader
"""
import threading
import time
from datetime import datetime
from typing import Optional, Callable
from config import CONCORD_COUNTDOWN_COLOR

class CONCORDTracker:
    """Handles CONCORD Rogue Analysis Beacon tracking"""
    
    def __init__(self):
        self.link_start: Optional[datetime] = None
        self.link_completed: bool = False
        self.countdown_active: bool = False
        self.countdown_thread: Optional[threading.Thread] = None
        self.stop_countdown: bool = False
        self.countdown_color: str = CONCORD_COUNTDOWN_COLOR
        self.countdown_seconds: int = 0
        
        # Status callbacks
        self.status_update_callback: Optional[Callable] = None
        self.countdown_update_callback: Optional[Callable] = None
        
    def set_status_callback(self, callback: Callable):
        """Set callback for status updates"""
        self.status_update_callback = callback
    
    def set_countdown_callback(self, callback: Callable):
        """Set callback for countdown updates"""
        self.countdown_update_callback = callback
    
    def start_link(self):
        """Start a CONCORD link process"""
        self.link_start = datetime.now()
        self.link_completed = False
        self.countdown_active = False
        self.stop_countdown = False
        print(f"🔗 CONCORD link started at {self.link_start}")
        
        if self.status_update_callback:
            self.status_update_callback("Linking...")
    
    def complete_link(self):
        """Mark CONCORD link as completed"""
        self.link_completed = True
        self.countdown_active = False
        self.stop_countdown = True
        print(f"✅ CONCORD link completed at {datetime.now()}")
        
        if self.status_update_callback:
            self.status_update_callback("Completed")
    
    def fail_link(self):
        """Mark CONCORD link as failed"""
        self.link_completed = True
        self.countdown_active = False
        self.stop_countdown = True
        print(f"❌ CONCORD link failed at {datetime.now()}")
        
        if self.status_update_callback:
            self.status_update_callback("Failed")
    
    def start_countdown(self, seconds: int = 300):
        """Start countdown timer (default 5 minutes)"""
        if self.countdown_active:
            print("⚠️ Countdown already active")
            return
        
        self.countdown_seconds = seconds
        self.countdown_active = True
        self.stop_countdown = False
        
        # Start countdown in separate thread
        self.countdown_thread = threading.Thread(target=self._countdown_loop, daemon=True)
        self.countdown_thread.start()
        
        print(f"⏰ CONCORD countdown started: {seconds} seconds")
    
    def _countdown_loop(self):
        """Internal countdown loop"""
        while self.countdown_seconds > 0 and not self.stop_countdown:
            if self.countdown_update_callback:
                self.countdown_update_callback(self.countdown_seconds, self.countdown_color)
            
            time.sleep(1)
            self.countdown_seconds -= 1
        
        if not self.stop_countdown:
            self._countdown_expired()
    
    def _countdown_expired(self):
        """Handle countdown expiration"""
        self.countdown_active = False
        print("⏰ CONCORD countdown expired")
        
        if self.countdown_update_callback:
            self.countdown_update_callback("EXPIRED", "#ff4444")  # Red for expired
    
    def stop_countdown_timer(self):
        """Stop the countdown timer"""
        self.stop_countdown = True
        self.countdown_active = False
        print("⏰ CONCORD countdown stopped")
    
    def reset_tracking(self):
        """Reset all CONCORD tracking data"""
        self.link_start = None
        self.link_completed = False
        self.countdown_active = False
        self.stop_countdown = True
        self.countdown_seconds = 0
        
        if self.status_update_callback:
            self.status_update_callback("Inactive")
        
        print("🔗 CONCORD tracking reset")
    
    def get_status(self) -> dict:
        """Get current CONCORD status"""
        return {
            'link_start': self.link_start,
            'link_completed': self.link_completed,
            'countdown_active': self.countdown_active,
            'countdown_seconds': self.countdown_seconds,
            'is_active': self.link_start is not None and not self.link_completed
        }
    
    def is_linking(self) -> bool:
        """Check if currently linking"""
        return self.link_start is not None and not self.link_completed
    
    def is_completed(self) -> bool:
        """Check if link is completed"""
        return self.link_completed
    
    def get_session_duration(self) -> Optional[float]:
        """Get current session duration in seconds"""
        if self.link_start:
            return (datetime.now() - self.link_start).total_seconds()
        return None
