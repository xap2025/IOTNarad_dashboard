from flask import request
from flask_socketio import SocketIO
import json
import paho.mqtt.client as mqtt
import random
import ssl
from threading import Thread, Lock
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone
import time
import uuid
from collections import defaultdict
import traceback
# ---------------- Flask App & SocketIO Setup ----------------
# Import from main app instead of creating new Flask instance

from main import socketio

# Import configuration from config.py
from config import MQTT_BROKER, MQTT_PORT, MQTT_CERTIFICATE_PATH, MQTT_PRIVATE_KEY_PATH, MQTT_ROOT_CA_PATH, INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET, SAVE_INTERVAL_SECONDS

# ---------------- MQTT Config ----------------
BROKER = MQTT_BROKER
PORT = MQTT_PORT
CLIENT_ID = f"bdms-02-{uuid.uuid4().hex[:6]}"

TOPICS = [
    ("bdms-01/DevReg/New/#", 1),
    ("bdms-01/data", 1)
]

CERTIFICATE_PATH = MQTT_CERTIFICATE_PATH
PRIVATE_KEY_PATH = MQTT_PRIVATE_KEY_PATH
ROOT_CA_PATH = MQTT_ROOT_CA_PATH

# ---------------- InfluxDB Config ----------------
INFLUXDB_URL = INFLUXDB_URL
INFLUXDB_TOKEN = INFLUXDB_TOKEN
INFLUXDB_ORG = INFLUXDB_ORG
INFLUXDB_BUCKET = INFLUXDB_BUCKET

# ----------------- Global State -----------------
mqtt_connected = False
connected_once = False
last_message_time = None
connection_lock = Lock()


influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)
query_api = influx_client.query_api()

last_write_time = {}  # Device_Id -> last write timestamp
# Interval between writes in seconds (adjust as needed)
#SAVE_INTERVAL_SECONDS = 60

# This is now imported from config.py, so you can remove the hardcoded value
# SAVE_INTERVAL_SECONDS is now set from the config import above

# ======= SOCKET.IO HANDLERS =======

@socketio.on('connect')
def handle_connect():
    print(f"✅ Frontend connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"❌ Frontend disconnected: {request.sid}")

@socketio.on('ping')
def handle_ping(message, callback):
    callback("pong")


# ----------------- Utility Functions (Preserved with minor enhancements) -----------------
def generate_unique_device_id():
    """Generates a unique device ID and verifies it doesn't exist in InfluxDB"""
    while True:
        device_id = f"XAP-{random.randint(1000, 9999)}"
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -5y)
        |> filter(fn: (r) => r._measurement == "Device_info" and r.Device_Id == "{device_id}")
        '''
        try:
            result = query_api.query(org=INFLUXDB_ORG, query=query)
            if not result:
                return device_id
        except Exception as e:
            print(f"⚠️ Error checking device ID uniqueness: {e}")
            continue

def device_exists(device_id):
    """Check if device exists in InfluxDB with proper error handling"""
    if not device_id:
        return False
        
    try:
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -5y)
        |> filter(fn: (r) => r["_measurement"] == "Device_info" and r["Device_Id"] == "{device_id}")
        |> limit(n:1)
        '''
        result = query_api.query(org=INFLUXDB_ORG, query=query)
        return len(result) > 0
    except Exception as e:
        print(f"❌ Error checking device existence: {e}")
        return False

def validate_json_format(data):
    """Validate incoming JSON structure with additional type checking"""
    try:
        # Required top-level fields
        required_keys = {
            "Device ID": str,
            "Battery Voltage": dict,
            "Charging": (str, int, float),
            "Temperature": (str, int, float),
            "GPS": dict,
            "SoC": (str, int, float),
            "SoH": (str, int, float),
            "Speed": (str, int, float),
            "Errors": (str, int)
        }
        
        # Battery Voltage sub-fields
        battery_keys = ["Total", "Battery1", "Battery2", "Battery3", 
                       "Battery4", "Battery5", "Battery6"]
        
        # GPS sub-fields
        gps_keys = ["Latitude", "Longitude"]
        
        # Top-level validation
        if not all(key in data for key in required_keys):
            return False
            
        # Type checking
        for field, expected_type in required_keys.items():
            if not isinstance(data[field], expected_type):
                return False
                
        # Nested structure validation
        return (all(key in data["Battery Voltage"] for key in battery_keys) and
                all(key in data["GPS"] for key in gps_keys))
                
    except Exception:
        return False

def convert_to_float_from_int_string(value_str):
    """Convert various number formats to float without preserving units"""
    if isinstance(value_str, (int, float)):
        return float(value_str)
        
    if not isinstance(value_str, str):
        return 0.0
        
    try:
        # Remove all non-numeric characters (except . and -)
        numeric_str = ''.join(c for c in value_str if c.isdigit() or c in '.-')
        
        if not numeric_str:  # If we're left with nothing
            return 0.0
            
        # Handle integer-encoded floats (like "1234" meaning 12.34)
        if '.' not in numeric_str and '-' not in numeric_str:
            num = float(numeric_str)
            return num / 10.0
            
        return float(numeric_str)
    except (ValueError, TypeError):
        return 0.0

def format_for_ui(data):
    """Convert data to same format as stored in InfluxDB (all numeric)"""
    formatted_data = data.copy()
    
    # Convert Battery Voltage values to float
    if "Battery Voltage" in formatted_data:
        for battery in ["Total", "Battery1", "Battery2", "Battery3", 
                       "Battery4", "Battery5", "Battery6"]:
            if battery in formatted_data["Battery Voltage"]:
                formatted_data["Battery Voltage"][battery] = convert_to_float_from_int_string(
                    formatted_data["Battery Voltage"][battery]
                )
    
    # Convert Charging current to float
    if "Charging" in formatted_data:
        formatted_data["Charging"] = convert_to_float_from_int_string(formatted_data["Charging"])
    
    # Other fields remain the same as before
    if "Temperature" in formatted_data:
        formatted_data["Temperature"] = float(formatted_data["Temperature"])
    
    if "GPS" in formatted_data:
        formatted_data["GPS"]["Latitude"] = float(formatted_data["GPS"]["Latitude"])
        formatted_data["GPS"]["Longitude"] = float(formatted_data["GPS"]["Longitude"])
    
    if "SoC" in formatted_data:
        formatted_data["SoC"] = float(str(formatted_data["SoC"]).replace('%', ''))
    if "SoH" in formatted_data:
        formatted_data["SoH"] = float(str(formatted_data["SoH"]).replace('%', ''))
    
    if "Speed" in formatted_data:
        formatted_data["Speed"] = float(formatted_data["Speed"])
    
    if "Errors" in formatted_data:
        formatted_data["Errors"] = int(formatted_data["Errors"])
    
    return formatted_data
# ----------------- Message Handlers (Preserved with minor enhancements) -----------------
def handle_device_registration(payload, client, serial_number_from_topic=None):
    """Handle device registration with improved error handling"""
    print("🚀 Handling device registration")
    serial_number = payload.get("SerialNumber") or serial_number_from_topic
    command = payload.get("Command")
    
    # Use serial number in reply topic if provided, otherwise use default
    if serial_number_from_topic:
        TOPIC_PUB = f"bdms-01/DevReg/Reply/{serial_number_from_topic}"
    else:
        TOPIC_PUB = "bdms-01/DevReg/Reply"
        
    if command == "new_device" and serial_number:
        # Check if device exists
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -5y)
        |> filter(fn: (r) => r._measurement == "Device_info")
        |> filter(fn: (r) => r._field == "Sr_No" and r._value == "{serial_number}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        result = query_api.query_data_frame(query)

        if not result.empty:
            # Existing device
            device_id = result["Device_Id"][0]
            print(f"ℹ️ SerialNumber {serial_number} already exists → Device ID: {device_id}")
            response = {"SerialNumber": serial_number, "DeviceId": device_id, "Ack": True}
        else:
            # New device
            device_id = generate_unique_device_id()
            date_of_mfg = datetime.utcnow().strftime("%Y-%m-%d")
            try:
                point = Point("Device_info").tag("Device_Id", device_id) \
                    .field("Sr_No", serial_number) \
                    .field("Owner", "Unassigned") \
                    .field("Permissions", -1) \
                    .field("Date_Of_MFG", datetime.utcnow().strftime("%Y-%m-%d"))\
                    .field("Device_Name", "Unnamed")  # <-- new field
                
                write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
                print(f"✅ New device {device_id} (SerialNumber: {serial_number}) saved to DB.")
                #response = {"SerialNumber": serial_number, "DeviceId": device_id, "Ack": True}
                emit_payload = {
                    'Device_Id': device_id, 'Sr_No': serial_number,
                    'Date_Of_MFG': date_of_mfg, 'Owner': 'Unassigned', 'Permissions': -1, 'Device_Name' : 'Unnamed',
                }
                socketio.emit('new_device_registered', emit_payload)
            
                
                print("✅ socketio.emit executed → Event: 'new_device_registered', Payload:", emit_payload)
                response = {"SerialNumber": serial_number, "DeviceId": device_id, "Ack": True}

            except Exception as e:
                print("❌ Error saving to DB:", e)
                response = {"SerialNumber": serial_number, "DeviceId": None, "Ack": False}

        # Send MQTT response
        #client.publish(TOPIC_PUB, json.dumps(response), qos=1)
        time.sleep(5)
        result = client.publish(TOPIC_PUB, json.dumps(response), qos=1, retain=True)
        status = result[0]
        if status == 0:
            print(f"📤✅ Message published successfully to {TOPIC_PUB} → {response}")
        else:
            print(f"❌ Failed to publish message to topic {TOPIC_PUB}. Status Code: {status}")

    

def handle_incoming_data(json_data):
    """Process incoming device data with enhanced validation"""
    print("📨 Raw MQTT Message Received:")
    print(json_data)  # <-- ADD THIS
    print("🚀 Inside handle_incoming_data()")
    # print(f"✅ Data written for device {device_id} at {now}")
    try:
        data = json.loads(json_data)
        print("📨 Raw MQTT Message Received:")
        print(json.dumps(data, indent=2))
        
        if not validate_json_format(data):
            print("⚠️ Skipping: Invalid data format")
            print("📦 Invalid JSON payload:", json.dumps(data, indent=2))
            return
            
        device_id = data.get("Device ID")  # ✅ assign before anything else
        #now = datetime.now(timezone.utc)   # ✅ keep your timestamp logic?
        #ts_now = time.time()  # current Unix time for tracking writes
        influx_time = datetime.now(timezone.utc)  # InfluxDB timestamp

        if not device_exists(device_id):
            print(f"⚠️ Skipping: Device ID {device_id} not found in Device_info")
            return
        
        # 🔹 Fetch latest Device_Name from Device_info
        device_name = "Unnamed"
        try:
            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -5y)
            |> filter(fn: (r) => r._measurement == "Device_info" and r.Device_Id == "{device_id}")
            |> last()
            |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
            '''
            result = query_api.query(org=INFLUXDB_ORG, query=query)
            for table in result:
                for record in table.records:
                    device_name = record.values.get("Device_Name", "Unnamed")

            # ✅ Fallback: agar pivot fail ho jaye
            if device_name == "Unnamed":
                query = f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                  |> range(start: -5y)
                  |> filter(fn: (r) => r._measurement == "Device_info" and r.Device_Id == "{device_id}" and r._field == "Device_Name")
                  |> last()
                '''
                result = query_api.query(org=INFLUXDB_ORG, query=query)
                for table in result:
                    for record in table.records:
                        device_name = record.get_value() or "Unnamed"
                        
        except Exception as e:
            print(f"⚠️ Could not fetch Device_Name for {device_id}: {e}")
        
        # Forward to frontend
        def emit_to_dash(device_id, data, device_name):
            try:
                # Apply all the same formatting as InfluxDB storage
                formatted_data = format_for_ui(data)
        
                print(f"📤 Emitting device_data for: {device_id}")
                print("📦 Emitted Payload:")
                print(json.dumps({
                    'device_id': device_id,
                    'device_name': device_name,
                    'timestamp': datetime.now().isoformat(),
                    'data': formatted_data
                }, indent=2))

                socketio.emit('device_data', {
                    'device_id': device_id,
                    'device_name': device_name,
                    'timestamp': datetime.now().isoformat(),
                    'data': formatted_data
                })

                print("✅ Socket.IO emit was called")

            except Exception as e:
                print("❌ Error during emit_to_dash:")
                print(e)
                #emit_to_dash(device_id, data)  # 🔥 Direct call to verify

        socketio.start_background_task(emit_to_dash, device_id, data, device_name)

         # 🧠 Check if it's time to write to InfluxDB
        
        #if device_id not in last_write_time or ts_now - last_write_time[device_id] >= SAVE_INTERVAL_SECONDS:
         
        point = Point("Device_Data").tag("Device_Id", device_id) \
            .field("Device_Name", device_name) \
            .field("Battery_Total", convert_to_float_from_int_string(data["Battery Voltage"]["Total"])) \
            .field("Battery1", convert_to_float_from_int_string(data["Battery Voltage"]["Battery1"])) \
            .field("Battery2", convert_to_float_from_int_string(data["Battery Voltage"]["Battery2"])) \
            .field("Battery3", convert_to_float_from_int_string(data["Battery Voltage"]["Battery3"])) \
            .field("Battery4", convert_to_float_from_int_string(data["Battery Voltage"]["Battery4"])) \
            .field("Battery5", convert_to_float_from_int_string(data["Battery Voltage"]["Battery5"])) \
            .field("Battery6", convert_to_float_from_int_string(data["Battery Voltage"]["Battery6"])) \
            .field("Charging", convert_to_float_from_int_string(data["Charging"])) \
            .field("Temperature", float(data["Temperature"])) \
            .field("Latitude", float(data["GPS"]["Latitude"])) \
            .field("Longitude", float(data["GPS"]["Longitude"])) \
            .field("SoC", float(data["SoC"].replace("%", ""))) \
            .field("SoH", float(data["SoH"].replace("%", ""))) \
            .field("Speed", float(data["Speed"])) \
            .field("Errors", int(data["Errors"])) \
            .time(influx_time)
          
        # Write to InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        #last_write_time[device_id] = ts_now  # ✅ update last write timestamp
        print(f"✅ Data written for device {device_id} at {influx_time}")

        #else:
            #print(f"⏳ Skipping InfluxDB write for {device_id} (waiting {SAVE_INTERVAL_SECONDS}s interval)")
        
        
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON: {json_data[:100]}...")
    except KeyError as e:
        print(f"❌ Missing expected field {e} in data")
    except Exception as e:
        print(f"❌ Error while parsing or writing data: {e}")
        print("📦 Raw Payload:", json_data)

# # ---------------- MQTT Setup ----------------
def on_connect(client, userdata, flags, rc):
    global mqtt_connected, connected_once

    with connection_lock:
        if rc == 0:
            mqtt_connected = True
            print(f"🔌 MQTT Connected successfully (Code: {rc})")
            
            if not connected_once:
                for topic, qos in TOPICS:
                    result, _ = client.subscribe(topic, qos)
                    if result == mqtt.MQTT_ERR_SUCCESS:
                        print(f"📡 Subscribed to: {topic} (QoS {qos})")
                    else:
                        print(f"❌ Failed to subscribe to: {topic} (Code: {result})")
                connected_once = True
            print(f"🔌 MQTT Connected (Code: {rc})")
        else:
            mqtt_connected = False
            print(f"❌ Failed to connect. Return code: {rc}")

def on_message(client, userdata, msg):
    global last_message_time  # ✅ Needed to update the global state
    try:
        last_message_time = datetime.now()  # ✅ Track latest message time
        print("RAW RECEIVED:", repr(msg.payload.decode()))
        payload = json.loads(msg.payload.decode())
        print(f"\n📩 Received on {msg.topic}: {payload}")
       
        
        # Handle wildcard device registration topics
        if msg.topic.startswith("bdms-01/DevReg/New/"):
            # Extract serial number from topic path
            # Topic format: bdms-01/DevReg/New/{serial_number}
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 4:
                serial_number_from_topic = topic_parts[3]
                print(f"📋 Extracted serial number from topic: {serial_number_from_topic}")
                handle_device_registration(payload, client, serial_number_from_topic)
            else:
                print(f"❌ Invalid topic format: {msg.topic}")
        elif msg.topic == "bdms-01/data":
            handle_incoming_data(msg.payload.decode())
            
    except Exception as e:
        print(f"❌ Message handling error: {e}")

def on_disconnect(client, userdata, rc):
    global mqtt_connected
    with connection_lock:
        mqtt_connected = False
        if rc != 0:
            print(f"🔌 Unexpected disconnection (Code: {rc}). Auto-reconnect will be attempted.")
        else:
            print("ℹ️ Graceful disconnection (Code: 0)")


def on_log(client, userdata, level, buf):
    if level == mqtt.MQTT_LOG_ERR:
        print(f"🧾 MQTT ERROR: {buf}")
    elif level == mqtt.MQTT_LOG_WARNING:
        print(f"⚠️ MQTT WARNING: {buf}")
    elif level == mqtt.MQTT_LOG_INFO:
        print(f"ℹ️ MQTT INFO: {buf}")
    elif level == mqtt.MQTT_LOG_DEBUG:
        print(f"🐛 MQTT DEBUG: {buf}")

# ============= MQTT Service =============
def create_mqtt_client():
    client = mqtt.Client(client_id=CLIENT_ID, clean_session=True)
    client.tls_set(
        ca_certs=ROOT_CA_PATH,
        certfile=CERTIFICATE_PATH,
        keyfile=PRIVATE_KEY_PATH,
        tls_version=ssl.PROTOCOL_TLSv1_2
    )

    # Reliability options
    client.max_inflight_messages_set(20)
    client.max_queued_messages_set(100)
    client.reconnect_delay_set(min_delay=2, max_delay=60)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_log = on_log
    
    return client

def start_mqtt_service():
    client = create_mqtt_client()
    try:
        client.connect(BROKER, PORT, keepalive=120)
        client.loop_start()
        print("✅ MQTT service started")
        return client
    except Exception as e:
        print(f"❌ MQTT connection failed: {e}")
        return None

# ============= Flask Routes =============
@socketio.on('get_mqtt_status')
def handle_status_request(callback):
    callback({
        'connected': mqtt_connected,
        'last_message': last_message_time.isoformat() if last_message_time else None,
        'subscriptions': TOPICS
    })

# ============= Main Service =============
def start_backend_services():
    if not hasattr(start_backend_services, '_started'):
        print("🛠️ Starting MQTT service inside worker...")
        mqtt_client = start_mqtt_service()
        start_backend_services._started = True
        return mqtt_client
    return None

# Initialize service when imported
#mqtt_client = start_backend_services()


