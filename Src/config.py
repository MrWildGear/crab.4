"""
Configuration constants and settings for EVE Log Reader
"""
import os

# UI Configuration
WINDOW_TITLE = "EVE Online Log Reader - Recent Logs Monitor"
WINDOW_SIZE = "1400x900"
DARK_THEME_COLORS = {
    "background": "#2b2b2b",
    "darker_background": "#1e1e1e", 
    "text": "#ffffff",
    "accent": "#4a9eff",
    "border": "#404040"
}

# Log File Configuration
LOG_PATTERNS = ["*.log", "*.txt", "*.xml"]
MAX_DAYS_OLD = 1  # Only show logs from last 24 hours by default
MAX_FILES_TO_SHOW = 10  # Maximum number of recent files to display

# EVE Online Log Directory Paths
EVE_LOG_PATHS = [
    os.path.expanduser("~/Documents/EVE/logs/Gamelogs"),  # Primary location
    os.path.expanduser("~/Documents/EVE/logs"),  # Fallback to logs folder
    os.path.expanduser("~/AppData/Local/CCP/EVE/logs/Gamelogs"),
    os.path.expanduser("~/AppData/Local/CCP/EVE/logs"),
    "C:/Users/Public/Documents/EVE/logs/Gamelogs",
    "C:/Users/Public/Documents/EVE/logs",
    "C:/Program Files/CCP/EVE/logs/Gamelogs",
    "C:/Program Files/CCP/EVE/logs"
]

# File Monitoring
MONITORING_INTERVAL = 1.0  # seconds
HASH_BUFFER_SIZE = 8192  # bytes for file hashing

# CONCORD Configuration
CONCORD_COUNTDOWN_COLOR = "#ffff00"  # Default yellow color for countdown
