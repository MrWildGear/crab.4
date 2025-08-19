# CRAB Tracker Documentation

Welcome to the CRAB Tracker documentation! This guide will help you understand, install, and use the CRAB Tracker application.

## What is CRAB Tracker?

CRAB Tracker is a comprehensive Python application designed for EVE Online players to monitor game logs, track CONCORD Rogue Analysis Beacon sessions, and analyze CRAB bounty data. It provides real-time monitoring, data export capabilities, and Google Forms integration for community data collection.

## Features

### Core Functionality
- **Real-time Log Monitoring**: Automatically detects and monitors EVE Online log files
- **Smart File Filtering**: Only processes recent log files based on configurable time limits
- **Content Hash Detection**: Reliable change detection using MD5 hashing
- **Multi-file Support**: Monitors multiple log files simultaneously

### EVE Online Specific
- **Beacon Tracking**: Tracks CONCORD Rogue Analysis Beacon sessions
- **Bounty Monitoring**: Monitors and calculates bounty earnings
- **CRAB Sessions**: Special tracking for CRAB-specific bounty sessions
- **Log Parsing**: Intelligent parsing of EVE Online log formats

### Data Management
- **Export Functions**: Export logs and session data to CSV/TXT formats
- **Google Forms Integration**: Submit beacon session data to Google Forms
- **Session Management**: Track and manage multiple gaming sessions
- **Data Visualization**: Real-time display of tracking information

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (optimized for EVE Online log locations)
- EVE Online installed and generating log files

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

## Project Structure

```
crab-tracker/
├── src/                           # Source code
│   ├── crab_tracker/             # Main package
│   │   ├── gui/                  # User interface
│   │   ├── core/                 # Core functionality
│   │   ├── services/             # External services
│   │   └── utils/                # Utility functions
│   ├── scripts/                  # Build and utility scripts
│   └── resources/                # Configuration and resources
├── tests/                        # Test suite
├── docs/                         # Documentation
├── requirements.txt               # Runtime dependencies
├── requirements-dev.txt           # Development dependencies
├── pyproject.toml                # Modern Python configuration
└── setup.py                      # Package setup
```

## Configuration

### Google Forms Integration
The application can submit beacon session data to Google Forms. Configure this in `src/resources/config/google_forms.json`:

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

## Usage

### Basic Operation
1. **Launch the application**
2. **Select log directory** (auto-detected by default)
3. **Configure filters** (days old, max files)
4. **Start monitoring** (enabled by default)
5. **View real-time updates**

### Beacon Tracking
1. **Start a gaming session**
2. **Activate a CONCORD Rogue Analysis Beacon**
3. **Monitor progress** in real-time
4. **Complete the beacon** to capture session data
5. **Export or submit data** as needed

### Bounty Monitoring
1. **Start bounty session** when beginning gameplay
2. **Monitor earnings** in real-time
3. **Track CRAB sessions** separately
4. **Export session data** for analysis

## Building

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

## Development

### Code Style
- **Formatting**: Black (88 character line length)
- **Linting**: Flake8
- **Type checking**: MyPy
- **Testing**: Pytest with coverage

### Adding Features
1. **Create feature branch**
2. **Implement functionality** in appropriate module
3. **Add tests** in `tests/` directory
4. **Update documentation**
5. **Submit pull request**

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=crab_tracker

# Run specific test file
pytest tests/test_time_utils.py
```

## Troubleshooting

### Common Issues
- **Log directory not found**: Check EVE Online installation path
- **Permission errors**: Run as administrator if needed
- **Import errors**: Ensure all dependencies are installed
- **Build failures**: Check PyInstaller installation

### Logs
Application logs are stored in the `logs/` directory:
- `crab_tracker.log`: Main application log
- `session_*.log`: Individual session logs

## Contributing

We welcome contributions! Please see our contributing guidelines for:
- Code style requirements
- Testing requirements
- Pull request process
- Issue reporting

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: This documentation
- **Community**: EVE Online community forums

## Changelog

### Version 1.0.0
- Initial release
- Core log monitoring functionality
- Beacon tracking system
- Bounty monitoring
- Google Forms integration
- Modern Python project structure
