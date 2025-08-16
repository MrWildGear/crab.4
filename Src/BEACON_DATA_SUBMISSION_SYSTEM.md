# 🚀 **Beacon Data Submission System**

## 📋 **Overview**

The EVE Log Reader now includes a comprehensive **Beacon Data Submission System** that automatically processes clipboard data when a CONCORD Rogue Analysis Beacon session ends. This system extracts loot information, calculates session statistics, and stores everything in a CSV file for later analysis and reporting.

## 🎯 **What Happens When "Submit Data" is Clicked**

### **1. Clipboard Data Retrieval**
- Automatically reads data from the user's clipboard
- Expects EVE Online loot format (tab-separated values)
- Handles the specific format: `Item Name | Amount | Category | Volume | Value`

### **2. Loot Data Parsing**
- **Rogue Drone Infestation Data**: Automatically detected and counted
- **All Other Loot**: Parsed and categorized with amounts and values
- **Value Calculation**: Total loot value automatically calculated
- **Error Handling**: Graceful fallback if parsing fails

### **3. Session Data Collection**
- **Beacon ID**: Unique identifier from the current session
- **Time Tracking**: Start time, end time, and total duration
- **CRAB Bounty**: Total ISK earned during the beacon session
- **Source File**: Log file that triggered the beacon
- **Export Date**: When the data was submitted

### **4. CSV Storage**
- **File**: `beacon_sessions.csv` (created automatically)
- **Format**: Comma-separated values with headers
- **Append Mode**: New sessions added to existing file
- **Encoding**: UTF-8 for international character support

### **5. Beacon Reset**
- **Session End**: Current beacon marked as completed
- **Countdown Stop**: Timer stops and shows final duration
- **Status Update**: UI shows "Status: Completed"
- **Fresh Start**: All tracking reset for new beacon session

## 📊 **CSV Data Structure**

### **Headers**
```csv
Beacon ID,Beacon Start,Beacon End,Total Time,Total CRAB Bounty (ISK),Rogue Drone Data Amount,Rogue Drone Data Value (ISK),Total Loot Value (ISK),Loot Details,Source File,Export Date
```

### **Example Row**
```csv
202508091648349426621020250810003849,2025-08-10 00:38:49,2025-08-10 01:15:23,0:36:34,1250000,1229,122900000,135000000,"[{'name': 'Rogue Drone Infestation Data', 'amount': 1229, 'value': 122900000}]",20250809_164834_94266210.txt,2025-08-15 16:39:00
```

## 🔍 **Loot Parsing Details**

### **Supported Format**
```
Exigent Heavy Drone Projection Mutaplasmid        1        Mutaplasmids                        1 m3        1 588 605,26 ISK
Exigent Medium Drone Projection Mutaplasmid        1        Mutaplasmids                        1 m3        6 109 861,70 ISK
Exigent Sentry Drone Firepower Mutaplasmid        1        Mutaplasmids                        1 m3        7 017 969,69 ISK
Rogue Drone Infestation Data        1229        Rogue Drone Analysis Data                        12,29 m3        122 900 000,00 ISK
```

### **Parsing Logic**
1. **Split by Multiple Spaces**: Uses `        ` (4 spaces) as separator
2. **Field Extraction**: Item Name, Amount, Category, Volume, Value
3. **Special Detection**: "Rogue Drone Infestation Data" automatically identified
4. **Value Conversion**: Removes "ISK", spaces, and converts commas to decimals
5. **Error Handling**: Defaults to safe values if parsing fails

## 🖥️ **User Interface Features**

### **Submit Data Button**
- **Location**: CONCORD Rogue Analysis Beacon frame
- **Color**: Green background (#44ff44)
- **Function**: Triggers the complete submission process
- **Confirmation**: Asks user to confirm before proceeding

### **View Sessions Button**
- **Location**: CONCORD Rogue Analysis Beacon frame
- **Color**: Dark background (#1e1e1e)
- **Function**: Opens session history viewer
- **Display**: Shows all recorded sessions in table format

### **Success Messages**
- **Completion Dialog**: Shows session summary with all key metrics
- **CSV Status**: Confirms data was saved successfully
- **Reset Confirmation**: Indicates beacon tracking has been reset

## 📈 **Session History Viewer**

### **Features**
- **Table Display**: Formatted view of all sessions
- **Summary Statistics**: Total sessions, bounties, and loot values
- **Export Function**: Save sessions to text file
- **Scrollable Interface**: Horizontal and vertical scrolling support

### **Display Columns**
- **Beacon ID**: Shortened for readability
- **Start/End Time**: Full timestamp information
- **Duration**: Total beacon run time
- **CRAB Bounty**: ISK earned during session
- **Rogue Data**: Amount of Rogue Drone Infestation Data
- **Loot Value**: Total value of all loot
- **Source File**: Log file that triggered the beacon

### **Summary Statistics**
- **Total Sessions**: Count of all recorded sessions
- **Total CRAB Bounty**: Sum of all ISK earned
- **Total Rogue Data**: Sum of all Rogue Drone Infestation Data
- **Total Loot Value**: Sum of all loot values

## 🔄 **Workflow Example**

### **Step 1: Beacon Activation**
1. User starts CONCORD beacon
2. Beacon ID automatically generated
3. CRAB session begins
4. Bounty tracking starts

### **Step 2: Beacon Completion**
1. Rats stop spawning
2. Loot drops from beacon
3. User copies loot to clipboard
4. User clicks "Submit Data"

### **Step 3: Data Processing**
1. Clipboard data automatically read
2. Loot parsed and categorized
3. Session statistics calculated
4. Data saved to CSV file

### **Step 4: Session Reset**
1. Beacon marked as completed
2. All tracking data cleared
3. UI reset for new session
4. Ready for next beacon

## 📁 **File Management**

### **CSV File**
- **Name**: `beacon_sessions.csv`
- **Location**: Same directory as the executable
- **Format**: Standard CSV with UTF-8 encoding
- **Backup**: Can be copied/moved for safekeeping

### **Export Options**
- **Text Export**: Detailed session information
- **Format**: Human-readable with clear sections
- **Location**: User-selected save location
- **Content**: Full session details and summary

## 🛡️ **Error Handling**

### **Clipboard Errors**
- **Empty Clipboard**: Warns user to copy loot data first
- **Invalid Format**: Graceful fallback with error logging
- **Access Denied**: Clear error message with troubleshooting tips

### **File System Errors**
- **Permission Issues**: Detailed error messages
- **Disk Space**: Checks available space before writing
- **File Locked**: Handles concurrent access gracefully

### **Data Validation**
- **Missing Fields**: Defaults to safe values
- **Invalid Numbers**: Converts to 0 with logging
- **Corrupted Data**: Skips problematic entries

## 🚀 **Future Enhancements**

### **Potential Features**
1. **Data Analytics**: Charts and graphs of session performance
2. **Fleet Integration**: Share session data across multiple accounts
3. **Market Integration**: Real-time ISK value calculations
4. **Backup System**: Automatic CSV backup to cloud storage
5. **Advanced Filtering**: Search and filter sessions by criteria

### **Export Formats**
1. **JSON**: Machine-readable data format
2. **Excel**: Direct spreadsheet export
3. **Database**: SQLite or MySQL integration
4. **API**: REST API for external applications

## 📋 **Usage Instructions**

### **For Users**
1. **Complete Beacon Session**: Run beacon until rats stop spawning
2. **Copy Loot Data**: Select and copy loot from EVE Online
3. **Click Submit Data**: Use the green "Submit Data" button
4. **Confirm Action**: Review and confirm the submission
5. **View History**: Use "View Sessions" to see all recorded sessions

### **For Developers**
1. **CSV Format**: Standard comma-separated values
2. **Data Structure**: Well-defined column headers
3. **Error Handling**: Comprehensive exception handling
4. **Logging**: Detailed console output for debugging
5. **Modular Design**: Easy to extend and modify

## 🎉 **Benefits**

### **For Users**
- **Automatic Tracking**: No manual data entry required
- **Session History**: Complete record of all beacon runs
- **Performance Analysis**: Track ISK earnings over time
- **Data Export**: Easy sharing and backup of session data

### **For Fleet Leaders**
- **Coordinated Tracking**: Multiple accounts can share data
- **Performance Metrics**: Compare beacon efficiency across pilots
- **Resource Planning**: Track Rogue Drone Infestation Data collection
- **Fleet Analytics**: Overall fleet performance statistics

---

**🎯 The Beacon Data Submission System is now fully integrated and ready for production use!**

This system provides a complete solution for tracking, analyzing, and reporting CONCORD Rogue Analysis Beacon sessions, making it easy to manage multiple beacon runs and analyze performance over time.
