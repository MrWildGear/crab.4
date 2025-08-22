import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
import threading
import time
import glob
import hashlib
import csv
import requests  # New import for Google Form submission
import logging  # New import for file logging

# Application version
APP_VERSION = "0.6.4"

# Timezone handling: All timestamps are handled in UTC to match EVE Online log format
# EVE Online logs use UTC timestamps, so we maintain UTC throughout the system

class EVELogReader:
    def __init__(self, root):
        self.root = root
        self.root.title(f"EVE Online Log Reader v{APP_VERSION} - Recent Logs Monitor")
        self.root.geometry("1400x900")
        
        # Setup logging for Google Form debugging
        self.setup_logging()
        
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
        self.current_beacon_id = None  # Unique Beacon ID for current session
        self.beacon_source_file = None  # Source log file for current beacon
        
        # CRAB-specific bounty tracking system
        self.crab_bounty_entries = []  # Store bounty entries during CRAB sessions
        self.crab_total_bounty_isk = 0  # Total ISK earned during CRAB sessions
        self.crab_session_active = False  # Whether a CRAB session is currently active
        
        # Settings for recent file filtering
        self.max_days_old = 1  # Only show logs from last 24 hours by default
        self.max_files_to_show = 10  # Maximum number of recent files to display
        
        self.setup_ui()
        self.load_log_files()
        
        # Start bounty tracking
        self.bounty_session_start = self.get_utc_now()
        
        # Scan for active CRAB beacons on startup
        self.scan_for_active_crab_beacons_on_startup()
        
        # Start monitoring automatically since it's enabled by default
        if self.high_freq_var.get():
            self.start_monitoring_only()
        
        # Initialize Google Form status display
        self.update_google_form_status_display()
    
    def get_utc_now(self):
        """Get current time in UTC"""
        return datetime.now(timezone.utc)
    
    def setup_logging(self):
        """Setup logging for Google Form debugging"""
        try:
            # Create logs directory if it doesn't exist
            if not os.path.exists('logs'):
                os.makedirs('logs')
            
            # Setup logging to file
            log_file = os.path.join('logs', 'google_form_debug.log')
            
            # Configure logging
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler()  # Also log to console
                ]
            )
            
            # Create logger for this class
            self.logger = logging.getLogger(__name__)
            self.logger.info("Logging initialized for Google Form debugging")
            
        except Exception as e:
            print(f"⚠️ Failed to setup logging: {e}")
            # Fallback to basic logging
            self.logger = None
    
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
        main_frame.rowconfigure(4, weight=1)  # Updated to account for version label
        
        # Version label
        version_label = ttk.Label(main_frame, text=f"Version {APP_VERSION}", 
                                 font=("Segoe UI", 8), foreground="#888888")
        version_label.grid(row=0, column=1, sticky=tk.E, pady=(0, 5))
        
        # Log directory selection
        ttk.Label(main_frame, text="Log Directory:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
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
        filter_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
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
        ttk.Label(main_frame, text="Recent Logs (UTC Timestamp Based):").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        
        # Bounty tracking display
        bounty_frame = ttk.LabelFrame(main_frame, text="💰 Bounty Tracking", padding="5")
        bounty_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
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
        concord_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
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
        
        # Beacon ID display
        self.beacon_id_var = tk.StringVar(value="Beacon ID: None")
        beacon_id_label = ttk.Label(concord_frame, textvariable=self.beacon_id_var,
                                   font=("Consolas", 8), foreground="#888888")
        beacon_id_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=(0, 20), pady=(5, 0))
        
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
        
        # CRAB end process buttons
        end_crab_failed_btn = tk.Button(concord_frame, text="Failed", command=self.end_crab_failed,
                                        bg="#ff4444", fg="#ffffff",  # Red background for failed
                                        activebackground="#cc3333",   # Darker red when clicked
                                        activeforeground="#ffffff",  # White text when clicked
                                        relief="raised", borderwidth=1,
                                        font=("Segoe UI", 9))
        end_crab_failed_btn.grid(row=0, column=6, padx=(20, 0))
        
        end_crab_submit_btn = tk.Button(concord_frame, text="Submit Data", command=self.end_crab_submit,
                                        bg="#44ff44", fg="#000000",  # Green background for submit
                                        activebackground="#33cc33",   # Darker green when clicked
                                        activeforeground="#000000",  # Black text when clicked
                                        relief="raised", borderwidth=1,
                                        font=("Segoe UI", 9))
        end_crab_submit_btn.grid(row=0, column=7, padx=(20, 0))
        
        # Copy Beacon ID button
        copy_beacon_id_btn = tk.Button(concord_frame, text="Copy Beacon ID", command=self.copy_beacon_id,
                                       bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                       activebackground="#404040",   # Darker when clicked
                                       activeforeground="#ffffff",  # White text when clicked
                                       relief="raised", borderwidth=1,
                                       font=("Segoe UI", 9))
        copy_beacon_id_btn.grid(row=0, column=8, padx=(20, 0))
        
        # View Beacon Sessions button
        view_beacon_sessions_btn = tk.Button(concord_frame, text="View Sessions", command=self.view_beacon_sessions,
                                            bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                            activebackground="#404040",   # Darker when clicked
                                            activeforeground="#ffffff",  # White text when clicked
                                            relief="raised", borderwidth=1,
                                            font=("Segoe UI", 9))
        view_beacon_sessions_btn.grid(row=0, column=9, padx=(20, 0))
        
        # Google Form Config button
        google_form_config_btn = tk.Button(concord_frame, text="Form Config", command=self.configure_google_form,
                                          bg="#1e1e1e", fg="#ffffff",
                                          activebackground="#404040",
                                          activeforeground="#ffffff",
                                          relief="raised", borderwidth=1,
                                          font=("Segoe UI", 9))
        google_form_config_btn.grid(row=0, column=10, padx=(20, 0))
        
        # Google Form Status display
        self.google_form_status_var = tk.StringVar(value="Form Status: Checking...")
        google_form_status_label = ttk.Label(concord_frame, textvariable=self.google_form_status_var,
                                            font=("Segoe UI", 8), foreground="#888888")
        google_form_status_label.grid(row=1, column=9, columnspan=2, sticky=tk.W, padx=(20, 0), pady=(5, 0))
        
        # CRAB Bounty Tracking display
        crab_bounty_frame = ttk.LabelFrame(main_frame, text="🦀 CRAB Bounty Tracking", padding="5")
        crab_bounty_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # CRAB bounty info labels
        self.crab_bounty_total_var = tk.StringVar(value="CRAB Total ISK: 0 ISK")
        crab_bounty_total_label = ttk.Label(crab_bounty_frame, textvariable=self.crab_bounty_total_var, 
                                           font=("Segoe UI", 10, "bold"))
        crab_bounty_total_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.crab_bounty_count_var = tk.StringVar(value="CRAB Bounties: 0")
        crab_bounty_count_label = ttk.Label(crab_bounty_frame, textvariable=self.crab_bounty_count_var)
        crab_bounty_count_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        self.crab_session_var = tk.StringVar(value="CRAB Session: Inactive")
        crab_session_label = ttk.Label(crab_bounty_frame, textvariable=self.crab_session_var)
        crab_session_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
        
        # CRAB bounty control buttons
        reset_crab_bounty_btn = tk.Button(crab_bounty_frame, text="Reset CRAB Bounties", command=self.reset_crab_bounty_tracking,
                                         bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                         activebackground="#404040",   # Darker when clicked
                                         activeforeground="#ffffff",  # White text when clicked
                                         relief="raised", borderwidth=1,
                                         font=("Segoe UI", 9))
        reset_crab_bounty_btn.grid(row=0, column=3, padx=(20, 0))
        
        show_crab_bounties_btn = tk.Button(crab_bounty_frame, text="Show CRAB Details", command=self.show_crab_bounty_details,
                                          bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                          activebackground="#404040",   # Darker when clicked
                                          activeforeground="#ffffff",  # White text when clicked
                                          relief="raised", borderwidth=1,
                                          font=("Segoe UI", 9))
        show_crab_bounties_btn.grid(row=0, column=4, padx=(20, 0))
        
        # Add CRAB bounty button for testing
        add_crab_bounty_btn = tk.Button(crab_bounty_frame, text="Add CRAB Bounty", command=self.add_test_crab_bounty,
                                       bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                                       activebackground="#404040",   # Darker when clicked
                                       activeforeground="#ffffff",  # White text when clicked
                                       relief="raised", borderwidth=1,
                                       font=("Segoe UI", 9))
        add_crab_bounty_btn.grid(row=0, column=5, padx=(20, 0))
        
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
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
        self.status_var = tk.StringVar(value="Starting up - Scanning for active CRAB beacons...")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
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
        control_frame.grid(row=10, column=0, columnspan=2, pady=(10, 0))
        
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
        
        # Version info button
        version_btn = tk.Button(control_frame, text=f"v{APP_VERSION}", command=self.show_version_info,
                               bg="#2b2b2b", fg="#888888",  # Darker background, gray text
                               activebackground="#404040",   # Darker when clicked
                               activeforeground="#888888",  # Gray text when clicked
                               relief="flat", borderwidth=1,
                               font=("Segoe UI", 8))
        version_btn.grid(row=0, column=9, padx=(20, 0))
        
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
                # Parse the timestamp and make it timezone-aware UTC
                timestamp = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                timestamp = timestamp.replace(tzinfo=timezone.utc)
                return timestamp, char_id
            except ValueError:
                return None, None
        
        return None, None
    
    def is_recent_file(self, file_path):
        """Check if a file is recent based on filename timestamp"""
        filename = os.path.basename(file_path)
        
        # Skip configuration and project files
        skip_patterns = [
            'google_form_config',
            'version_info',
            'requirements',
            'README',
            'LICENSE',
            'CHANGELOG',
            'build',
            'setup',
            'test',
            'example',
            'sample'
        ]
        
        # Check if this is a configuration/project file that should be skipped
        for pattern in skip_patterns:
            if pattern.lower() in filename.lower():
                return False
        
        # Try to parse timestamp from filename
        timestamp, char_id = self.parse_filename_timestamp(filename)
        
        if timestamp:
            # Check if file is within the specified days old
            days_old = (self.get_utc_now() - timestamp).days
            return days_old <= self.max_days_old
        
        # If no timestamp in filename, this is likely not an EVE log file
        # Only process files that look like they might be EVE logs
        if filename.endswith('.txt') and not any(pattern.lower() in filename.lower() for pattern in skip_patterns):
            # For .txt files without timestamps, check if they look like EVE logs
            # by checking if they contain EVE-specific content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_line = f.readline().strip()
                    # Check if first line contains EVE log patterns
                    if any(pattern in first_line for pattern in ['[', '(', 'bounty)', 'combat', 'EVE', 'CONCORD']):
                        # This looks like an EVE log, use modification time
                        mtime = os.path.getmtime(file_path)
                        file_time = datetime.fromtimestamp(mtime, tz=timezone.utc)
                        days_old = (self.get_utc_now() - file_time).days
                        return days_old <= self.max_days_old
            except:
                pass
        
        # Skip this file
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
    
    def scan_for_active_crab_beacons(self):
        """Scan existing log entries for active CRAB beacons and auto-start tracking if recent"""
        try:
            print("🔍 Scanning existing log entries for active CRAB beacons...")
            
            current_time = self.get_utc_now()
            active_beacon_found = False
            
            # Look for CONCORD link start messages in recent logs
            for timestamp, line, source_file in self.all_log_entries:
                if not timestamp:
                    continue
                
                concord_message_type = self.detect_concord_message(line)
                if concord_message_type == "link_start":
                    # Calculate how long ago this beacon started
                    time_since_start = current_time - timestamp
                    time_since_start_minutes = time_since_start.total_seconds() / 60
                    
                    print(f"🔗 Found CONCORD beacon start message from {time_since_start_minutes:.1f} minutes ago")
                    
                    # Only auto-start tracking if beacon started less than 1 minute ago
                    if time_since_start_minutes <= 1.0:
                        print(f"✅ Beacon started {time_since_start_minutes:.1f} minutes ago - auto-starting CRAB tracking")
                        
                        # Validate that the beacon timestamp is not in the future
                        current_time = self.get_utc_now()
                        beacon_timestamp = timestamp
                        if beacon_timestamp > current_time:
                            print(f"⚠️ Warning: Auto-scan beacon timestamp {beacon_timestamp} is in the future, using current time instead")
                            beacon_timestamp = current_time
                        
                        # Set up beacon tracking
                        self.concord_link_start = beacon_timestamp
                        self.concord_status_var.set("Status: Linking")
                        self.concord_countdown_active = True
                        
                        # Generate unique Beacon ID
                        self.current_beacon_id = self.generate_beacon_id(source_file, timestamp)
                        self.beacon_source_file = source_file
                        
                        # Start CRAB bounty tracking session
                        self.start_crab_session()
                        
                        # Start countdown timer
                        self.start_concord_countdown()
                        
                        # Update displays
                        self.update_concord_display()
                        self.update_bounty_display()
                        
                        active_beacon_found = True
                        print(f"🔗 Auto-started CRAB beacon tracking - ID: {self.current_beacon_id}")
                        print(f"📁 Source file: {self.beacon_source_file}")
                        print(f"⏰ Started {time_since_start_minutes:.1f} minutes ago")
                        
                        # Only track the first active beacon found
                        break
                    else:
                        print(f"⏰ Beacon started {time_since_start_minutes:.1f} minutes ago - too old to auto-track")
                
                elif concord_message_type == "link_complete":
                    # If we find a completion message, check if it's recent enough to consider the beacon still active
                    time_since_completion = current_time - timestamp
                    time_since_completion_minutes = time_since_completion.total_seconds() / 60
                    
                    print(f"✅ Found CONCORD beacon completion message from {time_since_completion_minutes:.1f} minutes ago")
                    
                    # Only consider it active if completed less than 1 minute ago
                    if time_since_completion_minutes <= 1.0:
                        print(f"✅ Beacon completed {time_since_completion_minutes:.1f} minutes ago - checking if we should track it")
                        
                        # Look for the corresponding start message
                        start_timestamp = self.find_beacon_start_timestamp(timestamp, source_file)
                        if start_timestamp:
                            time_since_start = current_time - start_timestamp
                            time_since_start_minutes = time_since_start.total_seconds() / 60
                            
                            if time_since_start_minutes <= 1.0:
                                print(f"✅ Beacon session completed recently - auto-starting tracking")
                                
                                # Validate that the beacon timestamp is not in the future
                                current_time = self.get_utc_now()
                                beacon_timestamp = start_timestamp
                                if beacon_timestamp > current_time:
                                    print(f"⚠️ Warning: Completed beacon timestamp {beacon_timestamp} is in the future, using current time instead")
                                    beacon_timestamp = current_time
                                
                                # Set up completed beacon tracking
                                self.concord_link_start = beacon_timestamp
                                self.concord_link_completed = True
                                self.concord_status_var.set("Status: Active")
                                self.concord_countdown_active = True
                                
                                # Generate unique Beacon ID
                                self.current_beacon_id = self.generate_beacon_id(source_file, start_timestamp)
                                self.beacon_source_file = source_file
                                
                                # Start CRAB bounty tracking session
                                self.start_crab_session()
                                
                                # Start countdown timer (will show elapsed time)
                                self.start_concord_countdown()
                                
                                # Update displays
                                self.update_concord_display()
                                self.update_bounty_display()
                                
                                active_beacon_found = True
                                print(f"🔗 Auto-started completed CRAB beacon tracking - ID: {self.current_beacon_id}")
                                print(f"📁 Source file: {self.beacon_source_file}")
                                print(f"⏰ Started {time_since_start_minutes:.1f} minutes ago, completed {time_since_completion_minutes:.1f} minutes ago")
                                
                                # Only track the first active beacon found
                                break
                            else:
                                print(f"⏰ Beacon session too old ({time_since_start_minutes:.1f} minutes) - not auto-tracking")
                        else:
                            print(f"⚠️ Could not find start timestamp for completed beacon")
                
                # Check for ongoing beacon sessions (started but not completed)
                elif concord_message_type == "link_start":
                    # We already handled link_start above, but let's also check if there's an ongoing session
                    # that might have started recently but hasn't completed yet
                    if not active_beacon_found:  # Only if we haven't found an active beacon yet
                        time_since_start = current_time - timestamp
                        time_since_start_minutes = time_since_start.total_seconds() / 60
                        
                        # Check if this is a very recent start (within 1 minute) that we should track
                        if time_since_start_minutes <= 1.0:
                            print(f"🔗 Found very recent beacon start ({time_since_start_minutes:.1f} minutes ago) - auto-starting tracking")
                            
                            # Validate that the beacon timestamp is not in the future
                            current_time = self.get_utc_now()
                            beacon_timestamp = timestamp
                            if beacon_timestamp > current_time:
                                print(f"⚠️ Warning: Very recent beacon timestamp {beacon_timestamp} is in the future, using current time instead")
                                beacon_timestamp = current_time
                            
                            # Set up beacon tracking
                            self.concord_link_start = beacon_timestamp
                            self.concord_status_var.set("Status: Linking")
                            self.concord_countdown_active = True
                            
                            # Generate unique Beacon ID
                            self.current_beacon_id = self.generate_beacon_id(source_file, timestamp)
                            self.beacon_source_file = source_file
                            
                            # Start CRAB bounty tracking session
                            self.start_crab_session()
                            
                            # Start countdown timer
                            self.start_concord_countdown()
                            
                            # Update displays
                            self.update_concord_display()
                            self.update_bounty_display()
                            
                            active_beacon_found = True
                            print(f"🔗 Auto-started recent CRAB beacon tracking - ID: {self.current_beacon_id}")
                            print(f"📁 Source file: {self.beacon_source_file}")
                            print(f"⏰ Started {time_since_start_minutes:.1f} minutes ago")
                            
                            # Only track the first active beacon found
                            break
            
            if not active_beacon_found:
                print("  No active CRAB beacons found in recent logs")
                
                # Check for expired but recent beacon sessions that might still be worth tracking
                self.check_for_expired_but_recent_beacons()
            else:
                print(f"✅ Auto-started CRAB beacon tracking successfully")
                
        except Exception as e:
            print(f"Error scanning for active CRAB beacons: {e}")
    
    def find_beacon_start_timestamp(self, completion_timestamp, source_file):
        """Find the start timestamp for a beacon that was completed"""
        try:
            # Look for the start message in the same source file
            # We'll look for messages within a reasonable time window (e.g., 2 hours before completion)
            start_window = completion_timestamp - timedelta(hours=2)
            
            for timestamp, line, file_name in self.all_log_entries:
                if file_name == source_file and timestamp and timestamp >= start_window:
                    concord_message_type = self.detect_concord_message(line)
                    if concord_message_type == "link_start":
                        return timestamp
            
            return None
            
        except Exception as e:
            print(f"Error finding beacon start timestamp: {e}")
            return None
    
    def find_beacon_end_timestamp(self, start_timestamp, source_file):
        """Find the end timestamp for a beacon that was started"""
        try:
            # Look for the completion message in the same source file
            # We'll look for messages within a reasonable time window (e.g., 2 hours after start)
            end_window = start_timestamp + timedelta(hours=2)
            
            # FIRST: Look for link_complete message (if it exists)
            for timestamp, line, file_name in self.all_log_entries:
                if file_name == source_file and timestamp and timestamp >= start_timestamp and timestamp <= end_window:
                    concord_message_type = self.detect_concord_message(line)
                    if concord_message_type == "link_complete":
                        print(f"✅ Found link_complete message at {timestamp}")
                        return timestamp
            
            # SECOND: Since there's no link_complete message, look for last bounty message
            # This indicates when the active combat/bounty collection ended
            last_bounty_time = None
            for timestamp, line, file_name in self.all_log_entries:
                if file_name == source_file and timestamp and timestamp >= start_timestamp and timestamp <= end_window:
                    if "(bounty)" in line:
                        last_bounty_time = timestamp
                        print(f"🔍 Found bounty message at {timestamp}")
            
            # THIRD: Look for last combat message (indicates session activity ended)
            last_combat_time = None
            for timestamp, line, file_name in self.all_log_entries:
                if file_name == source_file and timestamp and timestamp >= start_timestamp and timestamp <= end_window:
                    if "(combat)" in line:
                        last_combat_time = timestamp
                        print(f"🔍 Found combat message at {timestamp}")
            
            # Return the latest of bounty or combat, or None if neither found
            if last_bounty_time and last_combat_time:
                end_time = max(last_bounty_time, last_combat_time)
                print(f"✅ Using latest activity time as beacon end: {end_time}")
                return end_time
            elif last_bounty_time:
                print(f"✅ Using last bounty time as beacon end: {last_bounty_time}")
                return last_bounty_time
            elif last_combat_time:
                print(f"✅ Using last combat time as beacon end: {last_combat_time}")
                return last_combat_time
            
            print(f"⚠️ No activity indicators found for beacon end time")
            return None
            
        except Exception as e:
            print(f"Error finding beacon end timestamp: {e}")
            return None
    
    def check_for_expired_but_recent_beacons(self):
        """Check for beacon sessions that have expired but are still recent enough to track"""
        try:
            current_time = self.get_utc_now()
            
            # Look for beacon start messages that are between 1-5 minutes old
            # These might be expired but still recent enough to be worth tracking
            for timestamp, line, source_file in self.all_log_entries:
                if not timestamp:
                    continue
                
                concord_message_type = self.detect_concord_message(line)
                if concord_message_type == "link_start":
                    time_since_start = current_time - timestamp
                    time_since_start_minutes = time_since_start.total_seconds() / 60
                    
                    # Check if beacon is between 1-5 minutes old (expired but recent)
                    if 1.0 < time_since_start_minutes <= 5.0:
                        print(f"⏰ Found expired but recent beacon ({time_since_start_minutes:.1f} minutes old) - offering to track")
                        
                        # Ask user if they want to track this expired beacon
                        result = messagebox.askyesno(
                            "Expired Beacon Detected", 
                            f"A CONCORD beacon was started {time_since_start_minutes:.1f} minutes ago.\n\n"
                            f"This beacon has expired (60-minute limit), but you can still track it\n"
                            f"for bounty and session data collection.\n\n"
                            f"Would you like to start tracking this beacon session?"
                        )
                        
                        if result:
                            print(f"✅ User chose to track expired beacon - starting tracking")
                            
                            # Validate that the beacon timestamp is not in the future
                            current_time = self.get_utc_now()
                            beacon_timestamp = timestamp
                            if beacon_timestamp > current_time:
                                print(f"⚠️ Warning: Expired beacon timestamp {beacon_timestamp} is in the future, using current UTC time instead")
                                beacon_timestamp = current_time
                            
                            # Set up expired beacon tracking
                            self.concord_link_start = beacon_timestamp
                            self.concord_status_var.set("Status: Expired (Tracking)")
                            self.concord_countdown_active = False  # Don't start countdown for expired beacon
                            self.concord_link_completed = False
                            
                            # Generate unique Beacon ID
                            self.current_beacon_id = self.generate_beacon_id(source_file, timestamp)
                            self.beacon_source_file = source_file
                            
                            # Start CRAB bounty tracking session
                            self.start_crab_session()
                            
                            # Update displays
                            self.update_concord_display()
                            self.update_bounty_display()
                            
                            print(f"🔗 Started tracking expired beacon - ID: {self.current_beacon_id}")
                            print(f"📁 Source file: {self.beacon_source_file}")
                            print(f"⏰ Started {time_since_start_minutes:.1f} minutes ago (expired)")
                            
                            # Only offer one expired beacon
                            break
                        else:
                            print(f"❌ User declined to track expired beacon")
                            break
            
        except Exception as e:
            print(f"Error checking for expired beacons: {e}")
    
    def scan_for_active_crab_beacons_on_startup(self):
        """Scan for active CRAB beacons when the app first starts up"""
        try:
            print("🚀 Starting up - scanning for active CRAB beacons...")
            
            # Wait a moment for the UI to fully initialize
            self.root.after(1000, self.perform_startup_crab_scan)
            
        except Exception as e:
            print(f"Error setting up startup CRAB scan: {e}")
    
    def perform_startup_crab_scan(self):
        """Perform the actual startup scan for active CRAB beacons"""
        try:
            print("🔍 Performing startup CRAB beacon scan...")
            self.status_var.set("🔍 Scanning for active CRAB beacons...")
            self.root.update()
            
            # Check if we have log entries loaded
            if not hasattr(self, 'all_log_entries') or not self.all_log_entries:
                print("  No log entries loaded yet - skipping startup scan")
                self.status_var.set("⚠️ No log entries loaded - skipping startup scan")
                return
            
            # Perform the scan
            self.scan_for_active_crab_beacons()
            
            # Update status to show scan completed
            if self.concord_countdown_active:
                print("✅ Startup scan completed - active CRAB beacon detected and tracking started")
                self.status_var.set("✅ Startup scan completed - Active CRAB beacon detected and tracking started!")
                
                # Update the status with beacon information
                if self.current_beacon_id:
                    short_id = self.current_beacon_id[-12:]  # Last 12 characters
                    self.status_var.set(f"✅ Active CRAB beacon detected! Beacon ID: ...{short_id}")
            else:
                print("✅ Startup scan completed - no active CRAB beacons found")
                self.status_var.set("✅ Startup scan completed - No active CRAB beacons found")
                
                # Set to ready status
                self.root.after(2000, lambda: self.status_var.set(f"v{APP_VERSION} | Ready - Monitoring recent log files only"))
            
        except Exception as e:
            print(f"Error during startup CRAB scan: {e}")
            self.status_var.set(f"❌ Startup scan error: {str(e)}")
    
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
            # Use timezone-aware min datetime to match our UTC timestamps
            utc_min = datetime.min.replace(tzinfo=timezone.utc)
            recent_files.sort(key=lambda x: self.parse_filename_timestamp(x.name)[0] or utc_min, reverse=True)
            
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
                                    
                                    # Also track in CRAB if session is active
                                    if self.crab_session_active:
                                        self.add_crab_bounty_entry(timestamp, bounty_amount, source_file)
                                else:
                                    print(f"🔄 Skipping duplicate bounty: {bounty_amount:,} ISK from {source_file}")
                            
                            # Check for CONCORD link messages
                            concord_message_type = self.detect_concord_message(line)
                            if concord_message_type == "link_start":
                                # Use the actual timestamp from the log line, not current time
                                beacon_timestamp = timestamp if timestamp else self.get_utc_now()
                                
                                # Validate that the beacon timestamp is not in the future
                                current_time = self.get_utc_now()
                                if beacon_timestamp > current_time:
                                    print(f"⚠️ Warning: Beacon timestamp {beacon_timestamp} is in the future, using current time instead")
                                    beacon_timestamp = current_time
                                
                                self.concord_link_start = beacon_timestamp
                                
                                # Debug logging for beacon start
                                if self.logger:
                                    self.logger.info(f"CONCORD beacon start detected")
                                    self.logger.info(f"Log line timestamp: {timestamp}")
                                    self.logger.info(f"Beacon timestamp set to: {beacon_timestamp}")
                                    self.logger.info(f"Current time: {current_time}")
                                
                                self.concord_status_var.set("Status: Linking")
                                self.concord_countdown_active = True
                                
                                # Generate unique Beacon ID
                                self.current_beacon_id = self.generate_beacon_id(source_file, beacon_timestamp)
                                self.beacon_source_file = source_file
                                
                                self.start_concord_countdown()
                                # Start CRAB bounty tracking session
                                self.start_crab_session()
                                
                                print(f"🔗 CONCORD Beacon started - ID: {self.current_beacon_id}")
                                print(f"📁 Source file: {self.beacon_source_file}")
                                print(f"⏰ Beacon start time: {beacon_timestamp}")
                                print(f"⏰ Current time: {current_time}")
                                
                            elif concord_message_type == "link_complete":
                                self.concord_link_completed = True
                                self.concord_status_var.set("Status: Active")
                                # Don't stop the countdown - let it continue to show total elapsed time
                                # self.concord_countdown_active = False
                                # self.stop_concord_countdown = True
                                self.concord_time_var.set(f"Link Time: {self.concord_link_start.strftime('%H:%M:%S')} - {self.get_utc_now().strftime('%H:%M:%S')}")
                                self.update_concord_display()
                                # CRAB session status will be updated by update_concord_display()
                                
                                print(f"✅ CONCORD Beacon completed - ID: {self.current_beacon_id}")
                            
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
            # Use timezone-aware min datetime to match our UTC timestamps
            utc_min = datetime.min.replace(tzinfo=timezone.utc)
            self.all_log_entries.sort(key=lambda x: x[0] if x[0] else utc_min, reverse=True)
            
            # Display combined logs
            self.display_combined_logs()
            
            # Update last refresh time
            self.last_refresh_time = self.get_utc_now()
            
            # Show file info and refresh status
            file_info = []
            for log_file in recent_files:
                timestamp, char_id = self.parse_filename_timestamp(log_file.name)
                if timestamp:
                    file_info.append(f"{log_file.name} (UTC: {timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
                else:
                    file_info.append(log_file.name)
            
            status_text = f"v{APP_VERSION} | Monitoring {len(recent_files)} recent files with {total_lines} total log entries | Last refresh: {self.last_refresh_time.strftime('%H:%M:%S')}"
            if self.high_freq_var.get():
                status_text += " | High-freq: ON"
            else:
                status_text += " | High-freq: OFF"
            
            # Add bounty information to status
            if self.bounty_entries:
                status_text += f" | 💰 Bounties: {len(self.bounty_entries)} ({self.total_bounty_isk:,} ISK)"
            
            # Add CRAB bounty information to status
            if self.crab_session_active:
                status_text += f" | 🦀 CRAB: {len(self.crab_bounty_entries)} ({self.crab_total_bounty_isk:,} ISK)"
            
            # Add CONCORD information to status
            if self.concord_countdown_active and not self.concord_link_completed:
                status_text += " | 🔗 CONCORD: Linking"
            elif self.concord_link_completed:
                status_text += " | 🔗 CONCORD: Active"
            
            # Add Beacon ID to status if available
            if self.current_beacon_id:
                # Show shortened version for status bar
                short_id = self.current_beacon_id[-12:]  # Last 12 characters
                status_text += f" | 🆔 Beacon: ...{short_id}"
            
            self.status_var.set(status_text)
            
            # Update bounty display
            self.update_bounty_display()
            
            # Update CONCORD display
            self.update_concord_display()
            
            # Scan for any bounties that might have been missed
            self.scan_existing_bounties()
            
            # Scan for active CRAB beacons in existing logs
            self.scan_for_active_crab_beacons()
            
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
            current_time = self.get_utc_now()
            
            print(f"\n--- Checking for file changes at {current_time.strftime('%H:%M:%S')} ---")
            
            for pattern in self.log_patterns:
                for log_file in Path(self.eve_log_dir).glob(pattern):
                    file_path = str(log_file)
                    if os.path.exists(file_path) and self.is_recent_file(file_path):
                        # Get current file stats
                        current_size = os.path.getsize(file_path)
                        current_mtime = os.path.getmtime(file_path)
                        current_mtime_dt = datetime.fromtimestamp(current_mtime, tz=timezone.utc)
                        
                        # Calculate current content hash
                        current_hash = self.calculate_file_hash(file_path)
                        
                        # Get last known stats
                        last_size = self.last_file_sizes.get(file_path, 0)
                        last_mtime = self.last_file_sizes.get(f"{file_path}_mtime", 0)
                        last_hash = self.last_file_hashes.get(file_path, None)
                        last_mtime_dt = datetime.fromtimestamp(last_mtime, tz=timezone.utc) if last_mtime > 0 else None
                        
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
                                last_mtime_str = last_mtime_dt.strftime('%H:%M:%S') if last_mtime_dt else 'Never'
                                print(f"  MTime: {last_mtime_str} -> {current_mtime_dt.strftime('%H:%M:%S')}")
                                print(f"  Time since last check: {time_since_last_check:.1f} seconds")
                            if size_changed:
                                print(f"  Size: {last_size} -> {current_size} bytes")
                        else:
                            # Show files that haven't changed for debugging
                            if last_hash and last_mtime_dt:
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
            r'(\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2})',  # M/D/YYYY H:MM:SS (handles single digits)
            r'(\d{2}:\d{2}:\d{2})',  # HH:MM:SS
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                timestamp_str = match.group(1)
                try:
                    # Try to parse the timestamp
                    if len(timestamp_str) == 8:  # HH:MM:SS
                        # Add today's date and treat as UTC time (EVE logs are UTC)
                        today = self.get_utc_now().strftime("%Y-%m-%d")
                        timestamp_str = f"{today} {timestamp_str}"
                        # Parse as UTC timestamp
                        utc_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        # Make it timezone-aware UTC
                        return utc_timestamp.replace(tzinfo=timezone.utc)
                    
                    if len(timestamp_str) == 19:  # YYYY-MM-DD HH:MM:SS
                        # Parse as UTC timestamp (EVE Online standard)
                        utc_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        return utc_timestamp.replace(tzinfo=timezone.utc)
                    elif len(timestamp_str) == 19:  # MM/DD/YYYY HH:MM:SS
                        # Parse as UTC timestamp (EVE Online standard)
                        utc_timestamp = datetime.strptime(timestamp_str, "%m/%d/%Y %H:%M:%S")
                        return utc_timestamp.replace(tzinfo=timezone.utc)
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
    
    def generate_beacon_id(self, source_file, beacon_timestamp):
        """Generate unique Beacon ID from file timestamp and beacon activation time"""
        try:
            # Parse filename to extract timestamp and character ID
            # Format: YYYYMMDD_HHMMSS_CharacterID.txt
            filename = os.path.basename(source_file)
            if not filename.endswith('.txt'):
                return None
            
            # Extract parts from filename
            parts = filename.replace('.txt', '').split('_')
            if len(parts) != 3:
                return None
            
            file_date = parts[0]  # YYYYMMDD
            file_time = parts[1]  # HHMMSS
            character_id = parts[2]  # Character ID
            
            # Format beacon timestamp
            beacon_date = beacon_timestamp.strftime('%Y%m%d')
            beacon_time = beacon_timestamp.strftime('%H%M%S')
            
            # Combine: FileTimestamp + CharacterID + BeaconTimestamp
            beacon_id = f"{file_date}{file_time}{character_id}{beacon_date}{beacon_time}"
            
            print(f"🔗 Generated Beacon ID: {beacon_id}")
            return beacon_id
            
        except Exception as e:
            print(f"Error generating Beacon ID: {e}")
            return None
    
    def detect_concord_message(self, line):
        """Detect CONCORD Rogue Analysis Beacon messages"""
        # Updated patterns based on actual EVE Online log messages
        # Pattern for link start message - more flexible matching
        link_start_pattern = r'\[CONCORD\].*Rogue Analysis Beacon.*link.*established'
        
        # Pattern for link completion message - more flexible matching
        link_complete_pattern = r'\[CONCORD\].*Rogue Analysis Beacon.*link.*completed'
        
        # Also check for alternative patterns that might exist
        alt_link_start_pattern = r'Your ship has started the link process with CONCORD Rogue Analysis Beacon'
        alt_link_complete_pattern = r'Your ship successfully completed the link process with CONCORD Rogue Analysis Beacon'
        
        if re.search(link_start_pattern, line, re.IGNORECASE) or re.search(alt_link_start_pattern, line, re.IGNORECASE):
            print("🔗 CONCORD link process started detected")
            return "link_start"
        elif re.search(link_complete_pattern, line, re.IGNORECASE) or re.search(alt_link_complete_pattern, line, re.IGNORECASE):
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
        start_time = self.get_utc_now()
        target_time = start_time + timedelta(minutes=60)
        
        while not self.stop_concord_countdown:
            current_time = self.get_utc_now()
            
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
        
        # Update Beacon ID display
        if self.current_beacon_id:
            self.beacon_id_var.set(f"Beacon ID: {self.current_beacon_id}")
        else:
            self.beacon_id_var.set("Beacon ID: None")
        
        # Update CRAB session status to match CONCORD status
        self.update_crab_session_status()
    
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
        self.current_beacon_id = None
        self.beacon_source_file = None
        
        # Reset CRAB tracking
        self.reset_crab_bounty_tracking()
        
        # Update display
        self.update_concord_display()
        print("🔄 CONCORD tracking reset")
    
    def test_concord_link_start(self):
        """Test function to simulate CONCORD link start message"""
        print("🧪 Testing CONCORD link start...")
        beacon_timestamp = self.get_utc_now()
        
        # Validate that the beacon timestamp is not in the future
        current_time = self.get_utc_now()
        if beacon_timestamp > current_time:
            print(f"⚠️ Warning: Test beacon timestamp {beacon_timestamp} is in the future, using current time instead")
            beacon_timestamp = current_time
        
        self.concord_link_start = beacon_timestamp
        self.concord_status_var.set("Status: Linking")
        self.concord_countdown_active = True
        
        # Generate test Beacon ID
        self.current_beacon_id = f"TEST{beacon_timestamp.strftime('%Y%m%d%H%M%S')}"
        self.beacon_source_file = "TEST_FILE.txt"
        
        self.start_concord_countdown()
        self.concord_time_var.set(f"Link Time: Started at {self.concord_link_start.strftime('%H:%M:%S')}")
        # Update displays to sync CRAB session status
        self.update_concord_display()
    
    def test_concord_link_complete(self):
        """Test function to simulate CONCORD link completion message"""
        print("🧪 Testing CONCORD link completion...")
        if self.concord_link_start:
            self.concord_link_completed = True
            self.concord_status_var.set("Status: Active")
            # Don't stop the countdown - let it continue to show elapsed time
            # self.concord_countdown_active = False
            # self.stop_concord_countdown = True
            completion_time = self.get_utc_now()
            self.concord_time_var.set(f"Link Time: {self.concord_link_start.strftime('%H:%M:%S')} - {completion_time.strftime('%H:%M:%S')}")
            self.update_concord_display()
            # CRAB session status will be updated by update_concord_display()
        else:
            messagebox.showwarning("Test Warning", "No link process started. Start a link first.")
    
    def end_crab_failed(self):
        """End CRAB session as failed - clear countdown and mark as failed"""
        if not self.concord_link_start:
            messagebox.showwarning("End CRAB Failed", "No CRAB session is currently running.")
            return
        
        # Ask for confirmation
        result = messagebox.askyesno(
            "End CRAB Session - Failed", 
            "Are you sure you want to end the CRAB session as failed?\n\n"
            "This will stop the countdown and mark the session as failed.\n\n"
            "This action cannot be undone."
        )
        
        if result:
            # Stop the countdown
            self.stop_concord_countdown = True
            if self.concord_countdown_thread and self.concord_countdown_thread.is_alive():
                self.concord_countdown_thread.join(timeout=1)
            
            # Mark as completed but failed
            self.concord_link_completed = True
            self.concord_status_var.set("Status: Failed")
            self.concord_countdown_var.set("Countdown: --:--")
            completion_time = self.get_utc_now()
            self.concord_time_var.set(f"Link Time: {self.concord_link_start.strftime('%H:%M:%S')} - {completion_time.strftime('%H:%M:%S')}")
            
            # End CRAB session
            self.end_crab_session()
            
            # Update display
            self.update_concord_display()
            print("❌ CRAB session ended as failed")
    
    def end_crab_submit(self):
        """End CRAB session and submit data from clipboard - clear countdown and mark as completed"""
        if not self.concord_link_start:
            messagebox.showwarning("End CRAB Submit", "No CRAB session is currently running.")
            return
        
        # Ask for confirmation
        result = messagebox.askyesno(
            "End CRAB Session - Submit Data", 
            "Are you sure you want to end the CRAB session and submit data?\n\n"
            "This will:\n"
            "• Copy data from your clipboard\n"
            "• Parse loot information\n"
            "• End the current beacon session\n"
            "• Save session data to CSV\n"
            "• Reset for new beacon\n\n"
            "This action cannot be undone."
        )
        
        if result:
            try:
                # Get clipboard data
                clipboard_data = self.root.clipboard_get()
                print(f"📋 Clipboard data retrieved: {len(clipboard_data)} characters")
                
                # Parse loot data from clipboard
                loot_data = self.parse_clipboard_loot(clipboard_data)
                
                # Validate that we still have a valid beacon start time
                if not self.concord_link_start:
                    messagebox.showerror("Error", "Beacon start time has been lost. Please restart the beacon session.")
                    return
                
                # Try to find the actual beacon end time from log files
                beacon_end_time = self.find_beacon_end_timestamp(self.concord_link_start, self.beacon_source_file)
                if not beacon_end_time:
                    # Fall back to current time if we can't find the actual end time
                    beacon_end_time = self.get_utc_now()
                    print(f"⚠️ Could not find actual beacon end time in logs, using current UTC time: {beacon_end_time}")
                    print(f"💡 Tip: If you know when the beacon actually ended, you can manually set the end time")
                    
                    # Ask user if they want to manually set the end time
                    result = messagebox.askyesno(
                        "Beacon End Time Not Found", 
                        f"Could not automatically determine when the beacon ended.\n\n"
                        f"Beacon start: {self.concord_link_start.strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                        f"Current time: {beacon_end_time.strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
                        f"Would you like to manually specify when the beacon ended?\n"
                        f"(This will give you more accurate duration calculations)"
                    )
                    
                    if result:
                        # For now, just show a message - TODO: implement time picker
                        messagebox.showinfo(
                            "Manual End Time", 
                            "Manual end time setting will be implemented in a future update.\n\n"
                            "For now, the system will use the current time as the beacon end time."
                        )
                else:
                    print(f"✅ Found actual beacon end time in logs: {beacon_end_time}")
                
                # Debug logging for time calculation
                if self.logger:
                    self.logger.info(f"Beacon end time: {beacon_end_time}")
                    self.logger.info(f"Beacon start time: {self.concord_link_start}")
                
                # Additional debug info for timing issues
                print(f"🔍 Debug: Beacon start time: {self.concord_link_start} (UTC)")
                print(f"🔍 Debug: Beacon end time: {beacon_end_time} (UTC)")
                print(f"🔍 Debug: Current UTC time: {self.get_utc_now()} (UTC)")
                print(f"🔍 Debug: Timezone info - Start: {self.concord_link_start.tzinfo}, End: {beacon_end_time.tzinfo}")
                
                total_beacon_time = beacon_end_time - self.concord_link_start
                total_beacon_time_str = str(total_beacon_time).split('.')[0]  # Remove microseconds
                
                # Debug logging for duration
                if self.logger:
                    self.logger.info(f"Calculated duration: {total_beacon_time_str}")
                
                print(f"🔍 Debug: Calculated duration: {total_beacon_time_str}")
                
                # Prepare session data for CSV
                session_data = {
                    'beacon_id': self.current_beacon_id or 'UNKNOWN',
                    'beacon_start': self.concord_link_start.strftime('%Y-%m-%d %H:%M:%S'),
                    'beacon_end': beacon_end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_time': total_beacon_time_str,
                    'total_crab_bounty': f"{self.crab_total_bounty_isk:,}",
                    'rogue_drone_data_amount': loot_data.get('rogue_drone_data', 0),
                    'rogue_drone_data_value': f"{loot_data.get('rogue_drone_data_value', 0):,}",
                    'total_loot_value': f"{loot_data.get('total_value', 0):,}",
                    'loot_details': loot_data.get('all_loot', ''),
                    'source_file': self.beacon_source_file or 'UNKNOWN'
                }
                
                # Save session data to CSV
                csv_saved = self.save_beacon_session_to_csv(session_data)
                
                # Submit to Google Form (if configured)
                if self.logger:
                    self.logger.info("Calling Google Form submission")
                else:
                    print("🌐 Starting Google Form submission...")
                    print(f"📊 Session data keys: {list(session_data.keys())}")
                    print(f"📁 Current working directory: {os.getcwd()}")
                    print(f"📁 Config file exists: {os.path.exists('google_form_config.json')}")
                
                form_submitted = self.submit_to_google_form(session_data)
                
                if self.logger:
                    self.logger.info(f"Google Form submission result: {form_submitted}")
                else:
                    print(f"🌐 Google Form submission result: {form_submitted}")
                
                # Stop the countdown
                self.stop_concord_countdown = True
                if self.concord_countdown_thread and self.concord_countdown_thread.is_alive():
                    self.concord_countdown_thread.join(timeout=1)
                
                # Mark as completed successfully
                self.concord_link_completed = True
                self.concord_status_var.set("Status: Completed")
                self.concord_countdown_var.set("Countdown: --:--")
                self.concord_time_var.set(f"Link Time: {self.concord_link_start.strftime('%H:%M:%S')} - {beacon_end_time.strftime('%H:%M:%S')}")
                
                # Reset beacon tracking for new session
                self.reset_concord_tracking()
                
                # Update display
                self.update_concord_display()
                
                # Show success message
                if csv_saved:
                    form_status = "✅ Submitted to Google Form" if form_submitted else "⚠️ Google Form not configured"
                    messagebox.showinfo(
                        "Beacon Session Completed", 
                        f"✅ CRAB session completed successfully!\n\n"
                        f"📊 Session Data:\n"
                        f"• Beacon ID: {session_data['beacon_id']}\n"
                        f"• Total Time: {total_beacon_time_str}\n"
                        f"• CRAB Bounty: {session_data['total_crab_bounty']} ISK\n"
                        f"• Rogue Drone Data: {session_data['rogue_drone_data_amount']} units\n"
                        f"• Total Loot Value: {session_data['total_loot_value']} ISK\n\n"
                        f"📁 Data saved to: beacon_sessions.csv\n"
                        f"🌐 {form_status}\n\n"
                        f"🔄 Beacon tracking reset for new session."
                    )
                else:
                    messagebox.showwarning(
                        "Beacon Session Completed", 
                        f"✅ CRAB session completed successfully!\n\n"
                        f"⚠️ Warning: Failed to save session data to CSV.\n"
                        f"Check the console for error details.\n\n"
                        f"🔄 Beacon tracking reset for new session."
                    )
                
                print(f"✅ CRAB session completed and data submitted successfully")
                print(f"📊 Session Summary:")
                print(f"   • Beacon ID: {session_data['beacon_id']}")
                print(f"   • Total Time: {total_beacon_time_str}")
                print(f"   • CRAB Bounty: {session_data['total_crab_bounty']} ISK")
                print(f"   • Rogue Drone Data: {session_data['rogue_drone_data_amount']} units")
                print(f"   • Total Loot Value: {session_data['total_loot_value']} ISK")
                
            except Exception as e:
                print(f"❌ Error during beacon session submission: {e}")
                messagebox.showerror(
                    "Submission Error", 
                    f"An error occurred while submitting beacon data:\n\n{str(e)}\n\n"
                    f"Check the console for details."
                )
    
    def parse_clipboard_loot(self, clipboard_text):
        """Parse loot data from clipboard text"""
        loot_data = {
            'rogue_drone_data': 0,
            'rogue_drone_data_value': 0,
            'total_value': 0,
            'all_loot': []
        }
        
        try:
            print(f" Raw clipboard data: {repr(clipboard_text)}")  # Debug: show raw data
            
            lines = clipboard_text.strip().split('\n')
            print(f" Clipboard has {len(lines)} lines")
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                print(f" Processing line {i+1}: {repr(line)}")
                
                # More flexible parsing - handle different spacing patterns
                # First try the original 4-space split
                parts = [part.strip() for part in line.split('        ') if part.strip()]
                
                # If that doesn't work, try splitting by multiple spaces
                if len(parts) < 5:
                    parts = [part.strip() for part in line.split('  ') if part.strip()]
                
                # If still not enough parts, try single space split and filter empty
                if len(parts) < 5:
                    parts = [part.strip() for part in line.split(' ') if part.strip()]
                
                print(f"🔍 Line {i+1} parsed into {len(parts)} parts: {parts}")
                
                if len(parts) >= 5:
                    item_name = parts[0]
                    amount_str = parts[1]
                    category = parts[2]
                    volume = parts[3]
                    value_str = parts[4]
                    
                    # Parse amount (remove any non-numeric characters)
                    try:
                        amount = int(amount_str.replace(',', ''))
                    except ValueError:
                        amount = 1
                    
                    # Parse value (remove "ISK" and spaces, convert to float)
                    try:
                        value_str_clean = value_str.replace('ISK', '').replace(' ', '').replace(',', '.')
                        value = float(value_str_clean)
                    except ValueError:
                        value = 0
                    
                    # Check if this is Rogue Drone Infestation Data
                    if "Rogue Drone Infestation Data" in item_name:
                        loot_data['rogue_drone_data'] = amount
                        loot_data['rogue_drone_data_value'] = value
                        print(f"🔍 Found Rogue Drone Infestation Data: {amount} units = {value:,.2f} ISK")
                    
                    # Add to total value
                    loot_data['total_value'] += value
                    
                    # Store loot details
                    loot_data['all_loot'].append({
                        'name': item_name,
                        'amount': amount,
                        'category': category,
                        'volume': volume,
                        'value': value
                    })
                    
                    print(f" Loot parsed: {item_name} x{amount} = {value:,.2f} ISK")
                else:
                    print(f"⚠️ Line {i+1} has insufficient parts ({len(parts)} < 5): {parts}")
            
            print(f"💰 Total loot value: {loot_data['total_value']:,.2f} ISK")
            print(f"🔍 Rogue Drone Data: {loot_data['rogue_drone_data']} units = {loot_data['rogue_drone_data_value']:,.2f} ISK")
            
        except Exception as e:
            print(f"❌ Error parsing clipboard loot: {e}")
            # Return default values if parsing fails
            loot_data['all_loot'] = [{'name': 'PARSE_ERROR', 'amount': 0, 'category': 'ERROR', 'volume': 'ERROR', 'value': 0}]
        
        return loot_data
    
    def save_beacon_session_to_csv(self, session_data):
        """Save beacon session data to CSV file"""
        try:
            csv_filename = "beacon_sessions.csv"
            file_exists = os.path.exists(csv_filename)
            
            with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                import csv
                writer = csv.writer(csvfile)
                
                # Write header if file is new
                if not file_exists:
                    header = [
                        'Beacon ID',
                        'Beacon Start',
                        'Beacon End', 
                        'Total Time',
                        'Total CRAB Bounty (ISK)',
                        'Rogue Drone Data Amount',
                        'Rogue Drone Data Value (ISK)',
                        'Total Loot Value (ISK)',
                        'Loot Details',
                        'Source File',
                        'Export Date'
                    ]
                    writer.writerow(header)
                
                # Write session data
                # Use current time with fallback for timestamp
                try:
                    export_time = self.get_utc_now().strftime('%Y-%m-%d %H:%M:%S')
                except AttributeError:
                    from datetime import datetime, timezone
                    export_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                
                row = [
                    session_data['beacon_id'],
                    session_data['beacon_start'],
                    session_data['beacon_end'],
                    session_data['total_time'],
                    session_data['total_crab_bounty'],
                    session_data['rogue_drone_data_amount'],
                    session_data['rogue_drone_data_value'],
                    session_data['total_loot_value'],
                    session_data['loot_details'],
                    session_data['source_file'],
                    export_time
                ]
                writer.writerow(row)
            
            print(f"💾 Beacon session data saved to {csv_filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving beacon session to CSV: {e}")
            return False
    
    def add_bounty_entry(self, timestamp, isk_amount, source_file):
        """Add a new bounty entry to the tracking system"""
        if self.bounty_session_start is None:
            self.bounty_session_start = self.get_utc_now()
        
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
        self.bounty_session_start = self.get_utc_now()
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
            current_time = self.get_utc_now()
            
            for pattern in self.log_patterns:
                for log_file in Path(self.eve_log_dir).glob(pattern):
                    if os.path.exists(log_file) and self.is_recent_file(log_file):
                        file_path = str(log_file)
                        mtime = os.path.getmtime(file_path)
                        mtime_dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
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
            current_time = self.get_utc_now()
            time_since_refresh = current_time - self.last_refresh_time
            minutes = int(time_since_refresh.total_seconds() // 60)
            seconds = int(time_since_refresh.total_seconds() % 60)
            
            # Get file modification info
            file_info = self.get_file_modification_info()
            if file_info:
                newest_file = file_info[0]
                newest_time = newest_file[1]
                newest_ago = newest_file[2]
                
                status_text = f"v{APP_VERSION} | Last refresh: {self.last_refresh_time.strftime('%H:%M:%S')} | Last check: {current_time.strftime('%H:%M:%S')} | Newest file: {newest_file[0]} ({newest_ago})"
            else:
                status_text = f"v{APP_VERSION} | Last refresh: {self.last_refresh_time.strftime('%H:%M:%S')} | Last check: {current_time.strftime('%H:%M:%S')}"
            
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
            
            current_time = self.get_utc_now()
            
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
            
            current_time = self.get_utc_now()
            
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
            now = self.get_utc_now()
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
        self.last_refresh_time = self.get_utc_now()
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
                    f.write(f"EVE Online Recent Logs - Exported on {self.get_utc_now().strftime('%Y-%m-%d %H:%M:%S')}\n")
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
                session_duration = self.get_utc_now() - self.bounty_session_start
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
                session_duration = self.get_utc_now() - self.bounty_session_start
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
                    f.write(f"EVE Online Bounty Tracking - Exported on {self.get_utc_now().strftime('%Y-%m-%d %H:%M:%S')}\n")
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
    
    # CRAB Bounty Tracking Functions
    def add_crab_bounty_entry(self, timestamp, isk_amount, source_file):
        """Add a new bounty entry to the CRAB tracking system"""
        if not self.crab_session_active:
            print("⚠️ CRAB session not active - bounty not tracked")
            return
        
        bounty_entry = {
            'timestamp': timestamp,
            'isk_amount': isk_amount,
            'source_file': source_file,
            'running_total': self.crab_total_bounty_isk + isk_amount
        }
        
        self.crab_bounty_entries.append(bounty_entry)
        self.crab_total_bounty_isk += isk_amount
        
        print(f"🦀 CRAB bounty tracked: {isk_amount:,} ISK (CRAB Total: {self.crab_total_bounty_isk:,} ISK)")
        self.update_crab_bounty_display()
    
    def reset_crab_bounty_tracking(self):
        """Reset CRAB bounty tracking to start fresh"""
        if self.crab_bounty_entries:
            # Ask for confirmation
            result = messagebox.askyesno(
                "Reset CRAB Bounty Tracking", 
                f"Are you sure you want to reset CRAB bounty tracking?\n\n"
                f"This will clear {len(self.crab_bounty_entries)} CRAB bounty entries "
                f"and {self.crab_total_bounty_isk:,} ISK in tracked earnings.\n\n"
                f"This action cannot be undone."
            )
            
            if not result:
                return
        
        self.crab_bounty_entries = []
        self.crab_total_bounty_isk = 0
        self.update_crab_bounty_display()
        print("🔄 CRAB bounty tracking reset")
    
    def show_crab_bounty_details(self):
        """Show detailed CRAB bounty information in a popup window"""
        try:
            if not self.crab_bounty_entries:
                messagebox.showinfo("CRAB Bounty Details", "No CRAB bounties tracked yet.")
                return
            
            # Create popup window
            popup = tk.Toplevel(self.root)
            popup.title("🦀 CRAB Bounty Details")
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
            text_widget.insert(tk.END, "🦀 CRAB Bounty Tracking Details\n")
            text_widget.insert(tk.END, "=" * 80 + "\n\n")
            
            # Session info
            if self.concord_link_start:
                text_widget.insert(tk.END, f"CRAB Session Started: {self.concord_link_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
                if self.concord_link_completed:
                    completion_time = self.get_utc_now()
                    session_duration = completion_time - self.concord_link_start
                    hours = int(session_duration.total_seconds() // 3600)
                    minutes = int((session_duration.total_seconds() % 3600) // 60)
                    text_widget.insert(tk.END, f"CRAB Session Duration: {hours}h {minutes}m\n")
                else:
                    text_widget.insert(tk.END, "CRAB Session Status: Active\n")
                
                text_widget.insert(tk.END, f"Total CRAB Bounties: {len(self.crab_bounty_entries)}\n")
                text_widget.insert(tk.END, f"Total CRAB ISK Earned: {self.crab_total_bounty_isk:,} ISK\n")
                
                if self.crab_bounty_entries:
                    # Calculate ISK per hour if session completed
                    if self.concord_link_completed:
                        session_duration = completion_time - self.concord_link_start
                        if session_duration.total_seconds() > 0:
                            isk_per_hour = (self.crab_total_bounty_isk / session_duration.total_seconds()) * 3600
                            text_widget.insert(tk.END, f"CRAB ISK per Hour: {isk_per_hour:,.0f} ISK/h\n")
                
                text_widget.insert(tk.END, "\n" + "=" * 80 + "\n\n")
            
            # Individual bounty entries
            text_widget.insert(tk.END, "Individual CRAB Bounty Entries (Newest First):\n")
            text_widget.insert(tk.END, "-" * 80 + "\n\n")
            
            # Sort entries by timestamp (newest first)
            sorted_entries = sorted(self.crab_bounty_entries, key=lambda x: x['timestamp'], reverse=True)
            
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
            text_widget.insert(tk.END, f"\n📊 CRAB Summary:\n")
            text_widget.insert(tk.END, f"Total CRAB Bounties: {len(self.crab_bounty_entries)}\n")
            text_widget.insert(tk.END, f"Total CRAB ISK: {self.crab_total_bounty_isk:,} ISK\n")
            
            if self.crab_bounty_entries:
                avg_bounty = self.crab_total_bounty_isk / len(self.crab_bounty_entries)
                text_widget.insert(tk.END, f"Average CRAB Bounty: {avg_bounty:,.0f} ISK\n")
                
                # Largest and smallest bounties
                largest = max(self.crab_bounty_entries, key=lambda x: x['isk_amount'])
                smallest = min(self.crab_bounty_entries, key=lambda x: x['isk_amount'])
                text_widget.insert(tk.END, f"Largest CRAB Bounty: {largest['isk_amount']:,} ISK\n")
                text_widget.insert(tk.END, f"Smallest CRAB Bounty: {smallest['isk_amount']:,} ISK\n")
            
            # Make text read-only
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error showing CRAB bounty details: {str(e)}")
    
    def update_crab_bounty_display(self):
        """Update the CRAB bounty display labels with current information"""
        try:
            # Update total ISK
            self.crab_bounty_total_var.set(f"CRAB Total ISK: {self.crab_total_bounty_isk:,} ISK")
            
            # Update bounty count
            self.crab_bounty_count_var.set(f"CRAB Bounties: {len(self.crab_bounty_entries)}")
            
            # Update session info
            if self.crab_session_active:
                self.crab_session_var.set("CRAB Session: Active")
            else:
                self.crab_session_var.set("CRAB Session: Inactive")
                
        except Exception as e:
            print(f"Error updating CRAB bounty display: {e}")
    
    def add_test_crab_bounty(self):
        """Test function to add a CRAB bounty for testing"""
        if not self.crab_session_active:
            messagebox.showwarning("CRAB Session Required", "CRAB session must be active to add bounties.\n\nStart a CONCORD link first.")
            return
        
        # Create a test bounty entry
        test_timestamp = self.get_utc_now()
        test_isk = 50000  # 50k ISK test bounty
        
        self.add_crab_bounty_entry(test_timestamp, test_isk, "TEST_CRAB_BOUNTY")
        print(f"🧪 Test CRAB bounty added: {test_isk:,} ISK")
    
    def start_crab_session(self):
        """Start a CRAB bounty tracking session"""
        self.crab_session_active = True
        self.update_crab_bounty_display()
        print("🦀 CRAB bounty tracking session started")
    
    def end_crab_session(self):
        """End the CRAB bounty tracking session"""
        self.crab_session_active = False
        self.update_crab_bounty_display()
        print("🦀 CRAB bounty tracking session ended")
    
    def copy_beacon_id(self):
        """Copy current Beacon ID to clipboard"""
        if self.current_beacon_id:
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(self.current_beacon_id)
                print(f"📋 Beacon ID copied to clipboard: {self.current_beacon_id}")
                messagebox.showinfo("Beacon ID Copied", f"Beacon ID copied to clipboard:\n{self.current_beacon_id}")
            except Exception as e:
                print(f"Error copying Beacon ID: {e}")
                messagebox.showerror("Error", f"Failed to copy Beacon ID: {str(e)}")
        else:
            messagebox.showwarning("No Beacon ID", "No active Beacon ID to copy.")
    
    def update_crab_session_status(self):
        """Update CRAB session status to match CONCORD status"""
        if self.concord_link_start:
            if self.concord_link_completed:
                # Check if this was manually ended with a specific status
                current_status = self.concord_status_var.get()
                if "Failed" in current_status:
                    # Keep the Failed status
                    self.crab_session_active = False
                    self.crab_session_var.set("CRAB Session: Failed")
                elif "Completed" in current_status:
                    # Keep the Completed status  
                    self.crab_session_active = False
                    self.crab_session_var.set("CRAB Session: Completed")
                else:
                    # CONCORD is Active, so CRAB should also be Active
                    self.crab_session_active = True
                    self.crab_session_var.set("CRAB Session: Active")
            else:
                # CONCORD is Linking, so CRAB should also be Linking
                self.crab_session_active = True
                self.crab_session_var.set("CRAB Session: Linking")
        else:
            # No CONCORD link, CRAB is inactive
            self.crab_session_active = False
            self.crab_session_var.set("CRAB Session: Inactive")
    
    def view_beacon_sessions(self):
        """View all beacon session data from CSV file"""
        try:
            csv_filename = "beacon_sessions.csv"
            
            if not os.path.exists(csv_filename):
                messagebox.showinfo("No Sessions", "No beacon sessions have been recorded yet.\n\nComplete a beacon session using the 'Submit Data' button to create the first entry.")
                return
            
            # Read CSV data
            sessions = []
            with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    sessions.append(row)
            
            if not sessions:
                messagebox.showinfo("No Sessions", "No beacon sessions found in the CSV file.")
                return
            
            # Create a new window to display the data
            sessions_window = tk.Toplevel(self.root)
            sessions_window.title(f"Beacon Sessions History - v{APP_VERSION}")
            sessions_window.geometry("1200x600")
            sessions_window.configure(bg="#2b2b2b")
            
            # Create a frame for the data
            main_frame = ttk.Frame(sessions_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Title label
            title_label = ttk.Label(main_frame, text=f"📊 Beacon Sessions History - {len(sessions)} Sessions", 
                                   font=("Segoe UI", 14, "bold"))
            title_label.pack(pady=(0, 10))
            
            # Create text widget with scrollbar
            text_frame = ttk.Frame(main_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            text_widget = tk.Text(text_frame, wrap=tk.NONE, 
                                 bg="#1e1e1e", fg="#ffffff",
                                 font=("Consolas", 9))
            
            # Add horizontal and vertical scrollbars
            v_scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            h_scrollbar = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
            text_widget.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Grid layout for text widget and scrollbars
            text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
            
            text_frame.columnconfigure(0, weight=1)
            text_frame.rowconfigure(0, weight=1)
            
            # Display header
            header = "Beacon ID | Start Time | End Time | Duration | CRAB Bounty | Rogue Data | Loot Value | Source File\n"
            text_widget.insert(tk.END, header)
            text_widget.insert(tk.END, "-" * 120 + "\n")
            
            # Display each session
            for i, session in enumerate(sessions, 1):
                # Format the data for display
                beacon_id = session.get('Beacon ID', 'UNKNOWN')
                start_time = session.get('Beacon Start', 'UNKNOWN')
                end_time = session.get('Beacon End', 'UNKNOWN')
                duration = session.get('Total Time', 'UNKNOWN')
                crab_bounty = session.get('Total CRAB Bounty (ISK)', '0')
                rogue_data = session.get('Rogue Drone Data Amount', '0')
                loot_value = session.get('Total Loot Value (ISK)', '0')
                source_file = session.get('Source File', 'UNKNOWN')
                
                # Shorten long values for display
                if len(beacon_id) > 20:
                    beacon_id = "..." + beacon_id[-17:]
                if len(source_file) > 25:
                    source_file = "..." + source_file[-22:]
                
                # Format the line
                line = f"{beacon_id:<20} | {start_time:<19} | {end_time:<19} | {duration:<8} | {crab_bounty:<11} | {rogue_data:<10} | {loot_value:<10} | {source_file}\n"
                text_widget.insert(tk.END, line)
            
            # Add summary at the bottom
            text_widget.insert(tk.END, "\n" + "=" * 120 + "\n")
            text_widget.insert(tk.END, "📈 SESSION SUMMARY\n")
            text_widget.insert(tk.END, "=" * 120 + "\n")
            
            # Calculate totals
            total_crab_bounty = sum(float(s.get('Total CRAB Bounty (ISK)', '0').replace(',', '')) for s in sessions)
            total_rogue_data = sum(int(s.get('Rogue Drone Data Amount', '0')) for s in sessions)
            total_loot_value = sum(float(s.get('Total Loot Value (ISK)', '0').replace(',', '')) for s in sessions)
            
            text_widget.insert(tk.END, f"Total Sessions: {len(sessions)}\n")
            text_widget.insert(tk.END, f"Total CRAB Bounty: {total_crab_bounty:,.0f} ISK\n")
            text_widget.insert(tk.END, f"Total Rogue Drone Data: {total_rogue_data:,} units\n")
            text_widget.insert(tk.END, f"Total Loot Value: {total_loot_value:,.0f} ISK\n")
            
            # Make text read-only
            text_widget.config(state=tk.DISABLED)
            
            # Add export button
            export_btn = tk.Button(main_frame, text="Export to Text File", 
                                  command=lambda: self.export_beacon_sessions_to_text(sessions),
                                  bg="#1e1e1e", fg="#ffffff",
                                  activebackground="#404040",
                                  activeforeground="#ffffff",
                                  relief="raised", borderwidth=1,
                                  font=("Segoe UI", 9))
            export_btn.pack(pady=(10, 0))
            
            print(f"📊 Beacon sessions history displayed: {len(sessions)} sessions")
            
        except Exception as e:
            print(f"❌ Error viewing beacon sessions: {e}")
            messagebox.showerror("Error", f"Error viewing beacon sessions:\n\n{str(e)}")
    
    def export_beacon_sessions_to_text(self, sessions):
        """Export beacon sessions to a text file"""
        try:
            # Get save file path
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Beacon Sessions"
            )
            
            if not file_path:
                return
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"EVE Online Beacon Sessions - Exported on {self.get_utc_now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, session in enumerate(sessions, 1):
                    f.write(f"SESSION {i}\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Beacon ID: {session.get('Beacon ID', 'UNKNOWN')}\n")
                    f.write(f"Start Time: {session.get('Beacon Start', 'UNKNOWN')}\n")
                    f.write(f"End Time: {session.get('Beacon End', 'UNKNOWN')}\n")
                    f.write(f"Duration: {session.get('Total Time', 'UNKNOWN')}\n")
                    f.write(f"CRAB Bounty: {session.get('Total CRAB Bounty (ISK)', '0')} ISK\n")
                    f.write(f"Rogue Drone Data: {session.get('Rogue Drone Data Amount', '0')} units\n")
                    f.write(f"Rogue Drone Value: {session.get('Rogue Drone Data Value (ISK)', '0')} ISK\n")
                    f.write(f"Total Loot Value: {session.get('Total Loot Value (ISK)', '0')} ISK\n")
                    f.write(f"Source File: {session.get('Source File', 'UNKNOWN')}\n")
                    f.write(f"Loot Details: {session.get('Loot Details', 'N/A')}\n")
                    f.write(f"Export Date: {session.get('Export Date', 'UNKNOWN')}\n\n")
                
                # Add summary
                total_crab_bounty = sum(float(s.get('Total CRAB Bounty (ISK)', '0').replace(',', '')) for s in sessions)
                total_rogue_data = sum(int(s.get('Rogue Drone Data Amount', '0')) for s in sessions)
                total_loot_value = sum(float(s.get('Total Loot Value (ISK)', '0').replace(',', '')) for s in sessions)
                
                f.write("SUMMARY\n")
                f.write("-" * 40 + "\n")
                f.write(f"Total Sessions: {len(sessions)}\n")
                f.write(f"Total CRAB Bounty: {total_crab_bounty:,.0f} ISK\n")
                f.write(f"Total Rogue Drone Data: {total_rogue_data:,} units\n")
                f.write(f"Total Loot Value: {total_loot_value:,.0f} ISK\n")
            
            messagebox.showinfo("Export Complete", f"Beacon sessions exported successfully to:\n{file_path}")
            print(f"💾 Beacon sessions exported to: {file_path}")
            
        except Exception as e:
            print(f"❌ Error exporting beacon sessions: {e}")
            messagebox.showerror("Export Error", f"Error exporting beacon sessions:\n\n{str(e)}")

    def submit_to_google_form(self, session_data):
        """Submit beacon session data to Google Form"""
        try:
            if self.logger:
                self.logger.info("Starting Google Form submission process")
                self.logger.debug(f"Session data received: {session_data}")
            else:
                print("🌐 Starting Google Form submission process")
                print(f"📊 Session data received: {session_data}")
                print(f"📁 Current working directory: {os.getcwd()}")
                print(f"📁 Config file path: {os.path.abspath('google_form_config.json')}")
            
            # Load Google Form configuration
            # Use absolute path to ensure we find the config file regardless of working directory
            config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "google_form_config.json")
            if self.logger:
                self.logger.debug(f"Looking for config file at: {config_file}")
            else:
                print(f"🔍 Looking for config file at: {config_file}")
            
            if not os.path.exists(config_file):
                if self.logger:
                    self.logger.warning("Google Form configuration not found - skipping form submission")
                else:
                    print("⚠️ Google Form configuration not found - skipping form submission")
                    print(f"📁 Files in current directory: {os.listdir('.')}")
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                import json
                config = json.load(f)
            
            form_url = config.get('form_url')
            field_mappings = config.get('field_mappings', {})
            
            if self.logger:
                self.logger.info(f"Loaded config - URL: {form_url}, Fields: {len(field_mappings)}")
            
            if not form_url or "YOUR_FORM_ID" in form_url:
                if self.logger:
                    self.logger.warning("Google Form URL not configured - skipping form submission")
                else:
                    print("⚠️ Google Form URL not configured - skipping form submission")
                return False
            
            if not field_mappings:
                if self.logger:
                    self.logger.warning("Google Form field mappings not configured - skipping form submission")
                else:
                    print("⚠️ Google Form field mappings not configured - skipping form submission")
                return False
            
            # Map session data to form fields
            form_fields = {}
            
            # Define mapping from Google Form field names to session data keys
            field_to_data_mapping = {
                "Beacon ID": "beacon_id",
                "Total Duration": "total_time", 
                "Total CRAB Bounty": "total_crab_bounty",
                "Rogue Drone Data Amount": "rogue_drone_data_amount",
                "Loot Details": "loot_details"  # This was correct, but let's verify the session data key
            }
            
            if self.logger:
                self.logger.debug(f"Field mapping: {field_to_data_mapping}")
                self.logger.debug(f"Available session data keys: {list(session_data.keys())}")
            
            for field_name, entry_id in field_mappings.items():
                # Get the corresponding session data key
                data_key = field_to_data_mapping.get(field_name)
                if data_key and data_key in session_data:
                    # Special handling for Loot Details - format as readable text
                    if field_name == "Loot Details":
                        loot_value = session_data[data_key]
                        if isinstance(loot_value, list) and loot_value:
                            # Format loot list as readable text
                            loot_text = []
                            for item in loot_value:
                                if isinstance(item, dict) and all(key in item for key in ['name', 'amount', 'category', 'volume', 'value']):
                                    loot_text.append(f"{item['name']} x{item['amount']} ({item['category']}) - {item['volume']} = {item['value']:,.2f} ISK")
                                else:
                                    loot_text.append(str(item))
                            form_fields[entry_id] = "\n".join(loot_text) if loot_text else "No loot data"
                        elif isinstance(loot_value, str) and loot_value.strip():
                            form_fields[entry_id] = loot_value
                        else:
                            form_fields[entry_id] = "No loot data"
                    else:
                        form_fields[entry_id] = session_data[data_key]
                    
                    if self.logger:
                        self.logger.debug(f"Mapped '{field_name}' -> '{data_key}' -> '{entry_id}': {form_fields[entry_id]}")
                else:
                    if self.logger:
                        self.logger.warning(f"Field '{field_name}' not found in session data (key: {data_key})")
                    else:
                        print(f"⚠️ Field '{field_name}' not found in session data (key: {data_key})")
            
            if not form_fields:
                if self.logger:
                    self.logger.warning("No valid field mappings found - skipping form submission")
                else:
                    print("⚠️ No valid field mappings found - skipping form submission")
                return False
            
            if self.logger:
                self.logger.info(f"Submitting to Google Form: {form_url}")
                self.logger.info(f"Form data prepared: {form_fields}")
                self.logger.info(f"Session data for debugging: {session_data}")
            else:
                print(f"🌐 Submitting to Google Form: {form_url}")
                print(f"📊 Form data: {form_fields}")
                print(f"📋 Session data keys available: {list(session_data.keys())}")
                print(f"🔍 Session data for debugging: {session_data}")
                print(f"🔗 Field mappings: {field_mappings}")
                print(f"🔗 Data mapping: {field_to_data_mapping}")
            
            # Submit the form
            response = requests.post(form_url, data=form_fields, timeout=30)
            
            if self.logger:
                self.logger.info(f"Form submission response: HTTP {response.status_code}")
                self.logger.debug(f"Response content: {response.text[:500]}...")  # First 500 chars
            
            if response.status_code == 200:
                if self.logger:
                    self.logger.info("✅ Data submitted to Google Form successfully!")
                else:
                    print("✅ Data submitted to Google Form successfully!")
                    print(f"📡 Response length: {len(response.text)} characters")
                return True
            else:
                if self.logger:
                    self.logger.error(f"❌ Form submission failed: HTTP {response.status_code}")
                    self.logger.error(f"Response content: {response.text}")
                else:
                    print(f"❌ Form submission failed: HTTP {response.status_code}")
                    print(f"📡 Response content: {response.text[:200]}...")
                return False
                
        except FileNotFoundError:
            if self.logger:
                self.logger.error("Google Form configuration file not found - skipping form submission")
            else:
                print("⚠️ Google Form configuration file not found - skipping form submission")
            return False
        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.error(f"Error reading Google Form configuration: {e}")
            else:
                print(f"❌ Error reading Google Form configuration: {e}")
            return False
        except requests.exceptions.Timeout:
            if self.logger:
                self.logger.error("Google Form submission timed out")
            else:
                print("❌ Google Form submission timed out")
            return False
        except requests.exceptions.RequestException as e:
            if self.logger:
                self.logger.error(f"Network error submitting to Google Form: {e}")
            else:
                print(f"❌ Network error submitting to Google Form: {e}")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"Unexpected error submitting to Google Form: {e}", exc_info=True)
            else:
                print(f"❌ Error submitting to Google Form: {e}")
            return False

    def get_google_form_status(self):
        """Get current Google Form submission status"""
        try:
            config_file = "google_form_config.json"
            if not os.path.exists(config_file):
                return "Not Configured"
            
            with open(config_file, 'r', encoding='utf-8') as f:
                import json
                config = json.load(f)
            
            form_url = config.get('form_url', '')
            field_mappings = config.get('field_mappings', {})
            
            if "YOUR_FORM_ID" in form_url or not form_url:
                return "URL Not Set"
            elif not field_mappings:
                return "Fields Not Mapped"
            else:
                return f"Configured ({len(field_mappings)} fields)"
                
        except Exception as e:
            print(f"Error checking Google Form status: {e}")
            return "Error"
    
    def update_google_form_status_display(self):
        """Update the Google Form status display in the UI"""
        try:
            status = self.get_google_form_status()
            self.google_form_status_var.set(f"Form Status: {status}")
        except Exception as e:
            print(f"Error updating Google Form status display: {e}")
            self.google_form_status_var.set("Form Status: Error")

    def configure_google_form(self):
        """Configure Google Form URL and field mappings"""
        try:
            # Create configuration window
            config_window = tk.Toplevel(self.root)
            config_window.title(f"Google Form Configuration - v{APP_VERSION}")
            config_window.geometry("600x500")
            config_window.configure(bg="#2b2b2b")
            config_window.resizable(False, False)
            
            # Make window modal
            config_window.transient(self.root)
            config_window.grab_set()
            
            # Main frame
            main_frame = ttk.Frame(config_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Title
            title_label = ttk.Label(main_frame, text="🌐 Google Form Configuration", 
                                   font=("Segoe UI", 14, "bold"))
            title_label.pack(pady=(0, 20))
            
            # Instructions
            instructions = """To configure Google Form submission:

1. Create a Google Form with the required fields
2. Get the form submission URL
3. Get the entry IDs for each field
4. Enter the information below

The form will automatically submit beacon session data after each completion."""
            
            instructions_label = ttk.Label(main_frame, text=instructions, 
                                         font=("Segoe UI", 9), justify=tk.LEFT)
            instructions_label.pack(pady=(0, 20))
            
            # Form URL input
            url_frame = ttk.Frame(main_frame)
            url_frame.pack(fill=tk.X, pady=(0, 10))
            
            url_label = ttk.Label(url_frame, text="Form Submission URL:")
            url_label.pack(anchor=tk.W)
            
            url_entry = tk.Entry(url_frame, width=70, font=("Consolas", 9))
            url_entry.pack(fill=tk.X, pady=(5, 0))
            
            # Load existing configuration if available
            default_url = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/formResponse"
            default_field_mappings = {
                "Beacon ID": "entry.123456789",
                "Beacon Start": "entry.234567890",
                "Beacon End": "entry.345678901",
                "Total Time": "entry.456789012",
                "CRAB Bounty": "entry.567890123",
                "Rogue Data Amount": "entry.678901234",
                "Rogue Data Value": "entry.789012345",
                "Total Loot Value": "entry.890123456",
                "Loot Details": "entry.901234567",
                "Source File": "entry.012345678",
                "Export Date": "entry.123456789"
            }
            
            # Try to load existing configuration
            try:
                if os.path.exists("google_form_config.json"):
                    with open("google_form_config.json", 'r', encoding='utf-8') as f:
                        import json
                        config = json.load(f)
                        if config.get('form_url') and "YOUR_FORM_ID" not in config.get('form_url', ''):
                            default_url = config.get('form_url')
                        if config.get('field_mappings'):
                            default_field_mappings.update(config.get('field_mappings'))
            except Exception as e:
                print(f"⚠️ Could not load existing configuration: {e}")
            
            url_entry.insert(0, default_url)
            
            # Field mappings frame
            mappings_frame = ttk.LabelFrame(main_frame, text="Field Mappings", padding="10")
            mappings_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
            
            # Create field mapping entries
            field_mappings = {}
            fields = [
                ("Beacon ID", default_field_mappings.get("Beacon ID", "entry.123456789")),
                ("Beacon Start", default_field_mappings.get("Beacon Start", "entry.234567890")),
                ("Beacon End", default_field_mappings.get("Beacon End", "entry.345678901")),
                ("Total Time", default_field_mappings.get("Total Time", "entry.456789012")),
                ("CRAB Bounty", default_field_mappings.get("CRAB Bounty", "entry.567890123")),
                ("Rogue Data Amount", default_field_mappings.get("Rogue Data Amount", "entry.678901234")),
                ("Rogue Data Value", default_field_mappings.get("Rogue Data Value", "entry.789012345")),
                ("Total Loot Value", default_field_mappings.get("Total Loot Value", "entry.890123456")),
                ("Loot Details", default_field_mappings.get("Loot Details", "entry.901234567")),
                ("Source File", default_field_mappings.get("Source File", "entry.012345678")),
                ("Export Date", default_field_mappings.get("Export Date", "entry.123456789"))
            ]
            
            for i, (field_name, default_entry) in enumerate(fields):
                row_frame = ttk.Frame(mappings_frame)
                row_frame.pack(fill=tk.X, pady=2)
                
                field_label = ttk.Label(row_frame, text=f"{field_name}:", width=20, anchor=tk.W)
                field_label.grid(row=0, column=0, sticky=tk.W)
                
                entry_field = tk.Entry(row_frame, width=20, font=("Consolas", 9))
                entry_field.grid(row=0, column=1, padx=(10, 0))
                entry_field.insert(0, default_entry)
                
                field_mappings[field_name] = entry_field
            
            # Buttons frame
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=(20, 0))
            
            # Test submission button
            test_btn = tk.Button(button_frame, text="Test Form Submission", 
                                command=lambda: self.test_google_form_submission(url_entry.get(), field_mappings),
                                bg="#1e1e1e", fg="#ffffff",
                                activebackground="#404040",
                                activeforeground="#ffffff",
                                relief="raised", borderwidth=1,
                                font=("Segoe UI", 9))
            test_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # Save configuration button
            save_btn = tk.Button(button_frame, text="Save Configuration", 
                                command=lambda: self.save_google_form_config(url_entry.get(), field_mappings, config_window),
                                bg="#44ff44", fg="#000000",
                                activebackground="#22cc22",
                                activeforeground="#000000",
                                relief="raised", borderwidth=1,
                                font=("Segoe UI", 9, "bold"))
            save_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # Cancel button
            cancel_btn = tk.Button(button_frame, text="Cancel", 
                                  command=config_window.destroy,
                                  bg="#ff4444", fg="#ffffff",
                                  activebackground="#cc2222",
                                  activeforeground="#ffffff",
                                  relief="raised", borderwidth=1,
                                  font=("Segoe UI", 9))
            cancel_btn.pack(side=tk.LEFT)
            
            print("🔧 Google Form configuration window opened")
            
        except Exception as e:
            print(f"❌ Error opening Google Form configuration: {e}")
            messagebox.showerror("Error", f"Error opening configuration window:\n\n{str(e)}")

    def test_google_form_submission(self, form_url, field_mappings):
        """Test Google Form submission with sample data"""
        try:
            if "YOUR_FORM_ID" in form_url:
                messagebox.showwarning("Invalid URL", "Please enter a valid Google Form submission URL first.")
                return
            
            # Create sample session data for testing
            sample_data = {
                'beacon_id': 'TEST_BEACON_123',
                'beacon_start': '2025-01-01 12:00:00',
                'beacon_end': '2025-01-01 12:30:00',
                'total_time': '0:30:00',
                'total_crab_bounty': '1,000,000',
                'rogue_drone_data_amount': '100',
                'rogue_drone_data_value': '10,000,000',
                'total_loot_value': '15,000,000',
                'loot_details': 'Test loot data',
                'source_file': 'test_file.txt',
                'export_date': self.get_utc_now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Map to form fields
            form_fields = {}
            for field_name, entry_widget in field_mappings.items():
                entry_id = entry_widget.get().strip()
                if entry_id and entry_id != "entry.123456789":  # Skip default placeholder
                    form_fields[entry_id] = sample_data.get(field_name.lower().replace(' ', '_'), '')
            
            if not form_fields:
                messagebox.showwarning("No Fields", "Please configure at least one field mapping.")
                return
            
            print(f"🧪 Testing Google Form submission to: {form_url}")
            print(f"📊 Test data: {form_fields}")
            
            # Submit test data
            response = requests.post(form_url, data=form_fields, timeout=30)
            
            if response.status_code == 200:
                messagebox.showinfo("Test Successful", 
                                  f"✅ Test submission successful!\n\n"
                                  f"Form URL: {form_url}\n"
                                  f"Fields: {len(form_fields)}\n"
                                  f"Response: HTTP {response.status_code}\n\n"
                                  f"Check your Google Form to see the test entry.")
                print("✅ Test submission successful!")
            else:
                messagebox.showwarning("Test Failed", 
                                     f"⚠️ Test submission failed:\n\n"
                                     f"HTTP Status: {response.status_code}\n"
                                     f"Response: {response.text[:200]}...\n\n"
                                     f"Check your form URL and field mappings.")
                print(f"❌ Test submission failed: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            messagebox.showerror("Test Failed", "Test submission timed out. Check your internet connection.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Test Failed", f"Network error during test:\n\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Test Failed", f"Error during test:\n\n{str(e)}")

    def save_google_form_config(self, form_url, field_mappings, config_window):
        """Save Google Form configuration"""
        try:
            # Validate form URL
            if "YOUR_FORM_ID" in form_url:
                messagebox.showwarning("Invalid URL", "Please enter a valid Google Form submission URL.")
                return
            
            # Collect field mappings
            config_data = {
                'form_url': form_url,
                'field_mappings': {}
            }
            
            for field_name, entry_widget in field_mappings.items():
                entry_id = entry_widget.get().strip()
                if entry_id and entry_id != "entry.123456789":  # Skip default placeholder
                    config_data['field_mappings'][field_name] = entry_id
            
            if not config_data['field_mappings']:
                messagebox.showwarning("No Fields", "Please configure at least one field mapping.")
                return
            
            # Save to configuration file
            config_file = "google_form_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Google Form configuration saved to: {config_file}")
            print(f"📊 Configuration: {config_data}")
            
            messagebox.showinfo("Configuration Saved", 
                              f"✅ Google Form configuration saved successfully!\n\n"
                              f"Form URL: {form_url}\n"
                              f"Fields: {len(config_data['field_mappings'])}\n\n"
                              f"Future beacon sessions will automatically submit to this form.")
            
            # Close configuration window
            config_window.destroy()
            
            # Update the status display
            self.update_google_form_status_display()
            
        except Exception as e:
            print(f"❌ Error saving Google Form configuration: {e}")
            messagebox.showerror("Save Error", f"Error saving configuration:\n\n{str(e)}")

    def show_version_info(self):
        """Show version information in a popup window"""
        version_info = f"""EVE Online Log Reader v{APP_VERSION}

Features:
• Real-time EVE log monitoring
• Bounty tracking and statistics
• CONCORD Rogue Analysis Beacon tracking
• CRAB bounty session management
• Google Form integration
• Dark theme UI
• High-frequency monitoring
• Content hash change detection

Built with Python and Tkinter
For EVE Online players and ISK hunters

© 2025 - EVE Log Reader Project"""
        
        messagebox.showinfo("Version Information", version_info)

def main():
    root = tk.Tk()
    app = EVELogReader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
