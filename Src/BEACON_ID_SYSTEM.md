# 🔗 **CONCORD Rogue Analysis Beacon ID System**

## 📋 **Overview**

The EVE Log Reader now includes a unique **Beacon ID** system that generates a virtually collision-free identifier for each CONCORD Rogue Analysis Beacon session. This system ensures that each beacon run can be uniquely identified and tracked, even when multiple accounts are running beacons simultaneously.

## 🆔 **Beacon ID Format**

### **Structure: `FileTimestamp + CharacterID + BeaconTimestamp`**

- **FileTimestamp**: `YYYYMMDDHHMMSS` (when the log file was created)
- **CharacterID**: Character identifier from the log filename
- **BeaconTimestamp**: `YYYYMMDDHHMMSS` (when the beacon was activated)

### **Example Beacon ID:**
```
File: 20250809_164834_94266210.txt
├── File Date: 2025-08-09
├── File Time: 16:48:34 UTC
├── Character ID: 94266210
├── Beacon Date: 2025-08-10
└── Beacon Time: 00:38:49 UTC

Final Beacon ID: 202508091648349426621020250810003849
```

## 🔧 **How It Works**

### **1. Automatic Detection**
When a CONCORD beacon message is detected in the logs:
```python
# Link start message detected
if concord_message_type == "link_start":
    beacon_timestamp = datetime.now()
    self.concord_link_start = beacon_timestamp
    
    # Generate unique Beacon ID
    self.current_beacon_id = self.generate_beacon_id(source_file, beacon_timestamp)
    self.beacon_source_file = source_file
```

### **2. ID Generation Process**
```python
def generate_beacon_id(self, source_file, beacon_timestamp):
    # Parse filename: YYYYMMDD_HHMMSS_CharacterID.txt
    filename = os.path.basename(source_file)
    parts = filename.replace('.txt', '').split('_')
    
    file_date = parts[0]      # YYYYMMDD
    file_time = parts[1]      # HHMMSS
    character_id = parts[2]   # Character ID
    
    # Format beacon timestamp
    beacon_date = beacon_timestamp.strftime('%Y%m%d')
    beacon_time = beacon_timestamp.strftime('%H%M%S')
    
    # Combine all parts
    beacon_id = f"{file_date}{file_time}{character_id}{beacon_date}{beacon_time}"
    return beacon_id
```

## 🎯 **Use Cases**

### **Single Account, Multiple Beacons**
- Each beacon gets a unique ID based on activation time
- Previous beacon data is overwritten (as intended)
- Beacon ID provides traceability for each run

### **Multiple Accounts, Multiple Beacons**
- Each account's beacon gets a unique ID
- Character ID in filename ensures uniqueness across accounts
- Beacon ID can be shared for coordination

### **Beacon Coordination**
- Share Beacon ID with fleet members
- Track specific beacon runs across multiple accounts
- Reference specific beacon sessions in communications

## 🖥️ **UI Features**

### **Beacon ID Display**
- **Main Display**: Shows full Beacon ID below status information
- **Status Bar**: Shows shortened version (last 12 characters)
- **Copy Button**: One-click copy to clipboard for sharing

### **Visual Indicators**
- **Beacon ID Label**: Monospace font for easy reading
- **Status Updates**: Real-time updates as beacon progresses
- **Source File**: Tracks which log file triggered the beacon

## 📊 **Tracking Information**

### **Stored Data**
- `current_beacon_id`: The unique identifier for current session
- `beacon_source_file`: Source log file that triggered the beacon
- `concord_link_start`: When the beacon linking began
- `concord_link_completed`: Whether linking completed successfully

### **Status States**
- **"Linking"**: Beacon is in linking phase
- **"Active"**: Beacon linking completed successfully
- **"Failed"**: Beacon session marked as failed
- **"Completed"**: Beacon session manually completed

## 🔄 **Session Management**

### **Automatic Session Start**
- CRAB bounty tracking automatically starts with beacon
- Session status syncs with CONCORD beacon status
- Bounty tracking tied to specific beacon ID

### **Session Reset**
- Beacon ID cleared when resetting CONCORD tracking
- All related data (CRAB bounties, timers) reset
- Fresh start for new beacon session

## 🧪 **Testing Features**

### **Test Functions**
- **Test Link Start**: Simulates beacon activation with test ID
- **Test Link Complete**: Simulates beacon completion
- **Copy Beacon ID**: Tests clipboard functionality

### **Test Beacon ID Format**
```
TEST + Current Timestamp
Example: TEST20250815161400
```

## 📋 **Beacon ID Benefits**

### **Uniqueness**
- **Virtually collision-free**: 32+ character alphanumeric ID
- **Time-based**: Includes both file creation and beacon activation times
- **Character-specific**: Includes character ID from filename

### **Traceability**
- **Source tracking**: Know which log file triggered the beacon
- **Time tracking**: Precise activation and completion times
- **Session linking**: Connect bounties to specific beacon runs

### **Coordination**
- **Fleet communication**: Share specific beacon IDs
- **Multi-account tracking**: Distinguish between different accounts
- **Session reference**: Reference specific beacon runs

## 🚀 **Future Enhancements**

### **Potential Features**
1. **Beacon History**: Store multiple beacon sessions
2. **Beacon Analytics**: Track performance across sessions
3. **Fleet Integration**: Share beacon data across multiple instances
4. **Export Functionality**: Export beacon session data

### **Multi-Beacon Support**
- **Concurrent beacons**: Handle multiple active beacons
- **Beacon queuing**: Queue system for multiple beacon requests
- **Session management**: Manage multiple beacon sessions simultaneously

## 📝 **Example Usage**

### **Scenario: Fleet Beacon Coordination**
1. **Account A** drops beacon, gets ID: `202508091648349426621020250810003849`
2. **Account A** shares Beacon ID with fleet
3. **Account B** references this ID in communications
4. **Account C** can track the same beacon session
5. **All accounts** coordinate using the unique identifier

### **Scenario: Multiple Beacon Runs**
1. **First beacon**: ID `202508091648349426621020250810003849`
2. **Second beacon**: ID `202508091648349426621020250810015623`
3. **Third beacon**: ID `202508091648349426621020250810023045`
4. Each run gets a unique identifier for tracking

## 🔍 **Technical Details**

### **ID Collision Probability**
- **32+ characters**: Provides 10^32+ possible combinations
- **Time-based**: Ensures temporal uniqueness
- **Character-specific**: Ensures account uniqueness
- **Practical collision**: Virtually impossible in real-world usage

### **Performance Impact**
- **Minimal overhead**: ID generation only when beacon starts
- **Efficient parsing**: Simple string operations
- **Memory efficient**: Single string storage
- **Real-time updates**: No performance impact on monitoring

---

**🎉 The Beacon ID system is now fully integrated and ready for use!**

Each CONCORD Rogue Analysis Beacon will automatically receive a unique identifier that can be used for coordination, tracking, and reference across multiple accounts and sessions.
