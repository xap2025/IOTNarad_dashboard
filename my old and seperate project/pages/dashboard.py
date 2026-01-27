import dash
from dash import html, dcc, Input, Output, State, register_page, callback, ctx, no_update
import dash_bootstrap_components as dbc
import smtplib
from email.message import EmailMessage
from influxdb_client import InfluxDBClient, Point
import pandas as pd
from datetime import datetime, timedelta
from dash import dash_table
import json
from influxdb_client.client.write_api import SYNCHRONOUS
from dash.exceptions import PreventUpdate
import re 
from threading import Thread
import time
from collections import defaultdict

# Import configuration from config.py (your config reads env vars)
from config import (
    MQTT_BROKER, MQTT_PORT, MQTT_CERTIFICATE_PATH, MQTT_PRIVATE_KEY_PATH, MQTT_ROOT_CA_PATH,
    INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET,
    SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD
)


# Store live data for each device
LIVE_DATA_MEMORY = defaultdict(dict)

#LIVE_DATA_TIMEOUT = 300  # 30 minutes in seconds


external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    {
        'href': 'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css',
        'rel': 'stylesheet'
    }
]

# Register the page
register_page(__name__, path='/dashboard')

# MQTT Config (not used directly in this file but kept for reference)
BROKER = MQTT_BROKER
PORT = MQTT_PORT

# InfluxDB Connection
INFLUXDB_URL = INFLUXDB_URL
TOKEN = INFLUXDB_TOKEN
ORG = INFLUXDB_ORG
BUCKET = INFLUXDB_BUCKET

client = InfluxDBClient(url=INFLUXDB_URL, token=TOKEN, org=ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

class EmailSender:
    def __init__(self, smtp_server, smtp_port, sender_email, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.password = password
        self.server = None
        self.last_connection_time = 0
        self.connect()

    def connect(self):
        try:
            if self.server:
                self.server.quit()
            self.server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            self.server.starttls()
            self.server.login(self.sender_email, self.password)
            self.last_connection_time = time.time()
            print("[EMAIL] SMTP connection established successfully.")
        except Exception as e:
            self.server = None
            print(f"[EMAIL ERROR] Failed to connect: {e}")

    def ensure_connection(self):
        try:
            if self.server is None:
                print("[EMAIL DEBUG] Reconnecting...")
                self.connect()
            else:
                status = self.server.noop()[0]
                if status != 250:
                    print(f"[EMAIL DEBUG] Server NOOP failed, reconnecting...")
                    self.connect()
                elif time.time() - self.last_connection_time > 300:
                    print("[EMAIL DEBUG] Reconnecting stale connection...")
                    self.connect()
        except Exception as e:
            print(f"[EMAIL ERROR] Connection check failed: {e}")
            self.connect()

    def send_email(self, receiver_email, subject, body):
        try:
            self.ensure_connection()
            if self.server is None:
                print("[EMAIL ERROR] SMTP server not connected.")
                return False

            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = receiver_email

            self.server.send_message(msg)
            print(f"[EMAIL SENT] to {receiver_email}")
            return True
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")
            return False
    
    def close(self):
        if self.server:
            try:
                self.server.quit()
                print("[EMAIL] SMTP connection closed.")
            except Exception as e:
                print(f"[EMAIL ERROR] Failed to close connection: {e}")

# Create email sender instance
email_sender = EmailSender(
    smtp_server=SMTP_SERVER,
    smtp_port=SMTP_PORT,
    sender_email=SENDER_EMAIL,
    password=SENDER_PASSWORD
)

# Fetch user details from InfluxDB
def fetch_user_details(user_id):
    if not user_id:
        return None
    
    query = f'''
    from(bucket: "Charger")
      |> range(start: -1y)
      |> filter(fn: (r) => r._measurement == "User_info")
      |> filter(fn: (r) => r.User_Id == "{user_id}")
      |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n:1)
    '''
    try:
        result = query_api.query(query=query)
        for table in result:
            for record in table.records:
                return record.values
    except Exception as e:
        print(f"[ERROR] User details fetch failed: {e}")
    return None

# Fetch devices for user
def fetch_devices_from_influxdb(user_id):
    if not user_id:
        return []

    query = f'''
    from(bucket: "Charger")
      |> range(start: -1y)
      |> filter(fn: (r) => r._measurement == "Device_info")
      {"" if user_id == "admin" else f'|> filter(fn: (r) => r._field == "Owner" and r._value == "{user_id}")'}
      |> keep(columns: ["Device_Id", "Owner"])
      |> group(columns: ["Device_Id"])
      |> distinct(column: "Device_Id")
    '''
    try:
        result = query_api.query_data_frame(query)
        if not result.empty and "Device_Id" in result.columns:
            result = result.dropna(subset=["Device_Id"])
            return result["Device_Id"].unique().tolist()
    except Exception as e:
        print(f"[ERROR] Device fetch failed: {e}")
    return []

# Fetch latest device data
def fetch_latest_device_data(device_id):
    query = f'''
    from(bucket: "Charger")
      |> range(start: -1y)
      |> filter(fn: (r) => r._measurement == "Device_Data" and r.Device_Id == "{device_id}")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: 1)
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    try:
        result = query_api.query(org=ORG, query=query)
        if not result or all(len(table.records) == 0 for table in result):
            return None

        fields = [
            "Battery_Total", "Charging", "Temperature", "SoC", "SoH", "Speed",
            "Errors", "Battery1", "Battery2", "Battery3", "Battery4", "Battery5", "Battery6",
            "Latitude", "Longitude"
        ]
        
        raw_data = {field: None for field in fields}
        raw_data["Device_Id"] = device_id
        raw_data["Timestamp"] = None

        for table in result:
            for record in table.records:
                values = record.values
                raw_data["Timestamp"] = values.get("_time")
                for field in fields:
                    raw_data[field] = values.get(field)

        def fmt(val, pattern="{:.2f}", suffix=""):
            try:
                if val is None: return "N/A"
                return pattern.format(float(val)) + suffix
            except:
                return "N/A"

        display_data = {
            "Device_Id": device_id,
            "Timestamp": raw_data["Timestamp"].strftime("%Y-%m-%d %H:%M:%S") if raw_data["Timestamp"] else "N/A",
            "Total_Volt": fmt(raw_data["Battery_Total"], "{:.2f}", "V"),
            "Current": fmt(raw_data["Charging"], "{:.2f}", "A"),
            "Temp": fmt(raw_data["Temperature"], "{:.1f}", "°C"),
            "SoC": fmt(raw_data["SoC"], "{:.0f}", "%"),
            "SoH": fmt(raw_data["SoH"], "{:.0f}", "%"),
            "Speed": fmt(raw_data["Speed"], "{:.1f}", " km/h"),
            "Errors": str(raw_data["Errors"]) if raw_data["Errors"] is not None else "N/A",
            "Battery1": fmt(raw_data["Battery1"]),
            "Battery2": fmt(raw_data["Battery2"]),
            "Battery3": fmt(raw_data["Battery3"]),
            "Battery4": fmt(raw_data["Battery4"]),
            "Battery5": fmt(raw_data["Battery5"]),
            "Battery6": fmt(raw_data["Battery6"]),
            "Latitude": fmt(raw_data["Latitude"], "{:.6f}"),
            "Longitude": fmt(raw_data["Longitude"], "{:.6f}"),
        }

        return {"raw": raw_data, "display": display_data}
    except Exception as e:
        print(f"[ERROR] Device data fetch failed: {e}")
        return None

# Create sidebar
def create_sidebar(user_id, company_name, email, phone_no, user_type, status):
    is_admin = str(user_id).lower() == "admin"
    return html.Div([
        html.Div([html.H2(user_id, className="logo-text")], className="sidebar-header"),
        html.Div([
            html.Img(src="assets/logo.png", className="logo-img"),
        ], className="profile-section"),
        html.Ul([
            html.Li(dcc.Link("🏠 Dashboard", href="/dashboard", className="sidebar-link")),
            html.Li(dcc.Link("📈 Analytics", href="/analytics", className="sidebar-link")),
            html.Li(dcc.Link("📡 Trackings", href="/tracking", className="sidebar-link")),
            html.Li(dcc.Link("👤 Profile", href="/profile", className="sidebar-link")),
            *( [html.Li(dcc.Link("⚙️ Settings", href="/admin", className="sidebar-link"))] if is_admin else [] )
        ], className="sidebar-menu"),
        html.Div([
            html.Ul([
                html.Li(dcc.Link("Help", href="#", className="sidebar-link")),
                html.Li(dcc.Link("Contact Us", href="/contactUs", className="sidebar-link")),
                html.Li(dcc.Link("↩️ Logout", href="/", className="sidebar-link"))
            ], className="sidebar-menu")
        ], className="sidebar-divider")
    ], className="sidebar")

# Send warning email
def send_warning_email(receiver_email, device_id, param_name, param_value):
    try:
        subject = f"🚨 Alert: Abnormal Value in {device_id}"
        body = f"Dear User,\n\n⚠️ Warning: Device '{device_id}' has abnormal value.\n\nParameter: {param_name}\nValue: {param_value}\n\nPlease check immediately.\n\nBest regards,\nXaptronic Team"
        return email_sender.send_email(receiver_email, subject, body)
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

# Async email sending
def send_warning_email_async(receiver_email, device_id, param_name, param_value):
    def background_send():
        send_warning_email(receiver_email, device_id, param_name, param_value)
    Thread(target=background_send).start()

def send_recovery_email(receiver_email, device_id, param_name, param_value):
    try:
        subject = f"✅ Recovery: {device_id} {param_name} Normalized"
        body = f"""Dear User,

Good news! Device '{device_id}' has returned to normal operation.

Parameter: {param_name}
Current Value: {param_value}

Alert resolved at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Best regards,
Xaptronic Team"""
        return email_sender.send_email(receiver_email, subject, body)
    except Exception as e:
        print(f"[RECOVERY EMAIL ERROR] {e}")
        return False

def send_recovery_email_async(*args):
    Thread(target=send_recovery_email, args=args).start()

def extract_device_number(device_id):
    """Extract numeric part for sorting (e.g., 'XAP-4567' -> 4567)"""
    match = re.search(r"(\d+)$", device_id)
    return int(match.group(1)) if match else float("inf")

# Generate real-time table data
def generate_table_data(user_id, selected_parameters):
    device_ids = fetch_devices_from_influxdb(user_id)
    device_ids = [d for d in device_ids if d]
    
    if not device_ids:
        return pd.DataFrame(columns=["Device_Id", "Device_Name", "Timestamp"] + selected_parameters)
    
    # Fetch device names from Device_info table
    Device_Names = {}
    for device_id in device_ids:
        query = f'''
        from(bucket: "Charger")
          |> range(start: -1y)
          |> filter(fn: (r) => r._measurement == "Device_info")
          |> filter(fn: (r) => r.Device_Id == "{device_id}")
          |> keep(columns: ["_time", "Device_Id", "Device_Name", "_field", "_value"])
          |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> sort(columns: ["_time"], desc: true)
          |> limit(n:1)
        '''
        #print(f"[DEBUG] Flux for {device_id} →\n{query.strip()}")
        tables = query_api.query(query, org=ORG)
        name = "Unnamed"
        for table in tables:
            for record in table.records:
                # pull Device_Name tag (now carried through by keep())
                name = record.values.get("Device_Name", "Unnamed")
        Device_Names[device_id] = name
        #print(f"[DEBUG] Fetched name for {device_id}: {name}")
        

    # Get main data
    data_list = []
    now = datetime.utcnow()
    recent_threshold = timedelta(minutes=10)  # ✅ You can change to 60 or more mins if needed
    
    for device_id in device_ids:
        latest_data = fetch_latest_device_data(device_id)
        if not latest_data:
            continue
        disp = latest_data["display"]
        disp["Timestamp"]   = disp.get("Timestamp", now)
        disp["Device_Id"]   = device_id
        disp["Device_Name"] = Device_Names.get(device_id, "Unnamed")
        # only keep the columns we want
        filtered = {
            k: v
            for k, v in disp.items()
            if k in ["Device_Id", "Device_Name", "Timestamp"] + selected_parameters
        }
        data_list.append(filtered)
        
    df = pd.DataFrame(data_list)

    if df.empty:
        return pd.DataFrame(columns=["Device ID", "Device Name", "Timestamp"] + selected_parameters)
    
    
    
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

        # Determine if device is recent or stale
        df["is_recent"] = df["Timestamp"].apply(lambda t: (now - t) < recent_threshold if pd.notnull(t) else False)

        # Extract numeric part from Device_Id for sorting
        df["device_number"] = df["Device_Id"].apply(extract_device_number)

        # Sort by:
        # 1. is_recent: True (1st), False (2nd)
        # 2. device_number: ascending
        df = df.sort_values(by=["is_recent", "device_number"], ascending=[False, True])

        # Drop helper columns
        df = df.drop(columns=["Timestamp", "is_recent", "device_number"])
    else:
        df = df.sort_values(by="Device_Id")
    print("[DEBUG] Final generate_table_data head:\n", df.head())
    return df

# Real-Time Data Table Component
def create_data_table():
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col(html.H5("Real-Time Battery Data", className="card-title"), width={"size": "auto", "order": "first"}, className="ps-0 text-start"),
                dbc.Col(html.H5("Loading time...",id="current-datetime", className="datetime-text", style={'white-space': 'nowrap'}), width={"size": "auto", "order": "last"}, className="pe-0 d-flex justify-content-end"),
                ], justify="between", className="align-items-center gx-2"),
            dcc.Store(id="parameter-storage", storage_type="session"),
            #dcc.Interval(id="clock-timer", interval=50000, n_intervals=0),
            html.Div(id="highlight-trigger", style={"display": "none"}),  # Hidden trigger for animations
            html.Div(
                children=[
                    dcc.Checklist(
                        id="parameter-selector",
                        options=[
                            {"label": "Total_Volt", "value": "Total_Volt"},
                            {"label": "Current", "value": "Current"},
                            {"label": "Temp", "value": "Temp"},
                            {"label": "SoC", "value": "SoC"},
                            {"label": "SoH", "value": "SoH"},
                            {"label": "Speed", "value": "Speed"},
                            {"label": "Errors", "value": "Errors"},
                            {"label": "Battery1", "value": "Battery1"},
                            {"label": "Battery2", "value": "Battery2"},
                            {"label": "Battery3", "value": "Battery3"},
                            {"label": "Battery4", "value": "Battery4"},
                            {"label": "Battery5", "value": "Battery5"},
                            {"label": "Battery6", "value": "Battery6"},
                            {"label": "Latitude", "value": "Latitude"},
                            {"label": "Longitude", "value": "Longitude"},
                        ],
                        value=["Total_Volt", "Current", "Temp", "SoC"],
                        persistence=True,
                        persistence_type='local',
                        labelStyle={
                            "display": "inline-block",
                            "marginRight": "12px",
                            "marginBottom": "8px",
                            "color": "white"
                        },
                        inputStyle={"marginRight": "5px"},
                        style={
                            "display": "flex",
                            "flexWrap": "wrap",
                            "padding": "15px",
                            "backgroundColor": "#1f2b3e",
                            "borderRadius": "0px",
                            "boxShadow": "0 0 10px rgba(0, 0, 0, 0.3)"
                        }
                    ),
                    dcc.Checklist(
                        id="display-columns",
                        options=[
                            {"label": "Device ID",   "value": "Device ID"},
                            {"label": "Device Name", "value": "Device Name"},
                        ],
                        value=["Device ID","Device Name"],   # default: both shown
                        inline=True,
                        persistence=True,
                        persistence_type='local',
                        inputStyle={"margin-right": "5px", "margin-left": "10px"},
                        style={"margin-top": "10px"},
                    ),
                ],
                style={"marginBottom": "20px"}
            ),

            # These are real-time only stores for display
            
            dcc.Store(id='socket-data-store', data={}),
            dcc.Store(id='device-data-trigger', data=0),
            dcc.Store(id='highlight-flip', data='A'),
            

            # Real-time data table
            html.Div(html.Div(id="real-time-table", className="styled-table-wrapper"), className="table-container"),
        ]),
        className="dashboard-card"
    )

# Threshold modal
def threshold_modal():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Set Thresholds")),
        dbc.ModalBody([
            html.Div(id="threshold-modal-title", className="mb-2"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Lower Threshold"),
                    dbc.Input(id="lower-threshold", type="number", step=0.01)
                ]),
                dbc.Col([
                    dbc.Label("Upper Threshold"),
                    dbc.Input(id="upper-threshold", type="number", step=0.01)
                ])
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Save", id="save-thresholds", color="success", className="me-2"),
            dbc.Button("Cancel", id="cancel-thresholds", color="secondary")
        ])
    ], id="threshold-modal", is_open=False)

# Layout

# dashboard.py - Complete Updated Layout
layout = html.Div([
   # 3. Required Data Stores
    dcc.Store(id="session-store", storage_type="session"),
    dcc.Store(id="user-details-store", storage_type="session"),
    
    dcc.Store(id='latest-device-data-store', storage_type='session'),
    dcc.Store(id="selected-parameters-store", storage_type="local"),
    dcc.Store(id="threshold-store", storage_type="local"),
    dcc.Store(id="selected-threshold-data", storage_type="local"),
    dcc.Store(id="device-ids-store", storage_type="session"),
    dcc.Store(id="email-tracker-store", data={}),
    dcc.Store(id="modal-lock", data=False),
    dcc.Store(id="threshold-save-trigger", data=0),


    # 4. UI Components
    dcc.Interval(id="initial-trigger", interval=500, n_intervals=0, max_intervals=1),
    dcc.Interval(id="table-refresh", interval=30000),

    
    html.Div(id="sidebar-container"),
    html.Div([create_data_table()], className="content"),

    # ✅ 4. MODAL placed outside table update area so it doesn't reset
    threshold_modal(),

    # 5. Hidden Triggers & Utilities
    html.Div(id="dash-ready-trigger", style={"display": "none"}),
    html.Div(id="connection-status", style={"display": "none"}),

    # 6. Network Monitoring
    html.Script(
        """
        // Real-time connection status monitoring
        window.addEventListener('load', () => {
            // Internet connection monitoring
            const updateOnlineStatus = () => {
                console.log(navigator.onLine ? '🟢 Online' : '🔴 Offline');
            };
            window.addEventListener('online', updateOnlineStatus);
            window.addEventListener('offline', updateOnlineStatus);
            
            // WebSocket specific monitoring
            setInterval(() => {
                const statusDiv = document.getElementById('connection-status');
                if (window.socketConnection && window.socketConnection.socket) {
                    statusDiv.textContent = window.socketConnection.connected ? 
                        'connected' : 'disconnected';
                }
            }, 5000);
        });
        """
    )
], className="dashboard-container")

# ===================== CALLBACKS =====================
if not globals().get("DASHBOARD_CALLBACK_REGISTERED"):
    globals()["DASHBOARD_CALLBACK_REGISTERED"] = True

    @callback(
        [Output("user-details-store", "data"), Output("sidebar-container", "children")],
        [Input("session-store", "data"), Input("url", "pathname")],
        prevent_initial_call=True
    )
    def update_sidebar(user_data, pathname):
        if user_data and isinstance(user_data, dict) and "User_Id" in user_data:
            user_id = user_data["User_Id"]
            user_details = fetch_user_details(user_id)
            if user_details:
                return user_details, create_sidebar(
                    user_details.get('User_Id', 'N/A'),
                    user_details.get('Company_Name', 'N/A'),
                    user_details.get('Email_Id', 'N/A'),
                    user_details.get('Phone_No', 'N/A'),
                    user_details.get('User_Type', 'N/A'),
                    user_details.get('status', 'N/A')
                )
        return dash.no_update, html.Div("Please log in.", style={'color': 'orange'})

    @callback(
        Output('device-data-trigger', 'data'),
        Input('socket-data-store', 'data'),
        State('socket-data-store', 'data'),
        prevent_initial_call=True
    )
    def trigger_device_update(_, data):
        if not data or not data.get('data'):
            raise PreventUpdate
        
        device_id = data.get("device_id")
        if device_id:
            LIVE_DATA_MEMORY[device_id] = {
            "timestamp": data.get("timestamp"),
            "data": data.get("data")
        }
        
        return data  # Return the full payload to trigger update

    @callback(
        Output("display-columns", "value"),
        Input("display-columns", "value"),
        prevent_initial_call=True
    )
    def enforce_display_columns(display_values):
        if "Device ID" not in display_values and "Device Name" not in display_values:
            # Prevent both from being deselected, return default ["Device ID"]
            return ["Device ID"]
        return display_values

    @callback(
    [
        Output("latest-device-data-store", "data"),
        Output("real-time-table", "children"),
        Output("selected-parameters-store", "data"),
        Output("device-ids-store", "data"),
        Output("email-tracker-store", "data"),
        Output("highlight-flip", "data")
    ],
    [
        Input("device-data-trigger", "data"),
        Input("parameter-selector", "value"),
        Input("display-columns", "value"),
        Input("initial-trigger", "n_intervals"),
        Input("table-refresh", "n_intervals"),
        Input("threshold-save-trigger", "data")
    ],
    [
        State("selected-parameters-store", "data"),
        State("session-store", "data"),
        State("threshold-store", "data"),
        State("user-details-store", "data"),
        State("email-tracker-store", "data"),
        State("latest-device-data-store", "data"),
        State("highlight-flip", "data")
    ]
)
    def update_real_time_table(trigger_data, selected_parameters, display_columns, initial_interval, refresh_interval, threshold_trigger, 
                         saved_params, session_data, thresholds, 
                         user_details, email_tracker, last_data, flip_trigger):
    
        ctx = dash.callback_context
        highlight_trigger = "B" if flip_trigger == "A" else "A"
        print("🔥 Highlight trigger flip:", highlight_trigger)

        # Initialize trackers if None
        email_tracker = email_tracker or {}
        thresholds = thresholds or {}

        # Authentication check
        if not session_data or "User_Id" not in session_data:
            return dash.no_update, html.Div("Login Required", style={"color": "red"}), dash.no_update, dash.no_update, email_tracker, highlight_trigger

        user_id = session_data["User_Id"]
        receiver_email = user_details.get("Email_Id")
        final_parameters = selected_parameters or saved_params or []
        device_ids = fetch_devices_from_influxdb(user_id)

        if not display_columns:
            display_columns = ["Device_Id", "Device_Name"]

        # Current time and data structures
        now = datetime.now()
        active_records = []
        inactive_records = []
        status_changes = False

        # Set timeout to 5 minutes (300 seconds)
        LIVE_DATA_TIMEOUT = 300  # 5 minutes in seconds


        # Fetch data from InfluxDB
        influx_data = generate_table_data(user_id, final_parameters)
        influx_data_dict = {row['Device_Id']: row for _, row in influx_data.iterrows()} if not influx_data.empty else {}

        
        # Track previous active devices
        previous_active_devices = set(last_data.get("active_devices", [])) if last_data else set()

        # Process each device
        for device in device_ids:
            device_active = False
            
            
            # Check live data first
            if device in LIVE_DATA_MEMORY:
                live_entry = LIVE_DATA_MEMORY[device]
                timestamp = live_entry.get("timestamp")
                
                if timestamp:
                    try:
                        ts_dt = datetime.fromisoformat(timestamp)
                        time_diff = (now - ts_dt).total_seconds()
                        
                        if time_diff <= LIVE_DATA_TIMEOUT:
                            # Device is active
                            device_active = True
                            try:
                                raw = live_entry.get("data", {})
                                record = {
                                    "Device_Id": device,
                                    "Status": "Active",
                                    "Device_Name": influx_data_dict.get(device, {}).get("Device_Name", "Unnamed"),
                                    "Total_Volt": f"{float(raw['Battery Voltage']['Total']):.2f}V",
                                    "Current": f"{float(raw['Charging']):.2f}A",
                                    "Temp": f"{float(raw['Temperature']):.1f}°C",
                                    "SoC": f"{float(raw['SoC']):.0f}%",
                                    "SoH": f"{float(raw['SoH']):.0f}%",
                                    "Speed": f"{float(raw['Speed']):.1f} km/h",
                                    "Errors": str(raw['Errors']),
                                    "Battery1": f"{float(raw['Battery Voltage']['Battery1']):.2f}",
                                    "Battery2": f"{float(raw['Battery Voltage']['Battery2']):.2f}",
                                    "Battery3": f"{float(raw['Battery Voltage']['Battery3']):.2f}",
                                    "Battery4": f"{float(raw['Battery Voltage']['Battery4']):.2f}",
                                    "Battery5": f"{float(raw['Battery Voltage']['Battery5']):.2f}",
                                    "Battery6": f"{float(raw['Battery Voltage']['Battery6']):.2f}",
                                    "Latitude": f"{float(raw['GPS']['Latitude']):.6f}",
                                    "Longitude": f"{float(raw['GPS']['Longitude']):.6f}"
                                }
                                filtered = {
                                    k: v for k, v in record.items()
                                    if k in display_columns + final_parameters + ["Status", "Device_Id", "Device_Name"]
                                }
                                
                                active_records.append(filtered)
                            except Exception as e:
                                print(f"Error processing active device {device}: {str(e)}")
                                device_active = False
                        else:
                            print(f"⏱️ Device {device} inactive - last update {int(time_diff/60)} mins ago")
                    except Exception as e:
                        print(f"⚠️ Error processing timestamp for device {device}: {str(e)}")
            
            # Handle inactive devices
            if not device_active:
                # Use InfluxDB data if available
                if device in influx_data_dict:
                    influx_row = influx_data_dict[device]
                    inactive_records.append({
                        "Device_Id": device,
                        "Device_Name": influx_data_dict[device].get("Device_Name", "Unnamed"),
                        "Status": f"Inactive ({int(time_diff/60)} mins ago)" if 'time_diff' in locals() else "Inactive",
                        **{param: influx_row.get(param, "N/A") for param in final_parameters}
                    })
                    
                else:
                    inactive_records.append({
                        "Device_Id": device,
                        "Device_Name": influx_data_dict[device].get("Device_Name", "Unnamed"),
                        "Status": f"Inactive ({int(time_diff/60)} mins ago)" if 'time_diff' in locals() else "Inactive",
                        **{param: "N/A" for param in final_parameters}
                    })
                
                # Check for status change
                if device in previous_active_devices:
                    print(f"🔄 Status change: {device} moved to inactive")
                    status_changes = True
                    
                    

        # Create DataFrames
        active_df = pd.DataFrame(active_records)
        inactive_df = pd.DataFrame(inactive_records)

        # Track current active devices for next callback
        current_active_devices = set(active_df['Device_Id']) if not active_df.empty else set()

        # Force UI update if status changed
        

        # Handle empty state
        if active_df.empty and inactive_df.empty:
            return {}, html.Div("No devices found", style={"color": "gray"}), final_parameters, {
                "User_Id": user_id, 
                "Device_Ids": device_ids,
                "active_devices": list(current_active_devices)
            }, email_tracker, highlight_trigger

        # Build tables function
        def build_table(df, is_active=True, display_columns=None):

            if display_columns is None:
                display_columns = ["Device ID", "Device Name"]

            column_key_map = {
                "Device ID": "Device_Id",
                "Device Name": "Device_Name"
            }   

            #header = html.Tr([html.Th("Device ID"), html.Th("Device Name")] + [html.Th(p) for p in final_parameters])
            header = []
            for col in display_columns:
                header.append(html.Th(col,style={"backgroundColor": "#f9f9f9"}))
            for param in final_parameters:
                header.append(html.Th(param,style={"backgroundColor": "#f9f9f9"}))
                
            rows = []
            
            for _, row in df.iterrows():
                device = row.get("Device_Id", "")
                #device = row["Device_Id"]
                #device_name = row.get("Device_Name", "Unnamed")
                #cells = [html.Td(device, style={"textAlign": "center", "verticalAlign": "middle"}), html.Td(device_name, style={"textAlign": "center", "verticalAlign": "middle"})]
                cells = []

                for col in display_columns:
                    key = column_key_map.get(col, col)
                    value = row.get(key, "")
                    cells.append(html.Td(value, style={"textAlign": "center", "verticalAlign": "middle"}))

                for param in final_parameters:
                    value = row.get(param, "N/A")
                    color = "white"
                    
                    if is_active:
                        try:
                            if value in [None, "N/A", "nan", "NaN", "", "-", "."]:
                                raise ValueError("Invalid value")
                            
                            cleaned_value = re.sub(r"[^\d\.\-]+", "", str(value))
                            if cleaned_value in ["", "-", "."]:
                                raise ValueError("Invalid numeric format")
                            
                            value_float = float(cleaned_value)
                            device_thresholds = thresholds.get(device, {}).get(param, {})
                            lower = float(device_thresholds.get("lower", float("-inf")))
                            upper = float(device_thresholds.get("upper", float("inf")))

                            violation_key = f"{device}-{param}"
                            current_status = value_float < lower or value_float > upper
                            previous_status = email_tracker.get(violation_key, {}).get('status', False)
                            color = "red" if current_status else "#1E90FF"

                            if current_status != previous_status:
                                if current_status:
                                    send_warning_email_async(receiver_email, device, param, value)
                                    message = "⚠️ Threshold exceeded!"
                                else:
                                    send_recovery_email_async(receiver_email, device, param, value)
                                    message = "✅ Value normalized."

                                email_tracker[violation_key] = {
                                    'status': current_status,
                                    'last_alert': datetime.now().timestamp(),
                                    'message': message
                                }
                            elif not current_status and violation_key in email_tracker:
                                del email_tracker[violation_key]
                                
                        except Exception as e:
                            print(f"[Threshold Error] {param}: {str(e)}")
                    
                        animate_class = ""
                        if is_active and ctx.triggered_id == "device-data-trigger" and device == trigger_data.get("device_id"):
                            animate_class = f"flash-green-{highlight_trigger}"
                        unique_key = f"{device}-{param}-{highlight_trigger}"

                        cells.append(
                            html.Td(
                                html.Div(
                                    str(value) if value is not None else "null",
                                    id={"type": "param-cell", "device": device, "param": param},
                                    className=animate_class,
                                    key=unique_key,
                                    n_clicks=0,
                                    style={"width": "100%", "height": "100%"},
                                ),
                                
                                style={
                                    "cursor": "pointer",
                                    "color": "#aaa" if not is_active else color,
                                    "textAlign": "center",
                                    "verticalAlign": "middle"
                                },
                            )
                        )
                
                    else:
                        # inactive devices — plain display, no threshold, no id, no color
                        cells.append(
                            html.Td(
                                str(value),
                                style={
                                    "color": "#999",
                                    "textAlign": "center",
                                    "verticalAlign": "middle"
                                }
                            )
                        )

                rows.append(html.Tr(
                    cells,
                    style={"backgroundColor": "#f9f9f9" if not is_active else "inherit"}
                ))
            
            return html.Table(
                [html.Thead(header), html.Tbody(rows)],
                className="table table-bordered",
                style={"marginBottom": "20px"}
            )
        if active_df.empty and inactive_df.empty:
            return {}, html.Div("No devices found", style={"color": "gray"}), final_parameters, {
                "User_Id": user_id,
                "Device_Ids": device_ids,
                "active_devices": list(current_active_devices)
            }, email_tracker, highlight_trigger
        # Build tables
        active_table = html.Div([
            html.H5("Active Devices", style={"marginTop": "20px", "color": "#4CAF50"}),
            build_table(active_df, is_active=True, display_columns=display_columns)
        ]) if not active_df.empty else html.Div()

        inactive_table = html.Div([
            html.H5("Inactive Devices", style={"marginTop": "20px", "color": "#aaa"}),
            build_table(inactive_df, is_active=False, display_columns=display_columns)
        ]) if not inactive_df.empty else html.Div()

        # Combine tables
        final_table = html.Div([active_table, inactive_table])

        # Prepare return data
        return_data = {
            "active": active_df.to_dict("records"),
            "inactive": inactive_df.to_dict("records")
        }

        return return_data, final_table, final_parameters, {
            "User_Id": user_id,
            "Device_Ids": device_ids,
            "active_devices": list(current_active_devices)
        }, email_tracker, highlight_trigger


    @callback(
        [Output("threshold-modal", "is_open"),
        Output("threshold-modal-title", "children"),
        Output("selected-threshold-data", "data"),
        Output("modal-lock", "data")],  # <-- new output
        [Input({"type": "param-cell", "device": dash.ALL, "param": dash.ALL}, "n_clicks_timestamp"),
        Input("save-thresholds", "n_clicks"),
        Input("cancel-thresholds", "n_clicks")],
        prevent_initial_call=True
    )

    def handle_modal(open_clicks, save_click, cancel_click):
        ctx = dash.callback_context
        ctx_trigger = ctx.triggered_id

        # ✅ If Save or Cancel clicked, close modal and unlock
        if not ctx_trigger or ctx_trigger in ["save-thresholds", "cancel-thresholds"]:
            return False, no_update, no_update, False

        # ✅ Opening modal via param-cell click
        if open_clicks and any(open_clicks):
            latest_index = max(
                [(i, ts) for i, ts in enumerate(open_clicks) if ts is not None],
                key=lambda x: x[1],
                default=(None, None)
            )[0]

            if latest_index is not None:
                triggered_id = ctx.inputs_list[0][latest_index]['id']
                device = triggered_id.get("device")
                param = triggered_id.get("param")

                if device and param:
                    title = f"Set thresholds for {param} of Device {device}"
                    return True, title, {"device": device, "param": param}, True

        # Fallback: keep modal closed and unlocked
        return no_update, no_update, no_update, no_update

    

    @callback(
        [Output("threshold-store", "data", allow_duplicate=True),
         Output("threshold-save-trigger", "data")],
        Input("save-thresholds", "n_clicks"),
        [State("lower-threshold", "value"),
         State("upper-threshold", "value"),
         State("selected-threshold-data", "data"),
         State("threshold-store", "data"),
         State("threshold-save-trigger", "data")],
        prevent_initial_call=True
    )
    def save_thresholds(n_clicks, lower, upper, selected_data, current_thresholds, prev_trigger):
        if not selected_data:
            raise PreventUpdate
            
        device_id = selected_data.get("device")
        parameter = selected_data.get("param")
        if not device_id or not parameter:
            raise PreventUpdate

        try:
            thresholds = current_thresholds or {}
            if device_id not in thresholds:
                thresholds[device_id] = {}
                
            thresholds[device_id][parameter] = {
                "lower": float(lower) if lower is not None else float('-inf'),
                "upper": float(upper) if upper is not None else float('inf')
            }

            # Flip trigger to force table refresh
            new_trigger = 1 if prev_trigger == 0 else 0
            return thresholds, new_trigger
        except Exception:
            return dash.no_update, dash.no_update

    @callback(
        Output("lower-threshold", "value"),
        Output("upper-threshold", "value"),
        Input("threshold-modal", "is_open"),
        [State("selected-threshold-data", "data"),
         State("threshold-store", "data")],
        prevent_initial_call=True
    )
    def populate_threshold_inputs(is_open, selected, store):
        if not is_open or not selected:
            raise PreventUpdate
            
        device = selected.get("device")
        param = selected.get("param")
        store = store or {}
        
        if device in store and param in store[device]:
            return store[device][param].get("lower"), store[device][param].get("upper")
        return None, None
    







    