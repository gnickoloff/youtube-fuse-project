#!/usr/bin/env python3
"""
Test Dashboard Components
"""

import sys
import os

def test_imports():
    """Test all required imports"""
    try:
        import flask
        print("✅ Flask available")
    except ImportError:
        print("❌ Flask not available")
        return False
    
    try:
        import psutil
        print("✅ psutil available")
    except ImportError:
        print("❌ psutil not available")
        return False
    
    try:
        import json
        import subprocess
        import time
        from datetime import datetime, timedelta
        import threading
        print("✅ Standard libraries available")
    except ImportError as e:
        print(f"❌ Standard library issue: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    try:
        if os.path.exists('youtube_config.json'):
            with open('youtube_config.json', 'r') as f:
                import json
                config = json.load(f)
                print("✅ Configuration file loads successfully")
                return True
        else:
            print("⚠️  No configuration file found")
            return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_templates():
    """Test template directory exists"""
    if os.path.exists('templates/dashboard.html'):
        print("✅ Dashboard template found")
        return True
    else:
        print("❌ Dashboard template missing")
        return False

def test_dashboard_class():
    """Test dashboard class instantiation"""
    try:
        sys.path.insert(0, '.')
        from dashboard import YouTubeFUSEDashboard
        
        dashboard = YouTubeFUSEDashboard()
        status = dashboard.get_system_status()
        print("✅ Dashboard class works")
        print(f"   FUSE mounted: {status['fuse_mounted']}")
        print(f"   Service status: {status['service_status']}")
        return True
    except Exception as e:
        print(f"❌ Dashboard class error: {e}")
        return False

def main():
    print("🧪 Testing YouTube FUSE Dashboard Components")
    print("=" * 50)
    
    tests = [
        ("Import Dependencies", test_imports),
        ("Configuration File", test_config),
        ("Template Files", test_templates),
        ("Dashboard Class", test_dashboard_class)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 {test_name}:")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Dashboard should work correctly.")
        print("\n🚀 To start the dashboard:")
        print("   ./start_dashboard.sh")
        print("   OR")
        print("   python3 dashboard.py")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        print("\n💡 Try:")
        print("   source venv/bin/activate")
        print("   pip install flask psutil")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
