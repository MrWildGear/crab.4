"""
Refactored EVE Log Reader - Main Application
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime

from config import WINDOW_TITLE, WINDOW_SIZE
from ui_theme import UITheme
from bounty_tracker import BountyTracker, CRABBountyTracker
from concord_tracker import CONCORDTracker
from log_monitor import LogMonitor
from utils import find_eve_log_directory

class EVELogReader:
    """Main application class for EVE Log Reader"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        
        # Initialize components
        self._init_components()
        self._setup_ui()
        self._setup_callbacks()
        self._start_initial_scan()
    
    def _init_components(self):
        """Initialize all component classes"""
        # Find EVE log directory
        self.eve_log_dir = find_eve_log_directory()
        
        # Initialize trackers
        self.bounty_tracker = BountyTracker()
        self.crab_tracker = CRABBountyTracker()
        self.concord_tracker = CONCORDTracker()
        
        # Initialize log monitor
        self.log_monitor = LogMonitor(self.eve_log_dir)
        
        # UI state variables
        self.dir_var = tk.StringVar(value=self.eve_log_dir)
        self.high_freq_var = tk.BooleanVar(value=True)
        self.max_days_var = tk.IntVar(value=1)
        self.max_files_var = tk.IntVar(value=10)
        
        # Status variables
        self.status_var = tk.StringVar(value="Ready")
        self.bounty_total_var = tk.StringVar(value="Total ISK: 0 ISK")
        self.bounty_count_var = tk.StringVar(value="Bounties: 0")
        self.concord_status_var = tk.StringVar(value="Inactive")
        self.crab_session_var = tk.StringVar(value="CRAB Session: Inactive")
        self.crab_bounty_total_var = tk.StringVar(value="CRAB Total ISK: 0 ISK")
        self.crab_bounty_count_var = tk.StringVar(value="CRAB Bounties: 0")
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Apply dark theme
        UITheme.apply_dark_theme(self.root)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Create UI sections
        self._create_directory_section(main_frame)
        self._create_filter_section(main_frame)
        self._create_control_section(main_frame)
        self._create_display_section(main_frame)
        self._create_status_section(main_frame)
    
    def _create_directory_section(self, parent):
        """Create directory selection section"""
        ttk.Label(parent, text="Log Directory:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        dir_frame = ttk.Frame(parent)
        dir_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        dir_entry = UITheme.create_dark_entry(dir_frame, textvariable=self.dir_var, width=70)
        dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = UITheme.create_dark_button(dir_frame, text="Browse", command=self._browse_directory)
        browse_btn.grid(row=0, column=1)
        
        refresh_btn = UITheme.create_dark_button(dir_frame, text="Refresh Recent", command=self._refresh_recent_logs)
        refresh_btn.grid(row=0, column=2, padx=(5, 0))
    
    def _create_filter_section(self, parent):
        """Create filtering controls section"""
        filter_frame = ttk.LabelFrame(parent, text="Recent Log Filtering", padding="5")
        filter_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Days filter
        ttk.Label(filter_frame, text="Max Days Old:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        days_spinbox = ttk.Spinbox(filter_frame, from_=1, to=30, textvariable=self.max_days_var, width=10)
        days_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Files filter
        ttk.Label(filter_frame, text="Max Files:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        files_spinbox = ttk.Spinbox(filter_frame, from_=5, to=50, textvariable=self.max_files_var, width=10)
        files_spinbox.grid(row=0, column=3, sticky=tk.W)
        
        # Apply button
        apply_btn = UITheme.create_dark_button(filter_frame, text="Apply Filters", command=self._apply_filters)
        apply_btn.grid(row=0, column=4, padx=(20, 0))
    
    def _create_control_section(self, parent):
        """Create control buttons section"""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="5")
        control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Monitoring controls
        self.high_freq_check = ttk.Checkbutton(
            control_frame, 
            text="High Frequency Monitoring", 
            variable=self.high_freq_var,
            command=self._toggle_high_frequency
        )
        self.high_freq_check.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        # Bounty controls
        bounty_frame = ttk.Frame(control_frame)
        bounty_frame.grid(row=0, column=1, padx=(0, 20))
        
        UITheme.create_dark_button(bounty_frame, text="Show Bounties", command=self._show_bounty_details).grid(row=0, column=0, padx=(0, 5))
        UITheme.create_dark_button(bounty_frame, text="Export Bounties", command=self._export_bounties).grid(row=0, column=1, padx=(0, 5))
        UITheme.create_dark_button(bounty_frame, text="Reset Bounties", command=self._reset_bounty_tracking).grid(row=0, column=2)
        
        # CRAB controls
        crab_frame = ttk.Frame(control_frame)
        crab_frame.grid(row=0, column=2, padx=(0, 20))
        
        UITheme.create_dark_button(crab_frame, text="Show CRAB", command=self._show_crab_bounty_details).grid(row=0, column=0, padx=(0, 5))
        UITheme.create_dark_button(crab_frame, text="Reset CRAB", command=self._reset_crab_bounty_tracking).grid(row=0, column=1)
        
        # Test controls
        test_frame = ttk.Frame(control_frame)
        test_frame.grid(row=0, column=3)
        
        UITheme.create_dark_button(test_frame, text="Test CONCORD", command=self._test_concord_link_start).grid(row=0, column=0, padx=(0, 5))
        UITheme.create_dark_button(test_frame, text="Test CRAB", command=self._add_test_crab_bounty).grid(row=0, column=1)
    
    def _create_display_section(self, parent):
        """Create main display section"""
        display_frame = ttk.LabelFrame(parent, text="Log Display", padding="5")
        display_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(display_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = UITheme.create_dark_text(text_frame, height=20, width=100)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
    
    def _create_status_section(self, parent):
        """Create status display section"""
        status_frame = ttk.LabelFrame(parent, text="Status", padding="5")
        status_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status row 1
        status_row1 = ttk.Frame(status_frame)
        status_row1.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(status_row1, textvariable=self.status_var).grid(row=0, column=0, padx=(0, 20))
        ttk.Label(status_row1, textvariable=self.concord_status_var).grid(row=0, column=1, padx=(0, 20))
        ttk.Label(status_row1, textvariable=self.crab_session_var).grid(row=0, column=2)
        
        # Status row 2
        status_row2 = ttk.Frame(status_frame)
        status_row2.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(status_row2, textvariable=self.bounty_total_var).grid(row=0, column=0, padx=(0, 20))
        ttk.Label(status_row2, textvariable=self.bounty_count_var).grid(row=0, column=1, padx=(0, 20))
        ttk.Label(status_row2, textvariable=self.crab_bounty_total_var).grid(row=0, column=2, padx=(0, 20))
        ttk.Label(status_row2, textvariable=self.crab_bounty_count_var).grid(row=0, column=3)
    
    def _setup_callbacks(self):
        """Setup callback functions between components"""
        # Set callbacks for log monitor
        self.log_monitor.set_callbacks(
            file_change=self._on_file_change,
            bounty_detected=self._on_bounty_detected,
            concord_detected=self._on_concord_detected
        )
        
        # Set callbacks for CONCORD tracker
        self.concord_tracker.set_status_callback(self._on_concord_status_update)
        self.concord_tracker.set_countdown_callback(self._on_concord_countdown_update)
    
    def _start_initial_scan(self):
        """Start initial log scan and monitoring"""
        # Start bounty tracking
        self.bounty_tracker.start_session()
        
        # Scan existing bounties
        existing_bounties = self.log_monitor.scan_existing_bounties()
        for bounty in existing_bounties:
            self.bounty_tracker.add_bounty(
                bounty['timestamp'],
                bounty['isk_amount'],
                bounty['source_file']
            )
        
        # Update displays
        self._update_bounty_display()
        
        # Start monitoring if enabled
        if self.high_freq_var.get():
            self._start_monitoring()
    
    def _browse_directory(self):
        """Browse for log directory"""
        directory = filedialog.askdirectory(initialdir=self.eve_log_dir)
        if directory:
            self.eve_log_dir = directory
            self.dir_var.set(directory)
            self.log_monitor.log_directory = directory
            self._refresh_recent_logs()
    
    def _apply_filters(self):
        """Apply filtering settings"""
        self.log_monitor.max_days_old = self.max_days_var.get()
        self.log_monitor.max_files_to_show = self.max_files_var.get()
        self._refresh_recent_logs()
    
    def _refresh_recent_logs(self):
        """Refresh recent logs display"""
        try:
            recent_files = self.log_monitor.get_recent_log_files()
            
            # Clear display
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            
            # Show recent files info
            self.log_text.insert(tk.END, f"📁 Recent Log Files ({len(recent_files)} found):\n")
            self.log_text.insert(tk.END, "=" * 50 + "\n\n")
            
            for i, file_path in enumerate(recent_files, 1):
                filename = os.path.basename(file_path)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                file_size = os.path.getsize(file_path)
                
                self.log_text.insert(tk.END, f"{i}. {filename}\n")
                self.log_text.insert(tk.END, f"   Modified: {mod_time}\n")
                self.log_text.insert(tk.END, f"   Size: {file_size:,} bytes\n\n")
            
            # Make text read-only
            self.log_text.config(state=tk.DISABLED)
            
            # Update status
            self.status_var.set(f"Found {len(recent_files)} recent log files")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing logs: {str(e)}")
    
    def _toggle_high_frequency(self):
        """Toggle high frequency monitoring"""
        if self.high_freq_var.get():
            self._start_monitoring()
        else:
            self._stop_monitoring()
    
    def _start_monitoring(self):
        """Start log monitoring"""
        self.log_monitor.start_monitoring()
        self.status_var.set("Monitoring active")
    
    def _stop_monitoring(self):
        """Stop log monitoring"""
        self.log_monitor.stop_monitoring()
        self.status_var.set("Monitoring stopped")
    
    def _on_file_change(self, file_path):
        """Handle file change events"""
        self.status_var.set(f"File changed: {os.path.basename(file_path)}")
    
    def _on_bounty_detected(self, timestamp, isk_amount, source_file):
        """Handle detected bounty events"""
        self.bounty_tracker.add_bounty(timestamp, isk_amount, source_file)
        self._update_bounty_display()
    
    def _on_concord_detected(self, line, file_path):
        """Handle detected CONCORD messages"""
        # This would need more sophisticated parsing to determine specific CONCORD events
        print(f"CONCORD message detected: {line}")
    
    def _on_concord_status_update(self, status):
        """Handle CONCORD status updates"""
        self.concord_status_var.set(f"CONCORD: {status}")
        self._update_crab_session_status()
    
    def _on_concord_countdown_update(self, text, color):
        """Handle CONCORD countdown updates"""
        # Update countdown display if needed
        pass
    
    def _update_bounty_display(self):
        """Update bounty display labels"""
        stats = self.bounty_tracker.get_statistics()
        self.bounty_total_var.set(f"Total ISK: {stats['total_isk']:,} ISK")
        self.bounty_count_var.set(f"Bounties: {stats['total_bounties']}")
    
    def _update_crab_session_status(self):
        """Update CRAB session status based on CONCORD status"""
        concord_status = self.concord_tracker.get_status()
        
        if concord_status['is_active']:
            if not concord_status['link_completed']:
                self.crab_session_var.set("CRAB Session: Linking")
            else:
                self.crab_session_var.set("CRAB Session: Active")
        else:
            self.crab_session_var.set("CRAB Session: Inactive")
    
    def _show_bounty_details(self):
        """Show detailed bounty information"""
        stats = self.bounty_tracker.get_statistics()
        
        details_window = tk.Toplevel(self.root)
        details_window.title("Bounty Details")
        details_window.geometry("600x400")
        
        text_widget = UITheme.create_dark_text(details_window)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, "💰 Bounty Details\n")
        text_widget.insert(tk.END, "=" * 30 + "\n\n")
        text_widget.insert(tk.END, f"Session Start: {stats['session_duration']}\n")
        text_widget.insert(tk.END, f"Total Bounties: {stats['total_bounties']}\n")
        text_widget.insert(tk.END, f"Total ISK: {stats['total_isk']:,} ISK\n")
        text_widget.insert(tk.END, f"Average Bounty: {stats['average_bounty']:,.0f} ISK\n")
        text_widget.insert(tk.END, f"Largest Bounty: {stats['largest_bounty']:,} ISK\n")
        text_widget.insert(tk.END, f"Smallest Bounty: {stats['smallest_bounty']:,} ISK\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def _export_bounties(self):
        """Export bounty data"""
        filename = self.bounty_tracker.export_bounties()
        if filename:
            messagebox.showinfo("Export Complete", f"Bounty data exported to {filename}")
    
    def _reset_bounty_tracking(self):
        """Reset bounty tracking"""
        self.bounty_tracker.reset_tracking()
        self._update_bounty_display()
        messagebox.showinfo("Reset Complete", "Bounty tracking has been reset")
    
    def _show_crab_bounty_details(self):
        """Show CRAB bounty details"""
        stats = self.crab_tracker.get_crab_statistics()
        
        details_window = tk.Toplevel(self.root)
        details_window.title("CRAB Bounty Details")
        details_window.geometry("600x400")
        
        text_widget = UITheme.create_dark_text(details_window)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, "🦀 CRAB Bounty Details\n")
        text_widget.insert(tk.END, "=" * 30 + "\n\n")
        text_widget.insert(tk.END, f"CRAB Session Active: {stats['crab_session_active']}\n")
        text_widget.insert(tk.END, f"Total CRAB Bounties: {stats['total_bounties']}\n")
        text_widget.insert(tk.END, f"Total CRAB ISK: {stats['total_isk']:,} ISK\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def _reset_crab_bounty_tracking(self):
        """Reset CRAB bounty tracking"""
        self.crab_tracker.reset_tracking()
        messagebox.showinfo("Reset Complete", "CRAB bounty tracking has been reset")
    
    def _test_concord_link_start(self):
        """Test CONCORD link start"""
        self.concord_tracker.start_link()
        self.concord_tracker.start_countdown(60)  # 1 minute test countdown
    
    def _add_test_crab_bounty(self):
        """Add test CRAB bounty"""
        if not self.crab_tracker.crab_session_active:
            messagebox.showwarning("CRAB Session Required", "CRAB session must be active to add bounties.")
            return
        
        self.crab_tracker.add_crab_bounty(datetime.now(), 50000, "TEST_CRAB_BOUNTY")
        print("🧪 Test CRAB bounty added: 50,000 ISK")

def main():
    """Main entry point"""
    root = tk.Tk()
    app = EVELogReader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
