"""
RS485 MODBUS Configuration Page
Matches the MODBUS configuration form from image 1
"""
from dash import html, dcc, Input, Output, State, ALL, callback, ctx, no_update
import dash_bootstrap_components as dbc
import json
import logging


def create_rs485_modbus_layout():
    """Create RS485 MODBUS configuration page matching image 1"""
    
    return html.Div([
        # Header
        html.Div([
            html.H5([
                html.I(className="fas fa-network-wired me-2", style={'color': '#667eea'}),
                "RS485 MODBUS Configuration"
            ], className='fw-bold mb-3'),
        ], className='mb-4'),
        
        # Communication Settings Section
        html.Div([
            html.H5([
                html.I(className="fas fa-cog me-2", style={'color': '#667eea'}),
                "Communication Settings"
            ], className='fw-bold mb-3'),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Baud Rate", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='modbus-baud-rate',
                        options=[
                            {'label': '9600', 'value': '9600'},
                            {'label': '19200', 'value': '19200'},
                            {'label': '38400', 'value': '38400'},
                            {'label': '57600', 'value': '57600'},
                            {'label': '115200', 'value': '115200'},
                        ],
                        value='9600',
                        clearable=False
                    ),
                ], md=3),
                
                dbc.Col([
                    dbc.Label("Data Bits", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='modbus-data-bits',
                        options=[
                            {'label': '7', 'value': '7'},
                            {'label': '8', 'value': '8'},
                        ],
                        value='8',
                        clearable=False
                    ),
                ], md=3),
                
                dbc.Col([
                    dbc.Label("Parity", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='modbus-parity',
                        options=[
                            {'label': 'None', 'value': 'None'},
                            {'label': 'Even', 'value': 'Even'},
                            {'label': 'Odd', 'value': 'Odd'},
                        ],
                        value='None',
                        clearable=False
                    ),
                ], md=3),
                
                dbc.Col([
                    dbc.Label("Stop Bits", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='modbus-stop-bits',
                        options=[
                            {'label': '1', 'value': '1'},
                            {'label': '2', 'value': '2'},
                        ],
                        value='1',
                        clearable=False
                    ),
                ], md=3),
            ], className='mb-4'),
        ], className='stat-card p-4 mb-4'),
        
        # Protocol Settings Section
        html.Div([
            html.H5([
                html.I(className="fas fa-exchange-alt me-2", style={'color': '#667eea'}),
                "Protocol Settings"
            ], className='fw-bold mb-3'),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Mode", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='modbus-mode',
                        options=[
                            {'label': 'RTU', 'value': 'RTU'},
                            {'label': 'ASCII', 'value': 'ASCII'},
                            {'label': 'TCP', 'value': 'TCP'},
                        ],
                        value='RTU',
                        clearable=False
                    ),
                ], md=6),
                
                dbc.Col([
                    dbc.Label("Role", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='modbus-role',
                        options=[
                            {'label': 'Master', 'value': 'Master'},
                            {'label': 'Slave', 'value': 'Slave'},
                        ],
                        value='Master',
                        clearable=False
                    ),
                ], md=6),
            ], className='mb-4'),
        ], className='stat-card p-4 mb-4'),
        
        # Slave Devices Section
        html.Div([
            html.H5([
                html.I(className="fas fa-server me-2", style={'color': '#667eea'}),
                "Slave Devices"
            ], className='fw-bold mb-3'),
            
            # Slave Devices Table
            html.Div([
                dbc.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Slave ID", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Function Code", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Register Address", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Data Type", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Endianness", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Variable Name", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Action", style={'backgroundColor': '#667eea', 'color': 'white'}),
                        ])
                    ]),
                    html.Tbody(id='modbus-slave-devices-tbody', children=[])
                ], bordered=True, hover=True, responsive=True, className='mb-3'),
            ], className='modbus-table-container'),
            
            # Add Device Button
            dbc.Button([
                html.I(className="fas fa-plus me-2"),
                "Add Device"
            ], id='add-modbus-device-btn', color='primary', className='mb-3', n_clicks=0),
            
            # Polling Interval
            dbc.Row([
                dbc.Col([
                    dbc.Label("Polling Interval (ms):", className='fw-bold'),
                ], md=3),
                dbc.Col([
                    dbc.Input(
                        id='modbus-polling-interval',
                        type='number',
                        value=1000,
                        min=100,
                        step=100
                    ),
                ], md=9),
            ]),
        ], className='stat-card p-4 mb-4'),
        
        # Save Configuration Button for RS485 MODBUS Tab
        html.Div([
            dbc.Button([
                html.I(className="fas fa-save me-2"),
                "Save Configuration"
            ], id='save-modbus-config-btn', color='primary', size='lg', className='mt-3'),
            html.Div(id='save-modbus-status-message', className='d-inline-block ms-3 mt-3'),
        ], className='text-end'),
        
        # Store for device data
        dcc.Store(id='modbus-devices-store', data=[{"index": 0, "slave_id": "1", "function_code": "0x03", "register_addr": "0", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name"}]),
        # Hidden trigger store to force updates
        dcc.Store(id='modbus-trigger-store', data=0),
    ])


# Callback to auto-load MODBUS configuration when device is selected or after save
@callback(
    [
        Output('modbus-baud-rate', 'value', allow_duplicate=True),
        Output('modbus-data-bits', 'value', allow_duplicate=True),
        Output('modbus-parity', 'value', allow_duplicate=True),
        Output('modbus-stop-bits', 'value', allow_duplicate=True),
        Output('modbus-mode', 'value', allow_duplicate=True),
        Output('modbus-role', 'value', allow_duplicate=True),
        Output('modbus-polling-interval', 'value', allow_duplicate=True),
        Output('modbus-devices-store', 'data', allow_duplicate=True),
    ],
    [
        Input('device-selector', 'value'),  # Trigger on device selection change
        Input('url', 'pathname'),  # Trigger on page load/navigation/refresh
        Input('config-reload-trigger', 'data'),  # Trigger after successful save
        Input('config-tabs', 'active_tab'),  # Trigger on tab switch
    ],
    [
        State('device-config-session-store', 'data'),
        State('device-selector', 'value'),  # Also get as State for fallback
    ],
    prevent_initial_call='initial_duplicate',
    allow_duplicate=True
)
def load_modbus_configuration(device_id, pathname, reload_trigger, active_tab, session_data, device_id_state):
    """Load saved MODBUS configuration for selected device and populate UI fields
    
    Triggers on:
    - Device selection change (device-selector value)
    - Page load/navigation (pathname change)
    - After successful save (config-reload-trigger timestamp update)
    - Browser refresh (pathname change)
    - Tab switch (active_tab change) - ensures latest config is always shown
    
    Loads configuration from database if exists, otherwise uses default values.
    """
    logger = logging.getLogger(__name__)
    
    # Get trigger info for logging
    triggered_id = ctx.triggered_id if hasattr(ctx, 'triggered_id') else None
    
    # Skip loading if triggered by tab switch but MODBUS tab is not active
    # But allow loading on device selection, save, or page load (even if tab not active yet)
    if triggered_id == 'config-tabs':
        if active_tab != 'tab-modbus':
            logger.debug(f"⏭️ Skipping MODBUS config load - triggered by tab switch but MODBUS tab not active (active: {active_tab})")
            return [no_update] * 8
    
    # Allow loading on dashboard page (device config is embedded in dashboard)
    skip_paths = ['/login', '/logout', '/']
    if pathname in skip_paths:
        logger.debug(f"⏭️ Skipping MODBUS config load for pathname: {pathname}")
        return [no_update] * 8
    
    # If device_id not available from Input, try to get it from reload_trigger or State
    if not device_id:
        if triggered_id == 'config-reload-trigger' and reload_trigger:
            # Extract device_id from reload trigger data
            device_id = reload_trigger.get('device_id')
            if device_id:
                logger.info(f"📌 Using device_id from reload trigger for MODBUS: {device_id}")
        elif triggered_id == 'config-tabs':
            # For tab switch, use device_id from State if available
            device_id = device_id_state
            if device_id:
                logger.debug(f"📌 Using device_id from State for MODBUS tab switch: {device_id}")
    
    if not device_id:
        # Still no device_id - skip loading
        if triggered_id == 'config-reload-trigger' or triggered_id == 'config-tabs':
            logger.debug(f"⏭️ Reload/tab switch triggered but no device selected for MODBUS (trigger: {triggered_id})")
        else:
            logger.debug(f"⏭️ No device selected, skipping MODBUS config load")
        return [no_update] * 8
    
    try:
        # Get logged-in user info
        username = None
        is_admin = False
        if session_data:
            username = session_data.get('username', '')
            user_type = session_data.get('user_type', 'user')
            is_admin = (username == 'admin')
        
        logger.info(f"🔄 Loading MODBUS configuration for device: {device_id}, user: {username}, trigger: {triggered_id}, active_tab: {active_tab}")
        
        # Verify device ownership (unless admin)
        if not is_admin and username:
            from app.services.device_info_service import DeviceInfoService
            device_info_service = DeviceInfoService()
            device_info = device_info_service.get_device_info(device_id)
            
            if not device_info:
                logger.warning(f"⚠️ Device {device_id} not found in database")
                return [no_update] * 8
            
            device_owner = device_info.get('Owner', 'Unassigned')
            if device_owner != username:
                logger.warning(f"⚠️ User {username} attempted to access device {device_id} owned by {device_owner} - Access denied")
                return [no_update] * 8
        
        from app.services.device_config_db import DeviceConfigDBService
        db_service = DeviceConfigDBService()
        
        if not db_service.is_connected():
            logger.warning("⚠️ Database not connected, cannot load MODBUS configuration")
            return [no_update] * 8
        
        # Load MODBUS config from database
        # If triggered by reload trigger, add a small delay to ensure DB write is flushed
        # CRITICAL: Always load from database to ensure we get the latest saved data
        # Don't preserve store - reload from database to show what was actually saved
        if triggered_id == 'config-reload-trigger':
            import time
            time.sleep(0.5)  # Wait 0.5 seconds to ensure database write is fully flushed
            logger.info(f"🔄 MODBUS reload triggered after save - loading from database to show saved data")
            # Continue to load from database below (don't return early)
        
        logger.info(f"🔄 Loading MODBUS config from database for device {device_id}, triggered by: {triggered_id}")
        modbus_config = db_service.get_modbus_config(device_id)
        
        # Set default values (used if no config exists in database)
        baud_rate = '9600'
        data_bits = '8'
        parity = 'None'
        stop_bits = '1'
        mode = 'RTU'
        role = 'Master'
        polling_interval = 1000
        devices_store = [{"index": 0, "slave_id": "1", "function_code": "0x03", "register_addr": "0", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name"}]
        
        # Populate from database if config exists
        if modbus_config:
            logger.info(f"✅ Loading MODBUS config from database for device {device_id}")
            
            comm_settings = modbus_config.get("communication_settings", {})
            protocol_settings = modbus_config.get("protocol_settings", {})
            
            baud_rate = str(comm_settings.get("baud_rate", 9600))
            data_bits = str(comm_settings.get("data_bits", 8))
            parity = comm_settings.get("parity", "None")
            stop_bits = str(comm_settings.get("stop_bits", 1))
            
            mode = protocol_settings.get("mode", "RTU")
            role = protocol_settings.get("role", "Master")
            polling_interval = modbus_config.get("polling_interval_ms", 1000)
            
            # Convert slave devices to store format
            # Load from Device: Create rows dynamically based on device data
            # CRITICAL: Sort by index first to ensure correct order, then re-index sequentially
            slave_devices_list = modbus_config.get("slave_devices", [])
            if slave_devices_list and len(slave_devices_list) > 0:
                devices_store = []
                # Sort by index first to ensure correct order (handles any index gaps)
                sorted_slaves = sorted(slave_devices_list, key=lambda x: x.get("index", 0))
                for idx, device in enumerate(sorted_slaves):
                    devices_store.append({
                        "index": idx,  # Re-index to ensure sequential indices (0, 1, 2, ...)
                        "slave_id": str(device.get("slave_id", str(idx + 1))),
                        "function_code": str(device.get("function_code", "0x03")),
                        "register_addr": str(device.get("register_address", device.get("register_addr", "0"))),  # Support both field names
                        "data_type": str(device.get("data_type", "int8")),
                        "endianness": str(device.get("endianness", "Big Endian")),
                        "var_name": str(device.get("variable_name", device.get("var_name", "")))
                    })
                logger.info(f"✅ Loaded {len(devices_store)} slave device(s) from database for device {device_id}")
                logger.debug(f"   Slave IDs loaded: {[d.get('slave_id') for d in devices_store]}")
                logger.debug(f"   Original indices: {[s.get('index') for s in sorted_slaves]}")
                logger.debug(f"   Re-indexed to: {[d.get('index') for d in devices_store]}")
            else:
                # No slave devices in database - use default single row
                devices_store = [{"index": 0, "slave_id": "1", "function_code": "0x03", "register_addr": "0", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name"}]
                logger.info(f"ℹ️ No slave devices in database for device {device_id}, using default single row")
        else:
            logger.info(f"ℹ️ No MODBUS config found in database for device {device_id}, using default values")
        
        return (
            baud_rate,
            data_bits,
            parity,
            stop_bits,
            mode,
            role,
            polling_interval,
            devices_store
        )
        
    except Exception as e:
        logger.error(f"Error loading MODBUS configuration: {e}")
        logger.exception("Full error traceback:")
        return [no_update] * 8


def create_modbus_slave_row(index, slave_id, function_code, register_addr, data_type, endianness, var_name):
    """Create a single MODBUS slave device row"""
    return html.Tr([
        html.Td(
            dbc.Input(
                id={'type': 'modbus-slave-id', 'index': index},
                type='text',
                value=slave_id,
                size='sm'
            )
        ),
        html.Td(
            dcc.Dropdown(
                id={'type': 'modbus-function-code', 'index': index},
                options=[
                    {'label': '0x01 - Read Coils', 'value': '0x01'},
                    {'label': '0x02 - Read Discrete Inputs', 'value': '0x02'},
                    {'label': '0x03 - Read Holding Registers', 'value': '0x03'},
                    {'label': '0x04 - Read Input Registers', 'value': '0x04'},
                    {'label': '0x05 - Write Single Coil', 'value': '0x05'},
                    {'label': '0x06 - Write Single Register', 'value': '0x06'},
                    {'label': '0x0F - Write Multiple Coils', 'value': '0x0F'},
                    {'label': '0x10 - Write Multiple Registers', 'value': '0x10'},
                ],
                value=function_code if isinstance(function_code, str) and function_code.startswith('0x') else '0x03',
                clearable=False,
                style={
                    'fontSize': '0.9rem',
                    'width': '100%',
                    'minWidth': '250px'
                },
                optionHeight=40,
                maxHeight=300
            ),
            style={'minWidth': '250px', 'width': '250px'}
        ),
        html.Td(
            dbc.Input(
                id={'type': 'modbus-register-addr', 'index': index},
                type='text',
                value=register_addr,
                size='sm'
            )
        ),
        html.Td(
            dcc.Dropdown(
                id={'type': 'modbus-data-type', 'index': index},
                options=[
                    {'label': 'int8', 'value': 'int8'},
                    {'label': 'uint8', 'value': 'uint8'},
                    {'label': 'int16', 'value': 'int16'},
                    {'label': 'uint16', 'value': 'uint16'},
                    {'label': 'int32', 'value': 'int32'},
                    {'label': 'uint32', 'value': 'uint32'},
                    {'label': 'float32', 'value': 'float32'},
                    {'label': 'float64', 'value': 'float64'},
                ],
                value=data_type,
                clearable=False,
                style={
                    'fontSize': '0.9rem',
                    'width': '100%',
                    'minWidth': '200px'
                },
                optionHeight=40,
                maxHeight=300
            ),
            style={'minWidth': '200px', 'width': '200px'}
        ),
        html.Td(
            dcc.Dropdown(
                id={'type': 'modbus-endianness', 'index': index},
                options=[
                    {'label': 'Big Endian', 'value': 'Big Endian'},
                    {'label': 'Little Endian', 'value': 'Little Endian'},
                ],
                value=endianness,
                clearable=False,
                style={
                    'fontSize': '0.9rem',
                    'width': '100%',
                    'minWidth': '180px'
                },
                optionHeight=40,
                maxHeight=300
            ),
            style={'minWidth': '180px', 'width': '180px'}
        ),
        html.Td(
            dbc.Input(
                id={'type': 'modbus-var-name', 'index': index},
                type='text',
                value=var_name,
                size='sm'
            )
        ),
        html.Td(
            dbc.Button(
                html.I(className="fas fa-trash"),
                id={'type': 'modbus-remove-device', 'index': index},
                color='danger',
                size='sm',
                outline=True,
                n_clicks=0
            )
        ),
    ])


# Callback to update table from store
@callback(
    Output('modbus-slave-devices-tbody', 'children'),
    Input('modbus-devices-store', 'data'),
    prevent_initial_call=False
)
def update_modbus_table(devices_data):
    """Update table rows from store data.
    
    This callback creates table rows based on the store data.
    It ensures all rows are preserved and displayed correctly.
    
    CRITICAL: This must create ALL rows from the store data, not just a subset.
    """
    logger = logging.getLogger(__name__)
    
    # Always ensure we have at least one device
    if not devices_data or len(devices_data) == 0:
        logger.warning("⚠️ MODBUS table: No devices data, creating default row")
        devices_data = [{"index": 0, "slave_id": "1", "function_code": "0x03", "register_addr": "0", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name"}]
    
    logger.info(f"📊 MODBUS table: Creating {len(devices_data)} row(s) from store data")
    
    # Create rows for ALL devices - preserve all rows
    # Sort by index to ensure correct order
    sorted_devices = sorted(devices_data, key=lambda x: x.get("index", 0))
    
    rows = []
    for device in sorted_devices:
        row = create_modbus_slave_row(
            device.get("index", 0),
            device.get("slave_id", "1"),
            device.get("function_code", "0x03"),
            device.get("register_addr", "0"),
            device.get("data_type", "int8"),
            device.get("endianness", "Big Endian"),
            device.get("var_name", "Variable Name")
        )
        rows.append(row)
    
    logger.info(f"✅ MODBUS table: Created {len(rows)} row(s) - all rows displayed")
    return rows


# Unified callback for add and remove operations
@callback(
    Output('modbus-devices-store', 'data'),
    Output('modbus-trigger-store', 'data'),
    Input('add-modbus-device-btn', 'n_clicks'),
    Input({'type': 'modbus-remove-device', 'index': ALL}, 'n_clicks'),
    [
        State('modbus-devices-store', 'data'),
        State('modbus-trigger-store', 'data'),
        # CRITICAL: Get current UI values to preserve user-filled data
        State({'type': 'modbus-slave-id', 'index': ALL}, 'value'),
        State({'type': 'modbus-function-code', 'index': ALL}, 'value'),
        State({'type': 'modbus-register-addr', 'index': ALL}, 'value'),
        State({'type': 'modbus-data-type', 'index': ALL}, 'value'),
        State({'type': 'modbus-endianness', 'index': ALL}, 'value'),
        State({'type': 'modbus-var-name', 'index': ALL}, 'value'),
    ],
    prevent_initial_call=True
)
def manage_modbus_devices(add_clicks, remove_clicks_list, devices_data, trigger_value, 
                          slave_ids, function_codes, register_addrs, data_types, endianness_list, var_names):
    """Handle both add and remove device operations"""
    if not ctx.triggered:
        return no_update, no_update
    
    # Get the triggered component
    triggered_id = ctx.triggered[0]['prop_id']
    
    # Initialize devices_data if needed
    if devices_data is None:
        devices_data = []
    if len(devices_data) == 0:
        devices_data = [{"index": 0, "slave_id": "1", "function_code": "0x03", "register_addr": "0", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name"}]
    
    # Handle ADD operation
    if 'add-modbus-device-btn' in triggered_id:
        logger = logging.getLogger(__name__)
        logger.info(f"➕ MODBUS: Adding new device. Current store has {len(devices_data)} row(s)")
        
        # CRITICAL: First, merge current UI values into store to preserve user-filled data
        # This ensures that any values the user just filled are preserved before adding new row
        updated_devices = []
        
        # Get current UI row count
        ui_row_count = len(slave_ids) if slave_ids else len(devices_data)
        
        # Merge UI values with store data - prioritize UI values (user just filled them)
        for idx in range(max(ui_row_count, len(devices_data))):
            if idx < len(devices_data):
                # Use store data as base
                device = devices_data[idx].copy()
            else:
                # New row from UI that's not in store yet
                device = {"index": idx, "slave_id": "1", "function_code": "0x03", "register_addr": "0", 
                          "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name"}
            
            # Override with UI values if available (user just filled them)
            if idx < ui_row_count:
                if slave_ids and idx < len(slave_ids) and slave_ids[idx] is not None:
                    device["slave_id"] = str(slave_ids[idx])
                if function_codes and idx < len(function_codes) and function_codes[idx]:
                    device["function_code"] = str(function_codes[idx])
                if register_addrs and idx < len(register_addrs) and register_addrs[idx] is not None:
                    device["register_addr"] = str(register_addrs[idx])
                if data_types and idx < len(data_types) and data_types[idx]:
                    device["data_type"] = str(data_types[idx])
                if endianness_list and idx < len(endianness_list) and endianness_list[idx]:
                    device["endianness"] = str(endianness_list[idx])
                if var_names and idx < len(var_names) and var_names[idx] is not None:
                    device["var_name"] = str(var_names[idx])
            
            device["index"] = idx  # Ensure correct index
            updated_devices.append(device)
        
        # Calculate next slave ID by finding the maximum existing slave ID and incrementing
        max_slave_id = 0
        for device in updated_devices:
            try:
                slave_id_str = str(device.get("slave_id", "1")).strip()
                # Remove any non-numeric characters and convert to int
                slave_id_num = int(''.join(filter(str.isdigit, slave_id_str)) or "1")
                max_slave_id = max(max_slave_id, slave_id_num)
            except (ValueError, TypeError):
                pass
        
        # Next slave ID is max + 1
        next_slave_id = str(max_slave_id + 1)
        
        # Add new device with next index and auto-incremented slave ID
        new_index = len(updated_devices)
        updated_devices.append({
            "index": new_index,
            "slave_id": next_slave_id,
            "function_code": "0x03",
            "register_addr": "0",
            "data_type": "int8",
            "endianness": "Big Endian",
            "var_name": "Variable Name"
        })
        
        logger.info(f"✅ MODBUS: Added new device. Store now has {len(updated_devices)} row(s). New slave ID: {next_slave_id}")
        
        # Use timestamp for trigger to track when row was added
        # This helps sync callback detect when row addition just happened
        import time
        new_trigger = time.time()  # Use current timestamp
        logger.debug(f"✅ MODBUS: Updated trigger store to {new_trigger} (timestamp)")
        return updated_devices, new_trigger
    
    # Handle REMOVE operation
    if 'modbus-remove-device' in triggered_id and 'index' in triggered_id:
        try:
            # Parse the index from the triggered ID
            prop_id_json = triggered_id.split('.n_clicks')[0]
            button_id = json.loads(prop_id_json)
            index_to_remove = button_id.get('index')
        except (json.JSONDecodeError, KeyError, ValueError):
            # Fallback parsing
            try:
                start_idx = triggered_id.find('"index":') + 8
                end_idx = triggered_id.find(',', start_idx)
                if end_idx == -1:
                    end_idx = triggered_id.find('}', start_idx)
                index_to_remove = int(triggered_id[start_idx:end_idx])
            except (ValueError, AttributeError):
                return no_update, no_update
        
        # Check if we have more than one row
        if len(devices_data) <= 1:
            return no_update, no_update
        
        # Remove the device at index_to_remove and re-index
        updated_devices = []
        for idx, device in enumerate(devices_data):
            device_index = device.get("index")
            # Skip the device we want to remove
            if device_index == index_to_remove:
                continue
            
            # Add remaining devices with re-indexed values
            updated_devices.append({
                "index": len(updated_devices),
                "slave_id": str(device.get("slave_id", "1")),
                "function_code": str(device.get("function_code", "0x03")),
                "register_addr": str(device.get("register_addr", "0")),
                "data_type": str(device.get("data_type", "int8")),
                "endianness": str(device.get("endianness", "Big Endian")),
                "var_name": str(device.get("var_name", "Variable Name"))
            })
        
        # Ensure at least one device remains
        if len(updated_devices) == 0:
            updated_devices = [{"index": 0, "slave_id": "1", "function_code": "0x03", "register_addr": "0", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name"}]
        
        # Increment trigger to force update detection
        new_trigger = (trigger_value if trigger_value is not None else 0) + 1
        return updated_devices, new_trigger
    
    return no_update, no_update


# Callback to sync user edits back into the devices store
@callback(
    Output('modbus-devices-store', 'data', allow_duplicate=True),
    [
        Input({'type': 'modbus-slave-id', 'index': ALL}, 'value'),
        Input({'type': 'modbus-function-code', 'index': ALL}, 'value'),
        Input({'type': 'modbus-register-addr', 'index': ALL}, 'value'),
        Input({'type': 'modbus-data-type', 'index': ALL}, 'value'),
        Input({'type': 'modbus-endianness', 'index': ALL}, 'value'),
        Input({'type': 'modbus-var-name', 'index': ALL}, 'value'),
    ],
    [
        State('modbus-devices-store', 'data'),  # Get current store state
        State('modbus-trigger-store', 'data'),  # Check if row addition is in progress
    ],
    prevent_initial_call=True
)
def sync_modbus_devices_store(slave_ids, function_codes, register_addrs, data_types, endianness_list, var_names, current_store, trigger_value):
    """Synchronize modbus-devices-store with the latest UI values.
    
    CRITICAL: This callback must NEVER reduce the number of rows.
    It should only update values in existing rows, or add rows if UI has more.
    
    IMPORTANT: This callback should NOT run during row addition.
    It should only run when user actually edits values in existing, fully-rendered rows.
    
    Strategy:
    1. Get current store state (preserves all existing rows)
    2. Merge UI values into store (update existing, add new if needed)
    3. Never remove rows - only update or add
    4. Skip update if data is incomplete (rows being added)
    """
    logger = logging.getLogger(__name__)
    
    # CRITICAL: Check trigger store - if it changed recently, row addition might be in progress
    # Wait a bit before syncing to avoid race conditions
    import time
    current_time = time.time()
    if trigger_value and isinstance(trigger_value, (int, float)):
        # Check if trigger_value is a timestamp (>= 1000000000 = year 2001) or counter (< 1000000000)
        if trigger_value >= 1000000000:  # Timestamp (seconds since epoch)
            # If trigger was updated very recently (< 2 seconds ago), skip sync
            # This prevents sync from running immediately after row addition
            time_since_trigger = current_time - trigger_value
            if time_since_trigger < 2.0:
                logger.debug(f"⚠️ MODBUS sync: Trigger store updated recently ({time_since_trigger:.2f}s ago). Skipping update (row addition likely in progress)")
                return no_update
        else:
            # Old counter format - treat as recent if < 10 (likely just added)
            if trigger_value < 10:
                logger.debug(f"⚠️ MODBUS sync: Trigger store has low counter value ({trigger_value}). Skipping update (row addition likely in progress)")
                return no_update
    
    # If no slave_ids from UI, don't update (inputs not ready)
    if not slave_ids or len(slave_ids) == 0:
        logger.debug("⚠️ MODBUS sync: No slave_ids from UI, skipping update (inputs not ready)")
        return no_update
    
    # Get current store state - this preserves all existing rows
    if current_store is None:
        current_store = []
    if len(current_store) == 0:
        current_store = [{"index": 0, "slave_id": "1", "function_code": "0x03", "register_addr": "0", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name"}]
    
    row_count = len(slave_ids)
    collections = [function_codes, register_addrs, data_types, endianness_list, var_names]
    
    # CRITICAL: Check if all collections have the same length
    # If not, inputs are still being rendered - don't update store
    # This prevents sync from running during row addition
    if any(len(lst) != row_count for lst in collections):
        logger.debug(f"⚠️ MODBUS sync: Mismatched collection lengths. slave_ids: {row_count}, others: {[len(lst) for lst in collections]}. Skipping update (inputs still rendering - likely row addition in progress)")
        return no_update
    
    # Check if any collection is None or empty (inputs not ready)
    if any(lst is None or len(lst) == 0 for lst in collections):
        logger.debug("⚠️ MODBUS sync: Some collections are None or empty. Skipping update (inputs not ready)")
        return no_update
    
    # CRITICAL: Only sync when UI rows match or are slightly more than store rows
    # If UI has fewer rows, it means rows are being removed or rendering - skip sync
    # If UI has significantly more rows (> 2), it means rows are being added - skip sync
    if row_count < len(current_store):
        logger.debug(f"⚠️ MODBUS sync: UI has {row_count} rows but store has {len(current_store)} rows. Skipping update (row removal or rendering in progress)")
        return no_update
    
    # If UI has many more rows, might be rendering - wait a bit
    if row_count > len(current_store) + 1:
        logger.debug(f"⚠️ MODBUS sync: UI has {row_count} rows but store has {len(current_store)} rows. Large difference suggests rendering. Skipping update.")
        return no_update
    
    # CRITICAL: Merge UI values with current store
    # Strategy: Update existing rows, add new rows if UI has more
    # NEVER reduce the number of rows
    
    # Create a map of current store by index for fast lookup
    store_map = {device.get("index", idx): device for idx, device in enumerate(current_store)}
    max_store_index = max(store_map.keys()) if store_map else -1
    
    # Build updated devices list
    # Start with all existing rows from store (preserves all rows)
    updated_devices = []
    
    # First, update existing rows with UI values (up to row_count)
    for idx in range(min(row_count, len(current_store))):
        if idx in store_map:
            # Update existing row with UI values
            device = store_map[idx].copy()
            device["slave_id"] = str(slave_ids[idx]) if slave_ids[idx] is not None else device.get("slave_id", str(idx + 1))
            device["function_code"] = str(function_codes[idx]) if function_codes[idx] else device.get("function_code", "0x03")
            device["register_addr"] = str(register_addrs[idx]) if register_addrs[idx] is not None else device.get("register_addr", "0")
            device["data_type"] = str(data_types[idx]) if data_types[idx] else device.get("data_type", "int8")
            device["endianness"] = str(endianness_list[idx]) if endianness_list[idx] else device.get("endianness", "Big Endian")
            device["var_name"] = str(var_names[idx]) if var_names[idx] is not None else device.get("var_name", "")
            updated_devices.append(device)
        else:
            # Row doesn't exist in store - create new from UI
            updated_devices.append({
                "index": idx,
                "slave_id": str(slave_ids[idx]) if slave_ids[idx] is not None else str(idx + 1),
                "function_code": str(function_codes[idx]) if function_codes[idx] else "0x03",
                "register_addr": str(register_addrs[idx]) if register_addrs[idx] is not None else "0",
                "data_type": str(data_types[idx]) if data_types[idx] else "int8",
                "endianness": str(endianness_list[idx]) if endianness_list[idx] else "Big Endian",
                "var_name": str(var_names[idx]) if var_names[idx] is not None else ""
            })
    
    # If UI has more rows than store, add new rows
    if row_count > len(current_store):
        for idx in range(len(current_store), row_count):
            updated_devices.append({
                "index": idx,
                "slave_id": str(slave_ids[idx]) if slave_ids[idx] is not None else str(idx + 1),
                "function_code": str(function_codes[idx]) if function_codes[idx] else "0x03",
                "register_addr": str(register_addrs[idx]) if register_addrs[idx] is not None else "0",
                "data_type": str(data_types[idx]) if data_types[idx] else "int8",
                "endianness": str(endianness_list[idx]) if endianness_list[idx] else "Big Endian",
                "var_name": str(var_names[idx]) if var_names[idx] is not None else ""
            })
    
    # CRITICAL: If store has more rows than UI, preserve them (don't remove)
    # This handles the case where UI is still rendering or rows are being added
    if len(current_store) > row_count:
        for idx in range(row_count, len(current_store)):
            if idx in store_map:
                # Preserve existing row from store
                updated_devices.append(store_map[idx].copy())
    
    # CRITICAL: Never reduce the number of rows
    # If we somehow ended up with fewer rows, restore from store
    if len(updated_devices) < len(current_store):
        logger.warning(f"⚠️ MODBUS sync: Would reduce rows from {len(current_store)} to {len(updated_devices)}. Preserving all rows from store.")
        # Restore all rows from store, but update the ones we have UI data for
        updated_devices = []
        for idx, device in enumerate(current_store):
            if idx < row_count:
                # Update with UI values
                device_copy = device.copy()
                device_copy["slave_id"] = str(slave_ids[idx]) if slave_ids[idx] is not None else device.get("slave_id", str(idx + 1))
                device_copy["function_code"] = str(function_codes[idx]) if function_codes[idx] else device.get("function_code", "0x03")
                device_copy["register_addr"] = str(register_addrs[idx]) if register_addrs[idx] is not None else device.get("register_addr", "0")
                device_copy["data_type"] = str(data_types[idx]) if data_types[idx] else device.get("data_type", "int8")
                device_copy["endianness"] = str(endianness_list[idx]) if endianness_list[idx] else device.get("endianness", "Big Endian")
                device_copy["var_name"] = str(var_names[idx]) if var_names[idx] is not None else device.get("var_name", "")
                updated_devices.append(device_copy)
            else:
                # Preserve row from store
                updated_devices.append(device.copy())
    
    # Ensure indices are sequential
    for idx, device in enumerate(updated_devices):
        device["index"] = idx
    
    logger.info(f"✅ MODBUS sync: Updated store with {len(updated_devices)} row(s) (UI had {row_count}, store had {len(current_store)})")
    return updated_devices
