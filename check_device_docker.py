"""
Check if a device is registered in the database (Docker version)
Usage: docker compose exec app python check_device_docker.py <serial_number>
   OR: docker compose exec app python check_device_docker.py
"""
import os
import sys
from app.services.device_info_service import DeviceInfoService

def check_device(serial_number: str):
    """Check if device exists in database"""
    print(f"Checking device: {serial_number}")
    print("=" * 50)
    
    # Initialize service
    service = DeviceInfoService()
    
    if not service.is_connected():
        print("❌ Error: Cannot connect to InfluxDB")
        print("   Please check your InfluxDB credentials in .env file")
        return False
    
    print("✅ Connected to InfluxDB")
    print(f"   URL: {service.url}")
    print(f"   Bucket: {service.bucket}")
    print(f"   Org: {service.org}")
    print("")
    
    # Check if device exists
    print(f"Checking if serial number '{serial_number}' exists...")
    exists = service.check_serial_number_exists(serial_number)
    
    if exists:
        print(f"✅ Device '{serial_number}' EXISTS in database")
        print("")
        
        # Get device info
        print("Fetching device information...")
        device_info = service.get_device_info(serial_number)
        
        if device_info:
            print("Device Information:")
            print(f"  Serial Number: {device_info.get('Sr_No')}")
            print(f"  Owner: {device_info.get('Owner')}")
            print(f"  Device Name: {device_info.get('Device_Name')}")
            print(f"  Date of Register: {device_info.get('Date_Of_Register')}")
            print(f"  Timestamp: {device_info.get('timestamp')}")
        else:
            print("⚠️  Device exists but could not fetch details")
    else:
        print(f"❌ Device '{serial_number}' NOT FOUND in database")
        print("")
        print("This means:")
        print("  - Device has not been registered yet")
        print("  - Or device initialization message was not received")
        print("  - Or there was an error during registration")
    
    print("")
    print("=" * 50)
    return exists


def list_all_devices():
    """List all registered devices"""
    print("Listing all registered devices...")
    print("=" * 50)
    
    # Initialize service
    service = DeviceInfoService()
    
    if not service.is_connected():
        print("❌ Error: Cannot connect to InfluxDB")
        return []
    
    # Get all devices
    devices = service.list_all_devices()
    
    if devices:
        print(f"✅ Found {len(devices)} device(s):")
        print("")
        for i, device in enumerate(devices, 1):
            print(f"  {i}. {device}")
    else:
        print("❌ No devices found in database")
    
    print("")
    print("=" * 50)
    return devices


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Check specific device
        serial_number = sys.argv[1]
        check_device(serial_number)
    else:
        # List all devices
        print("No serial number provided. Listing all devices...")
        print("")
        list_all_devices()
        print("")
        print("Usage: docker compose exec app python check_device_docker.py <serial_number>")
        print("Example: docker compose exec app python check_device_docker.py TEST88888")

