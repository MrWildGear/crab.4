"""
Main window GUI for CRAB Tracker application.

This module provides the main user interface for the application,
including log display, controls, and status information.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime
from typing import List, Optional
import os
import hashlib

from ..core.log_parser import LogParser, LogEntry
from ..core.bounty_tracker import BountyTracker
from ..core.beacon_tracker import BeaconTracker
from ..core.file_monitor import FileMonitor, FileChangeEvent
from ..services.google_forms import GoogleFormsService
from ..services.logging_service import LoggingService
from ..utils.eve_paths import find_eve_log_directory
from ..utils.time_utils import format_duration


class MainWindow:
    """Main application window for CRAB Tracker."""
    
    def __init__(self, root):
        """Initialize the main window."""
        self.root = root
        self.root.title("CRAB Tracker - EVE Online Log Reader")
        self.root.geometry("1200x800")
        
        # Initialize services
        self.logging_service = LoggingService()
        self.logging_service.setup_logging()
        
        # Initialize other services after logging is set up
        self.log_parser = LogParser()
        self.bounty_tracker = BountyTracker()
        self.beacon_tracker = BeaconTracker()
        self.file_monitor = FileMonitor()
        self.google_forms_service = GoogleFormsService()
        
        # State variables
        self.monitoring_var = tk.BooleanVar(value=True)  # Auto-monitor enabled by default
        self.high_freq_var = tk.BooleanVar(value=True)   # High-frequency monitoring enabled by default
        self.monitoring_active = False
        self.monitoring_thread = None
        self.stop_monitoring_flag = False
        
        # File tracking for change detection
        self.last_file_sizes = {}
        self.last_file_hashes = {}
        
        # Display variables
        self.all_log_entries = []
        self.last_refresh_time = datetime.now()
        self.last_check_time = datetime.now()  # Track when we last checked for changes
        
        # Setup UI
        self.setup_ui()
        self.setup_file_monitoring()
        
        # Load initial log files
        self.load_log_files()
        
        # Start auto-monitoring automatically since it's enabled by default
        if self.monitoring_var.get():
            self.start_auto_monitoring()
        
        self.apply_dark_theme()
        
        # Start display update timer
        self.update_display_timer()
        
        # Force initial status update
        self.update_status_display()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Create main frames
        self.create_control_panel()
        self.create_log_display()
        self.create_status_panel()
        self.create_bounty_panel()
        self.create_beacon_panel()
    
    def create_control_panel(self):
        """Create the control panel at the top."""
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Log directory selection
        ttk.Label(control_frame, text="Log Directory:").grid(row=0, column=0, padx=5, pady=2)
        
        self.log_dir_var = tk.StringVar(value=find_eve_log_directory() or "")
        log_dir_entry = ttk.Entry(control_frame, textvariable=self.log_dir_var, width=50)
        log_dir_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Button(control_frame, text="Browse", command=self.browse_log_directory).grid(row=0, column=2, padx=5, pady=2)
        
        # Filter controls
        ttk.Label(control_frame, text="Max Days Old:").grid(row=1, column=0, padx=5, pady=2)
        
        self.max_days_var = tk.IntVar(value=1)
        days_spinbox = ttk.Spinbox(control_frame, from_=1, to=30, textvariable=self.max_days_var, width=10)
        days_spinbox.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(control_frame, text="Max Files:").grid(row=1, column=2, padx=5, pady=2)
        
        self.max_files_var = tk.IntVar(value=10)
        files_spinbox = ttk.Spinbox(control_frame, from_=5, to=50, textvariable=self.max_files_var, width=10)
        files_spinbox.grid(row=1, column=3, padx=5, pady=2, sticky="w")
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=5)
        
        ttk.Button(button_frame, text="Apply Filters", command=self.apply_filters).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_logs).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Clear Display", command=self.clear_display).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Export Logs", command=self.export_logs).grid(row=0, column=3, padx=5)
        
        # Test and debug buttons
        test_frame = ttk.LabelFrame(control_frame, text="Testing & Debug Tools")
        test_frame.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        ttk.Button(test_frame, text="Create Test Log", command=self.create_test_log, 
                  style="Info.TButton").grid(row=0, column=0, padx=2, pady=2)
        ttk.Button(test_frame, text="Add Test Bounty", command=self.add_test_bounty, 
                  style="Info.TButton").grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(test_frame, text="Parse Clipboard Loot", command=self.parse_clipboard_loot, 
                  style="Info.TButton").grid(row=0, column=2, padx=2, pady=2)
        
        # Monitoring controls
        ttk.Label(button_frame, text="Auto-monitor:").grid(row=0, column=4, padx=5, pady=2)
        ttk.Checkbutton(button_frame, text="", variable=self.monitoring_var, 
                       command=self.toggle_monitoring).grid(row=0, column=5, padx=5, pady=2)
        
        ttk.Label(button_frame, text="High-frequency:").grid(row=0, column=6, padx=5, pady=2)
        ttk.Checkbutton(button_frame, text="", variable=self.high_freq_var, 
                       command=self.toggle_high_frequency).grid(row=0, column=7, padx=5, pady=2)
    
    def create_log_display(self):
        """Create the main log display area."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # Log entries tab
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="Log Entries")
        
        # Log display
        log_display_frame = ttk.Frame(log_frame)
        log_display_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_display_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Text widget for logs
        self.log_text = tk.Text(log_display_frame, wrap="word", yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Configure text widget
        self.log_text.tag_configure("timestamp", foreground="#00ff00")
        self.log_text.tag_configure("source", foreground="#0088ff")
        self.log_text.tag_configure("bounty", foreground="#ffff00")
        self.log_text.tag_configure("beacon", foreground="#ff00ff")
    
    def create_status_panel(self):
        """Create the status panel on the left."""
        status_frame = ttk.LabelFrame(self.root, text="Status")
        status_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Monitoring status
        ttk.Label(status_frame, text="Monitoring:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.monitoring_status_label = ttk.Label(status_frame, text="Inactive")
        self.monitoring_status_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Last refresh
        ttk.Label(status_frame, text="Last Refresh:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.last_refresh_label = ttk.Label(status_frame, text="Never")
        self.last_refresh_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Last check
        ttk.Label(status_frame, text="Last Check:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.last_check_label = ttk.Label(status_frame, text="Never")
        self.last_check_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Files monitored
        ttk.Label(status_frame, text="Files Monitored:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.files_monitored_label = ttk.Label(status_frame, text="0")
        self.files_monitored_label.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        # Log entries count
        ttk.Label(status_frame, text="Log Entries:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.log_entries_label = ttk.Label(status_frame, text="0")
        self.log_entries_label.grid(row=4, column=1, sticky="w", padx=5, pady=2)
    
    def create_bounty_panel(self):
        """Create the bounty tracking panel."""
        bounty_frame = ttk.LabelFrame(self.root, text="Bounty Tracking")
        bounty_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Session controls
        ttk.Button(bounty_frame, text="Start Session", command=self.start_bounty_session).grid(row=0, column=0, padx=5, pady=2)
        ttk.Button(bounty_frame, text="End Session", command=self.end_bounty_session).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(bounty_frame, text="Start CRAB", command=self.start_crab_session).grid(row=0, column=2, padx=5, pady=2)
        ttk.Button(bounty_frame, text="End CRAB", command=self.end_crab_session).grid(row=0, column=3, padx=5, pady=2)
        
        # Bounty display
        ttk.Label(bounty_frame, text="Total Bounty:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.total_bounty_label = ttk.Label(bounty_frame, text="0 ISK")
        self.total_bounty_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(bounty_frame, text="CRAB Bounty:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.crab_bounty_label = ttk.Label(bounty_frame, text="0 ISK")
        self.crab_bounty_label.grid(row=1, column=3, sticky="w", padx=5, pady=2)
        
        ttk.Label(bounty_frame, text="Session Duration:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.session_duration_label = ttk.Label(bounty_frame, text="0s")
        self.session_duration_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
    
    def create_beacon_panel(self):
        """Create the beacon tracking panel."""
        beacon_frame = ttk.LabelFrame(self.root, text="CONCORD Rogue Analysis Beacon")
        beacon_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # CONCORD status display
        concord_frame = ttk.Frame(beacon_frame)
        concord_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        # Status and countdown in same row
        ttk.Label(concord_frame, text="Status:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.concord_status_var = tk.StringVar(value="Status: Inactive")
        self.concord_status_label = ttk.Label(concord_frame, textvariable=self.concord_status_var)
        self.concord_status_label.grid(row=0, column=1, sticky="w", padx=(0, 20))
        
        # Countdown timer with color
        self.concord_countdown_var = tk.StringVar(value="Countdown: --:--")
        self.concord_countdown_label = tk.Label(concord_frame, textvariable=self.concord_countdown_var,
                                              font=("Consolas", 10, "bold"), foreground="#ffff00",
                                              background="#2b2b2b", relief="flat")
        self.concord_countdown_label.grid(row=0, column=2, sticky="w", padx=(0, 20))
        
        # Link time display
        self.concord_time_var = tk.StringVar(value="Link Time: Not started")
        concord_time_label = ttk.Label(concord_frame, textvariable=self.concord_time_var)
        concord_time_label.grid(row=0, column=3, sticky="w", padx=(0, 20))
        
        # Beacon ID display
        self.beacon_id_var = tk.StringVar(value="Beacon ID: None")
        beacon_id_label = ttk.Label(concord_frame, textvariable=self.beacon_id_var,
                                   font=("Consolas", 8), foreground="#888888")
        beacon_id_label.grid(row=1, column=0, columnspan=4, sticky="w", padx=(0, 20), pady=(5, 0))
        
        # CONCORD control buttons
        control_frame = ttk.Frame(beacon_frame)
        control_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        ttk.Button(control_frame, text="Reset CONCORD Tracking", command=self.reset_concord_tracking).grid(row=0, column=0, padx=2)
        ttk.Button(control_frame, text="Copy Beacon ID", command=self.copy_beacon_id).grid(row=0, column=1, padx=2)
        ttk.Button(control_frame, text="View Beacon Sessions", command=self.view_beacon_sessions).grid(row=0, column=2, padx=2)
        
        # Test buttons for debugging
        test_frame = ttk.LabelFrame(beacon_frame, text="Debug Tools")
        test_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        ttk.Button(test_frame, text="Test Link Start", command=self.test_concord_link_start).grid(row=0, column=0, padx=2, pady=2)
        ttk.Button(test_frame, text="Test Link Complete", command=self.test_concord_link_complete).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(test_frame, text="Test CONCORD Detection", command=self.test_concord_detection, 
                  style="Info.TButton").grid(row=0, column=2, padx=2, pady=2)
        
        # CRAB session control buttons
        crab_frame = ttk.LabelFrame(beacon_frame, text="CRAB Session Controls")
        crab_frame.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        ttk.Button(crab_frame, text="End CRAB Failed", command=self.end_crab_failed, 
                  style="Danger.TButton").grid(row=0, column=0, padx=2, pady=2)
        ttk.Button(crab_frame, text="Submit Data", command=self.end_crab_submit, 
                  style="Success.TButton").grid(row=0, column=1, padx=2, pady=2)
        
        # Data export buttons
        export_frame = ttk.Frame(beacon_frame)
        export_frame.grid(row=4, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        ttk.Button(export_frame, text="Export Beacon Data", command=self.export_beacon_data).grid(row=0, column=0, padx=2)
        ttk.Button(export_frame, text="Update Loot from Clipboard", command=self.update_beacon_loot_from_clipboard, 
                  style="Info.TButton").grid(row=0, column=1, padx=2)
        ttk.Button(export_frame, text="Debug Session", command=self.show_session_debug_info, 
                  style="Info.TButton").grid(row=0, column=2, padx=2)
        ttk.Button(export_frame, text="Test Google Forms", command=self.test_google_forms, 
                  style="Info.TButton").grid(row=0, column=3, padx=2)
        
        # Set up countdown callback
        self.beacon_tracker.set_countdown_callback(self.update_concord_countdown)
        self.beacon_tracker.set_beacon_started_callback(self.on_beacon_started)
        self.beacon_tracker.set_beacon_reset_callback(self.on_beacon_reset)
    
    def show_session_debug_info(self):
        """Show debug information about the current session state."""
        try:
            active_session = self.beacon_tracker.get_active_session()
            if not active_session:
                messagebox.showinfo("Debug Info", "No active beacon session found.")
                return
            
            debug_info = f"Session Debug Information:\n"
            debug_info += f"Beacon ID: {active_session.beacon_id}\n"
            debug_info += f"Duration: {active_session.get_duration()}\n"
            debug_info += f"Rogue Drone Data: {active_session.rogue_drone_data} units\n"
            debug_info += f"Loot Details Count: {len(active_session.loot_details)}\n"
            
            if active_session.loot_details:
                debug_info += f"\nLoot Details:\n"
                for i, loot in enumerate(active_session.loot_details, 1):
                    debug_info += f"{i}. {loot}\n"
            else:
                debug_info += f"\nLoot Details: None"
            
            # Check clipboard
            try:
                clipboard_text = self.root.clipboard_get()
                if clipboard_text and clipboard_text.strip():
                    debug_info += f"\n\nClipboard Content (first 100 chars):\n{clipboard_text[:100]}..."
                else:
                    debug_info += f"\n\nClipboard: Empty or whitespace only"
            except tk.TclError:
                debug_info += f"\n\nClipboard: Access error"
            
            messagebox.showinfo("Session Debug Info", debug_info)
            
        except Exception as e:
            messagebox.showerror("Debug Error", f"Error getting debug info: {e}")
    
    def apply_dark_theme(self):
        """Apply dark theme to the application."""
        style = ttk.Style()
        
        # Define dark theme colors
        bg_color = "#2b2b2b"
        fg_color = "#ffffff"
        entry_bg = "#404040"
        button_bg = "#505050"
        button_active = "#606060"
        select_bg = "#404040"
        field_bg = "#353535"
        highlight_bg = "#555555"  # Better highlight color
        border_color = "#666666"  # Subtle border color
        
        # Use default theme and override with custom styles
        try:
            style.theme_use('default')  # Use simple default theme
        except:
            pass
        
        # Configure ttk widgets
        style.configure("TFrame", background=bg_color, borderwidth=0)
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TLabelframe", background=bg_color, foreground=fg_color, borderwidth=1)
        style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color)
        
        # Configure buttons with more explicit styling
        style.configure("TButton", 
                       background=button_bg, 
                       foreground=fg_color,
                       borderwidth=1,
                       focuscolor="none",
                       relief="flat",
                       bordercolor=border_color)
        style.map("TButton",
                 background=[('active', button_active), ('pressed', select_bg)],
                 foreground=[('active', fg_color), ('pressed', fg_color)],
                 bordercolor=[('active', highlight_bg), ('pressed', highlight_bg)])
        
        # Configure special button styles
        style.configure("Danger.TButton", 
                       background="#8B0000",  # Dark red
                       foreground=fg_color,
                       borderwidth=1,
                       focuscolor="none",
                       relief="flat",
                       bordercolor="#FF0000")
        style.map("Danger.TButton",
                 background=[('active', "#A00000"), ('pressed', "#600000")],
                 foreground=[('active', fg_color), ('pressed', fg_color)],
                 bordercolor=[('active', "#FF4444"), ('pressed', "#CC0000")])
        
        style.configure("Success.TButton", 
                       background="#006400",  # Dark green
                       foreground=fg_color,
                       borderwidth=1,
                       focuscolor="none",
                       relief="flat",
                       bordercolor="#00FF00")
        style.map("Success.TButton",
                 background=[('active', "#008000"), ('pressed', "#004000")],
                 foreground=[('active', fg_color), ('pressed', fg_color)],
                 bordercolor=[('active', "#44FF44"), ('pressed', "#00CC00")])
        
        # Configure Info button style
        style.configure("Info.TButton", 
                       background="#0066CC",  # Dark blue
                       foreground=fg_color,
                       borderwidth=1,
                       focuscolor="none",
                       relief="flat",
                       bordercolor="#3399FF")
        style.map("Info.TButton",
                 background=[('active', "#0077DD"), ('pressed', "#0055AA")],
                 foreground=[('active', fg_color), ('pressed', fg_color)],
                 bordercolor=[('active', "#55AAFF"), ('pressed', "#2277CC")])
        
        # Configure entry widgets - simplified approach
        style.configure("TEntry", 
                       fieldbackground=field_bg,
                       foreground=fg_color,
                       insertcolor=fg_color)
        style.map("TEntry",
                 fieldbackground=[('focus', entry_bg)],
                 foreground=[('focus', fg_color)])
        
        # Configure spinbox - simplified approach
        style.configure("TSpinbox", 
                       fieldbackground=field_bg,
                       foreground=fg_color,
                       insertcolor=fg_color,
                       arrowcolor=fg_color)
        style.map("TSpinbox",
                 fieldbackground=[('focus', entry_bg)],
                 foreground=[('focus', fg_color)])
        
        # Configure checkbuttons
        style.configure("TCheckbutton", 
                       background=bg_color, 
                       foreground=fg_color,
                       focuscolor="none",
                       borderwidth=0)
        style.map("TCheckbutton",
                 background=[('active', bg_color)])
        
        # Configure notebook
        style.configure("TNotebook", background=bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", 
                       background=button_bg, 
                       foreground=fg_color,
                       padding=[10, 2])
        style.map("TNotebook.Tab",
                 background=[('selected', entry_bg), ('active', button_active)])
        
        # Configure main window
        self.root.configure(bg=bg_color)
        
        # Configure text widget
        self.log_text.configure(
            bg="#1e1e1e",
            fg=fg_color,
            insertbackground=fg_color,
            selectbackground=select_bg,
            selectforeground=fg_color,
            borderwidth=0,
            highlightthickness=0
        )
        
        # Configure scrollbar styling for better dark theme
        try:
            # Style the scrollbar to match dark theme
            style.configure("Vertical.TScrollbar", 
                           background=button_bg,
                           troughcolor=bg_color,
                           borderwidth=0,
                           arrowcolor=fg_color,
                           darkcolor=button_bg,
                           lightcolor=button_bg)
            style.map("Vertical.TScrollbar",
                     background=[('active', button_active), ('pressed', select_bg)])
        except:
            pass
        
        # Force refresh of all widgets to ensure theme is applied
        self.root.update_idletasks()
        
        # Apply manual styling to specific widgets that might not respond to ttk styling
        self.apply_manual_widget_styling(field_bg, fg_color)
    
    def apply_manual_widget_styling(self, field_bg, fg_color):
        """Apply manual styling to widgets that don't respond to ttk theming."""
        style = ttk.Style()
        
        # Force style configuration with element options
        try:
            # Configure the actual visual elements of ttk widgets
            style.element_create("Custom.Entry.field", "from", "clam",
                                map={"fieldbackground": [("active", field_bg), ("focus", field_bg), ("!focus", field_bg)]})
            
            style.layout("Custom.TEntry", [
                ("Custom.Entry.field", {"sticky": "nswe", "border": 1, "children": [
                    ("Entry.padding", {"sticky": "nswe", "children": [
                        ("Entry.textarea", {"sticky": "nswe"})
                    ]})
                ]})
            ])
            
            style.configure("Custom.TEntry", 
                           fieldbackground=field_bg,
                           foreground=fg_color,
                           insertcolor=fg_color)
            
            # Apply custom style to entry widgets
            def configure_widget(widget):
                try:
                    widget_class = widget.winfo_class()
                    if widget_class == 'TEntry':
                        widget.configure(style="Custom.TEntry")
                    elif widget_class == 'TSpinbox':
                        # For spinbox, try direct style override
                        style.configure("Custom.TSpinbox", 
                                       fieldbackground=field_bg,
                                       foreground=fg_color,
                                       insertcolor=fg_color)
                        widget.configure(style="Custom.TSpinbox")
                except Exception as e:
                    print(f"Failed to configure widget {widget}: {e}")
            
            def traverse_widgets(parent):
                try:
                    for child in parent.winfo_children():
                        configure_widget(child)
                        traverse_widgets(child)
                except:
                    pass
            
            # Apply to all widgets in the application
            traverse_widgets(self.root)
            
        except Exception as e:
            print(f"Failed to create custom styles: {e}")
        
        # Force update
        self.root.update()
    
    def setup_file_monitoring(self):
        """Setup file monitoring with callbacks."""
        self.file_monitor.add_change_callback(self.on_file_changed)
    
    def on_file_changed(self, event: FileChangeEvent):
        """Handle file change events."""
        if event.event_type == 'modified':
            self.refresh_logs()
    
    def browse_log_directory(self):
        """Open directory browser for log directory selection."""
        directory = filedialog.askdirectory(title="Select EVE Online Log Directory")
        if directory:
            self.log_dir_var.set(directory)
            self.file_monitor.log_directory = directory
            self.load_log_files()
    
    def apply_filters(self):
        """Apply current filter settings."""
        self.file_monitor.set_monitoring_settings(
            max_days_old=self.max_days_var.get(),
            max_files_to_show=self.max_files_var.get()
        )
        self.load_log_files()
    
    def refresh_logs(self):
        """Refresh logs from monitored files."""
        try:
            # Get recent files
            recent_files = self.file_monitor.get_recent_files()
            
            # Parse all files
            self.all_log_entries = []
            for file_path in recent_files:
                if os.path.exists(file_path):
                    entries = self.log_parser.parse_log_file(file_path)
                    self.all_log_entries.extend(entries)
            
            # Sort by timestamp
            self.all_log_entries = self.log_parser.sort_entries_by_time(self.all_log_entries)
            
            # Process log entries through beacon tracker for CONCORD detection
            self.process_log_entries_for_beacon_tracking()
            
            # Update display
            self.update_log_display()
            
            # Update last refresh time
            self.last_refresh_time = datetime.now()
            
            # Force status update
            self.update_status_display()
            
            print(f"Logs refreshed: {len(self.all_log_entries)} entries from {len(recent_files)} files")
            
        except Exception as e:
            print(f"Error refreshing logs: {e}")
            # Still update the refresh time even if there's an error
            self.last_refresh_time = datetime.now()
            self.update_status_display()
    
    def clear_display(self):
        """Clear the log display."""
        self.log_text.delete(1.0, tk.END)
        self.all_log_entries = []
        self.update_status_display()
    
    def create_test_log(self):
        """Create a test log file to test auto-refresh functionality."""
        try:
            # Get the current log directory
            log_dir = self.log_dir_var.get()
            if not log_dir or not os.path.exists(log_dir):
                messagebox.showerror("Error", "Please select a valid log directory first.")
                return
            
            # Create a test log file with current timestamp
            now = datetime.now()
            timestamp_str = now.strftime("%Y%m%d_%H%M%S")
            test_filename = f"{timestamp_str}_99999999_test.txt"
            test_file_path = os.path.join(log_dir, test_filename)
            
            # Create test log content
            test_content = f"{now.strftime('%Y-%m-%d %H:%M:%S')} [TEST] Auto-refresh test log entry\n"
            test_content += f"{now.strftime('%Y-%m-%d %H:%M:%S')} [TEST] This is a test log to verify auto-refresh\n"
            test_content += f"{now.strftime('%Y-%m-%d %H:%M:%S')} [TEST] File created at: {now}\n"
            test_content += f"{now.strftime('%Y-%m-%d %H:%M:%S')} [TEST] Testing beacon tracking functionality\n"
            test_content += f"{now.strftime('%Y-%m-%d %H:%M:%S')} [TEST] Testing bounty monitoring system\n"
            
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            print(f"Created test log: {test_filename}")
            messagebox.showinfo("Test Log Created", 
                              f"Test log file created successfully!\n\n"
                              f"Filename: {test_filename}\n"
                              f"Location: {log_dir}\n\n"
                              f"The auto-monitor should detect this file and refresh automatically.")
            
            # Wait a moment then refresh to show the new file
            self.root.after(2000, self.refresh_logs)
            
        except Exception as e:
            print(f"Error creating test log: {e}")
            messagebox.showerror("Error", f"Error creating test log: {str(e)}")
    
    def add_test_bounty(self):
        """Test function to add a test bounty for testing."""
        try:
            # Check if bounty session is active
            bounty_summary = self.bounty_tracker.get_bounty_summary()
            if not bounty_summary['session_active']:
                messagebox.showwarning("Bounty Session Required", 
                                     "Bounty session must be active to add bounties.\n\n"
                                     "Please start a bounty session first.")
                return
            
            # Get current beacon ID if available
            beacon_id = self.beacon_tracker.current_beacon_id
            beacon_info = f" (Beacon: {beacon_id})" if beacon_id else ""
            
            # Create a test bounty entry
            test_timestamp = datetime.now()
            test_isk = 50000  # 50k ISK test bounty
            test_source = "TEST_BOUNTY"
            test_target = "Test Target"
            test_character = "Test Character"
            
            # Add the test bounty with beacon tracking
            if beacon_id:
                self.bounty_tracker.add_bounty_with_beacon(
                    timestamp=test_timestamp,
                    amount=test_isk,
                    source=test_source,
                    target=test_target,
                    beacon_id=beacon_id,
                    character_name=test_character
                )
                print(f"Test bounty added: {test_isk:,} ISK{beacon_info}")
            else:
                # Fallback to regular bounty entry if no beacon
                from ..core.bounty_tracker import BountyEntry
                bounty_entry = BountyEntry(
                    timestamp=test_timestamp,
                    amount=test_isk,
                    source=test_source,
                    target=test_target,
                    session_id=self.bounty_tracker._get_current_session_id()
                )
                self.bounty_tracker.add_bounty_entry(bounty_entry)
                print(f"Test bounty added: {test_isk:,} ISK (No beacon)")
            
            messagebox.showinfo("Test Bounty Added", 
                              f"Test bounty added successfully!\n\n"
                              f"Amount: {test_isk:,} ISK\n"
                              f"Source: {test_source}\n"
                              f"Target: {test_target}\n"
                              f"Character: {test_character}\n"
                              f"Time: {test_timestamp.strftime('%H:%M:%S')}{beacon_info}\n\n"
                              f"Check the bounty display to see the updated total.")
            
            # Update the display
            self.update_status_display()
            
        except Exception as e:
            print(f"Error adding test bounty: {e}")
            messagebox.showerror("Error", f"Error adding test bounty: {str(e)}")
    
    def parse_clipboard_loot(self):
        """Parse loot data from clipboard text for enhanced loot processing."""
        try:
            # Get clipboard content
            try:
                clipboard_text = self.root.clipboard_get()
            except tk.TclError:
                messagebox.showwarning("No Clipboard Data", 
                                     "No data found in clipboard.\n\n"
                                     "Please copy loot data from EVE Online first.")
                return
            
            if not clipboard_text.strip():
                messagebox.showwarning("Empty Clipboard", 
                                     "Clipboard appears to be empty.\n\n"
                                     "Please copy loot data from EVE Online first.")
                return
            
            # Parse the loot data
            loot_data = self._parse_loot_text(clipboard_text)
            
            if not loot_data['all_loot']:
                messagebox.showwarning("No Loot Found", 
                                     "No valid loot data found in clipboard.\n\n"
                                     "Please ensure you copied loot data from EVE Online.")
                return
            
            # Show loot analysis results
            self._show_loot_analysis(loot_data)
            
        except Exception as e:
            print(f"Error parsing clipboard loot: {e}")
            messagebox.showerror("Error", f"Error parsing clipboard loot: {str(e)}")
    
    def _parse_loot_text(self, clipboard_text):
        """Parse loot data from text format."""
        loot_data = {
            'rogue_drone_data': 0,
            'rogue_drone_data_value': 0,
            'total_value': 0,
            'all_loot': []
        }
        
        try:
            lines = clipboard_text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse loot line format:
                # Item Name        Amount    Category    Volume    Value
                # Example: Rogue Drone Infestation Data        1229        Rogue Drone Analysis Data        12,29 m3        122 900 000,00 ISK
                
                # Split by multiple spaces to separate fields
                parts = [part.strip() for part in line.split('        ') if part.strip()]
                
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
                        print(f"Found Rogue Drone Infestation Data: {amount} units = {value:,.2f} ISK")
                    
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
                    
                    print(f"Loot parsed: {item_name} x{amount} = {value:,.2f} ISK")
            
            print(f"Total loot value: {loot_data['total_value']:,.2f} ISK")
            print(f"Rogue Drone Data: {loot_data['rogue_drone_data']} units = {loot_data['rogue_drone_data_value']:,.2f} ISK")
            
        except Exception as e:
            print(f"Error parsing loot text: {e}")
            # Return default values if parsing fails
            loot_data['all_loot'] = [{'name': 'PARSE_ERROR', 'amount': 0, 'category': 'ERROR', 'volume': 'ERROR', 'value': 0}]
        
        return loot_data
    
    def _show_loot_analysis(self, loot_data):
        """Display loot analysis results in a popup window."""
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Loot Analysis Results")
        popup.geometry("800x600")
        popup.transient(self.root)
        popup.grab_set()
        popup.configure(bg="#2b2b2b")  # Dark background
        
        # Create text widget
        text_frame = tk.Frame(popup)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10),
                             bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                             insertbackground="#ffffff",   # White cursor
                             selectbackground="#4a9eff",  # Blue selection
                             selectforeground="#ffffff")  # White text when selected
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview,
                                bg="#1e1e1e", troughcolor="#2b2b2b",  # Dark scrollbar
                                activebackground="#404040",            # Darker when active
                                relief="flat", borderwidth=0)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate with loot analysis
        text_widget.insert(tk.END, "EVE Online Loot Analysis Results\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        
        text_widget.insert(tk.END, f"Total Loot Value: {loot_data['total_value']:,.2f} ISK\n")
        text_widget.insert(tk.END, f"Rogue Drone Data: {loot_data['rogue_drone_data']} units\n")
        text_widget.insert(tk.END, f"Rogue Drone Value: {loot_data['rogue_drone_data_value']:,.2f} ISK\n")
        text_widget.insert(tk.END, f"Total Items: {len(loot_data['all_loot'])}\n\n")
        
        text_widget.insert(tk.END, "Detailed Loot Breakdown:\n")
        text_widget.insert(tk.END, "-" * 30 + "\n")
        
        for i, loot in enumerate(loot_data['all_loot'], 1):
            text_widget.insert(tk.END, f"{i}. {loot['name']}\n")
            text_widget.insert(tk.END, f"   Amount: {loot['amount']:,}\n")
            text_widget.insert(tk.END, f"   Category: {loot['category']}\n")
            text_widget.insert(tk.END, f"   Volume: {loot['volume']}\n")
            text_widget.insert(tk.END, f"   Value: {loot['value']:,.2f} ISK\n\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def export_logs(self):
        """Export current logs to a file."""
        if not self.all_log_entries:
            messagebox.showinfo("Info", "No logs to export")
            return
        
        try:
            filename = f"eve_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=filename
            )
            
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    for entry in self.all_log_entries:
                        f.write(f"{entry}\n")
                
                messagebox.showinfo("Success", f"Logs exported to {filepath}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting logs: {e}")
    
    def load_log_files(self):
        """Load and display log files based on current settings."""
        try:
            # Get recent files
            recent_files = self.file_monitor.get_recent_files()
            
            # Parse all files
            self.all_log_entries = []
            for file_path in recent_files:
                if os.path.exists(file_path):
                    entries = self.log_parser.parse_log_file(file_path)
                    self.all_log_entries.extend(entries)
            
            # Sort by timestamp
            self.all_log_entries = self.log_parser.sort_entries_by_time(self.all_log_entries)
            
            # Process log entries through beacon tracker for CONCORD detection and bounty tracking
            self.process_log_entries_for_beacon_tracking()
            
            # Update display
            self.update_log_display()
            
            # Update last refresh time
            self.last_refresh_time = datetime.now()
            
            # Force status update
            self.update_status_display()
            
            print(f"Logs loaded: {len(self.all_log_entries)} entries from {len(recent_files)} files")
            
        except Exception as e:
            print(f"Error loading log files: {e}")
            messagebox.showerror("Error", f"Error loading log files: {e}")
            # Still update the refresh time even if there's an error
            self.last_refresh_time = datetime.now()
            self.update_status_display()
    
    def process_log_entries_for_beacon_tracking(self):
        """Process log entries through beacon tracker for CONCORD message detection and bounty tracking."""
        try:
            if not self.all_log_entries:
                return
            
            print(f"Processing {len(self.all_log_entries)} log entries for beacon tracking and bounty detection...")
            
            for entry in self.all_log_entries:
                if entry.content and entry.timestamp:
                    # Process through beacon tracker for CONCORD detection
                    detection = self.beacon_tracker.detect_concord_message(entry.content)
                    if detection:
                        print(f"CONCORD message detected: {detection['type']} at {entry.timestamp.strftime('%H:%M:%S')}")
                        
                        # Handle different types of CONCORD messages
                        if detection['type'] == 'link_start':
                            # Start CONCORD link process
                            beacon_id = self.beacon_tracker.start_concord_link(entry.timestamp, entry.source_file)
                            print(f"CONCORD link started: {beacon_id}")
                            
                        elif detection['type'] == 'link_complete':
                            # Complete CONCORD link process
                            self.beacon_tracker.complete_concord_link()
                            print("CONCORD link completed")
                            
                        elif detection['type'] == 'link_failed':
                            # Handle link failure
                            self.beacon_tracker.reset_concord_tracking()
                            print("CONCORD link failed - tracking reset")
                            
                        elif detection['type'] == 'beacon_activated':
                            # Beacon activated
                            print("CONCORD beacon activated")
                            
                        elif detection['type'] == 'analysis_in_progress':
                            # Analysis in progress
                            progress = detection.get('progress', 0)
                            print(f"CONCORD analysis progress: {progress}%")
                            
                        elif detection['type'] == 'analysis_complete':
                            # Analysis complete
                            progress = detection.get('progress', 0)
                            print(f"CONCORD analysis complete: {progress}%")
                            
                        # Update displays after processing
                        self.update_concord_display()
                        self.update_status_display()
                    
                    # Process bounty information from parsed data
                    if hasattr(entry, 'parsed_data') and entry.parsed_data:
                        self.process_bounty_data(entry)
            
            print("Beacon tracking and bounty processing completed")
            
        except Exception as e:
            print(f"Error processing log entries for beacon tracking: {e}")
            import traceback
            traceback.print_exc()
    
    def process_bounty_data(self, entry):
        """Process bounty data from log entry."""
        try:
            if not entry.parsed_data:
                return
            
            # Check for bounty received
            if 'bounty_received' in entry.parsed_data:
                bounty_match = entry.parsed_data['bounty_received']
                if bounty_match and len(bounty_match) > 0:
                    bounty_amount_str = bounty_match[0]
                    try:
                        # Parse bounty amount (remove commas and convert to int)
                        bounty_amount = int(bounty_amount_str.replace(',', ''))
                        print(f"Bounty detected: {bounty_amount:,} ISK at {entry.timestamp.strftime('%H:%M:%S')}")
                        
                        # Add bounty to tracker if session is active
                        bounty_summary = self.bounty_tracker.get_bounty_summary()
                        if bounty_summary['session_active']:
                            # Get current beacon ID if available
                            beacon_id = self.beacon_tracker.current_beacon_id
                            
                            if beacon_id:
                                # Add bounty with beacon tracking
                                self.bounty_tracker.add_bounty_with_beacon(
                                    timestamp=entry.timestamp,
                                    amount=bounty_amount,
                                    source="LOG_PARSER",
                                    target="Unknown",
                                    beacon_id=beacon_id,
                                    character_name="Unknown"
                                )
                                print(f"Bounty added with beacon tracking: {bounty_amount:,} ISK")
                            else:
                                # Add regular bounty entry
                                from ..core.bounty_tracker import BountyEntry
                                bounty_entry = BountyEntry(
                                    timestamp=entry.timestamp,
                                    amount=bounty_amount,
                                    source="LOG_PARSER",
                                    target="Unknown",
                                    session_id=self.bounty_tracker._get_current_session_id()
                                )
                                self.bounty_tracker.add_bounty_entry(bounty_entry)
                                print(f"Bounty added: {bounty_amount:,} ISK")
                        else:
                            print("Bounty detected but no active session - starting session automatically")
                            # Start bounty session automatically
                            self.bounty_tracker.start_session()
                            self.bounty_tracker.start_crab_session()
                            
                            # Add bounty with beacon tracking if available
                            beacon_id = self.beacon_tracker.current_beacon_id
                            if beacon_id:
                                self.bounty_tracker.add_bounty_with_beacon(
                                    timestamp=entry.timestamp,
                                    amount=bounty_amount,
                                    source="LOG_PARSER",
                                    target="Unknown",
                                    beacon_id=beacon_id,
                                    character_name="Unknown"
                                )
                            else:
                                from ..core.bounty_tracker import BountyEntry
                                bounty_entry = BountyEntry(
                                    timestamp=entry.timestamp,
                                    amount=bounty_amount,
                                    source="LOG_PARSER",
                                    target="Unknown",
                                    session_id=self.bounty_tracker._get_current_session_id()
                                )
                                self.bounty_tracker.add_bounty_entry(bounty_entry)
                        
                        # Update displays
                        self.update_status_display()
                        
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing bounty amount '{bounty_amount_str}': {e}")
            
            # Check for bounty kill
            if 'bounty_kill' in entry.parsed_data:
                bounty_match = entry.parsed_data['bounty_kill']
                if bounty_match and len(bounty_match) >= 2:
                    target_name = bounty_match[0]
                    bounty_amount_str = bounty_match[1]
                    try:
                        bounty_amount = int(bounty_amount_str.replace(',', ''))
                        print(f"Bounty kill detected: {target_name} - {bounty_amount:,} ISK")
                        # Similar processing as above...
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing bounty kill data: {e}")
                        
        except Exception as e:
            print(f"Error processing bounty data: {e}")
            import traceback
            traceback.print_exc()
    
    def update_log_display(self):
        """Update the log display with current entries."""
        self.log_text.delete(1.0, tk.END)
        
        for entry in self.all_log_entries:
            # Format timestamp
            if entry.timestamp:
                timestamp_str = entry.timestamp.strftime("%H:%M:%S")
                self.log_text.insert(tk.END, f"[{timestamp_str}] ", "timestamp")
            else:
                self.log_text.insert(tk.END, "[??:??:??] ")
            
            # Format source file
            source_name = os.path.basename(entry.source_file) if entry.source_file else "Unknown"
            self.log_text.insert(tk.END, f"[{source_name}] ", "source")
            
            # Format content with special highlighting
            content = entry.content
            if "bounty" in content.lower():
                self.log_text.insert(tk.END, content, "bounty")
            elif "beacon" in content.lower():
                self.log_text.insert(tk.END, content, "beacon")
            else:
                self.log_text.insert(tk.END, content)
            
            self.log_text.insert(tk.END, "\n")
        
        # Scroll to top
        self.log_text.see("1.0")
    
    def update_status_display(self):
        """Update the status display."""
        try:
            # Update monitoring status
            if self.monitoring_active:
                if self.high_freq_var.get():
                    status_text = "High-Freq Active"
                else:
                    status_text = "Normal Active"
            else:
                status_text = "Inactive"
            
            self.monitoring_status_label.config(text=status_text)
            
            # Update last refresh
            if self.last_refresh_time:
                refresh_text = self.last_refresh_time.strftime("%H:%M:%S")
            else:
                refresh_text = "Never"
            
            self.last_refresh_label.config(text=refresh_text)
            
            # Update last check
            if self.last_check_time:
                check_text = self.last_check_time.strftime("%H:%M:%S")
            else:
                check_text = "Never"
            
            self.last_check_label.config(text=check_text)
            
            # Add monitoring activity indicator
            if self.monitoring_active:
                time_since_check = (datetime.now() - self.last_check_time).total_seconds()
                if time_since_check < 2:  # Very recent check
                    activity_text = "🟢 Active"
                elif time_since_check < 5:  # Recent check
                    activity_text = "🟡 Recent"
                else:  # Stale check
                    activity_text = "🔴 Stale"
                
                # Update monitoring status with activity indicator
                self.monitoring_status_label.config(text=f"{status_text} - {activity_text}")
            
            # Update files monitored
            try:
                recent_files = self.file_monitor.get_recent_files()
                files_count = len(recent_files) if recent_files else 0
                self.files_monitored_label.config(text=str(files_count))
            except Exception as e:
                self.files_monitored_label.config(text="0")
            
            # Update log entries count
            entries_count = len(self.all_log_entries) if self.all_log_entries else 0
            self.log_entries_label.config(text=str(entries_count))
            
            # Update bounty display
            try:
                bounty_summary = self.bounty_tracker.get_bounty_summary()
                self.total_bounty_label.config(text=f"{bounty_summary['total_bounty']:,} ISK")
                self.crab_bounty_label.config(text=f"{bounty_summary['crab_bounty']:,} ISK")
                
                if bounty_summary['session_active']:
                    duration = bounty_summary['session_duration']
                    self.session_duration_label.config(text=format_duration(duration.total_seconds()))
                else:
                    self.session_duration_label.config(text="0s")
            except Exception as e:
                self.total_bounty_label.config(text="0 ISK")
                self.crab_bounty_label.config(text="0 ISK")
                self.session_duration_label.config(text="0s")
            
            # Update CONCORD display
            try:
                self.update_concord_display()
            except Exception as e:
                pass  # CONCORD display handles its own errors
            
            # Update beacon-bounty integration status
            try:
                self._update_beacon_bounty_status()
            except Exception as e:
                pass  # Handle errors gracefully
                
        except Exception as e:
            print(f"Error in update_status_display: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_beacon_bounty_status(self):
        """Update beacon-bounty integration status display."""
        try:
            beacon_status = self.beacon_tracker.get_concord_status()
            bounty_summary = self.bounty_tracker.get_bounty_summary()
            
            # Check if beacon and bounty are integrated
            beacon_active = beacon_status['has_active_countdown']
            bounty_active = bounty_summary['crab_session_active']
            
            if beacon_active and bounty_active:
                # Both active - show integration status
                beacon_id = self.beacon_tracker.current_beacon_id
                beacon_bounty_total = self.bounty_tracker.get_beacon_bounty_total(beacon_id) if beacon_id else 0
                
                status_text = f"🟢 Beacon-Bounty Integrated (Beacon: {beacon_id[:8]}... | Bounty: {beacon_bounty_total:,} ISK)"
                print(f"Beacon-Bounty Status: {status_text}")
            elif beacon_active:
                status_text = "🟡 Beacon Active (Bounty tracking needed)"
                print(f"Beacon-Bounty Status: {status_text}")
            elif bounty_active:
                status_text = "🟡 Bounty Active (No beacon session)"
                print(f"Beacon-Bounty Status: {status_text}")
            else:
                status_text = "🔴 No Active Sessions"
                print(f"Beacon-Bounty Status: {status_text}")
            
        except Exception as e:
            print(f"Error updating beacon-bounty status: {e}")
    
    def toggle_monitoring(self):
        """Toggle automatic monitoring on/off."""
        if self.monitoring_var.get():
            self.start_auto_monitoring()
        else:
            self.stop_auto_monitoring()
    
    def toggle_high_frequency(self):
        """Toggle high-frequency monitoring on/off."""
        if self.high_freq_var.get():
            if self.monitoring_var.get():
                self.start_auto_monitoring()
        else:
            # If high-frequency is disabled, stop auto-monitoring
            if self.monitoring_var.get():
                self.stop_auto_monitoring()
                # Restart with normal monitoring
                self.start_monitoring()
    
    def start_monitoring(self):
        """Start automatic monitoring."""
        try:
            self.file_monitor.start_monitoring()
            self.monitoring_active = True
            self.update_status_display()
        except Exception as e:
            messagebox.showerror("Error", f"Error starting monitoring: {e}")
            self.monitoring_var.set(False)
    
    def stop_monitoring(self):
        """Stop automatic monitoring."""
        self.file_monitor.stop_monitoring()
        self.monitoring_active = False
        self.update_status_display()
    
    def start_auto_monitoring(self):
        """Start high-frequency monitoring in a separate thread."""
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            self.stop_monitoring_flag = False
            self.monitoring_thread = threading.Thread(target=self.high_frequency_monitor_loop, daemon=True)
            self.monitoring_thread.start()
            self.monitoring_active = True
            self.update_status_display()
            print("Auto-monitoring started")
    
    def stop_auto_monitoring(self):
        """Stop high-frequency monitoring."""
        self.stop_monitoring_flag = True
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2.0)
        self.monitoring_active = False
        self.update_status_display()
        print("Auto-monitoring stopped")
    
    def high_frequency_monitor_loop(self):
        """High-frequency monitoring loop to detect file changes."""
        print("High-frequency monitoring loop started")
        while not self.stop_monitoring_flag:
            try:
                time.sleep(1)  # Check every 1 second for high-frequency monitoring
                
                if not self.stop_monitoring_flag:
                    print("Checking for file changes (auto-monitor)...")
                    
                    # Update last check time
                    self.last_check_time = datetime.now()
                    
                    # Get current file sizes and hashes
                    current_file_sizes = {}
                    current_file_hashes = {}
                    for file_path in self.file_monitor.get_recent_files():
                        if os.path.exists(file_path):
                            current_file_sizes[file_path] = os.path.getsize(file_path)
                            current_file_hashes[file_path] = self.calculate_file_hash(file_path)
                    
                    # Compare with previous state
                    changed_files = []
                    for file_path in current_file_sizes:
                        if file_path in self.last_file_sizes:
                            if (current_file_sizes[file_path] != self.last_file_sizes[file_path] or 
                                current_file_hashes[file_path] != self.last_file_hashes[file_path]):
                                changed_files.append(file_path)
                        else:
                            # New file added
                            changed_files.append(file_path)
                    
                    # Check for deleted files
                    for file_path in self.last_file_sizes:
                        if file_path not in current_file_sizes:
                            changed_files.append(file_path)
                    
                    # Update last state
                    self.last_file_sizes = current_file_sizes
                    self.last_file_hashes = current_file_hashes
                    
                    # If any file changed, refresh logs
                    if changed_files:
                        print(f"Changed files detected: {len(changed_files)} - refreshing automatically")
                        self.root.after(0, self.refresh_logs)
                        self.root.after(0, self.update_status_display)
                    else:
                        print("No changes detected, continuing to monitor...")
                        # Update status to show we're still checking
                        self.root.after(0, self.update_status_display)
            
            except Exception as e:
                print(f"High-frequency monitoring loop error: {e}")
                time.sleep(1)  # Wait a bit before retrying
    
    def calculate_file_hash(self, file_path):
        """Calculate MD5 hash of file content for change detection."""
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
    
    def start_bounty_session(self):
        """Start a new bounty tracking session."""
        self.bounty_tracker.start_session()
        self.update_status_display()
    
    def end_bounty_session(self):
        """End the current bounty tracking session."""
        result = self.bounty_tracker.end_session()
        if result:
            messagebox.showinfo("Session Ended", 
                              f"Session ended\nDuration: {result['duration']}\nTotal Bounty: {result['total_bounty']:,} ISK")
        self.update_status_display()
    
    def start_crab_session(self):
        """Start a CRAB bounty session."""
        self.bounty_tracker.start_crab_session()
        self.update_status_display()
    
    def end_crab_session(self):
        """End the CRAB bounty session."""
        self.bounty_tracker.end_crab_session()
        self.update_status_display()
    

    
    def export_beacon_data(self):
        """Export beacon session data to a file."""
        try:
            filepath = self.beacon_tracker.export_session_data('csv')
            messagebox.showinfo("Success", f"Beacon data exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting beacon data: {e}")
    
    def update_concord_countdown(self, text: str, color: str):
        """Update CONCORD countdown display."""
        self.concord_countdown_var.set(text)
        self.concord_countdown_label.config(foreground=color, background="#2b2b2b")
    
    def on_beacon_started(self, beacon_id: str):
        """Called when a beacon session starts - automatically start bounty tracking."""
        try:
            # Start bounty session if not already active
            if not self.bounty_tracker.session_start:
                self.bounty_tracker.start_session()
            
            # Start CRAB session
            self.bounty_tracker.start_crab_session()
            
            # Update status to show beacon-bounty integration
            self.update_status_display()
            
            print(f"Beacon session started: {beacon_id}")
            print("Bounty tracking automatically started for this beacon session")
            
        except Exception as e:
            print(f"Error starting bounty tracking for beacon {beacon_id}: {e}")
    
    def on_beacon_reset(self):
        """Called when beacon tracking is reset - clear bounty session."""
        try:
            # End CRAB session
            self.bounty_tracker.end_crab_session()
            
            # Update status
            self.update_status_display()
            
            print("Beacon tracking reset - bounty session cleared")
            
        except Exception as e:
            print(f"Error resetting bounty tracking: {e}")
    
    def reset_concord_tracking(self):
        """Reset CONCORD tracking to start fresh."""
        status = self.beacon_tracker.get_concord_status()
        if status['countdown_active']:
            # Ask for confirmation
            result = messagebox.askyesno(
                "Reset CONCORD Tracking",
                "Are you sure you want to reset CONCORD tracking?\n\n"
                "This will stop the current countdown and clear all tracking data.\n\n"
                "This action cannot be undone."
            )
            
            if not result:
                return
        
        self.beacon_tracker.reset_concord_tracking()
        self.update_concord_display()
        messagebox.showinfo("Reset Complete", "CONCORD tracking has been reset")
    
    def copy_beacon_id(self):
        """Copy current Beacon ID to clipboard."""
        beacon_id = self.beacon_tracker.current_beacon_id
        if beacon_id:
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(beacon_id)
                messagebox.showinfo("Beacon ID Copied", f"Beacon ID copied to clipboard:\n{beacon_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy Beacon ID: {e}")
        else:
            messagebox.showinfo("No Beacon ID", "No active beacon session found")
    
    def view_beacon_sessions(self):
        """View detailed beacon session history."""
        sessions = self.beacon_tracker.get_all_sessions()
        if not sessions:
            messagebox.showinfo("No Sessions", "No beacon sessions recorded yet")
            return
        
        # Create a new window to display session history
        session_window = tk.Toplevel(self.root)
        session_window.title("Beacon Session History")
        session_window.geometry("800x600")
        
        # Create text widget with scrollbar
        text_frame = tk.Frame(session_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate with session data
        text_widget.insert(tk.END, "CONCORD Rogue Analysis Beacon Sessions\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        
        for i, session in enumerate(sessions, 1):
            text_widget.insert(tk.END, f"Session {i}:\n")
            text_widget.insert(tk.END, f"  Beacon ID: {session.beacon_id}\n")
            text_widget.insert(tk.END, f"  Start Time: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            if session.end_time:
                text_widget.insert(tk.END, f"  End Time: {session.end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            text_widget.insert(tk.END, f"  Duration: {session.get_duration()}\n")
            text_widget.insert(tk.END, f"  Status: {'Active' if session.is_active() else 'Completed' if session.completed else 'Failed'}\n")
            text_widget.insert(tk.END, f"  Rogue Drone Data: {session.rogue_drone_data}\n")
            if session.loot_details:
                text_widget.insert(tk.END, f"  Loot: {', '.join(session.loot_details)}\n")
            text_widget.insert(tk.END, f"  Source: {session.source_file}\n")
            text_widget.insert(tk.END, "-" * 30 + "\n\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def test_concord_link_start(self):
        """Test function to simulate CONCORD link start."""
        beacon_id = self.beacon_tracker.test_concord_link_start()
        self.update_concord_display()
        messagebox.showinfo("Test Complete", f"CONCORD link start test completed.\nBeacon ID: {beacon_id}")
    
    def test_concord_link_complete(self):
        """Test function to simulate CONCORD link completion."""
        self.beacon_tracker.test_concord_link_complete()
        self.update_concord_display()
        messagebox.showinfo("Test Complete", "CONCORD link completion test completed.")
    
    def test_concord_detection(self):
        """Test advanced CONCORD message detection with sample messages."""
        try:
            # Sample CONCORD messages for testing
            test_messages = [
                "Your ship has started the link process with CONCORD Rogue Analysis Beacon",
                "Your ship successfully completed the link process with CONCORD Rogue Analysis Beacon",
                "CONCORD Rogue Analysis Beacon has been activated",
                "Analysis in progress... 45%",
                "Analysis complete... 100%",
                "Your ship failed to complete the link process with CONCORD Rogue Analysis Beacon"
            ]
            
            # Test each message
            results = []
            for message in test_messages:
                detection = self.beacon_tracker.detect_concord_message(message)
                if detection:
                    results.append({
                        'message': message,
                        'detection': detection
                    })
            
            # Show results
            self._show_concord_detection_results(results)
            
        except Exception as e:
            print(f"Error testing CONCORD detection: {e}")
            messagebox.showerror("Error", f"Error testing CONCORD detection: {str(e)}")
    
    def _show_concord_detection_results(self, results):
        """Display CONCORD detection test results."""
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("CONCORD Detection Test Results")
        popup.geometry("900x700")
        popup.transient(self.root)
        popup.grab_set()
        popup.configure(bg="#2b2b2b")  # Dark background
        
        # Create text widget
        text_frame = tk.Frame(popup)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10),
                             bg="#1e1e1e", fg="#ffffff",  # Dark background, white text
                             insertbackground="#ffffff",   # White cursor
                             selectbackground="#4a9eff",  # Blue selection
                             selectforeground="#ffffff")  # White text when selected
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview,
                                bg="#1e1e1e", troughcolor="#2b2b2b",  # Dark scrollbar
                                activebackground="#404040",            # Darker when active
                                relief="flat", borderwidth=0)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate with detection results
        text_widget.insert(tk.END, "CONCORD Message Detection Test Results\n")
        text_widget.insert(tk.END, "=" * 60 + "\n\n")
        
        if results:
            text_widget.insert(tk.END, f"Successfully detected {len(results)} CONCORD messages:\n\n")
            
            for i, result in enumerate(results, 1):
                detection = result['detection']
                text_widget.insert(tk.END, f"{i}. Message Type: {detection['type'].upper()}\n")
                text_widget.insert(tk.END, f"   Raw Message: {detection['message']}\n")
                text_widget.insert(tk.END, f"   Timestamp: {detection['timestamp'].strftime('%H:%M:%S')}\n")
                
                if 'progress' in detection:
                    text_widget.insert(tk.END, f"   Progress: {detection['progress']}%\n")
                
                text_widget.insert(tk.END, f"   Raw Match: {detection['raw_match']}\n")
                text_widget.insert(tk.END, "-" * 50 + "\n\n")
        else:
            text_widget.insert(tk.END, "No CONCORD messages were detected.\n")
            text_widget.insert(tk.END, "This may indicate an issue with the detection patterns.\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def end_crab_failed(self):
        """End CRAB session as failed - clear countdown and mark as failed."""
        try:
            # Ask for confirmation
            result = messagebox.askyesno(
                "End CRAB Session - Failed",
                "Are you sure you want to end the CRAB session as failed?\n\n"
                "This will stop the current countdown and mark the session as failed.\n\n"
                "This action cannot be undone."
            )
            
            if not result:
                return
            
            # End the CRAB session as failed
            self.bounty_tracker.end_crab_session()
            
            # Reset CONCORD tracking
            self.beacon_tracker.reset_concord_tracking()
            
            # Update displays
            self.update_concord_display()
            self.update_status_display()
            
            messagebox.showinfo("CRAB Session Failed", 
                              "CRAB session has been marked as failed.\n"
                              "CONCORD tracking has been reset.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error ending CRAB session: {e}")
    
    def end_crab_submit(self):
        """End CRAB session and submit data - clear countdown and mark as completed."""
        try:
            # Ask for confirmation
            result = messagebox.askyesno(
                "End CRAB Session - Submit Data",
                "Are you sure you want to end the CRAB session and submit data?\n\n"
                "This will stop the current countdown and submit the session data.\n\n"
                "This action cannot be undone."
            )
            
            if not result:
                return
            
            # End the CRAB session
            self.bounty_tracker.end_crab_session()
            
            # Get session data for submission
            active_session = self.beacon_tracker.get_active_session()
            if active_session:
                # First check if the session already has loot data from previous clipboard updates
                clipboard_loot_data = None
                
                # If session doesn't have loot details, try to read from clipboard
                if not active_session.loot_details or len(active_session.loot_details) == 0:
                    try:
                        clipboard_text = self.root.clipboard_get()
                        if clipboard_text and clipboard_text.strip():
                            clipboard_loot_data = self._parse_loot_text(clipboard_text)
                            print(f"Clipboard loot data parsed: {clipboard_loot_data['total_value']:,.2f} ISK")
                            
                            # Update the session with this loot data so it's stored for future use
                            if clipboard_loot_data and clipboard_loot_data['all_loot']:
                                active_session.rogue_drone_data = clipboard_loot_data['rogue_drone_data']
                                active_session.loot_details.clear()
                                for loot in clipboard_loot_data['all_loot']:
                                    active_session.loot_details.append(f"{loot['name']} x{loot['amount']} ({loot['value']:,.0f} ISK)")
                                
                                print(f"Session updated with clipboard loot data")
                    except tk.TclError:
                        print("No clipboard data found for loot parsing")
                    except Exception as e:
                        print(f"Error parsing clipboard loot: {e}")
                else:
                    print(f"Session already has loot data: {len(active_session.loot_details)} items")
                
                # Prepare session data with clipboard loot if available
                session_data = {
                    'Beacon ID': active_session.beacon_id,
                    'Total Duration': str(active_session.get_duration()),
                    'Total CRAB Bounty': str(self.bounty_tracker.get_crab_total_bounty()),
                    'Rogue Drone Data Amount': str(active_session.rogue_drone_data),
                    'Loot Details': ', '.join(active_session.loot_details) if active_session.loot_details else 'None'
                }
                
                # Add clipboard loot data if available (either from current clipboard or session)
                if clipboard_loot_data and clipboard_loot_data['all_loot']:
                    # Add clipboard loot data to existing fields to ensure submission
                    session_data['Clipboard Loot Total Value'] = f"{clipboard_loot_data['total_value']:,.2f} ISK"
                    session_data['Clipboard Rogue Drone Data'] = str(clipboard_loot_data['rogue_drone_data'])
                    session_data['Clipboard Loot Items'] = str(len(clipboard_loot_data['all_loot']))
                    
                    # Also append clipboard loot to the Loot Details field to ensure it gets submitted
                    clipboard_loot_summary = f" | Clipboard: {clipboard_loot_data['total_value']:,.2f} ISK, {clipboard_loot_data['rogue_drone_data']} RDD, {len(clipboard_loot_data['all_loot'])} items"
                    session_data['Loot Details'] += clipboard_loot_summary
                    
                    # Show loot summary to user
                    loot_summary = f"Clipboard Loot Found:\n"
                    loot_summary += f"Total Value: {clipboard_loot_data['total_value']:,.2f} ISK\n"
                    loot_summary += f"Rogue Drone Data: {clipboard_loot_data['rogue_drone_data']} units\n"
                    loot_summary += f"Items: {len(clipboard_loot_data['all_loot'])}\n\n"
                    loot_summary += "This loot data will be included in your submission."
                    
                    messagebox.showinfo("Loot Data Found", loot_summary)
                elif active_session.loot_details and len(active_session.loot_details) > 0:
                    # Session has loot data from previous updates
                    print(f"Using session loot data: {len(active_session.loot_details)} items")
                    
                    # Show session loot summary to user
                    loot_summary = f"Session Loot Data Found:\n"
                    loot_summary += f"Rogue Drone Data: {active_session.rogue_drone_data} units\n"
                    loot_summary += f"Items: {len(active_session.loot_details)}\n\n"
                    loot_summary += "This loot data will be included in your submission."
                    
                    messagebox.showinfo("Session Loot Data Found", loot_summary)
                
                # Submit to Google Forms
                print(f"Submitting session data to Google Forms...")
                print(f"Session data keys: {list(session_data.keys())}")
                print(f"Loot Details field content: {session_data['Loot Details']}")
                
                success = self.google_forms_service.submit_beacon_session(session_data)
                
                if success:
                    print(f"Google Forms submission successful")
                    messagebox.showinfo("Success", 
                                      "CRAB session completed and data submitted to Google Forms!\n\n"
                                      "Session data has been recorded and submitted.")
                else:
                    print(f"Google Forms submission failed")
                    messagebox.showwarning("Submission Warning", 
                                         "CRAB session completed but failed to submit to Google Forms.\n\n"
                                         "You can manually submit using the 'Submit to Google Forms' button.")
            else:
                messagebox.showinfo("CRAB Session Completed", 
                                  "CRAB session has been completed.\n"
                                  "No active beacon session found for data submission.")
            
            # Reset CONCORD tracking
            self.beacon_tracker.reset_concord_tracking()
            
            # Update displays
            self.update_concord_display()
            self.update_status_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error ending CRAB session: {e}")
    
    def update_beacon_loot_from_clipboard(self):
        """Update the current beacon session with loot data from clipboard."""
        try:
            # Check if there's an active beacon session
            active_session = self.beacon_tracker.get_active_session()
            if not active_session:
                messagebox.showwarning("No Active Session", 
                                     "No active beacon session found.\n\n"
                                     "Please start a beacon session first.")
                return
            
            # Try to read clipboard loot data
            try:
                clipboard_text = self.root.clipboard_get()
                if not clipboard_text or not clipboard_text.strip():
                    messagebox.showwarning("No Clipboard Data", 
                                         "No data found in clipboard.\n\n"
                                         "Please copy loot data from EVE Online first.")
                    return
            except tk.TclError:
                messagebox.showwarning("No Clipboard Data", 
                                     "No data found in clipboard.\n\n"
                                     "Please copy loot data from EVE Online first.")
                return
            
            # Parse the loot data
            loot_data = self._parse_loot_text(clipboard_text)
            
            if not loot_data['all_loot']:
                messagebox.showwarning("No Loot Found", 
                                     "No valid loot data found in clipboard.\n\n"
                                     "Please ensure you copied loot data from EVE Online.")
                return
            
            # Update the beacon session with loot data
            active_session.rogue_drone_data = loot_data['rogue_drone_data']
            
            # Clear existing loot details and add new ones
            active_session.loot_details.clear()
            for loot in loot_data['all_loot']:
                active_session.loot_details.append(f"{loot['name']} x{loot['amount']} ({loot['value']:,.0f} ISK)")
            
            # Show success message with loot summary
            loot_summary = f"Beacon session loot updated successfully!\n\n"
            loot_summary += f"Total Loot Value: {loot_data['total_value']:,.2f} ISK\n"
            loot_summary += f"Rogue Drone Data: {loot_data['rogue_drone_data']} units\n"
            loot_summary += f"Items: {len(loot_data['all_loot'])}\n\n"
            loot_summary += "This loot data will now be included when you submit your session."
            
            messagebox.showinfo("Loot Updated", loot_summary)
            
            # Update the display
            self.update_concord_display()
            
        except Exception as e:
            print(f"Error updating beacon loot from clipboard: {e}")
            messagebox.showerror("Error", f"Error updating loot data: {str(e)}")
    
    def update_concord_display(self):
        """Update the CONCORD display with current status."""
        status = self.beacon_tracker.get_concord_status()
        
        # Update status
        self.concord_status_var.set(f"Status: {status['status']}")
        
        # Update link time
        if status['link_start']:
            link_time = status['link_start'].strftime('%H:%M:%S')
            self.concord_time_var.set(f"Link Time: {link_time}")
        else:
            self.concord_time_var.set("Link Time: Not started")
        
        # Update Beacon ID
        beacon_id = self.beacon_tracker.current_beacon_id
        if beacon_id:
            # Show shortened beacon ID
            short_id = beacon_id[:20] + "..." if len(beacon_id) > 23 else beacon_id
            self.beacon_id_var.set(f"Beacon ID: {short_id}")
        else:
            self.beacon_id_var.set("Beacon ID: None")
        
        # If no countdown is active, reset countdown display
        if not status['countdown_active']:
            self.concord_countdown_var.set("Countdown: --:--")
            self.concord_countdown_label.config(foreground="#ffff00", background="#2b2b2b")
    
    def update_display_timer(self):
        """Update display elements that need regular updates."""
        try:
            self.update_status_display()
        except Exception as e:
            print(f"Error in update_display_timer: {e}")
        
        # Schedule next update
        self.root.after(1000, self.update_display_timer)  # Update every second
    
    def test_google_forms(self):
        """Test Google Forms configuration and connection."""
        try:
            # Test configuration loading
            config_debug = self.google_forms_service.test_config_loading()
            
            # Test connection
            connection_success = self.google_forms_service.test_connection()
            
            # Create debug report
            debug_report = f"Google Forms Configuration Test\n"
            debug_report += f"=" * 40 + "\n\n"
            
            debug_report += f"Environment: {config_debug.get('environment', 'Unknown')}\n"
            debug_report += f"Config Loaded: {config_debug.get('config_loaded', False)}\n"
            debug_report += f"Config Keys: {config_debug.get('config_keys', [])}\n"
            debug_report += f"Form URL: {config_debug.get('form_url', 'None')}\n"
            debug_report += f"Field Mappings Count: {config_debug.get('field_mappings_count', 0)}\n"
            debug_report += f"Version: {config_debug.get('version', 'Unknown')}\n"
            debug_report += f"Last Updated: {config_debug.get('last_updated', 'Unknown')}\n\n"
            
            if 'environment' in config_debug and config_debug['environment'] == 'PyInstaller Executable':
                debug_report += f"Executable Directory: {config_debug.get('executable_dir', 'Unknown')}\n"
                debug_report += f"Working Directory: {config_debug.get('working_dir', 'Unknown')}\n\n"
                
                debug_report += f"Config File Locations:\n"
                for path, exists in config_debug.get('config_file_exists', {}).items():
                    debug_report += f"  {path}: {'✓ EXISTS' if exists else '✗ NOT FOUND'}\n"
                debug_report += "\n"
            
            debug_report += f"Connection Test: {'✓ SUCCESS' if connection_success else '✗ FAILED'}\n"
            
            if config_debug.get('field_mappings'):
                debug_report += f"\nField Mappings:\n"
                for field_name, entry_id in config_debug.get('field_mappings', {}).items():
                    debug_report += f"  {field_name} -> {entry_id}\n"
            
            # Show debug report
            messagebox.showinfo("Google Forms Test Results", debug_report)
            
        except Exception as e:
            messagebox.showerror("Test Error", f"Error testing Google Forms: {e}")
