"""Quick script to check RTD parameters in database"""
from app.services.realtime_data_db import RealtimeDataDBService

db = RealtimeDataDBService()
print(f"Connected: {db.is_connected()}")

if db.is_connected():
    # Get all unique parameter names for device
    query = '''
        from(bucket: "iotnarad-bucket")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "Realtime_Data")
        |> filter(fn: (r) => r.device_id == "8C4B144D3274")
        |> group(columns: ["parameter_name"])
        |> distinct(column: "parameter_name")
        |> limit(n: 20)
    '''
    
    result = db.query_api.query(org=db.org, query=query)
    
    params = []
    for table in result:
        for record in table.records:
            param_name = record.values.get('parameter_name')
            if param_name:
                params.append(param_name)
    
    print(f"\nParameters found in database (last 1 hour):")
    for p in params:
        print(f"  - '{p}'")
    
    # Also check latest values
    print(f"\nLatest values:")
    for param in params[:5]:  # Check first 5
        latest = db.get_latest_value("8C4B144D3274", param)
        print(f"  {param}: {latest}")

