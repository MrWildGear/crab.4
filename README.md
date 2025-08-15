# EVE Online Log Reader

A powerful Python application for monitoring and reading EVE Online game logs in real-time with advanced filtering and dark mode interface.

## 🌟 Features

### **Real-Time Log Monitoring**
- **High-frequency monitoring** (1-second intervals) for instant updates
- **Content hash detection** - catches all file changes reliably
- **Multi-file monitoring** - monitors all log files simultaneously
- **Automatic refresh** when changes are detected

### **Smart Log Filtering**
- **UTC timestamp recognition** from EVE log filenames (`YYYYMMDD_HHMMSS_characterID.txt`)
- **Recent logs only** - configurable "max days old" filter
- **File limit control** - set maximum number of files to display
- **Performance optimized** - only processes recent, relevant logs

### **User Interface**
- **Dark mode theme** - easy on the eyes for long gaming sessions
- **Real-time status updates** - shows monitoring status and last refresh time
- **Source file tracking** - each log entry shows which file it came from
- **Responsive design** - handles large log files efficiently

### **Advanced Features**
- **Export functionality** - save filtered logs to text files
- **Debug tools** - file modification times and content hash information
- **Test log creation** - for testing and debugging
- **Manual refresh** - immediate refresh when needed

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Windows (tested on Windows 10/11)

### Quick Start
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/eve-log-reader.git
   cd eve-log-reader
   ```

2. **Install dependencies**
   ```bash
   pip install -r Src/requirements.txt
   ```

3. **Run the application**
   ```bash
   python Src/eve_log_reader.py
   ```

### Alternative Launch Methods
- **Batch file**: Double-click `Src\run_eve_log_reader.bat`
- **Direct execution**: Navigate to `Src` folder and run `python eve_log_reader.py`

## 📁 Project Structure

```
eve-log-reader/
├── Src/                          # Source code directory
│   ├── eve_log_reader.py         # Main application
│   ├── README.md                 # Detailed documentation
│   ├── test_app.py               # Testing and debugging tools
│   ├── run_eve_log_reader.bat    # Windows batch launcher
│   └── requirements.txt          # Python dependencies
├── README.md                     # This file (GitHub main page)
└── .gitignore                   # Git ignore file
```

## 🎮 How It Works

### **EVE Log Detection**
The app automatically finds your EVE Online log directory:
- **Primary**: `~/Documents/EVE/logs/Gamelogs/`
- **Fallback**: `~/Documents/EVE/logs/`
- **Alternative**: `~/AppData/Local/CCP/EVE/logs/`

### **Log File Format Support**
- **EVE format**: `YYYYMMDD_HHMMSS_characterID.txt`
- **Standard formats**: `.log`, `.txt`, `.xml`
- **Timestamp extraction** from both filenames and content

### **Change Detection System**
1. **Content hashing** (MD5) - most reliable method
2. **Modification time** - secondary detection
3. **File size** - tertiary detection
4. **Real-time monitoring** every 1 second

## ⚙️ Configuration

### **Filter Settings**
- **Max days old**: 1-30 days (default: 1 day)
- **Max files to show**: 5-50 files (default: 10 files)
- **High-frequency monitoring**: Enable/disable 1-second monitoring
- **Content hash detection**: Enable/disable hash-based change detection

### **Interface Options**
- **Dark theme**: Always enabled for gaming comfort
- **Font size**: Monospace font for log readability
- **Status display**: Real-time monitoring information

## 🔧 Usage

### **Basic Operation**
1. **Launch the app** - it automatically finds your EVE logs
2. **Adjust filters** - set how many days old and files to show
3. **Monitor in real-time** - logs update automatically when changes occur
4. **Export when needed** - save filtered logs to external files

### **Advanced Features**
- **Show File Times**: View detailed modification times for debugging
- **Show File Hashes**: Monitor content hash changes
- **Create Test Log**: Generate test files for testing
- **Manual Refresh**: Force immediate refresh

### **Keyboard Shortcuts**
- **Ctrl+A**: Select all text
- **Ctrl+C**: Copy selected text
- **Ctrl+F**: Find in logs (if implemented)
- **F5**: Manual refresh

## 🐛 Troubleshooting

### **Common Issues**

#### **No Logs Found**
- Verify EVE Online is installed and has generated logs
- Check the log directory path in the app
- Ensure log files have `.txt`, `.log`, or `.xml` extensions

#### **Auto-refresh Not Working**
- Enable "High-frequency monitoring (1s)" checkbox
- Check "Content hash detection" is enabled
- Verify log files are being updated by EVE Online
- Use "Show File Times" to debug file modification issues

#### **Performance Issues**
- Reduce "Max files to show" setting
- Reduce "Max days old" setting
- Disable high-frequency monitoring if not needed

### **Debug Tools**
- **Console output**: Check terminal/console for detailed logging
- **File Times**: Shows when files were last modified
- **File Hashes**: Shows content hash changes
- **Test Log**: Creates test files to verify monitoring

## 🤝 Contributing

Contributions are welcome! Here are some ways to help:

### **Bug Reports**
- Use GitHub Issues to report bugs
- Include detailed steps to reproduce
- Attach relevant log files or screenshots

### **Feature Requests**
- Suggest new features via GitHub Issues
- Describe the use case and benefits
- Consider implementation complexity

### **Code Contributions**
- Fork the repository
- Create a feature branch
- Submit a pull request with clear description

### **Documentation**
- Improve README files
- Add code comments
- Create usage examples

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **EVE Online** community for log format insights
- **Python Tkinter** for the GUI framework
- **Open source contributors** who inspired this project

## 📞 Support

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For general questions and help
- **Wiki**: For detailed documentation (if created)

---

**Happy EVE Online log monitoring!** 🚀

*Built with Python and designed for gamers who need real-time log insights.*
