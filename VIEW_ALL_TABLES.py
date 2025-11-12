"""
Script to view all tables (measurements) in InfluxDB
Yeh script sabhi tables ko list karta hai aur unka data dikhata hai
"""
import os
from influxdb_client import InfluxDBClient

# InfluxDB Configuration
url = os.getenv('INFLUXDB_URL', 'https://us-east-1-1.aws.cloud2.influxdata.com')
token = os.getenv('INFLUXDB_TOKEN', 'T0ZoSucqSCbNtgfcZSYE81-vYA7DdXpPFRb17vc2iUZsUZ0CsebGlOTpr9XTGFjlaiyqI5bwUhtqLQe2zU7wnA==')
org = os.getenv('INFLUXDB_ORG', 'iot-narad-gcp')
bucket = os.getenv('INFLUXDB_BUCKET', 'iot_data_gcp')

# Initialize client
try:
    client = InfluxDBClient(url=url, token=token, org=org, timeout=30000)
    query_api = client.query_api()
    print("✅ InfluxDB connected successfully!")
except Exception as e:
    print(f"❌ Error connecting to InfluxDB: {e}")
    exit(1)

print("=" * 60)
print("InfluxDB Tables (Measurements) Viewer")
print("=" * 60)
print(f"Bucket: {bucket}")
print(f"Org: {org}")
print(f"URL: {url}")

# 1. List All Measurements
print("\n📊 Step 1: Listing All Measurements (Tables)")
print("-" * 60)

query = f'''
import "influxdata/influxdb/schema"

schema.measurements(bucket: "{bucket}")
'''

try:
    result = query_api.query(org=org, query=query)
    
    measurements = []
    for table in result:
        for record in table.records:
            measurement = record.get_value()
            measurements.append(measurement)
    
    if measurements:
        print(f"✅ Found {len(measurements)} measurements:")
        for i, measurement in enumerate(measurements, 1):
            print(f"   {i}. {measurement}")
    else:
        print("❌ No measurements found")
        measurements = []
        
except Exception as e:
    print(f"❌ Error: {e}")
    measurements = []

# 2. Count Records in Each Measurement
print("\n📈 Step 2: Counting Records in Each Measurement")
print("-" * 60)

measurement_counts = {}
for measurement in measurements:
    try:
        query = f'''
        from(bucket: "{bucket}")
          |> range(start: -365d)
          |> filter(fn: (r) => r._measurement == "{measurement}")
          |> count()
        '''
        
        result = query_api.query(org=org, query=query)
        
        count = 0
        for table in result:
            for record in table.records:
                count = record.get_value()
                break
        
        measurement_counts[measurement] = count
        print(f"   {measurement}: {count} records")
        
    except Exception as e:
        print(f"   {measurement}: Error - {e}")
        measurement_counts[measurement] = 0

# 3. View Sample Data from Each Measurement
print("\n📄 Step 3: Viewing Sample Data from Each Measurement")
print("-" * 60)

for measurement in measurements:
    try:
        query = f'''
        from(bucket: "{bucket}")
          |> range(start: -365d)
          |> filter(fn: (r) => r._measurement == "{measurement}")
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: 1)
        '''
        
        result = query_api.query(org=org, query=query)
        
        print(f"\n   📋 {measurement}:")
        found = False
        for table in result:
            for record in table.records:
                found = True
                # Get tags
                tags = {k: v for k, v in record.values.items() 
                       if k not in ['_start', '_stop', '_time', '_measurement', '_field', '_value', 'result', 'table'] 
                       and not k.startswith('_')}
                
                # Get fields
                fields = {}
                for k, v in record.values.items():
                    if k == '_field':
                        field_name = v
                    elif k == '_value':
                        fields[field_name] = v
                
                if tags:
                    print(f"      Tags: {tags}")
                if fields:
                    print(f"      Fields: {list(fields.keys())[:5]}...")  # Show first 5 fields
                print(f"      Time: {record.get_time()}")
                break
            if found:
                break
        
        if not found:
            print(f"      No data found")
        
    except Exception as e:
        print(f"   {measurement}: Error - {e}")

# 4. List All Devices in Device_Config
print("\n🔌 Step 4: Listing All Devices in Device_Config")
print("-" * 60)

try:
    query = f'''
    import "influxdata/influxdb/schema"
    
    schema.tagValues(
      bucket: "{bucket}",
      tag: "device_id",
      predicate: (r) => r._measurement == "Device_Config",
      start: -365d
    )
    '''
    
    result = query_api.query(org=org, query=query)
    
    devices = []
    for table in result:
        for record in table.records:
            devices.append(record.get_value())
    
    if devices:
        print(f"✅ Found {len(devices)} devices:")
        for device in devices:
            print(f"   - {device}")
    else:
        print("❌ No devices found")
        
except Exception as e:
    print(f"❌ Error: {e}")

# 5. List All Users in User_info
print("\n👥 Step 5: Listing All Users in User_info")
print("-" * 60)

try:
    query = f'''
    import "influxdata/influxdb/schema"
    
    schema.tagValues(
      bucket: "{bucket}",
      tag: "User_Id",
      predicate: (r) => r._measurement == "User_info",
      start: -365d
    )
    '''
    
    result = query_api.query(org=org, query=query)
    
    users = []
    for table in result:
        for record in table.records:
            users.append(record.get_value())
    
    if users:
        print(f"✅ Found {len(users)} users:")
        for user in users:
            print(f"   - {user}")
    else:
        print("❌ No users found")
        
except Exception as e:
    print(f"❌ Error: {e}")

# 6. View Detailed Data from Device_Config
print("\n🔍 Step 6: Viewing Detailed Data from Device_Config")
print("-" * 60)

try:
    query = f'''
    from(bucket: "{bucket}")
      |> range(start: -365d)
      |> filter(fn: (r) => r._measurement == "Device_Config")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: 5)
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    
    result = query_api.query(org=org, query=query)
    
    count = 0
    for table in result:
        for record in table.records:
            count += 1
            print(f"\n   📄 Configuration {count}:")
            print(f"      Device ID: {record.values.get('device_id', 'N/A')}")
            print(f"      Device Name: {record.values.get('device_name', 'N/A')}")
            print(f"      Device Type: {record.values.get('device_type', 'N/A')}")
            print(f"      Location: {record.values.get('location', 'N/A')}")
            print(f"      Version: {record.values.get('version', 'N/A')}")
            print(f"      Time: {record.get_time()}")
            if count >= 5:
                break
        if count >= 5:
            break
    
    if count == 0:
        print("   ❌ No configurations found")
        
except Exception as e:
    print(f"❌ Error: {e}")

# 7. Summary
print("\n" + "=" * 60)
print("📊 Summary")
print("=" * 60)
print(f"Total Measurements: {len(measurements)}")
print(f"Total Records: {sum(measurement_counts.values())}")
print("\nMeasurements with Records:")
for measurement, count in measurement_counts.items():
    if count > 0:
        print(f"   {measurement}: {count} records")

# Close client
client.close()

print("\n" + "=" * 60)
print("✅ Completed!")
print("=" * 60)
print("\n💡 Tip: Use InfluxDB Cloud UI for better visualization")
print("   URL: https://cloud2.influxdata.com")

