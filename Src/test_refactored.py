"""
Test script for refactored EVE Log Reader modules
"""
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test configuration module"""
    print("Testing config module...")
    try:
        from config import WINDOW_TITLE, LOG_PATTERNS, EVE_LOG_PATHS
        print(f"✓ Window title: {WINDOW_TITLE}")
        print(f"✓ Log patterns: {LOG_PATTERNS}")
        print(f"✓ EVE log paths: {len(EVE_LOG_PATHS)} paths configured")
        return True
    except Exception as e:
        print(f"✗ Config module error: {e}")
        return False

def test_utils():
    """Test utility functions"""
    print("\nTesting utils module...")
    try:
        from utils import find_eve_log_directory, parse_filename_timestamp, is_recent_file
        
        # Test directory finding
        log_dir = find_eve_log_directory()
        print(f"✓ Found log directory: {log_dir}")
        
        # Test filename parsing
        test_filename = "20240101_120000_test.log"
        timestamp = parse_filename_timestamp(test_filename)
        print(f"✓ Parsed timestamp: {timestamp}")
        
        # Test recent file check
        is_recent = is_recent_file(__file__)
        print(f"✓ Recent file check: {is_recent}")
        
        return True
    except Exception as e:
        print(f"✗ Utils module error: {e}")
        return False

def test_ui_theme():
    """Test UI theme module"""
    print("\nTesting UI theme module...")
    try:
        from ui_theme import UITheme
        
        # Test theme class
        theme = UITheme()
        print("✓ UITheme class created successfully")
        
        # Test color constants
        from config import DARK_THEME_COLORS
        print(f"✓ Dark theme colors: {len(DARK_THEME_COLORS)} colors defined")
        
        return True
    except Exception as e:
        print(f"✗ UI theme module error: {e}")
        return False

def test_bounty_tracker():
    """Test bounty tracking module"""
    print("\nTesting bounty tracker module...")
    try:
        from bounty_tracker import BountyTracker, CRABBountyTracker
        
        # Test basic bounty tracker
        tracker = BountyTracker()
        tracker.start_session()
        tracker.add_bounty(datetime.now(), 100000, "test.log")
        stats = tracker.get_statistics()
        print(f"✓ Basic tracker: {stats['total_bounties']} bounties, {stats['total_isk']:,} ISK")
        
        # Test CRAB tracker
        crab_tracker = CRABBountyTracker()
        crab_tracker.start_crab_session()
        crab_tracker.add_crab_bounty(datetime.now(), 50000, "crab_test.log")
        crab_stats = crab_tracker.get_crab_statistics()
        print(f"✓ CRAB tracker: {crab_stats['total_bounties']} bounties, {crab_stats['total_isk']:,} ISK")
        
        return True
    except Exception as e:
        print(f"✗ Bounty tracker module error: {e}")
        return False

def test_concord_tracker():
    """Test CONCORD tracking module"""
    print("\nTesting CONCORD tracker module...")
    try:
        from concord_tracker import CONCORDTracker
        
        tracker = CONCORDTracker()
        
        # Test status callbacks
        status_updates = []
        def status_callback(status):
            status_updates.append(status)
        
        tracker.set_status_callback(status_callback)
        tracker.start_link()
        
        print(f"✓ CONCORD tracker: {tracker.get_status()}")
        print(f"✓ Status updates: {status_updates}")
        
        return True
    except Exception as e:
        print(f"✗ CONCORD tracker module error: {e}")
        return False

def test_log_monitor():
    """Test log monitoring module"""
    print("\nTesting log monitor module...")
    try:
        from log_monitor import LogMonitor
        
        # Test with current directory
        monitor = LogMonitor(".")
        
        # Test getting recent files
        recent_files = monitor.get_recent_log_files()
        print(f"✓ Log monitor: {len(recent_files)} recent files found")
        
        # Test monitoring status
        status = monitor.get_monitoring_status()
        print(f"✓ Monitoring status: {status}")
        
        return True
    except Exception as e:
        print(f"✗ Log monitor module error: {e}")
        return False

def test_main_app_import():
    """Test that main app can be imported"""
    print("\nTesting main app import...")
    try:
        from eve_log_reader_refactored import EVELogReader
        print("✓ Main app class imported successfully")
        return True
    except Exception as e:
        print(f"✗ Main app import error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 Running refactored EVE Log Reader tests...\n")
    
    tests = [
        test_config,
        test_utils,
        test_ui_theme,
        test_bounty_tracker,
        test_concord_tracker,
        test_log_monitor,
        test_main_app_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The refactored code is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
