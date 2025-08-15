"""
UI Theme and Styling for EVE Log Reader
"""
import tkinter as tk
from tkinter import ttk
from config import DARK_THEME_COLORS

class UITheme:
    """Handles UI theming and styling"""
    
    @staticmethod
    def apply_dark_theme(root):
        """Apply dark mode styling to the application"""
        colors = DARK_THEME_COLORS
        
        # Configure root window
        root.configure(bg=colors["background"])
        
        # Configure ttk styles
        style = ttk.Style()
        
        # Configure main frame style
        style.configure("TFrame", background=colors["background"])
        
        # Configure label styles
        style.configure("TLabel", 
                       background=colors["background"], 
                       foreground=colors["text"],
                       font=("Segoe UI", 9))
        
        # Configure button styles
        style.configure("TButton", 
                       background=colors["darker_background"], 
                       foreground=colors["text"],
                       borderwidth=1,
                       focuscolor=colors["accent"])
        
        # Configure entry styles
        style.configure("TEntry", 
                       fieldbackground=colors["darker_background"], 
                       foreground=colors["text"],
                       borderwidth=1,
                       insertcolor=colors["text"])
        
        # Configure spinbox styles
        style.configure("TSpinbox", 
                       fieldbackground=colors["darker_background"], 
                       foreground=colors["text"],
                       borderwidth=1,
                       insertcolor=colors["text"])
        
        # Configure checkbox styles
        style.configure("TCheckbutton", 
                       background=colors["background"], 
                       foreground=colors["text"])
        
        # Configure label frame styles
        style.configure("TLabelframe", 
                       background=colors["background"], 
                       bordercolor=colors["border"])
        style.configure("TLabelframe.Label", 
                       background=colors["background"], 
                       foreground=colors["text"])
        
        # Configure scrollbar styles
        style.configure("Vertical.TScrollbar", 
                       background=colors["darker_background"], 
                       troughcolor=colors["background"],
                       bordercolor=colors["border"],
                       arrowcolor=colors["text"])
    
    @staticmethod
    def create_dark_button(parent, text, command, **kwargs):
        """Create a button with dark theme styling"""
        colors = DARK_THEME_COLORS
        return tk.Button(
            parent, 
            text=text, 
            command=command,
            bg=colors["darker_background"], 
            fg=colors["text"],
            activebackground=colors["border"],
            activeforeground=colors["text"],
            relief="raised", 
            borderwidth=1,
            font=("Segoe UI", 9),
            **kwargs
        )
    
    @staticmethod
    def create_dark_entry(parent, **kwargs):
        """Create an entry widget with dark theme styling"""
        colors = DARK_THEME_COLORS
        return tk.Entry(
            parent,
            bg=colors["darker_background"], 
            fg=colors["text"],
            insertbackground=colors["text"],
            selectbackground=colors["accent"],
            selectforeground=colors["text"],
            relief="sunken", 
            borderwidth=1,
            font=("Segoe UI", 9),
            **kwargs
        )
    
    @staticmethod
    def create_dark_text(parent, **kwargs):
        """Create a text widget with dark theme styling"""
        colors = DARK_THEME_COLORS
        text_widget = tk.Text(
            parent,
            bg=colors["darker_background"],
            fg=colors["text"],
            insertbackground=colors["text"],
            selectbackground=colors["accent"],
            selectforeground=colors["text"],
            relief="sunken",
            borderwidth=1,
            font=("Consolas", 9),
            **kwargs
        )
        
        # Configure tags for syntax highlighting
        text_widget.tag_configure("timestamp", foreground="#4a9eff")
        text_widget.tag_configure("bounty", foreground="#00ff00")
        text_widget.tag_configure("error", foreground="#ff4444")
        text_widget.tag_configure("warning", foreground="#ffff00")
        text_widget.tag_configure("info", foreground="#44ff44")
        
        return text_widget
