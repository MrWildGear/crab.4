# Refactored EVE Log Reader

This is a refactored version of the EVE Log Reader that has been restructured for better maintainability, readability, and extensibility.

## Code Structure

The refactored code is organized into several focused modules:

### 1. `config.py`
- **Purpose**: Centralized configuration and constants
- **Contains**: UI settings, log file patterns, directory paths, monitoring intervals
- **Benefits**: Easy to modify settings, no hardcoded values scattered throughout code

### 2. `utils.py`
- **Purpose**: Utility functions for common operations
- **Contains**: File operations, parsing functions, directory finding
- **Benefits**: Reusable functions, easier testing, cleaner main code

### 3. `ui_theme.py`
- **Purpose**: UI theming and styling
- **Contains**: Dark theme application, styled widget creation
- **Benefits**: Consistent UI appearance, easy theme changes, reusable UI components

### 4. `bounty_tracker.py`
- **Purpose**: Bounty tracking and statistics
- **Contains**: `BountyTracker` class and `CRABBountyTracker` subclass
- **Benefits**: Separated concerns, easier to extend bounty functionality

### 5. `concord_tracker.py`
- **Purpose**: CONCORD Rogue Analysis Beacon tracking
- **Contains**: `CONCORDTracker` class with countdown and status management
- **Benefits**: Isolated CONCORD logic, easier to modify countdown behavior

### 6. `log_monitor.py`
- **Purpose**: Log file monitoring and change detection
- **Contains**: `LogMonitor` class for file watching and parsing
- **Benefits**: Separated file monitoring logic, easier to modify monitoring behavior

### 7. `eve_log_reader_refactored.py`
- **Purpose**: Main application class
- **Contains**: UI setup, component coordination, event handling
- **Benefits**: Cleaner main class, focused on orchestration rather than implementation

## Key Improvements

### 1. **Separation of Concerns**
- Each module has a single, well-defined responsibility
- UI logic is separated from business logic
- File monitoring is independent of bounty tracking

### 2. **Modularity**
- Easy to add new features by extending existing classes
- Simple to modify individual components without affecting others
- Clear interfaces between modules

### 3. **Maintainability**
- Smaller, focused classes are easier to understand and modify
- Consistent coding patterns throughout
- Better error handling and logging

### 4. **Extensibility**
- Easy to add new bounty types
- Simple to implement new monitoring features
- Clean plugin-like architecture

### 5. **Testing**
- Individual components can be tested in isolation
- Mock objects can be easily created for testing
- Clear dependencies make testing straightforward

## Usage

### Running the Refactored Version
```bash
cd Src
python eve_log_reader_refactored.py
```

### Adding New Features

#### Adding a New Bounty Type
1. Create a new class inheriting from `BountyTracker`
2. Override methods as needed
3. Add to the main application

#### Adding New Monitoring Features
1. Extend the `LogMonitor` class
2. Add new callback types
3. Implement in the main application

#### Modifying UI
1. Update `ui_theme.py` for new styling
2. Modify the appropriate UI creation method in the main class
3. Update configuration in `config.py` if needed

## Migration from Original

The refactored version maintains the same functionality as the original but with a cleaner structure:

- **Same UI**: All buttons, displays, and controls work identically
- **Same Features**: Bounty tracking, CONCORD monitoring, CRAB sessions
- **Better Code**: More maintainable and easier to extend

## Benefits of Refactoring

1. **Easier Debugging**: Issues are isolated to specific modules
2. **Faster Development**: New features can be added without understanding the entire codebase
3. **Better Collaboration**: Multiple developers can work on different modules
4. **Easier Testing**: Individual components can be unit tested
5. **Cleaner Code**: Each class and method has a single, clear purpose

## Future Enhancements

With this refactored structure, it's now much easier to add:

- New bounty tracking systems
- Different log file formats
- Additional monitoring features
- Plugin system for extensions
- Better error handling and recovery
- Performance optimizations
- Unit tests for each component

## File Organization

```
Src/
├── config.py                          # Configuration constants
├── utils.py                           # Utility functions
├── ui_theme.py                        # UI theming and styling
├── bounty_tracker.py                  # Bounty tracking system
├── concord_tracker.py                 # CONCORD tracking system
├── log_monitor.py                     # Log file monitoring
├── eve_log_reader_refactored.py      # Main application
├── requirements_refactored.txt        # Dependencies (none external)
└── README_REFACTORED.md              # This file
```

The refactored code is now much more maintainable and follows software engineering best practices while preserving all the original functionality.
