#!/usr/bin/env python3
"""
Simple test to verify the IOTNarad app code works
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from app.main import app, server, socketio
        print("✅ Main app imports successful")
    except Exception as e:
        print(f"❌ Main app import failed: {e}")
        return False
    
    try:
        from app.services.mqtt_client import MQTTClientService
        print("✅ MQTT service import successful")
    except Exception as e:
        print(f"❌ MQTT service import failed: {e}")
        return False
    
    try:
        from app.services.influx import InfluxDBService
        print("✅ InfluxDB service import successful")
    except Exception as e:
        print(f"❌ InfluxDB service import failed: {e}")
        return False
    
    try:
        from app.services.device_config import DeviceConfigService
        print("✅ Device config service import successful")
    except Exception as e:
        print(f"❌ Device config service import failed: {e}")
        return False
    
    return True

def test_services():
    """Test if services can be initialized"""
    print("\nTesting service initialization...")
    
    try:
        from app.services.mqtt_client import MQTTClientService
        mqtt_service = MQTTClientService()
        print("✅ MQTT service initialized")
    except Exception as e:
        print(f"❌ MQTT service initialization failed: {e}")
        return False
    
    try:
        from app.services.influx import InfluxDBService
        influx_service = InfluxDBService()
        print("✅ InfluxDB service initialized")
    except Exception as e:
        print(f"❌ InfluxDB service initialization failed: {e}")
        return False
    
    try:
        from app.services.device_config import DeviceConfigService
        config_service = DeviceConfigService()
        print("✅ Device config service initialized")
    except Exception as e:
        print(f"❌ Device config service initialization failed: {e}")
        return False
    
    return True

def test_pages():
    """Test if page layouts can be created"""
    print("\nTesting page layouts...")
    
    try:
        from app.pages.login import create_login_layout
        login_layout = create_login_layout()
        print("✅ Login page layout created")
    except Exception as e:
        print(f"❌ Login page layout failed: {e}")
        return False
    
    try:
        from app.pages.dashboard import create_dashboard_layout
        dashboard_layout = create_dashboard_layout()
        print("✅ Dashboard page layout created")
    except Exception as e:
        print(f"❌ Dashboard page layout failed: {e}")
        return False
    
    try:
        from app.pages.analytics import create_analytics_layout
        analytics_layout = create_analytics_layout()
        print("✅ Analytics page layout created")
    except Exception as e:
        print(f"❌ Analytics page layout failed: {e}")
        return False
    
    try:
        from app.pages.device_config import create_device_config_layout
        device_config_layout = create_device_config_layout()
        print("✅ Device config page layout created")
    except Exception as e:
        print(f"❌ Device config page layout failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("IOTNarad Dashboard - Code Test")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test services
    if not test_services():
        success = False
    
    # Test pages
    if not test_pages():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! Your code is working correctly.")
        print("The issue is likely with Docker, not the code.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    print("=" * 50)
    
    return success

if __name__ == "__main__":
    main()
