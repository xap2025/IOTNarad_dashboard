"""
Script to clean up old boolean data from Realtime_Data measurement
This is needed because InfluxDB doesn't allow field type conflicts.
We're converting all boolean values to integers (true=1, false=0).
"""
import os
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
from influxdb_client.client.delete_api import DeleteApi
from datetime import datetime, timedelta

load_dotenv()

# InfluxDB Configuration
url = os.getenv('INFLUXDB_URL', 'http://influxdb:8086')
token = os.getenv('INFLUXDB_TOKEN', '')
org = os.getenv('INFLUXDB_ORG', 'iotnarad')
bucket = os.getenv('INFLUXDB_BUCKET', 'iotnarad-bucket')

import sys

# Check for --yes flag to skip confirmation
skip_confirmation = '--yes' in sys.argv

if not skip_confirmation:
    print("⚠️  WARNING: This script will DELETE all data from Realtime_Data measurement")
    print("   This is necessary to fix the field type conflict issue.")
    print("   After deletion, new data will be saved as integers (1/0) instead of booleans.")
    print()
    response = input("Do you want to continue? (yes/no): ")

    if response.lower() != 'yes':
        print("Cancelled.")
        exit(0)
else:
    print("⚠️  WARNING: Deleting all data from Realtime_Data measurement (--yes flag detected)")
    print("   This is necessary to fix the field type conflict issue.")

try:
    client = InfluxDBClient(url=url, token=token, org=org, timeout=30000)
    delete_api = client.delete_api()
    
    # Delete all data from Realtime_Data measurement
    # This will remove both boolean and integer data
    # New data will be saved as integers only
    
    start_time = datetime(1970, 1, 1)  # Start of epoch
    stop_time = datetime.utcnow()
    
    print(f"\n🗑️  Deleting all data from Realtime_Data measurement...")
    print(f"   Bucket: {bucket}")
    print(f"   Time range: {start_time} to {stop_time}")
    
    delete_api.delete(
        start=start_time,
        stop=stop_time,
        predicate='_measurement="Realtime_Data"',
        bucket=bucket,
        org=org
    )
    
    print("✅ Successfully deleted all Realtime_Data")
    print("\n📝 Next steps:")
    print("   1. Restart the application")
    print("   2. New data will be saved as integers (boolean true=1, false=0)")
    print("   3. Digital values will display as ON/OFF in the UI")
    
    client.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

