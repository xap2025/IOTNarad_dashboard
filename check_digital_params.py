"""
Quick script to check Digital parameter names in config vs RTD payload
"""
from app.services.device_config_db import DeviceConfigDBService
from app.services.realtime_data_db import RealtimeDataDBService

device_id = "8C4B144D3274"

print("=" * 60)
print("Checking Digital Config vs RTD Parameter Names")
print("=" * 60)

# Get Digital config
db_service = DeviceConfigDBService()
digital_config = db_service.get_digital_config(device_id)

if digital_config:
    print(f"\n📊 Digital Config Parameters:")
    
    # NPN Inputs
    npn_inputs = digital_config.get('npn_input', [])
    print(f"\n  NPN Inputs ({len(npn_inputs)}):")
    for ch in npn_inputs:
        if ch.get('enabled', False):
            name = ch.get('name', '')
            print(f"    - '{name}' (enabled)")
    
    # PNP Inputs
    pnp_inputs = digital_config.get('pnp_input', [])
    print(f"\n  PNP Inputs ({len(pnp_inputs)}):")
    for ch in pnp_inputs:
        if ch.get('enabled', False):
            name = ch.get('name', '')
            print(f"    - '{name}' (enabled)")
else:
    print("\n❌ No Digital config found")

# Get RTD parameters from database
print(f"\n📊 RTD Parameters in Database (last 1 hour):")
rtd_service = RealtimeDataDBService()

query = f'''
    from(bucket: "{rtd_service.bucket}")
    |> range(start: -1h)
    |> filter(fn: (r) => r._measurement == "Realtime_Data")
    |> filter(fn: (r) => r.device_id == "{device_id}")
    |> filter(fn: (r) => r.data_type == "Digital")
    |> group(columns: ["parameter_name"])
    |> distinct(column: "parameter_name")
    |> limit(n: 20)
'''

result = rtd_service.query_api.query(org=rtd_service.org, query=query)

rtd_params = []
for table in result:
    for record in table.records:
        param_name = record.values.get('parameter_name')
        if param_name:
            rtd_params.append(param_name)

if rtd_params:
    print(f"\n  Found {len(rtd_params)} Digital parameters:")
    for p in rtd_params:
        print(f"    - '{p}'")
else:
    print("\n  ❌ No Digital parameters found in database")

# Compare
print(f"\n📊 Comparison:")
print(f"  RTD Payload expects: 'proxy motor', 'proxy counter'")
if digital_config:
    config_names = []
    for ch in npn_inputs + pnp_inputs:
        if ch.get('enabled', False):
            config_names.append(ch.get('name', ''))
    print(f"  Config has: {config_names}")
    
    if 'proxy motor' in config_names and 'proxy counter' in config_names:
        print("\n  ✅ Parameter names match!")
    else:
        print("\n  ❌ Parameter names MISMATCH!")
        print(f"     Missing in config: {set(['proxy motor', 'proxy counter']) - set(config_names)}")

