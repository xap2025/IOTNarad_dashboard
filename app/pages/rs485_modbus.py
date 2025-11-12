"""
RS485 MODBUS Configuration Page
Matches the MODBUS configuration form from image 1
"""
from dash import html, dcc, Input, Output, State, ALL, callback, ctx, no_update
import dash_bootstrap_components as dbc
import json


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
            ]),
            
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
        
        # Store for device data
        dcc.Store(id='modbus-devices-store', data=[{"index": 0, "slave_id": "1", "function_code": "0x03", "register_addr": "0", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name"}]),
        # Hidden trigger store to force updates
        dcc.Store(id='modbus-trigger-store', data=0),
    ])


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
                style={'fontSize': '0.9rem'}
            )
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
                style={'fontSize': '0.9rem'}
            )
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
                style={'fontSize': '0.9rem'}
            )
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
    """Update table rows from store data"""
    # Always ensure we have at least one device
    if not devices_data or len(devices_data) == 0:
        devices_data = [{"index": 0, "slave_id": "1", "function_code": "0x03", "register_addr": "0", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name"}]
    
    # Create rows for all devices
    rows = []
    for device in devices_data:
        rows.append(create_modbus_slave_row(
            device.get("index", 0),
            device.get("slave_id", "1"),
            device.get("function_code", "0x03"),
            device.get("register_addr", "0"),
            device.get("data_type", "int8"),
            device.get("endianness", "Big Endian"),
            device.get("var_name", "Variable Name")
        ))
    
    return rows


# Unified callback for add and remove operations
@callback(
    Output('modbus-devices-store', 'data'),
    Output('modbus-trigger-store', 'data'),
    Input('add-modbus-device-btn', 'n_clicks'),
    Input({'type': 'modbus-remove-device', 'index': ALL}, 'n_clicks'),
    State('modbus-devices-store', 'data'),
    State('modbus-trigger-store', 'data'),
    prevent_initial_call=True
)
def manage_modbus_devices(add_clicks, remove_clicks_list, devices_data, trigger_value):
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
        # Create new list with existing devices - rebuild to ensure fresh object
        updated_devices = []
        for idx, device in enumerate(devices_data):
            updated_devices.append({
                "index": idx,
                "slave_id": str(device.get("slave_id", "1")),
                "function_code": str(device.get("function_code", "0x03")),
                "register_addr": str(device.get("register_addr", "0")),
                "data_type": str(device.get("data_type", "int8")),
                "endianness": str(device.get("endianness", "Big Endian")),
                "var_name": str(device.get("var_name", "Variable Name"))
            })
        
        # Add new device with next index
        new_index = len(updated_devices)
        updated_devices.append({
            "index": new_index,
            "slave_id": "1",
            "function_code": "0x03",
            "register_addr": "0",
            "data_type": "int8",
            "endianness": "Big Endian",
            "var_name": "Variable Name"
        })
        
        # Increment trigger to force update detection
        new_trigger = (trigger_value if trigger_value is not None else 0) + 1
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
