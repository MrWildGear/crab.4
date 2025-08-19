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
        
        # Files monitored
        ttk.Label(status_frame, text="Files Monitored:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.files_monitored_label = ttk.Label(status_frame, text="0")
        self.files_monitored_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Log entries count
        ttk.Label(status_frame, text="Log Entries:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.log_entries_label = ttk.Label(status_frame, text="0")
        self.log_entries_label.grid(row=3, column=1, sticky="w", padx=5, pady=2)
    
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
        beacon_frame = ttk.LabelFrame(self.root, text="Beacon Tracking")
        beacon_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Beacon status
        ttk.Label(beacon_frame, text="Current Beacon:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.current_beacon_label = ttk.Label(beacon_frame, text="None")
        self.current_beacon_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(beacon_frame, text="Beacon Duration:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.beacon_duration_label = ttk.Label(beacon_frame, text="0s")
        self.beacon_duration_label.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        # Beacon controls
        ttk.Button(beacon_frame, text="Submit to Google Forms", command=self.submit_to_google_forms).grid(row=1, column=0, columnspan=2, padx=5, pady=2)
        ttk.Button(beacon_frame, text="Export Beacon Data", command=self.export_beacon_data).grid(row=1, column=2, columnspan=2, padx=5, pady=2)
    
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
                initialname=filename
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
            print(f"Updating status display - monitoring_active: {self.monitoring_active}, high_freq: {self.high_freq_var.get()}")
            
            # Update monitoring status
            if self.monitoring_active:
                if self.high_freq_var.get():
                    status_text = "High-Freq Active"
                else:
                    status_text = "Normal Active"
            else:
                status_text = "Inactive"
            
            print(f"Setting monitoring status to: {status_text}")
            self.monitoring_status_label.config(text=status_text)
            
            # Update last refresh
            if self.last_refresh_time:
                refresh_text = self.last_refresh_time.strftime("%H:%M:%S")
            else:
                refresh_text = "Never"
            
            print(f"Setting last refresh to: {refresh_text}")
            self.last_refresh_label.config(text=refresh_text)
            
            # Update files monitored
            try:
                recent_files = self.file_monitor.get_recent_files()
                files_count = len(recent_files) if recent_files else 0
                print(f"Setting files monitored to: {files_count}")
                self.files_monitored_label.config(text=str(files_count))
            except Exception as e:
                print(f"Error getting files count: {e}")
                self.files_monitored_label.config(text="0")
            
            # Update log entries count
            entries_count = len(self.all_log_entries) if self.all_log_entries else 0
            print(f"Setting log entries to: {entries_count}")
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
                print(f"Error updating bounty display: {e}")
                self.total_bounty_label.config(text="0 ISK")
                self.crab_bounty_label.config(text="0 ISK")
                self.session_duration_label.config(text="0s")
            
            # Update beacon display
            try:
                active_session = self.beacon_tracker.get_active_session()
                if active_session:
                    beacon_id = active_session.beacon_id[:8] + "..."
                    self.current_beacon_label.config(text=beacon_id)
                    
                    duration = active_session.get_duration()
                    self.beacon_duration_label.config(text=format_duration(duration.total_seconds()))
                else:
                    self.current_beacon_label.config(text="None")
                    self.beacon_duration_label.config(text="0s")
            except Exception as e:
                print(f"Error updating beacon display: {e}")
                self.current_beacon_label.config(text="None")
                self.beacon_duration_label.config(text="0s")
            
            print("Status display update completed successfully")
                
        except Exception as e:
            print(f"Error in update_status_display: {e}")
            import traceback
            traceback.print_exc()
    
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
    
    def submit_to_google_forms(self):
        """Submit current beacon session data to Google Forms."""
        active_session = self.beacon_tracker.get_active_session()
        if not active_session:
            messagebox.showinfo("Info", "No active beacon session to submit")
            return
        
        try:
            # Prepare session data
            session_data = {
                'Beacon ID': active_session.beacon_id,
                'Total Duration': str(active_session.get_duration()),
                'Total CRAB Bounty': str(self.bounty_tracker.get_crab_total_bounty()),
                'Rogue Drone Data Amount': str(active_session.rogue_drone_data),
                'Loot Details': ', '.join(active_session.loot_details) if active_session.loot_details else 'None'
            }
            
            # Submit to Google Forms
            success = self.google_forms_service.submit_beacon_session(session_data)
            
            if success:
                messagebox.showinfo("Success", "Beacon session data submitted to Google Forms")
            else:
                messagebox.showerror("Error", "Failed to submit to Google Forms")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error submitting to Google Forms: {e}")
    
    def export_beacon_data(self):
        """Export beacon session data to a file."""
        try:
            filepath = self.beacon_tracker.export_session_data('csv')
            messagebox.showinfo("Success", f"Beacon data exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting beacon data: {e}")
    
    def update_display_timer(self):
        """Update display elements that need regular updates."""
        try:
            self.update_status_display()
        except Exception as e:
            print(f"Error in update_display_timer: {e}")
        
        # Schedule next update
        self.root.after(1000, self.update_display_timer)  # Update every second
