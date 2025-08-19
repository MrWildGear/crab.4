"""
Tests for time utility functions.
"""

import pytest
from datetime import datetime, timedelta

from crab_tracker.utils.time_utils import (
    format_duration,
    parse_eve_timestamp,
    parse_eve_filename_timestamp,
    get_time_difference,
    is_recent_timestamp
)


class TestFormatDuration:
    """Test duration formatting functions."""
    
    def test_format_duration_zero(self):
        """Test formatting zero duration."""
        assert format_duration(0) == "0s"
    
    def test_format_duration_seconds(self):
        """Test formatting seconds only."""
        assert format_duration(30) == "30s"
        assert format_duration(59) == "59s"
    
    def test_format_duration_minutes(self):
        """Test formatting minutes and seconds."""
        assert format_duration(60) == "1m 00s"
        assert format_duration(90) == "1m 30s"
        assert format_duration(3599) == "59m 59s"
    
    def test_format_duration_hours(self):
        """Test formatting hours, minutes, and seconds."""
        assert format_duration(3600) == "1h"
        assert format_duration(3661) == "1h 01m 01s"
        assert format_duration(7325) == "2h 02m 05s"
    
    def test_format_duration_negative(self):
        """Test formatting negative duration."""
        assert format_duration(-10) == "0s"


class TestParseEveTimestamp:
    """Test EVE timestamp parsing functions."""
    
    def test_parse_eve_timestamp_valid(self):
        """Test parsing valid EVE timestamps."""
        # Test various formats
        assert parse_eve_timestamp("2025.01.15 16:48:34") is not None
        assert parse_eve_timestamp("2025-01-15 16:48:34") is not None
        assert parse_eve_timestamp("15/01/2025 16:48:34") is not None
    
    def test_parse_eve_timestamp_invalid(self):
        """Test parsing invalid timestamps."""
        assert parse_eve_timestamp("invalid") is None
        assert parse_eve_timestamp("") is None
        assert parse_eve_timestamp("2025.13.45 25:70:99") is None


class TestParseEveFilenameTimestamp:
    """Test EVE filename timestamp parsing."""
    
    def test_parse_eve_filename_timestamp_valid(self):
        """Test parsing valid EVE filename timestamps."""
        filename = "20250115_164834_94266210.txt"
        result = parse_eve_filename_timestamp(filename)
        assert result is not None
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 16
        assert result.minute == 48
        assert result.second == 34
    
    def test_parse_eve_filename_timestamp_invalid(self):
        """Test parsing invalid EVE filename timestamps."""
        assert parse_eve_filename_timestamp("invalid.txt") is None
        assert parse_eve_filename_timestamp("20250115_164834.txt") is None
        assert parse_eve_filename_timestamp("") is None


class TestTimeDifference:
    """Test time difference calculations."""
    
    def test_get_time_difference(self):
        """Test time difference calculation."""
        time1 = datetime(2025, 1, 15, 16, 0, 0)
        time2 = datetime(2025, 1, 15, 16, 1, 30)
        
        diff = get_time_difference(time1, time2)
        assert diff == timedelta(minutes=1, seconds=30)
    
    def test_get_time_difference_strings(self):
        """Test time difference with string timestamps."""
        time1 = "2025.01.15 16:00:00"
        time2 = "2025.01.15 16:01:30"
        
        diff = get_time_difference(time1, time2)
        assert diff == timedelta(minutes=1, seconds=30)


class TestRecentTimestamp:
    """Test recent timestamp checking."""
    
    def test_is_recent_timestamp(self):
        """Test recent timestamp checking."""
        now = datetime.now()
        past = now - timedelta(hours=12)  # 12 hours ago
        old = now - timedelta(days=2)     # 2 days ago
        
        assert is_recent_timestamp(past, max_days=1) is True
        assert is_recent_timestamp(old, max_days=1) is False
        assert is_recent_timestamp(old, max_days=3) is True
    
    def test_is_recent_timestamp_invalid(self):
        """Test recent timestamp checking with invalid input."""
        assert is_recent_timestamp("invalid", max_days=1) is False
        assert is_recent_timestamp(None, max_days=1) is False
