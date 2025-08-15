import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time
import glob
import hashlib

class EVELogReader:
    def __init__(self, root):
        self.root = root
        self.root.title("EVE Online Log Reader - Recent Logs Monitor")
        self.root.geometry("1400x900")
        
        # EVE Online log directory (default location)
        self.eve_log_dir = self.find_eve_log_directory()
        
        # Log file patterns
        self.log_patterns = [
            "*.log",
            "*.txt",
            "*.xml"
        ]
        
        # Store all log entries from recent files only
        self.all_log_entries = []
        self.last_file_sizes = {}
        self.last_file_hashes = {}  # Store content hashes for change detection
        
        # Bounty tracking system
        self.bounty_entries = []  # Store bounty entries with timestamps
        self.total_bounty_isk = 0  # Total ISK earned from bounties
        self.bounty_session_start = None  # When bounty tracking started
        
        # CONCORD Rogue Analysis Beacon tracking system
        self.concord_link_start = None  # When the link process started
        self.concord_link_completed = False  # Whether the link process completed
        self.concord_countdown_active = False  # Whether countdown is active
        self.concord_countdown_thread = None  # Thread for countdown timer
        self.stop_concord_countdown = False  # Flag to stop countdown
        self.concord_countdown_color = "#ffff00"  # Default yellow color for countdown
        
        # Settings for recent file filtering
        self.max_days_old = 1  # Only show logs from last 24 hours by default
        self.max_files_to_show = 10  # Maximum number of recent files to display
        
        self.setup_ui()
        self.load_log_files()
        
        # Start bounty tracking
        self.bounty_session_start = datetime.now()
        
        # Start monitoring automatically since it's enabled by default
        if self.high_freq_var.get():
            self.start_monitoring_only()
    
    def apply_dark_theme(self):
        """Apply dark mode styling to the application"""
        # Configure dark theme colors
        dark_bg = "#2b2b2b"      # Dark gray background
        darker_bg = "#1e1e1e"    # Even darker for frames
        text_color = "#ffffff"    # White text
        accent_color = "#4a9eff"  # Blue accent for highlights
        border_color = "#404040"  # Dark border
        
        # Configure root window
        self.root.configure(bg=dark_bg)
        
        # Configure ttk styles
        style = ttk.Style()
        
        # Configure main frame style
        style.configure("TFrame", background=dark_bg)
        
        # Configure label styles
        style.configure("TLabel", 
                       background=dark_bg, 
                       foreground=text_color,
                       font=("Segoe UI", 9))
        
        # Configure button styles
        style.configure("TButton", 
                       background=darker_bg, 
                       foreground=text_color,
                       borderwidth=1,
                       focuscolor=accent_color)
        
        # Configure entry styles
        style.configure("TEntry", 
                       fieldbackground=darker_bg, 
                       foreground=text_color,
                       borderwidth=1,
                       insertcolor=text_color)
        
        # Configure spinbox styles
        style.configure("TSpinbox", 
                       fieldbackground=darker_bg, 
                       foreground=text_color,
                       borderwidth=1,
                       insertcolor=text_color)
        
        # Configure checkbox styles
        style.configure("TCheckbutton", 
                       background=dark_bg, 
                       foreground=text_color)
        
        # Configure label frame styles
        style.configure("TLabelframe", 
                       background=dark_bg, 
                       bordercolor=border_color)
        style.configure("TLabelframe.Label", 
                       background=dark_bg, 
                       foreground=text_color)
        
        # Configure scrollbar styles
        style.configure("Vertical.TScrollbar", 
                       background=darker_bg, 
                       troughcolor=dark_bg,
                       bordercolor=border_color,
                       arrowcolor=text_color)
    
    def find_eve_log_directory(self):
        """Find the EVE Online log directory"""
        # Common EVE Online log locations - Gamelogs is the standard folder
        possible_paths = [
            os.path.expanduser("~/Documents/EVE/logs/Gamelogs"),  # Primary location
            os.path.expanduser("~/Documents/EVE/logs"),  # Fallback to logs folder
            os.path.expanduser("~/AppData/Local/CCP/EVE/logs/Gamelogs"),
            os.path.expanduser("~/AppData/Local/CCP/EVE/logs"),
            "C:/Users/Public/Documents/EVE/logs/Gamelogs",
            "C:/Users/Public/Documents/EVE/logs",
            "C:/Program Files/CCP/EVE/logs/Gamelogs",
            "C:/Program Files/CCP/EVE/logs"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # If not found, return user's Documents folder
        return os.path.expanduser("~/Documents")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Apply dark mode styling
        self.apply_dark_theme()
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Log directory selection
        ttk.Label(main_frame, text="Log Directory:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.dir_var = tk.StringVar(value=self.eve_log_dir)
        dir_entry = tk.Entry(dir_frame, textvariable=self.dir_var, width=70,
                            bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                            insertbackground="#ffffff",   # White cursor
                            selectbackground="#4a9eff",  # Blue selection
                            selectforeground="#ffffff",  # White text when selected
                            relief="sunken", borderwidth=1,
                            font=("Segoe UI", 9))
        dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = tk.Button(dir_frame, text="Browse", command=self.browse_directory,
                              bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                              activebackground="#404040",   # Darker when clicked
                              activeforeground="#ffffff",  # White text when clicked
                              relief="raised", borderwidth=1,
                              font=("Segoe UI", 9))
        browse_btn.grid(row=0, column=1)
        
        refresh_btn = tk.Button(dir_frame, text="Refresh Recent", command=self.refresh_recent_logs,
                               bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                               activebackground="#404040",   # Darker when clicked
                               activeforeground="#ffffff",  # White text when clicked
                               relief="raised", borderwidth=1,
                               font=("Segoe UI", 9))
        refresh_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Filtering controls
        filter_frame = ttk.LabelFrame(main_frame, text="Recent Log Filtering", padding="5")
        filter_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Days old filter
        ttk.Label(filter_frame, text="Max days old:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.days_var = tk.StringVar(value=str(self.max_days_old))
        days_spin = tk.Spinbox(filter_frame, from_=1, to=30, width=5, textvariable=self.days_var,
                               bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                               insertbackground="#ffffff",   # White cursor
                               selectbackground="#4a9eff",  # Blue selection
                               selectforeground="#ffffff",  # White text when selected
                               relief="sunken", borderwidth=1,
                               font=("Segoe UI", 9))
        days_spin.grid(row=0, column=1, padx=(0, 20))
        
        # Max files filter
        ttk.Label(filter_frame, text="Max files to show:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.files_var = tk.StringVar(value=str(self.max_files_to_show))
        files_spin = tk.Spinbox(filter_frame, from_=5, to=50, width=5, textvariable=self.files_var,
                                bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                insertbackground="#ffffff",   # White cursor
                                selectbackground="#4a9eff",  # Blue selection
                                selectforeground="#ffffff",  # White text when selected
                                relief="sunken", borderwidth=1,
                                font=("Segoe UI", 9))
        files_spin.grid(row=0, column=3, padx=(0, 20))
        
        # Apply filters button
        apply_btn = tk.Button(filter_frame, text="Apply Filters", command=self.apply_filters,
                             bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                             activebackground="#404040",   # Darker when clicked
                             activeforeground="#ffffff",  # White text when clicked
                             relief="raised", borderwidth=1,
                             font=("Segoe UI", 9))
        apply_btn.grid(row=0, column=4)
        
        # File monitoring status
        ttk.Label(main_frame, text="Recent Logs (UTC Timestamp Based):").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        # Bounty tracking display
        bounty_frame = ttk.LabelFrame(main_frame, text="💰 Bounty Tracking", padding="5")
        bounty_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Bounty info labels
        self.bounty_total_var = tk.StringVar(value="Total ISK Earned: 0 ISK")
        bounty_total_label = ttk.Label(bounty_frame, textvariable=self.bounty_total_var, 
                                      font=("Segoe UI", 10, "bold"))
        bounty_total_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.bounty_count_var = tk.StringVar(value="Bounties: 0")
        bounty_count_label = ttk.Label(bounty_frame, textvariable=self.bounty_count_var)
        bounty_count_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        self.bounty_session_var = tk.StringVar(value="Session: Not started")
        bounty_session_label = ttk.Label(bounty_frame, textvariable=self.bounty_session_var)
        bounty_session_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
        
        # Bounty control buttons
        reset_bounty_btn = tk.Button(bounty_frame, text="Reset Bounty Tracking", command=self.reset_bounty_tracking,
                                    bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                    activebackground="#404040",   # Darker when clicked
                                    activeforeground="#ffffff",  # White text when clicked
                                    relief="raised", borderwidth=1,
                                    font=("Segoe UI", 9))
        reset_bounty_btn.grid(row=0, column=3, padx=(20, 0))
        
        show_bounties_btn = tk.Button(bounty_frame, text="Show Bounty Details", command=self.show_bounty_details,
                                     bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                     activebackground="#404040",   # Darker when clicked
                                     activeforeground="#ffffff",  # White text when clicked
                                     relief="raised", borderwidth=1,
                                     font=("Segoe UI", 9))
        show_bounties_btn.grid(row=0, column=4, padx=(20, 0))
        
        # CONCORD Rogue Analysis Beacon tracking display
        concord_frame = ttk.LabelFrame(main_frame, text="🔗 CONCORD Rogue Analysis Beacon", padding="5")
        concord_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # CONCORD status labels
        self.concord_status_var = tk.StringVar(value="Status: Inactive")
        concord_status_label = ttk.Label(concord_frame, textvariable=self.concord_status_var, 
                                        font=("Segoe UI", 10, "bold"))
        concord_status_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.concord_countdown_var = tk.StringVar(value="Countdown: --:--")
        self.concord_countdown_label = ttk.Label(concord_frame, textvariable=self.concord_countdown_var,
                                                font=("Consolas", 10, "bold"), foreground=self.concord_countdown_color)
        self.concord_countdown_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        self.concord_time_var = tk.StringVar(value="Link Time: Not started")
        concord_time_label = ttk.Label(concord_frame, textvariable=self.concord_time_var)
        concord_time_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
        
        # CONCORD control buttons
        reset_concord_btn = tk.Button(concord_frame, text="Reset CONCORD Tracking", command=self.reset_concord_tracking,
                                     bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                     activebackground="#404040",   # Darker when clicked
                                     activeforeground="#ffffff",  # White text when clicked
                                     relief="raised", borderwidth=1,
                                     font=("Segoe UI", 9))
        reset_concord_btn.grid(row=0, column=3, padx=(20, 0))
        
        # Test buttons for CONCORD messages
        test_link_start_btn = tk.Button(concord_frame, text="Test Link Start", command=self.test_concord_link_start,
                                       bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                       activebackground="#404040",   # Darker when clicked
                                       activeforeground="#ffffff",  # White text when clicked
                                       relief="raised", borderwidth=1,
                                       font=("Segoe UI", 9))
        test_link_start_btn.grid(row=0, column=4, padx=(20, 0))
        
        test_link_complete_btn = tk.Button(concord_frame, text="Test Link Complete", command=self.test_concord_link_complete,
                                           bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                           activebackground="#404040",   # Darker when clicked
                                           activeforeground="#ffffff",  # White text when clicked
                                           relief="raised", borderwidth=1,
                                           font=("Segoe UI", 9))
        test_link_complete_btn.grid(row=0, column=5, padx=(20, 0))
        
        # End CONCORD process button
        end_concord_btn = tk.Button(concord_frame, text="End Process", command=self.end_concord_process,
                                    bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                    activebackground="#404040",   # Darker when clicked
                                    activeforeground="#ffffff",  # White text when clicked
                                    relief="raised", borderwidth=1,
                                    font=("Segoe UI", 9))
        end_concord_btn.grid(row=0, column=6, padx=(20, 0))
        
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Create text widget with scrollbar for combined logs
        self.text_widget = tk.Text(status_frame, wrap=tk.WORD, height=25,
                                  bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                  insertbackground="#ffffff",   # White cursor
                                  selectbackground="#4a9eff",  # Blue selection
                                  selectforeground="#ffffff",  # White text when selected
                                  font=("Consolas", 9))        # Monospace font for logs
        scrollbar = tk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.text_widget.yview,
                                bg="#1e1e1e", troughcolor="#2b2b2b",  # Dark scrollbar
                                activebackground="#404040",            # Darker when active
                                relief="flat", borderwidth=0)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Monitoring recent log files only")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Apply dark styling to status bar
        style = ttk.Style()
        style.configure("Status.TLabel", 
                       background="#1e1e1e", 
                       foreground="#ffffff",
                       relief="sunken",
                       borderwidth=1,
                       bordercolor="#404040")
        status_bar.configure(style="Status.TLabel")
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=8, column=0, columnspan=2, pady=(10, 0))
        
        # High-frequency monitoring checkbox
        self.high_freq_var = tk.BooleanVar(value=True)
        high_freq_cb = ttk.Checkbutton(control_frame, text="High-frequency monitoring (1s)", 
                                      variable=self.high_freq_var, command=self.toggle_high_frequency)
        high_freq_cb.grid(row=0, column=0, padx=(0, 20))
        
        # Aggressive change detection checkbox
        self.aggressive_detection_var = tk.BooleanVar(value=True)
        aggressive_cb = ttk.Checkbutton(control_frame, text="Content hash detection", 
                                       variable=self.aggressive_detection_var)
        aggressive_cb.grid(row=0, column=1, padx=(0, 20))
        
        # Manual refresh button
        manual_refresh_btn = tk.Button(control_frame, text="Manual Refresh", command=self.manual_refresh,
                                      bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                      activebackground="#404040",   # Darker when clicked
                                      activeforeground="#ffffff",  # White text when clicked
                                      relief="raised", borderwidth=1,
                                      font=("Segoe UI", 9))
        manual_refresh_btn.grid(row=0, column=2, padx=(0, 20))
        
        # Clear button
        clear_btn = tk.Button(control_frame, text="Clear Display", command=self.clear_display,
                             bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                             activebackground="#404040",   # Darker when clicked
                             activeforeground="#ffffff",  # White text when clicked
                             relief="raised", borderwidth=1,
                             font=("Segoe UI", 9))
        clear_btn.grid(row=0, column=3, padx=(0, 20))
        
        # Export button
        export_btn = tk.Button(control_frame, text="Export Recent Logs", command=self.export_logs,
                              bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                              activebackground="#404040",   # Darker when clicked
                              activeforeground="#ffffff",  # White text when clicked
                              relief="raised", borderwidth=1,
                              font=("Segoe UI", 9))
        export_btn.grid(row=0, column=4)
        
        # Export bounties button
        export_bounties_btn = tk.Button(control_frame, text="Export Bounties", command=self.export_bounties,
                                       bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                       activebackground="#404040",   # Darker when clicked
                                       activeforeground="#ffffff",  # White text when clicked
                                       relief="raised", borderwidth=1,
                                       font=("Segoe UI", 9))
        export_bounties_btn.grid(row=0, column=5, padx=(20, 0))
        
        # Test log creation button (for debugging auto-refresh)
        test_log_btn = tk.Button(control_frame, text="Create Test Log", command=self.create_test_log,
                                bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                activebackground="#404040",   # Darker when clicked
                                activeforeground="#ffffff",  # White text when clicked
                                relief="raised", borderwidth=1,
                                font=("Segoe UI", 9))
        test_log_btn.grid(row=0, column=6, padx=(20, 0))
        
        # Show file times button (for debugging)
        show_times_btn = tk.Button(control_frame, text="Show File Times", command=self.show_file_times,
                                  bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                  activebackground="#404040",   # Darker when clicked
                                  activeforeground="#ffffff",  # White text when clicked
                                  relief="raised", borderwidth=1,
                                  font=("Segoe UI", 9))
        show_times_btn.grid(row=0, column=7, padx=(20, 0))
        
        # Show file hashes button (for debugging content detection)
        show_hashes_btn = tk.Button(control_frame, text="Show File Hashes", command=self.show_file_hashes,
                                   bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                   activebackground="#404040",   # Darker when clicked
                                   activeforeground="#ffffff",  # White text when clicked
                                   relief="raised", borderwidth=1,
                                   font=("Segoe UI", 9))
        show_hashes_btn.grid(row=0, column=8, padx=(20, 0))
        
        self.auto_refresh_thread = None
        self.stop_auto_refresh = False
        self.last_refresh_time = None
        self.monitoring_thread = None
        self.stop_monitoring_only = False
    
    def browse_directory(self):
        """Browse for log directory"""
        directory = filedialog.askdirectory(initialdir=self.eve_log_dir)
        if directory:
            self.eve_log_dir = directory
            self.dir_var.set(directory)
            self.refresh_recent_logs()
    
    def apply_filters(self):
        """Apply the current filter settings"""
        try:
            self.max_days_old = int(self.days_var.get())
            self.max_files_to_show = int(self.files_var.get())
            self.refresh_recent_logs()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for the filters.")
    
    def parse_filename_timestamp(self, filename):
        """Parse UTC timestamp from EVE log filename format: Date_startTime_characterID.txt"""
        # Pattern: YYYYMMDD_HHMMSS_characterID.txt
        pattern = r'(\d{8})_(\d{6})_(\d+)\.(txt|log|xml)$'
        match = re.match(pattern, filename)
        
        if match:
            date_str = match.group(1)  # YYYYMMDD
            time_str = match.group(2)  # HHMMSS
            char_id = match.group(3)   # Character ID
            
            try:
                # Parse the timestamp
                timestamp = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                return timestamp, char_id
            except ValueError:
                return None, None
        
        return None, None
    
    def is_recent_file(self, file_path):
        """Check if a file is recent based on filename timestamp"""
        filename = os.path.basename(file_path)
        timestamp, char_id = self.parse_filename_timestamp(filename)
        
        if timestamp:
            # Check if file is within the specified days old
            days_old = (datetime.now() - timestamp).days
            return days_old <= self.max_days_old
        
        # If no timestamp in filename, fall back to file modification time
        try:
            mtime = os.path.getmtime(file_path)
            file_time = datetime.fromtimestamp(mtime)
            days_old = (datetime.now() - file_time).days
            return days_old <= self.max_days_old
        except:
            return False
    
    def load_log_files(self):
        """Load available log files from the selected directory"""
        try:
            if os.path.exists(self.eve_log_dir):
                self.refresh_recent_logs()
            else:
                self.status_var.set("Directory not found")
                
        except Exception as e:
            self.status_var.set(f"Error loading files: {str(e)}")
    
    def scan_existing_bounties(self):
        """Scan existing log entries for bounty entries that may have been missed"""
        try:
            print("🔍 Scanning existing log entries for bounties...")
            bounty_count = 0
            
            for timestamp, line, source_file in self.all_log_entries:
                bounty_amount = self.extract_bounty(line)
                if bounty_amount and timestamp:
                    # Check if this bounty is already tracked
                    bounty_exists = any(
                        entry['timestamp'] == timestamp and 
                        entry['isk_amount'] == bounty_amount and 
                        entry['source_file'] == source_file
                        for entry in self.bounty_entries
                    )
                    
                    if not bounty_exists:
                        self.add_bounty_entry(timestamp, bounty_amount, source_file)
                        bounty_count += 1
            
            if bounty_count > 0:
                print(f"💰 Found {bounty_count} additional bounties in existing logs")
                self.update_bounty_display()
            else:
                print("  No additional bounties found in existing logs")
                
        except Exception as e:
            print(f"Error scanning existing bounties: {e}")
    
    def refresh_recent_logs(self):
        """Refresh and combine only recent log files"""
        try:
            self.status_var.set("Refreshing recent log files...")
            self.root.update()
            
            # Get all log files
            all_log_files = []
            for pattern in self.log_patterns:
                all_log_files.extend(Path(self.eve_log_dir).glob(pattern))
            
            if not all_log_files:
                self.status_var.set("No log files found")
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(tk.END, "No log files found in the selected directory.")
                return
            
            # Filter for recent files only
            recent_files = []
            for log_file in all_log_files:
                if self.is_recent_file(log_file):
                    recent_files.append(log_file)
            
            if not recent_files:
                self.status_var.set("No recent log files found")
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(tk.END, f"No log files found from the last {self.max_days_old} day(s).")
                return
            
            # Sort files by timestamp (newest first)
            recent_files.sort(key=lambda x: self.parse_filename_timestamp(x.name)[0] or datetime.min, reverse=True)
            
            # Limit to max files to show
            if len(recent_files) > self.max_files_to_show:
                recent_files = recent_files[:self.max_files_to_show]
            
            # Process recent files and combine entries
            self.all_log_entries = []
            total_lines = 0
            
            for log_file in recent_files:
                try:
                    if os.path.exists(log_file):
                        # Read the file
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                        
                        # Process lines and add file source info
                        for line in lines:
                            timestamp = self.extract_timestamp(line)
                            source_file = log_file.name
                            
                            # Check for bounty entries
                            bounty_amount = self.extract_bounty(line)
                            if bounty_amount and timestamp:
                                # Check if this bounty is already tracked to avoid duplicates
                                bounty_exists = any(
                                    entry['timestamp'] == timestamp and 
                                    entry['isk_amount'] == bounty_amount and 
                                    entry['source_file'] == source_file
                                    for entry in self.bounty_entries
                                )
                                
                                if not bounty_exists:
                                    print(f"💰 Processing bounty: {bounty_amount:,} ISK from {source_file}")
                                    self.add_bounty_entry(timestamp, bounty_amount, source_file)
                                else:
                                    print(f"🔄 Skipping duplicate bounty: {bounty_amount:,} ISK from {source_file}")
                            
                            # Check for CONCORD link messages
                            concord_message_type = self.detect_concord_message(line)
                            if concord_message_type == "link_start":
                                self.concord_link_start = datetime.now()
                                self.concord_status_var.set("Status: Linking")
                                self.concord_countdown_active = True
                                self.start_concord_countdown()
                            elif concord_message_type == "link_complete":
                                self.concord_link_completed = True
                                self.concord_status_var.set("Status: Active")
                                # Don't stop the countdown - let it continue to show total elapsed time
                                # self.concord_countdown_active = False
                                # self.stop_concord_countdown = True
                                self.concord_time_var.set(f"Link Time: {self.concord_link_start.strftime('%H:%M:%S')} - {datetime.now().strftime('%H:%M:%S')}")
                                self.update_concord_display()
                            
                            self.all_log_entries.append((timestamp, line, source_file))
                        
                        total_lines += len(lines)
                        
                        # Store file size and modification time for change detection
                        self.last_file_sizes[str(log_file)] = os.path.getsize(log_file)
                        self.last_file_sizes[f"{str(log_file)}_mtime"] = os.path.getmtime(log_file)
                        
                        # Store content hash for change detection
                        content_hash = self.calculate_file_hash(log_file)
                        if content_hash:
                            self.last_file_hashes[str(log_file)] = content_hash
                        
                except Exception as e:
                    print(f"Error reading {log_file}: {e}")
                    continue
            
            # Sort all entries by timestamp (newest first)
            self.all_log_entries.sort(key=lambda x: x[0] if x[0] else datetime.min, reverse=True)
            
            # Display combined logs
            self.display_combined_logs()
            
            # Update last refresh time
            self.last_refresh_time = datetime.now()
            
            # Show file info and refresh status
            file_info = []
            for log_file in recent_files:
                timestamp, char_id = self.parse_filename_timestamp(log_file.name)
                if timestamp:
                    file_info.append(f"{log_file.name} (UTC: {timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
                else:
                    file_info.append(log_file.name)
            
            status_text = f"Monitoring {len(recent_files)} recent files with {total_lines} total log entries | Last refresh: {self.last_refresh_time.strftime('%H:%M:%S')}"
            if self.high_freq_var.get():
                status_text += " | High-freq: ON"
            else:
                status_text += " | High-freq: OFF"
            
            # Add bounty information to status
            if self.bounty_entries:
                status_text += f" | 💰 Bounties: {len(self.bounty_entries)} ({self.total_bounty_isk:,} ISK)"
            
            # Add CONCORD information to status
            if self.concord_countdown_active and not self.concord_link_completed:
                status_text += " | 🔗 CONCORD: Linking"
            elif self.concord_link_completed:
                status_text += " | 🔗 CONCORD: Active"
            
            self.status_var.set(status_text)
            
            # Update bounty display
            self.update_bounty_display()
            
            # Update CONCORD display
            self.update_concord_display()
            
            # Scan for any bounties that might have been missed
            self.scan_existing_bounties()
            
        except Exception as e:
            self.status_var.set(f"Error refreshing logs: {str(e)}")
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(tk.END, f"Error refreshing logs: {str(e)}")
    
    def display_combined_logs(self):
        """Display all combined log entries"""
        self.text_widget.delete(1.0, tk.END)
        
        if not self.all_log_entries:
            self.text_widget.insert(tk.END, "No log entries found.")
            return
        
        # Display entries with file source information
        for timestamp, line, source_file in self.all_log_entries:
            # Format the display line
            if timestamp:
                time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                display_line = f"[{time_str}] [{source_file}] {line}"
            else:
                display_line = f"[NO-TIME] [{source_file}] {line}"
            
            self.text_widget.insert(tk.END, display_line)
        
        # Scroll to top to show newest entries
        self.text_widget.see("1.0")
    
    def check_for_changes(self):
        """Check if any recent log files have changed using content hashing"""
        try:
            changed_files = []
            current_time = datetime.now()
            
            print(f"\n--- Checking for file changes at {current_time.strftime('%H:%M:%S')} ---")
            
            for pattern in self.log_patterns:
                for log_file in Path(self.eve_log_dir).glob(pattern):
                    file_path = str(log_file)
                    if os.path.exists(file_path) and self.is_recent_file(file_path):
                        # Get current file stats
                        current_size = os.path.getsize(file_path)
                        current_mtime = os.path.getmtime(file_path)
                        current_mtime_dt = datetime.fromtimestamp(current_mtime)
                        
                        # Calculate current content hash
                        current_hash = self.calculate_file_hash(file_path)
                        
                        # Get last known stats
                        last_size = self.last_file_sizes.get(file_path, 0)
                        last_mtime = self.last_file_sizes.get(f"{file_path}_mtime", 0)
                        last_hash = self.last_file_hashes.get(file_path, None)
                        last_mtime_dt = datetime.fromtimestamp(last_mtime) if last_mtime > 0 else None
                        
                        # Calculate time differences
                        time_since_last_check = (current_time - current_mtime_dt).total_seconds()
                        
                        # PRIMARY: Check if content hash changed (most reliable)
                        # SECONDARY: Check if modification time changed
                        # TERTIARY: Check if size changed
                        hash_changed = current_hash and last_hash and current_hash != last_hash
                        mtime_changed = current_mtime != last_mtime
                        size_changed = current_size != last_size
                        
                        if hash_changed or mtime_changed or size_changed:
                            changed_files.append(log_file)
                            
                            # Update stored values
                            self.last_file_sizes[file_path] = current_size
                            self.last_file_sizes[f"{file_path}_mtime"] = current_mtime
                            if current_hash:
                                self.last_file_hashes[file_path] = current_hash
                            
                            # Detailed debug info
                            print(f"✓ File changed: {os.path.basename(file_path)}")
                            if hash_changed:
                                print(f"  Content: HASH CHANGED (most reliable indicator)")
                                print(f"  Old hash: {last_hash[:8]}...")
                                print(f"  New hash: {current_hash[:8]}...")
                            if mtime_changed:
                                print(f"  MTime: {last_mtime_dt.strftime('%H:%M:%S') if last_mtime_dt else 'Never'} -> {current_mtime_dt.strftime('%H:%M:%S')}")
                                print(f"  Time since last check: {time_since_last_check:.1f} seconds")
                            if size_changed:
                                print(f"  Size: {last_size} -> {current_size} bytes")
                        else:
                            # Show files that haven't changed for debugging
                            if last_hash:
                                time_since_last_change = (current_time - last_mtime_dt).total_seconds()
                                print(f"  No change: {os.path.basename(file_path)} (last modified: {time_since_last_change:.1f}s ago, hash: {last_hash[:8]}...)")
                            else:
                                print(f"  New file: {os.path.basename(file_path)} (first time seen)")
            
            if changed_files:
                print(f"✓ Found {len(changed_files)} changed files")
            else:
                print("  No files changed")
            
            print("--- End change check ---\n")
            return changed_files
            
        except Exception as e:
            print(f"Error checking for changes: {e}")
            return []
    
    def extract_timestamp(self, line):
        """Extract timestamp from log line"""
        # Common EVE log timestamp patterns
        patterns = [
            r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]',  # [YYYY-MM-DD HH:MM:SS] (exported format)
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',  # YYYY-MM-DD HH:MM:SS
            r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})',  # MM/DD/YYYY HH:MM:SS
            r'(\d{2}:\d{2}:\d{2})',  # HH:MM:SS
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                timestamp_str = match.group(1)
                try:
                    # Try to parse the timestamp
                    if len(timestamp_str) == 8:  # HH:MM:SS
                        # Add today's date
                        today = datetime.now().strftime("%Y-%m-%d")
                        timestamp_str = f"{today} {timestamp_str}"
                    
                    if len(timestamp_str) == 19:  # YYYY-MM-DD HH:MM:SS
                        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    elif len(timestamp_str) == 19:  # MM/DD/YYYY HH:MM:SS
                        return datetime.strptime(timestamp_str, "%m/%d/%Y %H:%M:%S")
                except ValueError:
                    continue
        
        return None
    
    def extract_bounty(self, line):
        """Extract bounty information from log line"""
        # Pattern for bounty entries: (bounty) <font size=12><b><color=0xff00aa00>AMOUNT ISK</color> added to next bounty payout
        # Simplified pattern to catch more variations
        bounty_patterns = [
            r'\(bounty\)\s*.*?<color[^>]*>([\d,]+)\s+ISK</color>.*?added to next bounty payout',
            r'\(bounty\)\s*.*?([\d,]+)\s+ISK.*?added to next bounty payout',
            r'\(bounty\)\s*.*?([\d,]+)\s+ISK',
        ]
        
        for pattern in bounty_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    # Remove commas and convert to integer
                    isk_amount = int(match.group(1).replace(',', ''))
                    print(f"🔍 Bounty detected: {isk_amount:,} ISK from line: {line.strip()}")
                    return isk_amount
                except ValueError:
                    print(f"⚠️ Failed to parse bounty amount: {match.group(1)}")
                    continue
        
        return None
    
    def detect_concord_message(self, line):
        """Detect CONCORD Rogue Analysis Beacon messages"""
        # Pattern for link start message
        link_start_pattern = r'Your ship has started the link process with CONCORD Rogue Analysis Beacon'
        
        # Pattern for link completion message
        link_complete_pattern = r'Your ship successfully completed the link process with CONCORD Rogue Analysis Beacon'
        
        if re.search(link_start_pattern, line, re.IGNORECASE):
            print("🔗 CONCORD link process started detected")
            return "link_start"
        elif re.search(link_complete_pattern, line, re.IGNORECASE):
            print("✅ CONCORD link process completed detected")
            return "link_complete"
        
        return None
    
    def start_concord_countdown(self):
        """Start the 60-minute countdown timer for CONCORD link"""
        if self.concord_countdown_thread and self.concord_countdown_thread.is_alive():
            return  # Already running
        
        self.stop_concord_countdown = False
        self.concord_countdown_thread = threading.Thread(target=self.concord_countdown_loop, daemon=True)
        self.concord_countdown_thread.start()
        print("🔗 CONCORD countdown timer started")
    
    def concord_countdown_loop(self):
        """Countdown loop for CONCORD link process"""
        start_time = datetime.now()
        target_time = start_time + timedelta(minutes=60)
        
        while not self.stop_concord_countdown:
            current_time = datetime.now()
            
            if self.concord_link_completed:
                # Link completed - show countdown format but in green
                remaining = target_time - current_time
                minutes = int(remaining.total_seconds() // 60)
                seconds = int(remaining.total_seconds() % 60)
                countdown_text = f"Countdown: {minutes:02d}:{seconds:02d}"
                color = "#00ff00"  # Green for completed
            else:
                # Link still active - show countdown
                remaining = target_time - current_time
                
                if remaining.total_seconds() <= 0:
                    # Time's up!
                    self.root.after(0, self.concord_countdown_expired)
                    break
                
                # Update countdown display
                minutes = int(remaining.total_seconds() // 60)
                seconds = int(remaining.total_seconds() % 60)
                countdown_text = f"Countdown: {minutes:02d}:{seconds:02d}"
                
                # Always yellow while linking (until completion)
                color = "#ffff00"  # Yellow while linking
            
            self.root.after(0, lambda: self.update_concord_countdown(countdown_text, color))
            
            time.sleep(1)  # Update every second
    
    def update_concord_countdown(self, text, color):
        """Update the countdown display with new text and color"""
        self.concord_countdown_var.set(text)
        # Update the countdown label color
        self.concord_countdown_color = color
        self.concord_countdown_label.configure(foreground=color)
    
    def concord_countdown_expired(self):
        """Handle countdown expiration"""
        self.concord_status_var.set("Status: EXPIRED (Linking)")
        self.concord_countdown_var.set("Countdown: EXPIRED")
        self.concord_countdown_active = False
        print("⚠️ CONCORD link countdown expired!")
    
    def update_concord_display(self):
        """Update the CONCORD display with current status"""
        if self.concord_link_start:
            if self.concord_link_completed:
                self.concord_status_var.set("Status: Active")
                # Don't change countdown text here - let the countdown loop handle it
            else:
                self.concord_status_var.set("Status: Linking")
        else:
            self.concord_status_var.set("Status: Inactive")
            self.concord_countdown_var.set("Countdown: --:--")
    
    def reset_concord_tracking(self):
        """Reset CONCORD tracking to start fresh"""
        if self.concord_countdown_active:
            # Ask for confirmation
            result = messagebox.askyesno(
                "Reset CONCORD Tracking", 
                "Are you sure you want to reset CONCORD tracking?\n\n"
                "This will stop the current countdown and clear all tracking data.\n\n"
                "This action cannot be undone."
            )
            
            if not result:
                return
        
        # Stop countdown if running
        self.stop_concord_countdown = True
        if self.concord_countdown_thread and self.concord_countdown_thread.is_alive():
            self.concord_countdown_thread.join(timeout=1)
        
        # Reset all variables
        self.concord_link_start = None
        self.concord_link_completed = False
        self.concord_countdown_active = False
        self.stop_concord_countdown = False
        
        # Update display
        self.update_concord_display()
        print("🔄 CONCORD tracking reset")
    
    def test_concord_link_start(self):
        """Test function to simulate CONCORD link start message"""
        print("🧪 Testing CONCORD link start...")
        self.concord_link_start = datetime.now()
        self.concord_status_var.set("Status: Linking")
        self.concord_countdown_active = True
        self.start_concord_countdown()
        self.concord_time_var.set(f"Link Time: Started at {self.concord_link_start.strftime('%H:%M:%S')}")
    
    def test_concord_link_complete(self):
        """Test function to simulate CONCORD link completion message"""
        print("🧪 Testing CONCORD link completion...")
        if self.concord_link_start:
            self.concord_link_completed = True
            self.concord_status_var.set("Status: Active")
            # Don't stop the countdown - let it continue to show elapsed time
            # self.concord_countdown_active = False
            # self.stop_concord_countdown = True
            completion_time = datetime.now()
            self.concord_time_var.set(f"Link Time: {self.concord_link_start.strftime('%H:%M:%S')} - {completion_time.strftime('%H:%M:%S')}")
            self.update_concord_display()
        else:
            messagebox.showwarning("Test Warning", "No link process started. Start a link first.")
    
    def end_concord_process(self):
        """End the CONCORD process manually"""
        if not self.concord_link_start:
            messagebox.showwarning("End Process", "No CONCORD process is currently running.")
            return
        
        # Ask for confirmation
        result = messagebox.askyesno(
            "End CONCORD Process", 
            "Are you sure you want to end the CONCORD process?\n\n"
            "This will mark the process as completed and change the status to 'Completed'.\n\n"
            "This action cannot be undone."
        )
        
        if result:
            self.concord_link_completed = True
            self.concord_status_var.set("Status: Completed")
            completion_time = datetime.now()
            self.concord_time_var.set(f"Link Time: {self.concord_link_start.strftime('%H:%M:%S')} - {completion_time.strftime('%H:%M:%S')}")
            self.update_concord_display()
            print("✅ CONCORD process manually ended")
    
    def add_bounty_entry(self, timestamp, isk_amount, source_file):
        """Add a new bounty entry to the tracking system"""
        if self.bounty_session_start is None:
            self.bounty_session_start = datetime.now()
        
        bounty_entry = {
            'timestamp': timestamp,
            'isk_amount': isk_amount,
            'source_file': source_file,
            'running_total': self.total_bounty_isk + isk_amount
        }
        
        self.bounty_entries.append(bounty_entry)
        self.total_bounty_isk += isk_amount
        
        print(f"💰 Bounty tracked: {isk_amount:,} ISK (Total: {self.total_bounty_isk:,} ISK)")
    
    def reset_bounty_tracking(self):
        """Reset bounty tracking to start fresh"""
        if self.bounty_entries:
            # Ask for confirmation
            result = messagebox.askyesno(
                "Reset Bounty Tracking", 
                f"Are you sure you want to reset bounty tracking?\n\n"
                f"This will clear {len(self.bounty_entries)} bounty entries "
                f"and {self.total_bounty_isk:,} ISK in tracked earnings.\n\n"
                f"This action cannot be undone."
            )
            
            if not result:
                return
        
        self.bounty_entries = []
        self.total_bounty_isk = 0
        self.bounty_session_start = datetime.now()
        self.update_bounty_display()
        print("🔄 Bounty tracking reset")
    
    def toggle_high_frequency(self):
        """Toggle high-frequency monitoring functionality"""
        if self.high_freq_var.get():
            print("Starting high-frequency monitoring...")
            self.start_monitoring_only()
        else:
            print("Stopping high-frequency monitoring...")
            self.stop_monitoring_only = True
    
    def start_monitoring_only(self):
        """Start monitoring-only thread (without auto-refresh)"""
        self.stop_monitoring_only = False
        self.monitoring_thread = threading.Thread(target=self.monitoring_only_loop, daemon=True)
        self.monitoring_thread.start()
        print("Monitoring-only thread started")
    
    def monitoring_only_loop(self):
        """Monitoring-only loop - checks for changes and refreshes automatically"""
        print("Monitoring loop started")
        while not self.stop_monitoring_only:
            time.sleep(1) # Check every 1 second for high-frequency monitoring
            if not self.stop_monitoring_only:
                print("Checking for file changes (monitoring)...")
                changed_files = self.check_for_changes()
                if changed_files:
                    print(f"Changed files detected: {len(changed_files)} - refreshing automatically")
                    self.root.after(0, self.refresh_recent_logs)
                else:
                    print("No changes detected, continuing to monitor...")
                    # Even if no changes, update status to show we're still checking
                    if self.last_refresh_time:
                        self.root.after(0, self.update_status_with_check_time)
    
    def calculate_file_hash(self, file_path):
        """Calculate MD5 hash of file content for change detection"""
        try:
            if not os.path.exists(file_path):
                return None
            
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return None
    
    def get_file_modification_info(self):
        """Get detailed information about file modification times"""
        try:
            file_info = []
            current_time = datetime.now()
            
            for pattern in self.log_patterns:
                for log_file in Path(self.eve_log_dir).glob(pattern):
                    if os.path.exists(log_file) and self.is_recent_file(log_file):
                        file_path = str(log_file)
                        mtime = os.path.getmtime(file_path)
                        mtime_dt = datetime.fromtimestamp(mtime)
                        time_ago = (current_time - mtime_dt).total_seconds()
                        
                        if time_ago < 60:
                            time_str = f"{time_ago:.0f}s ago"
                        elif time_ago < 3600:
                            time_str = f"{time_ago/60:.0f}m ago"
                        else:
                            time_str = f"{time_ago/3600:.1f}h ago"
                        
                        file_info.append((log_file.name, mtime_dt, time_str))
            
            # Sort by modification time (newest first)
            file_info.sort(key=lambda x: x[1], reverse=True)
            return file_info
            
        except Exception as e:
            print(f"Error getting file modification info: {e}")
            return []
    
    def update_status_with_check_time(self):
        """Update status to show last check time and file modification info"""
        if self.last_refresh_time:
            current_time = datetime.now()
            time_since_refresh = current_time - self.last_refresh_time
            minutes = int(time_since_refresh.total_seconds() // 60)
            seconds = int(time_since_refresh.total_seconds() % 60)
            
            # Get file modification info
            file_info = self.get_file_modification_info()
            if file_info:
                newest_file = file_info[0]
                newest_time = newest_file[1]
                newest_ago = newest_file[2]
                
                status_text = f"Last refresh: {self.last_refresh_time.strftime('%H:%M:%S')} | Last check: {current_time.strftime('%H:%M:%S')} | Newest file: {newest_file[0]} ({newest_ago})"
            else:
                status_text = f"Last refresh: {self.last_refresh_time.strftime('%H:%M:%S')} | Last check: {current_time.strftime('%H:%M:%S')}"
            
            # Add monitoring status
            if self.high_freq_var.get():
                status_text += " | High-freq: ON"
            else:
                status_text += " | High-freq: OFF"
            
            # Add CONCORD status
            if self.concord_countdown_active and not self.concord_link_completed:
                status_text += " | 🔗 CONCORD: Linking"
            elif self.concord_link_completed:
                status_text += " | 🔗 CONCORD: Active"
            
            self.status_var.set(status_text)
    
    def show_file_times(self):
        """Show detailed file modification times for debugging"""
        try:
            file_info = self.get_file_modification_info()
            
            if not file_info:
                messagebox.showinfo("File Times", "No recent files found.")
                return
            
            # Create popup window
            popup = tk.Toplevel(self.root)
            popup.title("File Modification Times")
            popup.geometry("600x400")
            popup.transient(self.root)
            popup.grab_set()
            popup.configure(bg="#2b2b2b")  # Dark background
            
            # Create text widget
            text_widget = tk.Text(popup, wrap=tk.WORD, font=("Consolas", 10),
                                 bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                 insertbackground="#ffffff",   # White cursor
                                 selectbackground="#4a9eff",  # Blue selection
                                 selectforeground="#ffffff")  # White text when selected
            scrollbar = tk.Scrollbar(popup, orient=tk.VERTICAL, command=text_widget.yview,
                                    bg="#1e1e1e", troughcolor="#2b2b2b",  # Dark scrollbar
                                    activebackground="#404040",            # Darker when active
                                    relief="flat", borderwidth=0)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
            scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            
            popup.columnconfigure(0, weight=1)
            popup.rowconfigure(0, weight=1)
            
            # Add header
            text_widget.insert(tk.END, "File Modification Times (Newest First)\n")
            text_widget.insert(tk.END, "=" * 60 + "\n\n")
            
            current_time = datetime.now()
            
            for filename, mtime, time_ago in file_info:
                # Calculate exact time difference
                time_diff = current_time - mtime
                seconds = time_diff.total_seconds()
                
                if seconds < 60:
                    exact_time = f"{seconds:.1f} seconds ago"
                elif seconds < 3600:
                    exact_time = f"{seconds/60:.1f} minutes ago"
                else:
                    exact_time = f"{seconds/3600:.2f} hours ago"
                
                text_widget.insert(tk.END, f"File: {filename}\n")
                text_widget.insert(tk.END, f"Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}\n")
                text_widget.insert(tk.END, f"Time ago: {exact_time}\n")
                
                # Add content hash information
                file_path = os.path.join(self.eve_log_dir, filename)
                if os.path.exists(file_path):
                    current_hash = self.calculate_file_hash(file_path)
                    if current_hash:
                        text_widget.insert(tk.END, f"Content Hash: {current_hash[:16]}...\n")
                
                text_widget.insert(tk.END, "-" * 40 + "\n")
            
            # Add footer
            text_widget.insert(tk.END, f"\nChecked at: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            text_widget.insert(tk.END, f"Total files: {len(file_info)}\n")
            
            # Make text read-only
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error showing file times: {str(e)}")
    
    def show_file_hashes(self):
        """Show detailed file content hash information for debugging"""
        try:
            file_info = self.get_file_modification_info()
            
            if not file_info:
                messagebox.showinfo("File Hashes", "No recent files found.")
                return
            
            # Create popup window
            popup = tk.Toplevel(self.root)
            popup.title("File Content Hashes")
            popup.geometry("700x500")
            popup.transient(self.root)
            popup.grab_set()
            popup.configure(bg="#2b2b2b")  # Dark background
            
            # Create text widget
            text_widget = tk.Text(popup, wrap=tk.WORD, font=("Consolas", 9),
                                 bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                 insertbackground="#ffffff",   # White cursor
                                 selectbackground="#4a9eff",  # Blue selection
                                 selectforeground="#ffffff")  # White text when selected
            scrollbar = tk.Scrollbar(popup, orient=tk.VERTICAL, command=text_widget.yview,
                                    bg="#1e1e1e", troughcolor="#2b2b2b",  # Dark scrollbar
                                    activebackground="#404040",            # Darker when active
                                    relief="flat", borderwidth=0)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
            scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            
            popup.columnconfigure(0, weight=1)
            popup.rowconfigure(0, weight=1)
            
            # Add header
            text_widget.insert(tk.END, "File Content Hashes (Newest First)\n")
            text_widget.insert(tk.END, "=" * 70 + "\n\n")
            
            current_time = datetime.now()
            
            for filename, mtime, time_ago in file_info:
                file_path = os.path.join(self.eve_log_dir, filename)
                
                text_widget.insert(tk.END, f"File: {filename}\n")
                text_widget.insert(tk.END, f"Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}\n")
                text_widget.insert(tk.END, f"Time ago: {time_ago}\n")
                
                # Current hash
                current_hash = self.calculate_file_hash(file_path)
                if current_hash:
                    text_widget.insert(tk.END, f"Current Hash: {current_hash}\n")
                
                # Last known hash
                last_hash = self.last_file_hashes.get(file_path)
                if last_hash:
                    text_widget.insert(tk.END, f"Last Hash:  {last_hash}\n")
                    if current_hash and last_hash != current_hash:
                        text_widget.insert(tk.END, "  → CONTENT CHANGED!\n")
                    elif current_hash and last_hash == current_hash:
                        text_widget.insert(tk.END, "  → No change\n")
                else:
                    text_widget.insert(tk.END, "Last Hash:  Not tracked yet\n")
                
                text_widget.insert(tk.END, "-" * 50 + "\n")
            
            # Add footer
            text_widget.insert(tk.END, f"\nChecked at: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            text_widget.insert(tk.END, f"Total files: {len(file_info)}\n")
            text_widget.insert(tk.END, f"Monitoring: {'High-frequency (1s)' if self.high_freq_var.get() else 'Normal (3s)'}\n")
            
            # Make text read-only
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error showing file hashes: {str(e)}")
    
    def create_test_log(self):
        """Create a test log file to test auto-refresh functionality"""
        try:
            # Create a test log file with current timestamp
            now = datetime.now()
            timestamp_str = now.strftime("%Y%m%d_%H%M%S")
            test_filename = f"{timestamp_str}_99999999_test.txt"
            test_file_path = os.path.join(self.eve_log_dir, test_filename)
            
            # Create test log content
            test_content = f"{now.strftime('%Y-%m-%d %H:%M:%S')} [TEST] Auto-refresh test log entry\n"
            test_content += f"{now.strftime('%Y-%m-%d %H:%M:%S')} [TEST] This is a test log to verify auto-refresh\n"
            test_content += f"{now.strftime('%Y-%m-%d %H:%M:%S')} [TEST] File created at: {now}\n"
            
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            print(f"Created test log: {test_filename}")
            self.status_var.set(f"Test log created: {test_filename}")
            
            # Wait a moment then refresh to show the new file
            self.root.after(1000, self.refresh_recent_logs)
            
        except Exception as e:
            print(f"Error creating test log: {e}")
            self.status_var.set(f"Error creating test log: {str(e)}")
    
    def manual_refresh(self):
        """Manually trigger a refresh of the logs"""
        print("Manual refresh triggered")
        self.refresh_recent_logs()
        self.last_refresh_time = datetime.now()
        self.status_var.set(f"Last refresh: {self.last_refresh_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def clear_display(self):
        """Clear the display"""
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, "Display cleared.")
    
    def export_logs(self):
        """Export recent logs to a file"""
        try:
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Recent Logs As"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"EVE Online Recent Logs - Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Filter: Last {self.max_days_old} day(s), Max {self.max_files_to_show} files\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for timestamp, line, source_file in self.all_log_entries:
                        if timestamp:
                            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                            export_line = f"[{time_str}] [{source_file}] {line}"
                        else:
                            export_line = f"[NO-TIME] [{source_file}] {line}"
                        f.write(export_line)
                
                self.status_var.set(f"Recent logs exported to {os.path.basename(file_path)}")
                messagebox.showinfo("Export Complete", f"Recent logs exported successfully to:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting logs: {str(e)}")
            self.status_var.set(f"Export error: {str(e)}")

    def show_bounty_details(self):
        """Show detailed bounty information in a popup window"""
        try:
            if not self.bounty_entries:
                messagebox.showinfo("Bounty Details", "No bounties tracked yet.")
                return
            
            # Create popup window
            popup = tk.Toplevel(self.root)
            popup.title("💰 Bounty Details")
            popup.geometry("800x600")
            popup.transient(self.root)
            popup.grab_set()
            popup.configure(bg="#2b2b2b")  # Dark background
            
            # Create text widget
            text_widget = tk.Text(popup, wrap=tk.WORD, font=("Consolas", 10),
                                 bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                 insertbackground="#ffffff",   # White cursor
                                 selectbackground="#4a9eff",  # Blue selection
                                 selectforeground="#ffffff")  # White text when selected
            scrollbar = tk.Scrollbar(popup, orient=tk.VERTICAL, command=text_widget.yview,
                                    bg="#1e1e1e", troughcolor="#2b2b2b",  # Dark scrollbar
                                    activebackground="#404040",            # Darker when active
                                    relief="flat", borderwidth=0)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
            scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            
            popup.columnconfigure(0, weight=1)
            popup.rowconfigure(0, weight=1)
            
            # Add header
            text_widget.insert(tk.END, "💰 EVE Online Bounty Tracking Details\n")
            text_widget.insert(tk.END, "=" * 80 + "\n\n")
            
            # Session info
            if self.bounty_session_start:
                session_duration = datetime.now() - self.bounty_session_start
                hours = int(session_duration.total_seconds() // 3600)
                minutes = int((session_duration.total_seconds() % 3600) // 60)
                
                text_widget.insert(tk.END, f"Session Started: {self.bounty_session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
                text_widget.insert(tk.END, f"Session Duration: {hours}h {minutes}m\n")
                text_widget.insert(tk.END, f"Total Bounties: {len(self.bounty_entries)}\n")
                text_widget.insert(tk.END, f"Total ISK Earned: {self.total_bounty_isk:,} ISK\n")
                
                if session_duration.total_seconds() > 0:
                    isk_per_hour = (self.total_bounty_isk / session_duration.total_seconds()) * 3600
                    text_widget.insert(tk.END, f"ISK per Hour: {isk_per_hour:,.0f} ISK/h\n")
                
                text_widget.insert(tk.END, "\n" + "=" * 80 + "\n\n")
            
            # Individual bounty entries
            text_widget.insert(tk.END, "Individual Bounty Entries (Newest First):\n")
            text_widget.insert(tk.END, "-" * 80 + "\n\n")
            
            # Sort entries by timestamp (newest first)
            sorted_entries = sorted(self.bounty_entries, key=lambda x: x['timestamp'], reverse=True)
            
            for i, entry in enumerate(sorted_entries, 1):
                timestamp = entry['timestamp']
                isk_amount = entry['isk_amount']
                source_file = entry['source_file']
                running_total = entry['running_total']
                
                text_widget.insert(tk.END, f"{i:2d}. {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                text_widget.insert(tk.END, f"    Amount: {isk_amount:,} ISK\n")
                text_widget.insert(tk.END, f"    Source: {source_file}\n")
                text_widget.insert(tk.END, f"    Running Total: {running_total:,} ISK\n")
                text_widget.insert(tk.END, "-" * 40 + "\n")
            
            # Summary
            text_widget.insert(tk.END, f"\n📊 Summary:\n")
            text_widget.insert(tk.END, f"Total Bounties: {len(self.bounty_entries)}\n")
            text_widget.insert(tk.END, f"Total ISK: {self.total_bounty_isk:,} ISK\n")
            
            if self.bounty_entries:
                avg_bounty = self.total_bounty_isk / len(self.bounty_entries)
                text_widget.insert(tk.END, f"Average Bounty: {avg_bounty:,.0f} ISK\n")
                
                # Largest and smallest bounties
                largest = max(self.bounty_entries, key=lambda x: x['isk_amount'])
                smallest = min(self.bounty_entries, key=lambda x: x['isk_amount'])
                text_widget.insert(tk.END, f"Largest Bounty: {largest['isk_amount']:,} ISK\n")
                text_widget.insert(tk.END, f"Smallest Bounty: {smallest['isk_amount']:,} ISK\n")
            
            # Make text read-only
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error showing bounty details: {str(e)}")
    
    def update_bounty_display(self):
        """Update the bounty display labels with current information"""
        try:
            # Update total ISK
            self.bounty_total_var.set(f"Total ISK Earned: {self.total_bounty_isk:,} ISK")
            
            # Update bounty count
            self.bounty_count_var.set(f"Bounties: {len(self.bounty_entries)}")
            
            # Update session info
            if self.bounty_session_start:
                session_duration = datetime.now() - self.bounty_session_start
                hours = int(session_duration.total_seconds() // 3600)
                minutes = int((session_duration.total_seconds() % 3600) // 60)
                self.bounty_session_var.set(f"Session: {hours}h {minutes}m")
            else:
                self.bounty_session_var.set("Session: Not started")
                
        except Exception as e:
            print(f"Error updating bounty display: {e}")

    def export_bounties(self):
        """Export bounty tracking data to a file"""
        try:
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Bounty Tracking As"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"EVE Online Bounty Tracking - Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Session Start: {self.bounty_session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total Bounties: {len(self.bounty_entries)}\n")
                    f.write(f"Total ISK Earned: {self.total_bounty_isk:,} ISK\n")
                    f.write("=" * 80 + "\n\n")
                    
                    # Sort entries by timestamp (newest first)
                    sorted_entries = sorted(self.bounty_entries, key=lambda x: x['timestamp'], reverse=True)
                    
                    for i, entry in enumerate(sorted_entries, 1):
                        timestamp = entry['timestamp']
                        isk_amount = entry['isk_amount']
                        source_file = entry['source_file']
                        running_total = entry['running_total']
                        
                        f.write(f"{i:2d}. {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"    Amount: {isk_amount:,} ISK\n")
                        f.write(f"    Source: {source_file}\n")
                        f.write(f"    Running Total: {running_total:,} ISK\n")
                        f.write("-" * 40 + "\n")
                
                self.status_var.set(f"Bounty tracking exported to {os.path.basename(file_path)}")
                messagebox.showinfo("Export Complete", f"Bounty tracking exported successfully to:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting bounties: {str(e)}")
            self.status_var.set(f"Export error: {str(e)}")

def main():
    root = tk.Tk()
    app = EVELogReader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
