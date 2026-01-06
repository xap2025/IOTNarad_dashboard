"""
CAN Bus Configuration Page
Matches the CAN Bus configuration form from image 2
"""
from dash import html, dcc, Input, Output, State, ALL, callback, ctx, no_update
import dash_bootstrap_components as dbc
import json
import logging


def create_can_bus_layout():
    """Create CAN Bus configuration page matching image 2"""
    
    return html.Div([
        # Header
        html.Div([
            html.H5([
                html.I(className="fas fa-bus me-2", style={'color': '#667eea'}),
                "CAN Bus Configuration"
            ], className='fw-bold mb-3'),
        ], className='mb-4'),
        
        # CAN Bus Communication Settings Section
        html.Div([
            html.H5([
                html.I(className="fas fa-cog me-2", style={'color': '#667eea'}),
                "CAN Bus Communication Settings"
            ], className='fw-bold mb-3'),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Baud Rate", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='can-baud-rate',
                        options=[
                            {'label': '125 kbps', 'value': '125'},
                            {'label': '250 kbps', 'value': '250'},
                            {'label': '500 kbps', 'value': '500'},
                            {'label': '1000 kbps (1 Mbps)', 'value': '1000'},
                        ],
                        value='125',
                        clearable=False
                    ),
                ], md=4),
                
                dbc.Col([
                    dbc.Label("Identifier Length", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='can-identifier-length',
                        options=[
                            {'label': '11-bit (Standard)', 'value': '11-bit'},
                            {'label': '29-bit (Extended)', 'value': '29-bit'},
                        ],
                        value='11-bit',
                        clearable=False
                    ),
                ], md=4),
                
                dbc.Col([
                    dbc.Label("CAN Mode", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='can-mode',
                        options=[
                            {'label': 'Normal Mode', 'value': 'Normal'},
                            {'label': 'Listen Only Mode', 'value': 'Listen'},
                            {'label': 'Loopback Mode', 'value': 'Loopback'},
                        ],
                        value='Normal',
                        clearable=False
                    ),
                ], md=4),
            ], className='mb-3'),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Filter Mode", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='can-filter-mode',
                        options=[
                            {'label': 'No Filtering', 'value': 'None'},
                            {'label': 'Accept Filter', 'value': 'Accept'},
                            {'label': 'Reject Filter', 'value': 'Reject'},
                        ],
                        value='None',
                        clearable=False
                    ),
                ], md=4),
                
                dbc.Col([
                    dbc.Label("Filter ID (Hex)", className='fw-bold mb-2'),
                    dbc.Input(
                        id='can-filter-id',
                        type='text',
                        value='0x123',
                        placeholder='0x123'
                    ),
                ], md=4),
                
                dbc.Col([
                    dbc.Label("Filter Mask (Hex)", className='fw-bold mb-2'),
                    dbc.Input(
                        id='can-filter-mask',
                        type='text',
                        value='0x7FF',
                        placeholder='0x7FF'
                    ),
                ], md=4),
            ]),
        ], className='stat-card p-4 mb-4'),
        
        # CAN Message Mapping Section
        html.Div([
            html.H5([
                html.I(className="fas fa-map me-2", style={'color': '#667eea'}),
                "CAN Message Mapping"
            ], className='fw-bold mb-3'),
            
            html.P("Map variables to 8-byte CAN data payload", className='text-muted mb-4'),
            
            # CAN Messages Subsection
            html.Div([
                html.H6("CAN Messages", className='fw-bold mb-3'),
                
                dbc.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("CAN ID (Hex)", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Direction", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Period (ms)", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Variable Name", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Action", style={'backgroundColor': '#667eea', 'color': 'white'}),
                        ])
                    ]),
                    html.Tbody(id='can-messages-tbody', children=[])
                ], bordered=True, hover=True, responsive=True, className='mb-3'),
                
                dbc.Button([
                    html.I(className="fas fa-plus me-2"),
                    "Add CAN Message"
                ], id='add-can-message-btn', color='primary', className='mb-4', n_clicks=0),
            ], className='mb-4'),
            
            # Data Mapping Subsection
            html.Div([
                html.H6("Data Mapping (8-byte payload)", className='fw-bold mb-3'),
                
                dbc.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("CAN ID", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Byte Position", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Data Length", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Data Type", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Endianness", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Variable Name", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Scale Factor", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Offset", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Action", style={'backgroundColor': '#667eea', 'color': 'white'}),
                        ])
                    ]),
                    html.Tbody(id='can-data-mapping-tbody', children=[])
                ], bordered=True, hover=True, responsive=True, className='mb-3'),
                
                dbc.Button([
                    html.I(className="fas fa-plus me-2"),
                    "Add Data Mapping"
                ], id='add-can-data-mapping-btn', color='primary', className='mb-3', n_clicks=0),
            ]),
        ], className='stat-card p-4 mb-4'),
        
        # Save Configuration Button for CAN Bus Tab
        html.Div([
            dbc.Button([
                html.I(className="fas fa-save me-2"),
                "Save Configuration"
            ], id='save-canbus-config-btn', color='primary', size='lg', className='mt-3'),
            html.Div(id='save-canbus-status-message', className='d-inline-block ms-3 mt-3'),
        ], className='text-end'),
        
        # Stores for CAN messages and data mappings
        dcc.Store(id='can-messages-store', data=[{"index": 0, "can_id": "0x123", "direction": "TX", "period": "100", "var_name": "Message Name"}]),
        dcc.Store(id='can-data-mapping-store', data=[{"index": 0, "can_id": "0x123", "byte_pos": "Byte 0", "data_len": "1 Byte", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name", "scale": "1", "offset": "0"}]),
        # Trigger stores
        dcc.Store(id='can-messages-trigger-store', data=0),
        dcc.Store(id='can-data-mapping-trigger-store', data=0),
    ])


# Callback to auto-load CAN Bus configuration when device is selected or after save
@callback(
    [
        Output('can-baud-rate', 'value', allow_duplicate=True),
        Output('can-identifier-length', 'value', allow_duplicate=True),
        Output('can-mode', 'value', allow_duplicate=True),
        Output('can-filter-mode', 'value', allow_duplicate=True),
        Output('can-filter-id', 'value', allow_duplicate=True),
        Output('can-filter-mask', 'value', allow_duplicate=True),
        Output('can-messages-store', 'data', allow_duplicate=True),
        Output('can-data-mapping-store', 'data', allow_duplicate=True),
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
def load_can_bus_configuration(device_id, pathname, reload_trigger, active_tab, session_data, device_id_state):
    """Load saved CAN Bus configuration for selected device and populate UI fields
    
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
    
    # Skip loading if triggered by tab switch but CAN Bus tab is not active
    # But allow loading on device selection, save, or page load (even if tab not active yet)
    if triggered_id == 'config-tabs':
        if active_tab != 'tab-canbus':
            logger.debug(f"⏭️ Skipping CAN Bus config load - triggered by tab switch but CAN Bus tab not active (active: {active_tab})")
            return [no_update] * 8
    
    # Allow loading on dashboard page (device config is embedded in dashboard)
    skip_paths = ['/login', '/logout', '/']
    if pathname in skip_paths:
        logger.debug(f"⏭️ Skipping CAN Bus config load for pathname: {pathname}")
        return [no_update] * 8
    
    # If device_id not available from Input, try to get it from reload_trigger or State
    if not device_id:
        if triggered_id == 'config-reload-trigger' and reload_trigger:
            # Extract device_id from reload trigger data
            device_id = reload_trigger.get('device_id')
            if device_id:
                logger.info(f"📌 Using device_id from reload trigger for CAN Bus: {device_id}")
        elif triggered_id == 'config-tabs':
            # For tab switch, use device_id from State if available
            device_id = device_id_state
            if device_id:
                logger.debug(f"📌 Using device_id from State for CAN Bus tab switch: {device_id}")
    
    if not device_id:
        # Still no device_id - skip loading
        if triggered_id == 'config-reload-trigger' or triggered_id == 'config-tabs':
            logger.debug(f"⏭️ Reload/tab switch triggered but no device selected for CAN Bus (trigger: {triggered_id})")
        else:
            logger.debug(f"⏭️ No device selected, skipping CAN Bus config load")
        return [no_update] * 8
    
    try:
        # Get logged-in user info
        username = None
        is_admin = False
        if session_data:
            username = session_data.get('username', '')
            user_type = session_data.get('user_type', 'user')
            is_admin = (username == 'admin')
        
        logger.info(f"🔄 Loading CAN Bus configuration for device: {device_id}, user: {username}, trigger: {triggered_id}, active_tab: {active_tab}")
        
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
            logger.warning("⚠️ Database not connected, cannot load CAN Bus configuration")
            return [no_update] * 8
        
        # Load CAN Bus config from database
        # If triggered by reload trigger, add a small delay to ensure DB write is flushed
        if triggered_id == 'config-reload-trigger':
            import time
            time.sleep(0.5)  # Wait 0.5 seconds to ensure database write is fully flushed
        
        logger.info(f"🔄 Loading CAN Bus config from database for device {device_id}, triggered by: {triggered_id}")
        can_bus_config = db_service.get_can_bus_config(device_id)
        
        # Set default values (used if no config exists in database)
        baud_rate = '125'
        identifier_length = '11-bit'
        can_mode = 'Normal'
        filter_mode = 'None'
        filter_id = '0x123'
        filter_mask = '0x7FF'
        messages_store = [{"index": 0, "can_id": "0x123", "direction": "TX", "period": "100", "var_name": "Message Name"}]
        data_mapping_store = [{"index": 0, "can_id": "0x123", "byte_pos": "Byte 0", "data_len": "1 Byte", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name", "scale": "1", "offset": "0"}]
        
        # Populate from database if config exists
        if can_bus_config:
            logger.info(f"✅ Loading CAN Bus config from database for device {device_id}")
            
            comm_settings = can_bus_config.get("communication_settings", {})
            
            baud_rate = str(comm_settings.get("baud_rate", 125))
            identifier_length = comm_settings.get("identifier_length", "11-bit")
            can_mode = comm_settings.get("can_mode", "Normal")
            filter_mode = comm_settings.get("filter_mode", "None")
            filter_id = comm_settings.get("filter_id", "0x123")
            filter_mask = comm_settings.get("filter_mask", "0x7FF")
            
            # Convert CAN messages to store format
            # Load from Device: Create rows dynamically based on device data
            can_messages_list = can_bus_config.get("can_messages", [])
            if can_messages_list and len(can_messages_list) > 0:
                messages_store = []
                for idx, message in enumerate(can_messages_list):
                    messages_store.append({
                        "index": idx,  # Re-index to ensure sequential indices
                        "can_id": str(message.get("can_id", "0x123")),
                        "direction": str(message.get("direction", "TX")),
                        "period": str(message.get("period_ms", message.get("period", 100))),  # Support both field names
                        "var_name": str(message.get("variable_name", message.get("var_name", "")))
                    })
                logger.info(f"✅ Loaded {len(messages_store)} CAN message(s) from database for device {device_id}")
            else:
                # No CAN messages in database - use default single row
                messages_store = [{"index": 0, "can_id": "0x123", "direction": "TX", "period": "100", "var_name": "Message Name"}]
                logger.info(f"ℹ️ No CAN messages in database for device {device_id}, using default single row")
            
            # Convert data mapping to store format
            # Load from Device: Create rows dynamically based on device data
            data_mapping_list = can_bus_config.get("data_mapping", [])
            if data_mapping_list and len(data_mapping_list) > 0:
                data_mapping_store = []
                for idx, mapping in enumerate(data_mapping_list):
                    data_mapping_store.append({
                        "index": idx,  # Re-index to ensure sequential indices
                        "can_id": str(mapping.get("can_id", "0x123")),
                        "byte_pos": str(mapping.get("byte_position", mapping.get("byte_pos", "Byte 0"))),  # Support both field names
                        "data_len": str(mapping.get("data_length", mapping.get("data_len", "1 Byte"))),  # Support both field names
                        "data_type": str(mapping.get("data_type", "int8")),
                        "endianness": str(mapping.get("endianness", "Big Endian")),
                        "var_name": str(mapping.get("variable_name", mapping.get("var_name", ""))),  # Support both field names
                        "scale": str(mapping.get("scale_factor", mapping.get("scale", 1.0))),  # Support both field names
                        "offset": str(mapping.get("offset", 0.0))  # Convert to string for UI
                    })
                logger.info(f"✅ Loaded {len(data_mapping_store)} data mapping(s) from database for device {device_id}")
            else:
                # No data mappings in database - use default single row
                data_mapping_store = [{"index": 0, "can_id": "0x123", "byte_pos": "Byte 0", "data_len": "1 Byte", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name", "scale": "1", "offset": "0"}]
                logger.info(f"ℹ️ No data mappings in database for device {device_id}, using default single row")
        else:
            logger.info(f"ℹ️ No CAN Bus config found in database for device {device_id}, using default values")
        
        return (
            baud_rate,
            identifier_length,
            can_mode,
            filter_mode,
            filter_id,
            filter_mask,
            messages_store,
            data_mapping_store
        )
        
    except Exception as e:
        logger.error(f"Error loading CAN Bus configuration: {e}")
        logger.exception("Full error traceback:")
        return [no_update] * 8


def create_can_message_row(index, can_id, direction, period, var_name):
    """Create a single CAN message row"""
    # Normalize direction value
    direction_value = direction if direction in ['TX', 'RX'] else ('TX' if 'TX' in str(direction) else 'RX')
    
    return html.Tr([
        html.Td(
            dbc.Input(
                id={'type': 'can-message-id', 'index': index},
                type='text',
                value=can_id,
                size='sm',
                placeholder='0x123'
            )
        ),
        html.Td(
            dcc.Dropdown(
                id={'type': 'can-message-direction', 'index': index},
                options=[
                    {'label': 'Transmit (TX)', 'value': 'TX'},
                    {'label': 'Receive (RX)', 'value': 'RX'},
                ],
                value=direction_value,
                clearable=False,
                style={'fontSize': '0.9rem'}
            )
        ),
        html.Td(
            dbc.Input(
                id={'type': 'can-message-period', 'index': index},
                type='number',
                value=period,
                size='sm',
                min=1
            )
        ),
        html.Td(
            dbc.Input(
                id={'type': 'can-message-var-name', 'index': index},
                type='text',
                value=var_name,
                size='sm'
            )
        ),
        html.Td(
            dbc.Button(
                html.I(className="fas fa-trash"),
                id={'type': 'can-remove-message', 'index': index},
                color='danger',
                size='sm',
                outline=True,
                n_clicks=0
            )
        ),
    ])


def create_can_data_mapping_row(index, can_id, byte_pos, data_len, data_type, endianness, var_name, scale, offset):
    """Create a single CAN data mapping row"""
    return html.Tr([
        html.Td(
            dbc.Input(
                id={'type': 'can-data-can-id', 'index': index},
                type='text',
                value=can_id,
                size='sm',
                placeholder='0x123'
            )
        ),
        html.Td(
            dcc.Dropdown(
                id={'type': 'can-data-byte-pos', 'index': index},
                options=[{'label': f'Byte {i}', 'value': f'Byte {i}'} for i in range(8)],
                value=byte_pos,
                clearable=False,
                style={'fontSize': '0.9rem'}
            )
        ),
        html.Td(
            dcc.Dropdown(
                id={'type': 'can-data-length', 'index': index},
                options=[
                    {'label': '1 Byte', 'value': '1 Byte'},
                    {'label': '2 Bytes', 'value': '2 Bytes'},
                    {'label': '4 Bytes', 'value': '4 Bytes'},
                    {'label': '8 Bytes', 'value': '8 Bytes'},
                ],
                value=data_len,
                clearable=False,
                style={'fontSize': '0.9rem'}
            )
        ),
        html.Td(
            dcc.Dropdown(
                id={'type': 'can-data-type', 'index': index},
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
                id={'type': 'can-data-endianness', 'index': index},
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
                id={'type': 'can-data-var-name', 'index': index},
                type='text',
                value=var_name,
                size='sm'
            )
        ),
        html.Td(
            dbc.Input(
                id={'type': 'can-data-scale', 'index': index},
                type='number',
                value=scale,
                size='sm',
                step=0.1
            )
        ),
        html.Td(
            dbc.Input(
                id={'type': 'can-data-offset', 'index': index},
                type='number',
                value=offset,
                size='sm',
                step=0.1
            )
        ),
        html.Td(
            dbc.Button(
                html.I(className="fas fa-trash"),
                id={'type': 'can-remove-data-mapping', 'index': index},
                color='danger',
                size='sm',
                outline=True,
                n_clicks=0
            )
        ),
    ])


# Callback to update CAN messages table from store
@callback(
    Output('can-messages-tbody', 'children'),
    Input('can-messages-store', 'data'),
    prevent_initial_call=False
)
def update_can_messages_table(messages_data):
    """Update CAN messages table rows from store data.
    
    This callback creates table rows based on the store data.
    It ensures all rows are preserved and displayed correctly.
    """
    logger = logging.getLogger(__name__)
    
    if not messages_data or len(messages_data) == 0:
        logger.debug("⚠️ CAN messages table: No messages data, creating default row")
        messages_data = [{"index": 0, "can_id": "0x123", "direction": "TX", "period": "100", "var_name": "Message Name"}]
    
    logger.debug(f"📊 CAN messages table: Creating {len(messages_data)} row(s) from store data")
    
    # Sort by index to ensure correct order
    sorted_messages = sorted(messages_data, key=lambda x: x.get("index", 0))
    
    rows = []
    for message in sorted_messages:
        rows.append(create_can_message_row(
            message.get("index", 0),
            message.get("can_id", "0x123"),
            message.get("direction", "TX"),
            message.get("period", "100"),
            message.get("var_name", "Message Name")
        ))
    
    logger.debug(f"✅ CAN messages table: Created {len(rows)} row(s)")
    return rows


# Callback to update CAN data mapping table from store
@callback(
    Output('can-data-mapping-tbody', 'children'),
    Input('can-data-mapping-store', 'data'),
    prevent_initial_call=False
)
def update_can_data_mapping_table(mappings_data):
    """Update CAN data mapping table rows from store data.
    
    This callback creates table rows based on the store data.
    It ensures all rows are preserved and displayed correctly.
    """
    logger = logging.getLogger(__name__)
    
    if not mappings_data or len(mappings_data) == 0:
        logger.debug("⚠️ CAN data mapping table: No mappings data, creating default row")
        mappings_data = [{"index": 0, "can_id": "0x123", "byte_pos": "Byte 0", "data_len": "1 Byte", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name", "scale": "1", "offset": "0"}]
    
    logger.debug(f"📊 CAN data mapping table: Creating {len(mappings_data)} row(s) from store data")
    
    # Sort by index to ensure correct order
    sorted_mappings = sorted(mappings_data, key=lambda x: x.get("index", 0))
    
    rows = []
    for mapping in sorted_mappings:
        rows.append(create_can_data_mapping_row(
            mapping.get("index", 0),
            mapping.get("can_id", "0x123"),
            mapping.get("byte_pos", "Byte 0"),
            mapping.get("data_len", "1 Byte"),
            mapping.get("data_type", "int8"),
            mapping.get("endianness", "Big Endian"),
            mapping.get("var_name", "Variable Name"),
            mapping.get("scale", "1"),
            mapping.get("offset", "0")
        ))
    
    logger.debug(f"✅ CAN data mapping table: Created {len(rows)} row(s)")
    return rows


# Unified callback for CAN messages (add and remove)
@callback(
    Output('can-messages-store', 'data'),
    Output('can-messages-trigger-store', 'data'),
    Input('add-can-message-btn', 'n_clicks'),
    Input({'type': 'can-remove-message', 'index': ALL}, 'n_clicks'),
    State('can-messages-store', 'data'),
    State('can-messages-trigger-store', 'data'),
    # CRITICAL: Get current UI values to preserve user-filled data
    State({'type': 'can-message-id', 'index': ALL}, 'value'),
    State({'type': 'can-message-direction', 'index': ALL}, 'value'),
    State({'type': 'can-message-period', 'index': ALL}, 'value'),
    State({'type': 'can-message-var-name', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def manage_can_messages(add_clicks, remove_clicks_list, messages_data, trigger_value,
                        can_ids, directions, periods, var_names):
    """Handle both add and remove CAN message operations"""
    if not ctx.triggered:
        return no_update, no_update
    
    triggered_id = ctx.triggered[0]['prop_id']
    
    # Initialize messages_data if needed
    if messages_data is None:
        messages_data = []
    if len(messages_data) == 0:
        messages_data = [{"index": 0, "can_id": "0x123", "direction": "TX", "period": "100", "var_name": "Message Name"}]
    
    # Handle ADD operation
    if 'add-can-message-btn' in triggered_id:
        logger = logging.getLogger(__name__)
        logger.info(f"➕ CAN: Adding new message. Current store has {len(messages_data)} row(s)")
        
        # CRITICAL: Build updated messages from CURRENT UI values, not from stale store
        # This ensures all user-filled values are preserved
        updated_messages = []
        
        # Get current UI row count - this is the source of truth
        ui_row_count = len(can_ids) if can_ids else 0
        
        # If we have UI values, use them directly (most up-to-date)
        if ui_row_count > 0 and can_ids and directions and periods and var_names:
            logger.debug(f"   Using UI values: {ui_row_count} row(s) from UI inputs")
            for idx in range(ui_row_count):
                updated_messages.append({
                    "index": idx,
                    "can_id": str(can_ids[idx]) if can_ids[idx] is not None else "0x123",
                    "direction": str(directions[idx]) if directions[idx] else "TX",
                    "period": str(periods[idx]) if periods[idx] is not None else "100",
                    "var_name": str(var_names[idx]) if var_names[idx] is not None else "Message Name"
                })
        else:
            # Fallback: Use store data if UI values not available
            logger.debug(f"   UI values not available, using store data")
            for idx, message in enumerate(messages_data):
                updated_messages.append({
                    "index": idx,
                    "can_id": str(message.get("can_id", "0x123")),
                    "direction": str(message.get("direction", "TX")),
                    "period": str(message.get("period", "100")),
                    "var_name": str(message.get("var_name", "Message Name"))
                })
        
        # Calculate next CAN ID by finding the maximum existing CAN ID and incrementing
        max_can_id = 0x123  # Default starting CAN ID
        for message in updated_messages:
            try:
                can_id_str = str(message.get("can_id", "0x123")).strip()
                # Remove '0x' prefix if present and convert hex to int
                if can_id_str.startswith('0x') or can_id_str.startswith('0X'):
                    can_id_num = int(can_id_str, 16)
                else:
                    can_id_num = int(can_id_str, 16) if all(c in '0123456789ABCDEFabcdef' for c in can_id_str) else int(can_id_str)
                max_can_id = max(max_can_id, can_id_num)
            except (ValueError, TypeError):
                pass
        
        # Next CAN ID is max + 1 (increment by 1)
        next_can_id = f"0x{max_can_id + 1:X}"
        
        new_index = len(updated_messages)
        updated_messages.append({
            "index": new_index,
            "can_id": next_can_id,
            "direction": "TX",
            "period": "100",
            "var_name": "Message Name"
        })
        
        logger.info(f"✅ CAN: Added new message. Store now has {len(updated_messages)} row(s). New CAN ID: {next_can_id}")
        
        # Use timestamp for trigger to track when row was added
        import time
        new_trigger = time.time()  # Use current timestamp
        logger.debug(f"✅ CAN: Updated trigger store to {new_trigger} (timestamp)")
        return updated_messages, new_trigger
    
    # Handle REMOVE operation
    if 'can-remove-message' in triggered_id and 'index' in triggered_id:
        try:
            prop_id_json = triggered_id.split('.n_clicks')[0]
            button_id = json.loads(prop_id_json)
            index_to_remove = button_id.get('index')
        except (json.JSONDecodeError, KeyError, ValueError):
            try:
                start_idx = triggered_id.find('"index":') + 8
                end_idx = triggered_id.find(',', start_idx)
                if end_idx == -1:
                    end_idx = triggered_id.find('}', start_idx)
                index_to_remove = int(triggered_id[start_idx:end_idx])
            except (ValueError, AttributeError):
                return no_update, no_update
        
        if len(messages_data) <= 1:
            return no_update, no_update
        
        updated_messages = []
        for message in messages_data:
            if message.get("index") != index_to_remove:
                updated_messages.append({
                    "index": len(updated_messages),
                    "can_id": str(message.get("can_id", "0x123")),
                    "direction": str(message.get("direction", "TX")),
                    "period": str(message.get("period", "100")),
                    "var_name": str(message.get("var_name", "Message Name"))
                })
        
        if len(updated_messages) == 0:
            updated_messages = [{"index": 0, "can_id": "0x123", "direction": "TX", "period": "100", "var_name": "Message Name"}]
        
        return updated_messages, (trigger_value if trigger_value is not None else 0) + 1
    
    return no_update, no_update


# Unified callback for CAN data mappings (add and remove)
@callback(
    Output('can-data-mapping-store', 'data'),
    Output('can-data-mapping-trigger-store', 'data'),
    Input('add-can-data-mapping-btn', 'n_clicks'),
    Input({'type': 'can-remove-data-mapping', 'index': ALL}, 'n_clicks'),
    State('can-data-mapping-store', 'data'),
    State('can-data-mapping-trigger-store', 'data'),
    # CRITICAL: Get current UI values to preserve user-filled data
    State({'type': 'can-data-can-id', 'index': ALL}, 'value'),
    State({'type': 'can-data-byte-pos', 'index': ALL}, 'value'),
    State({'type': 'can-data-length', 'index': ALL}, 'value'),
    State({'type': 'can-data-type', 'index': ALL}, 'value'),
    State({'type': 'can-data-endianness', 'index': ALL}, 'value'),
    State({'type': 'can-data-var-name', 'index': ALL}, 'value'),
    State({'type': 'can-data-scale', 'index': ALL}, 'value'),
    State({'type': 'can-data-offset', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def manage_can_data_mappings(add_clicks, remove_clicks_list, mappings_data, trigger_value,
                              can_ids, byte_positions, data_lengths, data_types, endianness_list, var_names, scales, offsets):
    """Handle both add and remove CAN data mapping operations"""
    if not ctx.triggered:
        return no_update, no_update
    
    triggered_id = ctx.triggered[0]['prop_id']
    
    # Initialize mappings_data if needed
    if mappings_data is None:
        mappings_data = []
    if len(mappings_data) == 0:
        mappings_data = [{"index": 0, "can_id": "0x123", "byte_pos": "Byte 0", "data_len": "1 Byte", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name", "scale": "1", "offset": "0"}]
    
    # Handle ADD operation
    if 'add-can-data-mapping-btn' in triggered_id:
        logger = logging.getLogger(__name__)
        logger.info(f"➕ CAN Data Mapping: Adding new mapping. Current store has {len(mappings_data)} row(s)")
        
        # CRITICAL: Build updated mappings from CURRENT UI values, not from stale store
        # This ensures all user-filled values are preserved
        updated_mappings = []
        
        # Get current UI row count - this is the source of truth
        ui_row_count = len(can_ids) if can_ids else 0
        
        # If we have UI values, use them directly (most up-to-date)
        if ui_row_count > 0 and can_ids and byte_positions and data_lengths and data_types and endianness_list and var_names and scales and offsets:
            logger.debug(f"   Using UI values: {ui_row_count} row(s) from UI inputs")
            for idx in range(ui_row_count):
                updated_mappings.append({
                    "index": idx,
                    "can_id": str(can_ids[idx]) if can_ids[idx] is not None else "0x123",
                    "byte_pos": str(byte_positions[idx]) if byte_positions[idx] else "Byte 0",
                    "data_len": str(data_lengths[idx]) if data_lengths[idx] else "1 Byte",
                    "data_type": str(data_types[idx]) if data_types[idx] else "int8",
                    "endianness": str(endianness_list[idx]) if endianness_list[idx] else "Big Endian",
                    "var_name": str(var_names[idx]) if var_names[idx] is not None else "Variable Name",
                    "scale": str(scales[idx]) if scales[idx] is not None else "1",
                    "offset": str(offsets[idx]) if offsets[idx] is not None else "0"
                })
        else:
            # Fallback: Use store data if UI values not available
            logger.debug(f"   UI values not available, using store data")
            for idx, mapping in enumerate(mappings_data):
                updated_mappings.append({
                    "index": idx,
                    "can_id": str(mapping.get("can_id", "0x123")),
                    "byte_pos": str(mapping.get("byte_pos", "Byte 0")),
                    "data_len": str(mapping.get("data_len", "1 Byte")),
                    "data_type": str(mapping.get("data_type", "int8")),
                    "endianness": str(mapping.get("endianness", "Big Endian")),
                    "var_name": str(mapping.get("var_name", "Variable Name")),
                    "scale": str(mapping.get("scale", "1")),
                    "offset": str(mapping.get("offset", "0"))
                })
        
        # Calculate next CAN ID by finding the maximum existing CAN ID and incrementing
        max_can_id = 0x123  # Default starting CAN ID
        for mapping in updated_mappings:
            try:
                can_id_str = str(mapping.get("can_id", "0x123")).strip()
                # Remove '0x' prefix if present and convert hex to int
                if can_id_str.startswith('0x') or can_id_str.startswith('0X'):
                    can_id_num = int(can_id_str, 16)
                else:
                    can_id_num = int(can_id_str, 16) if all(c in '0123456789ABCDEFabcdef' for c in can_id_str) else int(can_id_str)
                max_can_id = max(max_can_id, can_id_num)
            except (ValueError, TypeError):
                pass
        
        # Next CAN ID is max + 1 (increment by 1)
        next_can_id = f"0x{max_can_id + 1:X}"
        
        new_index = len(updated_mappings)
        updated_mappings.append({
            "index": new_index,
            "can_id": next_can_id,
            "byte_pos": "Byte 0",
            "data_len": "1 Byte",
            "data_type": "int8",
            "endianness": "Big Endian",
            "var_name": "Variable Name",
            "scale": "1",
            "offset": "0"
        })
        
        logger.info(f"✅ CAN Data Mapping: Added new mapping. Store now has {len(updated_mappings)} row(s). New CAN ID: {next_can_id}")
        
        # Use timestamp for trigger to track when row was added
        import time
        new_trigger = time.time()  # Use current timestamp
        logger.debug(f"✅ CAN Data Mapping: Updated trigger store to {new_trigger} (timestamp)")
        return updated_mappings, new_trigger
    
    # Handle REMOVE operation
    if 'can-remove-data-mapping' in triggered_id and 'index' in triggered_id:
        try:
            prop_id_json = triggered_id.split('.n_clicks')[0]
            button_id = json.loads(prop_id_json)
            index_to_remove = button_id.get('index')
        except (json.JSONDecodeError, KeyError, ValueError):
            try:
                start_idx = triggered_id.find('"index":') + 8
                end_idx = triggered_id.find(',', start_idx)
                if end_idx == -1:
                    end_idx = triggered_id.find('}', start_idx)
                index_to_remove = int(triggered_id[start_idx:end_idx])
            except (ValueError, AttributeError):
                return no_update, no_update
        
        if len(mappings_data) <= 1:
            return no_update, no_update
        
        updated_mappings = []
        for mapping in mappings_data:
            if mapping.get("index") != index_to_remove:
                updated_mappings.append({
                    "index": len(updated_mappings),
                    "can_id": str(mapping.get("can_id", "0x123")),
                    "byte_pos": str(mapping.get("byte_pos", "Byte 0")),
                    "data_len": str(mapping.get("data_len", "1 Byte")),
                    "data_type": str(mapping.get("data_type", "int8")),
                    "endianness": str(mapping.get("endianness", "Big Endian")),
                    "var_name": str(mapping.get("var_name", "Variable Name")),
                    "scale": str(mapping.get("scale", "1")),
                    "offset": str(mapping.get("offset", "0"))
                })
        
        if len(updated_mappings) == 0:
            updated_mappings = [{"index": 0, "can_id": "0x123", "byte_pos": "Byte 0", "data_len": "1 Byte", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name", "scale": "1", "offset": "0"}]
        
        return updated_mappings, (trigger_value if trigger_value is not None else 0) + 1
    
    return no_update, no_update


# Sync callback for CAN messages store
@callback(
    Output('can-messages-store', 'data', allow_duplicate=True),
    [
        Input({'type': 'can-message-id', 'index': ALL}, 'value'),
        Input({'type': 'can-message-direction', 'index': ALL}, 'value'),
        Input({'type': 'can-message-period', 'index': ALL}, 'value'),
        Input({'type': 'can-message-var-name', 'index': ALL}, 'value'),
    ],
    [
        State('can-messages-store', 'data'),  # Get current store state
        State('can-messages-trigger-store', 'data'),  # Check if row addition is in progress
    ],
    prevent_initial_call=True
)
def sync_can_messages_store(can_ids, directions, periods, var_names, current_store, trigger_value):
    """Synchronize can-messages-store with the latest UI values.
    
    CRITICAL: This callback must NEVER reduce the number of rows.
    It should only update values in existing rows, or add rows if UI has more.
    
    IMPORTANT: This callback should NOT run during row addition.
    It should only run when user actually edits values in existing, fully-rendered rows.
    """
    logger = logging.getLogger(__name__)
    
    # CRITICAL: Check trigger store - if it changed recently, row addition might be in progress
    import time
    current_time = time.time()
    if trigger_value and isinstance(trigger_value, (int, float)):
        if trigger_value >= 1000000000:  # Timestamp (seconds since epoch)
            time_since_trigger = current_time - trigger_value
            if time_since_trigger < 2.0:
                logger.debug(f"⚠️ CAN messages sync: Trigger store updated recently ({time_since_trigger:.2f}s ago). Skipping update")
                return no_update
        else:
            if trigger_value < 10:
                logger.debug(f"⚠️ CAN messages sync: Trigger store has low counter value ({trigger_value}). Skipping update")
                return no_update
    
    if not can_ids or len(can_ids) == 0:
        logger.debug("⚠️ CAN messages sync: No can_ids from UI, skipping update")
        return no_update
    
    if current_store is None:
        current_store = []
    if len(current_store) == 0:
        current_store = [{"index": 0, "can_id": "0x123", "direction": "TX", "period": "100", "var_name": "Message Name"}]
    
    row_count = len(can_ids)
    collections = [directions, periods, var_names]
    
    if any(len(lst) != row_count for lst in collections):
        logger.debug(f"⚠️ CAN messages sync: Mismatched collection lengths. can_ids: {row_count}, others: {[len(lst) for lst in collections]}. Skipping update")
        return no_update
    
    if any(lst is None or len(lst) == 0 for lst in collections):
        logger.debug("⚠️ CAN messages sync: Some collections are None or empty. Skipping update")
        return no_update
    
    if row_count < len(current_store):
        logger.debug(f"⚠️ CAN messages sync: UI has {row_count} rows but store has {len(current_store)} rows. Skipping update")
        return no_update
    
    if row_count > len(current_store) + 1:
        logger.debug(f"⚠️ CAN messages sync: UI has {row_count} rows but store has {len(current_store)} rows. Large difference suggests rendering. Skipping update.")
        return no_update
    
    # CRITICAL: Merge UI values with current store
    updated_messages = []
    store_map = {msg.get("index", idx): msg for idx, msg in enumerate(current_store)}
    max_store_index = max(store_map.keys()) if store_map else -1
    
    # Start with all existing rows from store (preserves all rows)
    for idx in range(max(len(current_store), row_count)):
        if idx < len(current_store):
            msg = current_store[idx].copy()
        else:
            msg = {"index": idx, "can_id": "0x123", "direction": "TX", "period": "100", "var_name": "Message Name"}
        
        # Override with UI values if available
        if idx < row_count:
            if can_ids and idx < len(can_ids) and can_ids[idx] is not None:
                msg["can_id"] = str(can_ids[idx])
            if directions and idx < len(directions) and directions[idx]:
                msg["direction"] = str(directions[idx])
            if periods and idx < len(periods) and periods[idx] is not None:
                msg["period"] = str(periods[idx])
            if var_names and idx < len(var_names) and var_names[idx] is not None:
                msg["var_name"] = str(var_names[idx])
        
        msg["index"] = idx
        updated_messages.append(msg)
    
    logger.debug(f"✅ CAN messages sync: Updated store with {len(updated_messages)} row(s) (UI had {row_count}, store had {len(current_store)})")
    return updated_messages


# Sync callback for CAN data mapping store
@callback(
    Output('can-data-mapping-store', 'data', allow_duplicate=True),
    [
        Input({'type': 'can-data-can-id', 'index': ALL}, 'value'),
        Input({'type': 'can-data-byte-pos', 'index': ALL}, 'value'),
        Input({'type': 'can-data-length', 'index': ALL}, 'value'),
        Input({'type': 'can-data-type', 'index': ALL}, 'value'),
        Input({'type': 'can-data-endianness', 'index': ALL}, 'value'),
        Input({'type': 'can-data-var-name', 'index': ALL}, 'value'),
        Input({'type': 'can-data-scale', 'index': ALL}, 'value'),
        Input({'type': 'can-data-offset', 'index': ALL}, 'value'),
    ],
    [
        State('can-data-mapping-store', 'data'),  # Get current store state
        State('can-data-mapping-trigger-store', 'data'),  # Check if row addition is in progress
    ],
    prevent_initial_call=True
)
def sync_can_data_mapping_store(can_ids, byte_positions, data_lengths, data_types, endianness_list, var_names, scales, offsets, current_store, trigger_value):
    """Synchronize can-data-mapping-store with the latest UI values.
    
    CRITICAL: This callback must NEVER reduce the number of rows.
    It should only update values in existing rows, or add rows if UI has more.
    
    IMPORTANT: This callback should NOT run during row addition.
    It should only run when user actually edits values in existing, fully-rendered rows.
    """
    logger = logging.getLogger(__name__)
    
    # CRITICAL: Check trigger store - if it changed recently, row addition might be in progress
    import time
    current_time = time.time()
    if trigger_value and isinstance(trigger_value, (int, float)):
        if trigger_value >= 1000000000:  # Timestamp (seconds since epoch)
            time_since_trigger = current_time - trigger_value
            if time_since_trigger < 2.0:
                logger.debug(f"⚠️ CAN data mapping sync: Trigger store updated recently ({time_since_trigger:.2f}s ago). Skipping update")
                return no_update
        else:
            if trigger_value < 10:
                logger.debug(f"⚠️ CAN data mapping sync: Trigger store has low counter value ({trigger_value}). Skipping update")
                return no_update
    
    if not can_ids or len(can_ids) == 0:
        logger.debug("⚠️ CAN data mapping sync: No can_ids from UI, skipping update")
        return no_update
    
    if current_store is None:
        current_store = []
    if len(current_store) == 0:
        current_store = [{"index": 0, "can_id": "0x123", "byte_pos": "Byte 0", "data_len": "1 Byte", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name", "scale": "1", "offset": "0"}]
    
    row_count = len(can_ids)
    collections = [byte_positions, data_lengths, data_types, endianness_list, var_names, scales, offsets]
    
    if any(len(lst) != row_count for lst in collections):
        logger.debug(f"⚠️ CAN data mapping sync: Mismatched collection lengths. can_ids: {row_count}, others: {[len(lst) for lst in collections]}. Skipping update")
        return no_update
    
    if any(lst is None or len(lst) == 0 for lst in collections):
        logger.debug("⚠️ CAN data mapping sync: Some collections are None or empty. Skipping update")
        return no_update
    
    if row_count < len(current_store):
        logger.debug(f"⚠️ CAN data mapping sync: UI has {row_count} rows but store has {len(current_store)} rows. Skipping update")
        return no_update
    
    if row_count > len(current_store) + 1:
        logger.debug(f"⚠️ CAN data mapping sync: UI has {row_count} rows but store has {len(current_store)} rows. Large difference suggests rendering. Skipping update.")
        return no_update
    
    # CRITICAL: Merge UI values with current store
    updated_mappings = []
    store_map = {mapping.get("index", idx): mapping for idx, mapping in enumerate(current_store)}
    max_store_index = max(store_map.keys()) if store_map else -1
    
    # Start with all existing rows from store (preserves all rows)
    for idx in range(max(len(current_store), row_count)):
        if idx < len(current_store):
            mapping = current_store[idx].copy()
        else:
            mapping = {"index": idx, "can_id": "0x123", "byte_pos": "Byte 0", "data_len": "1 Byte", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name", "scale": "1", "offset": "0"}
        
        # Override with UI values if available
        if idx < row_count:
            if can_ids and idx < len(can_ids) and can_ids[idx] is not None:
                mapping["can_id"] = str(can_ids[idx])
            if byte_positions and idx < len(byte_positions) and byte_positions[idx]:
                mapping["byte_pos"] = str(byte_positions[idx])
            if data_lengths and idx < len(data_lengths) and data_lengths[idx]:
                mapping["data_len"] = str(data_lengths[idx])
            if data_types and idx < len(data_types) and data_types[idx]:
                mapping["data_type"] = str(data_types[idx])
            if endianness_list and idx < len(endianness_list) and endianness_list[idx]:
                mapping["endianness"] = str(endianness_list[idx])
            if var_names and idx < len(var_names) and var_names[idx] is not None:
                mapping["var_name"] = str(var_names[idx])
            if scales and idx < len(scales) and scales[idx] is not None:
                mapping["scale"] = str(scales[idx])
            if offsets and idx < len(offsets) and offsets[idx] is not None:
                mapping["offset"] = str(offsets[idx])
        
        mapping["index"] = idx
        updated_mappings.append(mapping)
    
    logger.debug(f"✅ CAN data mapping sync: Updated store with {len(updated_mappings)} row(s) (UI had {row_count}, store had {len(current_store)})")
    return updated_mappings
