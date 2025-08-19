# 🦀 CRAB Tracker

**EVE Online Log Reader & Beacon Analysis Tool**

A comprehensive Python application for monitoring EVE Online game logs, tracking CONCORD Rogue Analysis Beacon sessions, and analyzing CRAB bounty data with real-time monitoring and Google Forms integration.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/yourusername/crab-tracker)

## ✨ Features

### 🎯 **Core Functionality**
- **Real-time Log Monitoring** - Automatically detects and monitors EVE Online log files
- **Smart File Filtering** - Only processes recent log files based on configurable time limits
- **Content Hash Detection** - Reliable change detection using MD5 hashing
- **Multi-file Support** - Monitors multiple log files simultaneously

### 🎮 **EVE Online Specific**
- **Beacon Tracking** - Tracks CONCORD Rogue Analysis Beacon sessions
- **Bounty Monitoring** - Monitors and calculates bounty earnings
- **CRAB Sessions** - Special tracking for CRAB-specific bounty sessions
- **Log Parsing** - Intelligent parsing of EVE Online log formats

### 📊 **Data Management**
- **Export Functions** - Export logs and session data to CSV/TXT formats
- **Google Forms Integration** - Submit beacon session data to Google Forms
- **Session Management** - Track and manage multiple gaming sessions
- **Data Visualization** - Real-time display of tracking information

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (Windows 10/11 optimized)
- **EVE Online** installed and generating log files

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/crab-tracker.git
   cd crab-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python src/scripts/run.py
   ```

### Alternative Launch Methods
- **Direct execution**: `python src/crab_tracker/main.py`
- **Package installation**: `pip install -e .` then `crab-tracker`

## 🏗️ Project Structure

```
crab-tracker/
├── src/                           # Source code
│   ├── crab_tracker/             # Main package
│   │   ├── gui/                  # User interface components
│   │   ├── core/                 # Core functionality modules
│   │   ├── services/             # External services integration
│   │   └── utils/                # Utility functions
│   ├── scripts/                  # Build and utility scripts
│   └── resources/                # Configuration and resources
├── tests/                        # Comprehensive test suite
├── docs/                         # Detailed documentation
├── requirements.txt               # Runtime dependencies
├── requirements-dev.txt           # Development dependencies
├── pyproject.toml                # Modern Python configuration
└── setup.py                      # Package setup
```

## ⚙️ Configuration

### Google Forms Integration
Configure beacon session data submission in `src/resources/config/google_forms.json`:

```json
{
  "form_url": "https://docs.google.com/forms/d/e/.../formResponse",
  "field_mappings": {
    "Beacon ID": "entry.1520906809",
    "Total Duration": "entry.66008066",
    "Total CRAB Bounty": "entry.257705337"
  }
}
```

### Log Directory Settings
- **Auto-detection**: Automatically finds EVE Online log directories
- **Manual selection**: Use the Browse button to select custom directories
- **Filter settings**: Configure maximum file age and count limits

## 🎮 Usage

### Basic Operation
1. **Launch the application**
2. **Select log directory** (auto-detected by default)
3. **Configure filters** (days old, max files)
4. **Start monitoring** (enabled by default)
5. **View real-time updates**

### Beacon Tracking
1. **Start a gaming session**
2. **Activate a CONCORD Rogue Analysis Beacon**
3. **Monitor progress** in real-time with countdown timer
4. **Use CRAB session controls**:
   - **End CRAB Failed** (red button) - Mark session as failed
   - **Submit Data** (green button) - Complete session and submit data
5. **Export data** to CSV format
6. **Debug tools** available for testing and troubleshooting

### Bounty Monitoring
1. **Start bounty session** when beginning gameplay
2. **Monitor earnings** in real-time
3. **Track CRAB sessions** separately
4. **Export session data** for analysis

## 🔨 Building

### Development Build
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Build executable
python src/scripts/build.py
```

### Production Build
```bash
# Use the batch script (Windows)
src\scripts\build_anti_malware.bat

# Or use PyInstaller directly
pyinstaller --onefile --windowed src/crab_tracker/main.py
```

## 🧪 Development

### Code Quality
- **Formatting**: [Black](https://black.readthedocs.io/) (88 character line length)
- **Linting**: [Flake8](https://flake8.pycqa.org/)
- **Type checking**: [MyPy](https://mypy-lang.org/)
- **Testing**: [Pytest](https://docs.pytest.org/) with coverage

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=crab_tracker

# Run specific test file
pytest tests/test_time_utils.py
```

### Adding Features
1. **Create feature branch**
2. **Implement functionality** in appropriate module
3. **Add tests** in `tests/` directory
4. **Update documentation**
5. **Submit pull request**

## 📚 Documentation

- **[Main Documentation](docs/README.md)** - Comprehensive usage guide
- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[Building Guide](docs/BUILDING.md)** - Build and deployment guide
- **[API Reference](docs/API.md)** - Developer API documentation

## 🐛 Troubleshooting

### Common Issues
- **Log directory not found**: Check EVE Online installation path
- **Permission errors**: Run as administrator if needed
- **Import errors**: Ensure all dependencies are installed
- **Build failures**: Check PyInstaller installation

### Logs
Application logs are stored in the `logs/` directory:
- `crab_tracker.log`: Main application log
- `session_*.log`: Individual session logs

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for:
- Code style requirements
- Testing requirements
- Pull request process
- Issue reporting

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/crab-tracker/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/crab-tracker/discussions)
- **Documentation**: [Documentation](docs/README.md)
- **Community**: EVE Online community forums

## 📈 Changelog

### Version 1.0.0
- Initial release with modern Python project structure
- Core log monitoring functionality
- Beacon tracking system
- Bounty monitoring
- Google Forms integration
- Comprehensive test suite
- Modern development tools and configuration

## 🙏 Acknowledgments

- **EVE Online Community** - For feedback and testing
- **Python Community** - For excellent tools and libraries
- **Open Source Contributors** - For making this project possible

---

**Made with ❤️ for the EVE Online community**

*Fly safe, capsuleer!*
