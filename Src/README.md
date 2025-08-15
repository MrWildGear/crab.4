# EVE Online Log Reader - Recent Logs Monitor

A Python application that monitors and displays EVE Online game logs from **RECENT files only** in the game logs folder, automatically filtering out old logs based on UTC timestamps in filenames.

## 🚀 **Smart Recent Logs Filtering**

- **📅 UTC Timestamp Parsing**: Automatically parses EVE log filenames (Date_startTime_characterID.txt)
- **⏰ Recent Files Only**: Only shows logs from the last 1-30 days (configurable)
- **📁 File Limit Control**: Limit to 5-50 most recent files (configurable)
- **🔄 Real-time Updates**: Detects file changes and updates automatically every 3 seconds
- **📊 Combined Recent View**: Shows logs from recent files in one unified timeline
- **🏷️ Source Tracking**: Each log entry shows which file it came from
- **💾 Export Functionality**: Save recent logs to a single file
- **🧹 Smart Refresh**: Only refreshes when recent files actually change

## Features

- **Automatic Log Detection**: Automatically finds EVE Online log directories
- **Smart Recent File Filtering**: Only monitors recent log files based on filename timestamps
- **UTC Timestamp Recognition**: Parses EVE log filename format: `YYYYMMDD_HHMMSS_characterID.txt`
- **Configurable Filters**: Set maximum days old (1-30) and maximum files to show (5-50)
- **Smart Timestamp Parsing**: Extracts and sorts log entries by timestamp across recent files
- **Newest First Display**: Shows the most recent log entries from recent files at the top
- **File Change Detection**: Automatically detects when recent log files are updated
- **Auto-refresh**: Option to automatically refresh every 3 seconds (enabled by default)
- **Export Capability**: Export recent logs to a single text file
- **User-friendly GUI**: Clean, intuitive interface built with tkinter

## Requirements

- Python 3.6 or higher
- tkinter (usually included with Python)
- Windows OS (optimized for EVE Online log locations)

## Installation

1. Make sure you have Python installed on your system
2. Download the `eve_log_reader.py` file
3. No additional packages need to be installed

## Usage

1. **Run the application**:
   ```bash
   python eve_log_reader.py
   ```

2. **Select Log Directory**:
   - The app will automatically try to find your EVE Online logs
   - Common locations include:
     - `~/Documents/EVE/logs`
     - `~/AppData/Local/CCP/EVE/logs`
     - `C:/Users/Public/Documents/EVE/logs`
   - Use the "Browse" button to manually select a different directory

3. **Configure Recent Log Filters**:
   - **Max days old**: Set how many days back to look (default: 1 day)
   - **Max files to show**: Set maximum number of recent files to monitor (default: 10)
   - Click "Apply Filters" to update the display

4. **Automatic Recent File Detection**:
   - The app automatically detects recent log files based on filename timestamps
   - Files are sorted by UTC timestamp (newest first)
   - Only recent files within your specified time range are monitored

5. **View Recent Combined Logs**:
   - Log entries from recent files are displayed in one unified view
   - Each entry shows: `[Timestamp] [Source File] Log Content`
   - Newest entries appear at the top
   - Use the scrollbar to navigate through the content

6. **Auto-refresh** (Enabled by default):
   - Automatically checks for file changes every 3 seconds
   - Only refreshes when recent files actually change
   - Uncheck to disable if needed

7. **Additional Controls**:
   - **Refresh Recent**: Manually refresh recent log files
   - **Clear Display**: Clear the current display
   - **Export Recent Logs**: Save recent logs to a single text file

## EVE Log Filename Format

The app recognizes EVE Online log filenames with UTC timestamps:
- **Format**: `YYYYMMDD_HHMMSS_characterID.txt`
- **Example**: `20250809_164834_94266210.txt`
  - Date: `20250809` (August 9, 2025)
  - Time: `164834` (16:48:34 UTC)
  - Character ID: `94266210`

## Supported Log Formats

The application automatically monitors various log file types:
- `.log` files
- `.txt` files  
- `.xml` files

## Timestamp Recognition

The app recognizes common EVE Online log timestamp formats:
- `YYYY-MM-DD HH:MM:SS`
- `MM/DD/YYYY HH:MM:SS`
- `HH:MM:SS` (assumes current date)

## How Recent Log Filtering Works

1. **Filename Parsing**: Scans log filenames for UTC timestamp patterns
2. **Time Filtering**: Only includes files within the specified days old range
3. **File Limiting**: Limits to the specified maximum number of recent files
4. **Content Reading**: Reads only the filtered recent files
5. **Entry Combination**: Combines all entries into a single dataset
6. **Timestamp Sorting**: Sorts all entries by timestamp (newest first)
7. **Display**: Shows unified timeline with source file information
8. **Change Detection**: Monitors only recent files for updates

## Benefits of Recent Log Filtering

- **Performance**: Only processes recent, relevant log files
- **Focus**: Shows only current EVE Online session activity
- **Efficiency**: Reduces memory usage and processing time
- **Relevance**: Eliminates old, outdated log information
- **Real-time**: Perfect for monitoring current gaming sessions
- **Configurable**: Adjust time range and file limits as needed

## Filter Settings

### **Max Days Old (1-30)**
- **1 day**: Only show logs from the last 24 hours
- **7 days**: Show logs from the last week
- **30 days**: Show logs from the last month

### **Max Files to Show (5-50)**
- **5 files**: Monitor only the 5 most recent log files
- **10 files**: Default setting for balanced performance
- **50 files**: Monitor up to 50 recent files

## Troubleshooting

- **No logs found**: Make sure EVE Online is installed and has generated log files
- **No recent logs**: Try increasing the "Max days old" setting
- **Encoding issues**: The app uses UTF-8 with error handling for compatibility
- **Performance**: Recent file filtering ensures optimal performance
- **Memory usage**: Only recent files are loaded into memory

## EVE Online Log Locations

EVE Online typically stores logs in these locations:
- **Documents**: `~/Documents/EVE/logs/`
- **AppData**: `~/AppData/Local/CCP/EVE/logs/`
- **Public**: `C:/Users/Public/Documents/EVE/logs/`

## Contributing

Feel free to modify the code to add features like:
- Filtering by log entry type or source file
- Search functionality across recent logs
- Different sorting options
- Log entry highlighting
- Custom log format support
- Advanced timestamp filtering options

## License

This project is open source and available under the MIT License.
