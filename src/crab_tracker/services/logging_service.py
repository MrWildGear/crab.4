"""
Logging service for CRAB Tracker application.

This module provides centralized logging functionality for the application,
including file logging and console output.
"""

import os
import logging
from datetime import datetime
from pathlib import Path


class LoggingService:
    """Centralized logging service for CRAB Tracker."""
    
    def __init__(self, log_level=logging.INFO):
        """
        Initialize the logging service.
        
        Args:
            log_level: Logging level (default: INFO)
        """
        self.log_level = log_level
        self.logger = None
        self.logs_dir = None
        
    def setup_logging(self, logs_dir=None):
        """
        Setup logging configuration.
        
        Args:
            logs_dir (str, optional): Directory for log files
        """
        if logs_dir is None:
            # Create logs directory in the current working directory
            self.logs_dir = Path.cwd() / "logs"
        else:
            self.logs_dir = Path(logs_dir)
        
        # Create logs directory if it doesn't exist
        self.logs_dir.mkdir(exist_ok=True)
        
        # Create main log file
        log_file = self.logs_dir / "crab_tracker.log"
        
        # Configure logging
        logging.basicConfig(
            level=self.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()  # Also log to console
            ]
        )
        
        # Create logger for this class
        self.logger = logging.getLogger(__name__)
        self.logger.info("Logging service initialized")
        self.logger.info(f"Log directory: {self.logs_dir}")
        
    def get_logger(self, name):
        """
        Get a logger instance with the specified name.
        
        Args:
            name (str): Logger name
            
        Returns:
            logging.Logger: Logger instance
        """
        return logging.getLogger(name)
    
    def log_info(self, message, logger_name=None):
        """Log an info message."""
        if logger_name:
            logger = self.get_logger(logger_name)
        else:
            logger = self.logger or logging.getLogger(__name__)
        logger.info(message)
    
    def log_warning(self, message, logger_name=None):
        """Log a warning message."""
        if logger_name:
            logger = self.get_logger(logger_name)
        else:
            logger = self.logger or logging.getLogger(__name__)
        logger.warning(message)
    
    def log_error(self, message, logger_name=None):
        """Log an error message."""
        if logger_name:
            logger = self.get_logger(logger_name)
        else:
            logger = self.logger or logging.getLogger(__name__)
        logger.error(message)
    
    def log_debug(self, message, logger_name=None):
        """Log a debug message."""
        if logger_name:
            logger = self.get_logger(logger_name)
        else:
            logger = self.logger or logging.getLogger(__name__)
        logger.debug(message)
    
    def create_session_log(self, session_name):
        """
        Create a session-specific log file.
        
        Args:
            session_name (str): Name of the session
            
        Returns:
            str: Path to the session log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_log_file = self.logs_dir / f"session_{session_name}_{timestamp}.log"
        
        # Create session logger
        session_logger = logging.getLogger(f"session.{session_name}")
        session_handler = logging.FileHandler(session_log_file, encoding='utf-8')
        session_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        session_handler.setFormatter(formatter)
        
        session_logger.addHandler(session_handler)
        session_logger.setLevel(logging.DEBUG)
        
        self.log_info(f"Session log created: {session_log_file}")
        return str(session_log_file)
