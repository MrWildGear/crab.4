# 🌐 **Google Form Integration Guide**

## 📋 **Overview**

The EVE Log Reader now includes **automatic Google Form submission** for beacon session data. When you click "Submit Data" after completing a beacon session, the application will:

1. ✅ Save data to local CSV file
2. 🌐 Submit data to Google Form (if configured)
3. 🔄 Reset beacon tracking for new session

## 🎯 **What You Need to Do**

### **Step 1: Create a Google Form**

1. **Go to [Google Forms](https://forms.google.com)**
2. **Create a new form** with the title "EVE Beacon Session Data"
3. **Add the following questions** in this exact order:

| Question Type | Question Text | Required |
|---------------|---------------|----------|
| **Short answer** | Beacon ID | ✅ Yes |
| **Date/Time** | Beacon Start Time | ✅ Yes |
| **Date/Time** | Beacon End Time | ✅ Yes |
| **Short answer** | Total Duration | ✅ Yes |
| **Number** | Total CRAB Bounty (ISK) | ✅ Yes |
| **Number** | Rogue Drone Data Amount | ✅ Yes |
| **Number** | Rogue Drone Data Value (ISK) | ✅ Yes |
| **Number** | Total Loot Value (ISK) | ✅ Yes |
| **Long answer** | Loot Details | ✅ Yes |
| **Short answer** | Source Log File | ✅ Yes |
| **Date/Time** | Export Date | ✅ Yes |

### **Step 2: Get the Form Submission URL**

1. **Click the "Send" button** in your Google Form
2. **Click the "Link" tab**
3. **Copy the form URL** (it will look like: `https://docs.google.com/forms/d/e/1FAIpQLSd.../viewform`)
4. **Convert to submission URL** by replacing `/viewform` with `/formResponse`

**Example:**
- **View URL**: `https://docs.google.com/forms/d/e/1FAIpQLSd.../viewform`
- **Submission URL**: `https://docs.google.com/forms/d/e/1FAIpQLSd.../formResponse`

### **Step 3: Get the Entry IDs**

1. **Open your Google Form in a web browser**
2. **Right-click and "View Page Source"**
3. **Search for "entry."** in the HTML source
4. **Note down the entry IDs** for each field:

```html
<!-- Example from HTML source -->
<input type="text" name="entry.123456789" value="">
<input type="text" name="entry.234567890" value="">
<input type="text" name="entry.345678901" value="">
<!-- etc... -->
```

**Important**: Each field will have a unique entry ID like `entry.123456789`

## 🔧 **Configuration in EVE Log Reader**

### **Step 1: Open Configuration**

1. **Run the EVE Log Reader application**
2. **Click the "Form Config" button** in the CONCORD Rogue Analysis Beacon frame
3. **Configuration window will open**

### **Step 2: Enter Form Details**

1. **Form Submission URL**: Paste your form submission URL
2. **Field Mappings**: Enter the entry IDs for each field

**Example Field Mappings:**
```
Beacon ID: entry.123456789
Beacon Start: entry.234567890
Beacon End: entry.345678901
Total Time: entry.456789012
CRAB Bounty: entry.567890123
Rogue Data Amount: entry.678901234
Rogue Data Value: entry.789012345
Total Loot Value: entry.890123456
Loot Details: entry.901234567
Source File: entry.012345678
Export Date: entry.123456789
```

### **Step 3: Test and Save**

1. **Click "Test Form Submission"** to verify everything works
2. **Click "Save Configuration"** to save your settings
3. **Configuration is saved** to `google_form_config.json`

## 🧪 **Testing the Integration**

### **Test with Sample Data**

1. **Click "Test Form Submission"** in the config window
2. **Application will submit test data** to your form
3. **Check your Google Form** to see the test entry
4. **Verify all fields are populated correctly**

### **Test with Real Beacon Session**

1. **Complete a beacon session** in EVE Online
2. **Copy loot data to clipboard**
3. **Click "Submit Data"** in the application
4. **Check both local CSV and Google Form**

## 📊 **What Gets Submitted**

### **Automatic Data Collection**

When you click "Submit Data", the application automatically:

- **📋 Reads clipboard data** (loot information)
- **🔍 Parses loot details** (Rogue Drone Data, values, etc.)
- **⏱️ Calculates session time** (start to finish)
- **💰 Tracks CRAB bounties** (total ISK earned)
- **🆔 Generates Beacon ID** (unique session identifier)
- **📁 Records source file** (log file that triggered beacon)

### **Data Sent to Google Form**

| Field | Example Value | Description |
|-------|---------------|-------------|
| **Beacon ID** | `202508091648349426621020250810003849` | Unique session identifier |
| **Beacon Start** | `2025-08-10 00:38:49` | When beacon was activated |
| **Beacon End** | `2025-08-10 01:15:23` | When session was completed |
| **Total Duration** | `0:36:34` | Total time running beacon |
| **CRAB Bounty** | `1,250,000` | Total ISK earned from rats |
| **Rogue Data Amount** | `1229` | Units of Rogue Drone Data |
| **Rogue Data Value** | `122,900,000` | ISK value of Rogue Data |
| **Total Loot Value** | `135,000,000` | Total value of all loot |
| **Loot Details** | `[{'name': 'Rogue Drone...'}]` | Detailed loot breakdown |
| **Source File** | `20250809_16483494266210.txt` | Log file that triggered beacon |
| **Export Date** | `2025-08-15 16:39:00` | When data was submitted |

## 🚀 **Benefits of Google Form Integration**

### **For Individual Users**
- **📈 Track performance** over multiple sessions
- **📊 Analyze earnings** and loot patterns
- **🔄 Automatic backup** of session data
- **📱 Access data** from anywhere via Google Sheets

### **For Fleet Leaders**
- **👥 Centralized data collection** from multiple pilots
- **📊 Fleet performance analytics** and reporting
- **💰 Revenue tracking** across all accounts
- **📈 Trend analysis** and optimization

### **For Data Analysis**
- **📊 Export to Google Sheets** for advanced analysis
- **📈 Create charts and graphs** of performance
- **🔍 Filter and sort** sessions by various criteria
- **📤 Share data** with team members

## ⚠️ **Troubleshooting**

### **Common Issues**

#### **1. Form Submission Fails**
- **Check form URL** - make sure it ends with `/formResponse`
- **Verify entry IDs** - ensure they match your form exactly
- **Check internet connection** - form submission requires internet access

#### **2. Data Not Appearing in Form**
- **Check form settings** - ensure form is accepting responses
- **Verify field types** - make sure field types match the data being sent
- **Check form quotas** - Google Forms have response limits

#### **3. Configuration Not Saving**
- **Check file permissions** - ensure the app can write to the directory
- **Verify JSON format** - check `google_form_config.json` file
- **Restart application** - configuration is loaded on startup

### **Error Messages**

| Error | Solution |
|-------|----------|
| **"Form URL not configured"** | Enter valid form submission URL |
| **"Fields not mapped"** | Configure at least one field mapping |
| **"Network error"** | Check internet connection |
| **"Form submission timed out"** | Check form URL and try again |
| **"Configuration not found"** | Use "Form Config" button to set up |

## 🔒 **Privacy and Security**

### **Data Handling**
- **Local storage**: All data is saved locally first
- **Form submission**: Only configured data is sent to Google
- **No tracking**: Application doesn't collect personal information
- **User control**: You control what data gets submitted

### **Google Forms Security**
- **Google's security**: Forms are hosted on Google's secure servers
- **Access control**: You control who can view form responses
- **Data ownership**: You own all data submitted to your forms

## 📱 **Mobile Access**

### **View Data Anywhere**
1. **Form responses** are automatically saved to Google Sheets
2. **Access via mobile** using Google Sheets app
3. **Real-time updates** as new sessions are submitted
4. **Offline access** with Google Sheets offline mode

### **Notifications**
- **Email notifications** when new responses are received
- **Mobile push notifications** via Google Forms app
- **Instant access** to fleet performance data

## 🎯 **Next Steps**

### **Immediate Actions**
1. **Create your Google Form** with the required fields
2. **Get the form submission URL** and entry IDs
3. **Configure the application** using "Form Config" button
4. **Test the integration** with a sample submission

### **Advanced Features**
1. **Set up Google Sheets** for data analysis
2. **Create automated reports** and dashboards
3. **Share data** with fleet members
4. **Track performance metrics** over time

---

## 🎉 **Ready to Go!**

Your EVE Log Reader is now equipped with **automatic Google Form integration**! 

**Every beacon session** will automatically:
- ✅ Save to local CSV
- 🌐 Submit to Google Form
- 📊 Update your data collection
- 🔄 Reset for next session

**No more manual data entry** - just complete your beacon and click "Submit Data"!

---

**Need help?** Check the troubleshooting section above or review the console output for detailed error messages.
