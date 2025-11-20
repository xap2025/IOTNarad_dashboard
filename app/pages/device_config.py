"""
Device Configuration Page
Configure Analog, Digital, and Communication settings for IoT devices
"""
from dash import html, dcc, Input, Output, State, ALL, callback, ctx, clientside_callback, ClientsideFunction, no_update
import dash_bootstrap_components as dbc
import time

# Module-level cache for device list (refreshes every 30 seconds)
# Cache structure: {'data': (options, default_value), 'user_key': str, 'timestamp': float}
_device_list_cache = None
_cache_timestamp = 0
_cache_ttl = 30  # Cache for 30 seconds


def create_device_config_layout():
    """Create device configuration page with tabs"""
    
    return html.Div([
        # Hidden store to trigger config reload after save
        dcc.Store(id='config-reload-trigger', data={'timestamp': 0}),
        # Session store to access logged-in user info
        dcc.Store(id='device-config-session-store', storage_type='session'),
        
        # Device Selection
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Label("Select Device", className='fw-bold mb-2'),
                    html.Div([
                    dcc.Dropdown(
                        id='device-selector',
                            options=[],
                            value=None,
                            placeholder='Loading devices...',
                        className='mb-3',
                        style={'borderRadius': '8px', 'minWidth': '400px', 'width': '100%'}
                    ),
                        html.Div(id='device-selector-loading', className='d-inline-block ms-2'),
                    ], className='d-flex align-items-center'),
                ], className='stat-card p-3'),
            ], md=12),
        ], className='mb-4'),
        
        # Configuration Tabs
        html.Div([
            dbc.Tabs([
                # Analog Tab
                dbc.Tab(
                    create_analog_config_tab(),
                    label="⚡ Analog",
                    tab_id='tab-analog',
                    className='pt-3'
                ),
                
                # Digital Tab
                dbc.Tab(
                    create_digital_config_tab(),
                    label="🔢 Digital",
                    tab_id='tab-digital',
                    className='pt-3'
                ),
                
                # RS485 MODBUS Tab
                dbc.Tab(
                    create_rs485_modbus_content(),
                    label="🔌 RS485 MODBUS",
                    tab_id='tab-modbus',
                    className='pt-3'
                ),
                
                # CAN Bus Tab
                dbc.Tab(
                    create_can_bus_content(),
                    label="🚌 CAN Bus",
                    tab_id='tab-canbus',
                    className='pt-3'
                ),
            ], id='config-tabs', active_tab='tab-analog'),
        ], className='stat-card p-4'),
        
        # Legacy Action Buttons (kept for backward compatibility, but individual save buttons are in each tab)
        # These buttons can be removed later if not needed
        html.Div([
            dbc.Button([
                html.I(className="fas fa-download me-2"),
                "Load from Device"
            ], id='load-config-btn', color='secondary', size='lg', className='me-2',
               outline=True),
            
            dbc.Button([
                html.I(className="fas fa-undo me-2"),
                "Reset to Default"
            ], id='reset-config-btn', color='warning', size='lg', outline=True),
        ], className='mt-4 text-end'),
        
        # Status Toast
        dbc.Toast(
            id='config-save-toast',
            header="Configuration Status",
            icon="info",
            duration=4000,
            is_open=False,
            dismissable=True,
            style={"position": "fixed", "top": 66, "right": 10, "width": 400, "zIndex": 9999},
        ),
    ])


def create_analog_config_tab():
    """Create analog configuration tab content"""
    
    return html.Div([
        # 4-20mA Input Section
        html.H5([
            html.I(className="fas fa-bolt me-2", style={'color': '#667eea'}),
            "4 to 20mA Input"
        ], className='fw-bold mb-3'),
        
        html.Div([
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th(html.I(className="fas fa-check-square"), style={'width': '50px'}),
                        html.Th("Channel"),
                        html.Th("Divider"),
                        html.Th("Multiplier"),
                        html.Th("IO Pin"),
                        html.Th("Name/Label"),
                    ])
                ]),
                html.Tbody([
                    create_analog_input_row(1, "AIN0", "4-20mA"),
                    create_analog_input_row(2, "AIN1", "4-20mA"),
                ])
            ], bordered=True, hover=True, responsive=True, className='mb-0'),
        ], className='config-table mb-4'),
        
        # 0-10V Input Section
        html.H5([
            html.I(className="fas fa-plug me-2", style={'color': '#667eea'}),
            "0 to 10V Input"
        ], className='fw-bold mb-3 mt-4'),
        
        html.Div([
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th(html.I(className="fas fa-check-square"), style={'width': '50px'}),
                        html.Th("Channel"),
                        html.Th("Divider"),
                        html.Th("Multiplier"),
                        html.Th("IO Pin"),
                        html.Th("Name/Label"),
                    ])
                ]),
                html.Tbody([
                    create_analog_input_row(3, "AIN2", "1-10V"),
                    create_analog_input_row(4, "AIN3", "1-10V"),
                ])
            ], bordered=True, hover=True, responsive=True, className='mb-0'),
        ], className='config-table mb-4'),
        
        # 0-10V Output Section
        html.H5([
            html.I(className="fas fa-arrow-right me-2", style={'color': '#667eea'}),
            "0 to 10V Output"
        ], className='fw-bold mb-3 mt-4'),
        
        html.Div([
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th(html.I(className="fas fa-check-square"), style={'width': '50px'}),
                        html.Th("Channel"),
                        html.Th("Value"),
                        html.Th("IO Pin"),
                        html.Th("Name/Label"),
                    ])
                ]),
                html.Tbody([
                    create_analog_output_row(1, "DOUT0"),
                    create_analog_output_row(2, "DOUT1"),
                ])
            ], bordered=True, hover=True, responsive=True, className='mb-0'),
        ], className='config-table mb-4'),
        
        # Scan Rate Section
        dbc.Row([
            dbc.Col([
                dbc.Label("Scan Rate (seconds):", className='fw-bold'),
            ], md=3),
            dbc.Col([
                dbc.Input(
                    id='analog-scan-rate',
                    type='number',
                    value=1000,
                    min=1000,
                    step=1,
                    placeholder='Enter scan rate...'
                ),
            ], md=9),
        ], className='mb-3'),
        
        # Save Configuration Button for Analog Tab
        # Hidden store to track message hide timer
        dcc.Store(id='save-analog-message-timer', data={'hide_at': 0}),
        # Interval to check if message should be hidden (check every 100ms)
        dcc.Interval(id='save-analog-hide-interval', interval=100, n_intervals=0, disabled=True),
        
        # Container with flexbox to keep button position fixed while message appears/disappears
        html.Div([
            # Status message on the left (fixed width to prevent shifting)
            html.Div(
                id='save-analog-status-message',
                style={
                    'display': 'inline-block',
                    'marginRight': '15px',
                    'marginTop': '15px',
                    'minWidth': '0px',
                    'maxWidth': '500px',
                    'verticalAlign': 'middle',
                    'textAlign': 'right'
                }
            ),
            # Button container (always in same position)
            html.Div([
                dbc.Button([
                    html.Span(id='save-analog-btn-spinner', children=[
                        html.I(className="fas fa-save me-2"),
                    ]),
                    html.Span(id='save-analog-btn-text', children="Save Configuration"),
                ], id='save-analog-config-btn', color='primary', size='lg', className='mt-3'),
            ], style={'display': 'inline-block', 'verticalAlign': 'top'}),
        ], className='text-end', style={'position': 'relative'}),
    ])


def create_analog_input_row(channel, io_pin, signal_type):
    """Create a single analog input row"""
    return html.Tr([
        html.Td(
            dbc.Checkbox(
                id={'type': 'analog-input-enable', 'index': channel},
                value=False
            )
        ),
        html.Td(str(channel), className='fw-bold'),
        html.Td(
            dbc.Input(
                id={'type': 'analog-input-div', 'index': channel},
                type='number',
                value=1,
                min=1,
                step=1,
                size='sm',
                style={'width': '100px'},
                required=True
            )
        ),
        html.Td(
            dbc.Input(
                id={'type': 'analog-input-mul', 'index': channel},
                type='number',
                value=1,
                min=1,
                step=1,
                size='sm',
                style={'width': '100px'},
                required=True
            )
        ),
        html.Td(
            html.Code(io_pin, className='badge bg-secondary')
        ),
        html.Td(
            dbc.Input(
                id={'type': 'analog-input-name', 'index': channel},
                type='text',
                placeholder=io_pin,
                value='',
                size='sm',
                required=True
            )
        ),
    ])


def create_analog_output_row(channel, io_pin):
    """Create a single analog output row"""
    return html.Tr([
        html.Td(
            dbc.Checkbox(
                id={'type': 'analog-output-enable', 'index': channel},
                value=False
            )
        ),
        html.Td(str(channel), className='fw-bold'),
        html.Td(
            dbc.Input(
                id={'type': 'analog-output-value', 'index': channel},
                type='number',
                value=0.0,
                min=0,
                max=10,
                step=0.1,
                size='sm',
                style={'width': '100px'},
                required=True
            )
        ),
        html.Td(
            html.Code(io_pin, className='badge bg-secondary')
        ),
        html.Td(
            dbc.Input(
                id={'type': 'analog-output-name', 'index': channel},
                type='text',
                placeholder=io_pin,
                value='',
                size='sm',
                required=True
            )
        ),
    ])


def create_digital_config_tab():
    """Create digital configuration tab content"""
    
    return html.Div([
        # NPN Section
        html.H5([
            html.I(className="fas fa-microchip me-2", style={'color': '#667eea'}),
            "NPN Configuration"
        ], className='fw-bold mb-3'),
        
        dbc.Row([
            # NPN Input
            dbc.Col([
                html.H6("Input", className='text-muted mb-3'),
                html.Div([
                    dbc.Table([
                        html.Thead([
                            html.Tr([
                                html.Th(html.I(className="fas fa-check-square"), style={'width': '50px'}),
                                html.Th("Ch"),
                                html.Th("IO Pin"),
                                html.Th("Name"),
                            ])
                        ]),
                        html.Tbody([
                            create_digital_io_row(1, "INP1H", "npn-input"),
                            create_digital_io_row(2, "INP2H", "npn-input"),
                            create_digital_io_row(3, "INP3H", "npn-input"),
                            create_digital_io_row(4, "INP4H", "npn-input"),
                        ])
                    ], bordered=True, hover=True, responsive=True, size='sm', className='mb-0'),
                ], className='config-table'),
            ], md=6),
            
            # NPN Output
            dbc.Col([
                html.H6("Output", className='text-muted mb-3'),
                html.Div([
                    dbc.Table([
                        html.Thead([
                            html.Tr([
                                html.Th(html.I(className="fas fa-check-square"), style={'width': '50px'}),
                                html.Th("Ch"),
                                html.Th("IO Pin"),
                                html.Th("Name"),
                            ])
                        ]),
                        html.Tbody([
                            create_digital_io_row(1, "OUTL1", "npn-output"),
                            create_digital_io_row(2, "OUTL2", "npn-output"),
                            create_digital_io_row(3, "OUTL3", "npn-output"),
                            create_digital_io_row(4, "OUTL4", "npn-output"),
                        ])
                    ], bordered=True, hover=True, responsive=True, size='sm', className='mb-0'),
                ], className='config-table'),
            ], md=6),
        ], className='mb-4'),
        
        # PNP Section
        html.H5([
            html.I(className="fas fa-microchip me-2", style={'color': '#667eea'}),
            "PNP Configuration"
        ], className='fw-bold mb-3 mt-4'),
        
        dbc.Row([
            # PNP Input
            dbc.Col([
                html.H6("Input", className='text-muted mb-3'),
                html.Div([
                    dbc.Table([
                        html.Thead([
                            html.Tr([
                                html.Th(html.I(className="fas fa-check-square"), style={'width': '50px'}),
                                html.Th("Ch"),
                                html.Th("IO Pin"),
                                html.Th("Name"),
                            ])
                        ]),
                        html.Tbody([
                            create_digital_io_row(1, "INP1L", "pnp-input"),
                            create_digital_io_row(2, "INP2L", "pnp-input"),
                            create_digital_io_row(3, "INP3L", "pnp-input"),
                            create_digital_io_row(4, "INP4L", "pnp-input"),
                        ])
                    ], bordered=True, hover=True, responsive=True, size='sm', className='mb-0'),
                ], className='config-table'),
            ], md=6),
            
            # PNP Output
            dbc.Col([
                html.H6("Output", className='text-muted mb-3'),
                html.Div([
                    dbc.Table([
                        html.Thead([
                            html.Tr([
                                html.Th(html.I(className="fas fa-check-square"), style={'width': '50px'}),
                                html.Th("Ch"),
                                html.Th("IO Pin"),
                                html.Th("Name"),
                            ])
                        ]),
                        html.Tbody([
                            create_digital_io_row(1, "OUTH1", "pnp-output"),
                            create_digital_io_row(2, "OUTH2", "pnp-output"),
                            create_digital_io_row(3, "OUTH3", "pnp-output"),
                            create_digital_io_row(4, "OUTH4", "pnp-output"),
                        ])
                    ], bordered=True, hover=True, responsive=True, size='sm', className='mb-0'),
                ], className='config-table'),
            ], md=6),
        ], className='mb-4'),
        
        # Relay Section
        html.H5([
            html.I(className="fas fa-toggle-on me-2", style={'color': '#667eea'}),
            "Relay Control"
        ], className='fw-bold mb-3 mt-4'),
        
        html.Div([
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th(html.I(className="fas fa-check-square"), style={'width': '50px'}),
                        html.Th("Relay Number"),
                        html.Th("IO Pin"),
                        html.Th("Name/Label"),
                    ])
                ]),
                html.Tbody([
                    create_digital_io_row(1, "RLY1", "relay"),
                    create_digital_io_row(2, "RLY2", "relay"),
                    create_digital_io_row(3, "RLY3", "relay"),
                    create_digital_io_row(4, "RLY4", "relay"),
                ])
            ], bordered=True, hover=True, responsive=True, className='mb-0'),
        ], className='config-table mb-4'),
        
        # Scan Rate Section
        dbc.Row([
            dbc.Col([
                dbc.Label("Scan Rate (seconds):", className='fw-bold'),
            ], md=3),
            dbc.Col([
                dbc.Input(
                    id='digital-scan-rate',
                    type='number',
                    value=1000,
                    min=1000,
                    step=1,
                    placeholder='Enter scan rate...'
                ),
            ], md=9),
        ], className='mb-3'),
        
        # Save Configuration Button for Digital Tab
        html.Div([
            html.Div([
                dbc.Button([
                    html.Span(id='save-digital-btn-spinner', children=[
                        html.I(className="fas fa-save me-2"),
                    ]),
                    html.Span(id='save-digital-btn-text', children="Save Configuration"),
                ], id='save-digital-config-btn', color='primary', size='lg', className='mt-3'),
            ], className='d-inline-block'),
            html.Div(id='save-digital-status-message', className='d-inline-block ms-3 mt-3'),
        ], className='text-end'),
    ])


def create_digital_io_row(channel, io_pin, pin_type):
    """Create a single digital I/O row"""
    return html.Tr([
        html.Td(
            dbc.Checkbox(
                id={'type': f'{pin_type}-enable', 'index': channel},
                value=False
            )
        ),
        html.Td(str(channel), className='fw-bold'),
        html.Td(
            html.Code(io_pin, className='badge bg-secondary')
        ),
        html.Td(
            dbc.Input(
                id={'type': f'{pin_type}-name', 'index': channel},
                type='text',
                placeholder='Enter name...',
                value='-',
                size='sm'
            )
        ),
    ])




def create_rs485_modbus_content():
    """Create RS485 MODBUS page content - imports from rs485_modbus.py"""
    from app.pages.rs485_modbus import create_rs485_modbus_layout
    return create_rs485_modbus_layout()


def create_can_bus_content():
    """Create CAN Bus page content - imports from can_bus.py"""
    from app.pages.can_bus import create_can_bus_layout
    return create_can_bus_layout()


# Callback to sync session data to device config page
@callback(
    Output('device-config-session-store', 'data'),
    [
        Input('url', 'pathname'),
        Input('session-store', 'data'),  # Changed from State to Input - triggers when session data changes
    ],
    prevent_initial_call=False
)
def sync_session_data(pathname, session_data):
    """Sync session data from main session store to device config session store"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔄 sync_session_data called - Pathname: {pathname}, Session data: {session_data if session_data else 'None/Empty'}")
    
    # If session_store has data, use it
    if session_data and isinstance(session_data, dict) and session_data.get('authenticated'):
        logger.info(f"✅ Using session-store data - Username: {session_data.get('username')}, User Type: {session_data.get('user_type')}")
        return session_data
    
    # Fallback to Flask session
    try:
        from flask import session as flask_session
        if flask_session.get('authenticated'):
            flask_data = {
                'authenticated': True,
                'username': flask_session.get('username', ''),
                'user_type': flask_session.get('user_type', 'user'),
                'user_data': flask_session.get('user_data', {})
            }
            logger.info(f"✅ Using Flask session data - Username: {flask_data.get('username')}, User Type: {flask_data.get('user_type')}")
            return flask_data
    except Exception as e:
        logger.warning(f"⚠️ Could not get Flask session: {e}")
        pass
    
    logger.warning("⚠️ No session data available - returning empty dict")
    return {}


# Callback to load device list (Serial Numbers) from Device_info on page load
# Uses multiple triggers to ensure it runs immediately when the page loads
@callback(
    [
        Output('device-selector', 'options'),
        Output('device-selector', 'value'),
        Output('device-selector-loading', 'children'),
    ],
    [
        Input('url', 'pathname'),
        Input('device-selector', 'id'),
        Input('device-config-session-store', 'data'),  # Changed from State to Input - triggers when session data changes
    ],
    prevent_initial_call=False
)
def load_device_list(pathname, _, session_data):
    """Load Serial Numbers from Device_info measurement filtered by logged-in user (optimized - single query with caching)"""
    global _device_list_cache, _cache_timestamp
    
    import logging
    logger = logging.getLogger(__name__)
    
    # Show loading spinner while fetching
    loading_spinner = dbc.Spinner(html.Div(), size="sm")
    
    try:
        from dash import ctx
        logger.info(f"🔄 load_device_list called - Pathname: {pathname}, Triggered ID: {ctx.triggered_id if hasattr(ctx, 'triggered_id') else 'None'}")
        
        # Allow loading on dashboard page or any authenticated page (device config is embedded in dashboard)
        # Only skip if explicitly on login/logout page
        skip_paths = ['/login', '/logout', '/']
        triggered_id = ctx.triggered_id if hasattr(ctx, 'triggered_id') else None
        if pathname in skip_paths and triggered_id == 'url':
            logger.info(f"⏭️ Skipping device list load for pathname: {pathname}")
            if _device_list_cache:
                return _device_list_cache[0], _device_list_cache[1], ""
            return [], None, ""
        
        # Get logged-in user info (fallback to Flask session if needed)
        username = None
        user_type = 'user'
        is_admin = False
        
        # Check session_data first - but verify it has actual data, not just empty dict
        if session_data and isinstance(session_data, dict) and session_data.get('authenticated'):
            username = session_data.get('username', '')
            user_type = session_data.get('user_type', 'user')
        else:
            # Fallback to Flask session directly
            try:
                from flask import session as flask_session
                if flask_session.get('authenticated'):
                    username = flask_session.get('username', '')
                    user_type = flask_session.get('user_type', 'user')
                    logger.info(f"🔍 Got user info from Flask session: {username}, {user_type}")
            except Exception as e:
                logger.warning(f"⚠️ Could not get Flask session: {e}")
                pass
        
        # Determine if admin (check both user_type and username)
        if user_type and str(user_type).lower() == 'admin':
            is_admin = True
            logger.info(f"✅ Admin detected via user_type: {user_type}")
        elif username and str(username).lower() == 'admin':
            is_admin = True
            logger.info(f"✅ Admin detected via username: {username}")
        
        logger.info(f"👤 Loading devices - Username: {username}, User Type: {user_type}, Is Admin: {is_admin}, Session Data: {session_data if session_data else 'None/Empty'}")
        
        # Build cache key that includes user info (different users see different devices)
        cache_key = f"{username}_{is_admin}"
        current_time = time.time()
        
        # Check cache first - but only if same user
        if _device_list_cache and isinstance(_device_list_cache, dict) and (current_time - _cache_timestamp) < _cache_ttl:
            cached_key = _device_list_cache.get('user_key')
            if cached_key == cache_key:
                cached_data = _device_list_cache.get('data', ([], None))
                logger.info(f"✅ Returning cached device list for user {username} (age: {current_time - _cache_timestamp:.1f}s)")
                return cached_data[0], cached_data[1], ""
        
        logger.info(f"📡 Fetching device list from database (cache expired or different user)")
        
        # Cache expired or not available, fetch from database
        # Show loading spinner while fetching
        from app.services.device_info_service import DeviceInfoService
        device_info_service = DeviceInfoService()
        
        if not device_info_service.is_connected():
            logger.error("❌ Device Info Service not connected to database")
            error_options = (
                [{'label': '⚠️ Database not connected', 'value': None, 'disabled': True}], 
                None,
                ""  # Hide spinner on error
            )
            _device_list_cache = {
                'data': (error_options[0], error_options[1]),
                'user_key': cache_key,
                'timestamp': current_time
            }
            _cache_timestamp = current_time
            return error_options
        
        # Get devices filtered by owner (admin sees all, regular users see only their devices)
        owner_filter_value = username if not is_admin and username else None
        logger.info(f"🔍 Calling get_all_devices_info - owner_filter: '{owner_filter_value}', is_admin: {is_admin}, username: '{username}'")
        
        all_devices_info = device_info_service.get_all_devices_info(
            owner_filter=owner_filter_value,
            is_admin=is_admin
        )
        
        logger.info(f"📊 Device query result: {len(all_devices_info) if all_devices_info else 0} devices found")
        if all_devices_info:
            logger.info(f"   Devices: {[d.get('Sr_No') for d in all_devices_info]}")
            # Log first device details for debugging
            if len(all_devices_info) > 0:
                first_device = all_devices_info[0]
                logger.info(f"   First device details: Sr_No={first_device.get('Sr_No')}, Owner={first_device.get('Owner')}, Device_Name={first_device.get('Device_Name')}")
        else:
            logger.warning(f"⚠️ No devices returned from query - owner_filter: '{owner_filter_value}', is_admin: {is_admin}")
        
        if not all_devices_info:
            logger.warning("⚠️ No devices found in database")
            no_devices_options = (
                [{'label': '⚠️ No devices found', 'value': None, 'disabled': True}], 
                None,
                ""  # Hide spinner
            )
            _device_list_cache = {
                'data': (no_devices_options[0], no_devices_options[1]),
                'user_key': cache_key,
                'timestamp': current_time
            }
            _cache_timestamp = current_time
            return no_devices_options
        
        # Build dropdown options with Serial Numbers (already sorted)
        options = []
        for device_info in all_devices_info:
            sr_no = device_info.get('Sr_No', '')
            device_name = device_info.get('Device_Name', 'Unnamed')
            label = f"🔌 {sr_no} - {device_name}"
            
            options.append({
                'label': label,
                'value': sr_no
            })
        
        logger.info(f"✅ Built {len(options)} dropdown options")
        
        # Set default value to first device
        default_value = all_devices_info[0].get('Sr_No') if all_devices_info else None
        
        logger.info(f"🎯 Default device selected: {default_value}")
        
        # Cache the results (with user key for cache invalidation)
        result = (options, default_value, "")  # Hide spinner after loading
        _device_list_cache = {
            'data': (options, default_value),
            'user_key': cache_key,
            'timestamp': current_time
        }
        _cache_timestamp = current_time
        
        logger.info(f"✅ Built {len(options)} dropdown options for user: {username} (is_admin: {is_admin})")
        
        return result
        
    except Exception as e:
        logger.error(f"Error loading device list: {e}")
        logger.exception("Full error traceback:")
        error_result = (
            [{'label': '⚠️ Error loading devices', 'value': None, 'disabled': True}], 
            None,
            ""
        )
        # Don't cache errors
        return error_result


# Callback to load saved configuration when device is selected or page loads
@callback(
    [
        # Analog inputs
        Output({'type': 'analog-input-enable', 'index': ALL}, 'value', allow_duplicate=True),
        Output({'type': 'analog-input-div', 'index': ALL}, 'value', allow_duplicate=True),
        Output({'type': 'analog-input-mul', 'index': ALL}, 'value', allow_duplicate=True),
        Output({'type': 'analog-input-name', 'index': ALL}, 'value', allow_duplicate=True),
        # Analog outputs
        Output({'type': 'analog-output-enable', 'index': ALL}, 'value', allow_duplicate=True),
        Output({'type': 'analog-output-value', 'index': ALL}, 'value', allow_duplicate=True),
        Output({'type': 'analog-output-name', 'index': ALL}, 'value', allow_duplicate=True),
        # Scan rates
        Output('analog-scan-rate', 'value', allow_duplicate=True),
        Output('digital-scan-rate', 'value', allow_duplicate=True),
        # Digital inputs/outputs (we'll need to add IDs for these)
    ],
    [
        Input('device-selector', 'value'),  # Trigger on device selection change
        Input('url', 'pathname'),  # Trigger on page load/navigation/refresh
        Input('config-reload-trigger', 'data'),  # Trigger after successful save
        Input('config-tabs', 'active_tab'),  # Trigger on tab switch to ensure latest config is shown
    ],
    State('device-config-session-store', 'data'),
    prevent_initial_call='initial_duplicate',  # Allow initial call on page load with duplicate outputs
    allow_duplicate=True
)
def load_device_configuration(device_id, pathname, reload_trigger, active_tab, session_data):
    """Load saved configuration for selected device and populate UI fields
    
    Triggers on:
    - Device selection change (device-selector value)
    - Page load/navigation (pathname change)
    - After successful save (config-reload-trigger timestamp update)
    - Browser refresh (pathname change)
    - Login/logout (pathname change)
    - Tab switch (active_tab change) - ensures latest config is always shown
    
    Loads configuration based on:
    - Logged-in user (User ID)
    - Device-User ownership mapping
    - Admin users see all devices
    - Regular users see only their assigned devices
    
    Auto-loads:
    - Analog config when device is selected or after save
    - Digital config when device is selected or after save
    - Shows default values if no config exists in database
    - Always shows the latest saved configuration
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Get trigger info for logging
    triggered_id = ctx.triggered_id if hasattr(ctx, 'triggered_id') else None
    
    # Allow loading on dashboard page (device config is embedded in dashboard)
    # Only skip if explicitly on login/logout page
    skip_paths = ['/login', '/logout', '/']
    if pathname in skip_paths:
        logger.debug(f"⏭️ Skipping config load for pathname: {pathname}")
        return [no_update] * 9
    
    if not device_id:
        # Try to get device ID from ctx if triggered by tab switch
        if triggered_id == 'config-tabs' or triggered_id == 'config-reload-trigger':
            # If triggered by tab switch or reload, try to get device from State or session
            # For now, skip if no device_id - this is acceptable as tab switch doesn't require reload
            logger.debug(f"⏭️ Tab switch/reload triggered but no device selected")
            return [no_update] * 9
        else:
            return [no_update] * 9  # Return no_update for all outputs
    
    try:
        # Get logged-in user info
        username = None
        is_admin = False
        if session_data:
            username = session_data.get('username', '')
            user_type = session_data.get('user_type', 'user')
            is_admin = (username == 'admin')
        
        logger.info(f"🔄 Loading configuration for device: {device_id}, user: {username}, is_admin: {is_admin}, trigger: {triggered_id}, active_tab: {active_tab}")
        
        # Verify device ownership (unless admin)
        if not is_admin and username:
            from app.services.device_info_service import DeviceInfoService
            device_info_service = DeviceInfoService()
            device_info = device_info_service.get_device_info(device_id)
            
            if not device_info:
                logger.warning(f"⚠️ Device {device_id} not found in database")
                return [no_update] * 9
            
            device_owner = device_info.get('Owner', 'Unassigned')
            if device_owner != username:
                logger.warning(f"⚠️ User {username} attempted to access device {device_id} owned by {device_owner} - Access denied")
                return [no_update] * 9  # Don't show config for devices user doesn't own
        
        from app.services.device_config_db import DeviceConfigDBService
        
        db_service = DeviceConfigDBService()
        
        if not db_service.is_connected():
            logger.warning("⚠️ Database not connected, cannot load configuration")
            return [no_update] * 9
        
        # Load configurations from individual tables (always get latest from database)
        # If triggered by reload trigger, add a small delay to ensure DB write is flushed
        if triggered_id == 'config-reload-trigger':
            import time
            time.sleep(0.5)  # Wait 0.5 seconds to ensure database write is fully flushed
        
        logger.info(f"🔄 Loading config from database for device {device_id}, triggered by: {triggered_id}")
        analog_config = db_service.get_analog_config(device_id)
        digital_config = db_service.get_digital_config(device_id)
        
        logger.info(f"📊 Loaded config - Analog: {analog_config is not None}, Digital: {digital_config is not None}")
        if analog_config:
            logger.debug(f"📊 Analog config keys: {list(analog_config.keys())}")
        if digital_config:
            logger.debug(f"📊 Digital config keys: {list(digital_config.keys())}")
        
        # If no configuration exists, use default values (don't reset to factory defaults)
        # Default values are already set in the initialization below
        
        # Prepare output lists with DEFAULT values (used when no config exists in database)
        # These defaults will be shown for new devices that haven't been configured yet
        analog_input_enable = [False] * 4  # Default: all channels disabled
        analog_input_div = [1] * 4         # Default: divider = 1
        analog_input_mul = [1] * 4         # Default: multiplier = 1
        analog_input_name = [''] * 4       # Default: empty names (will use IO pin as fallback)
        
        analog_output_enable = [False] * 2 # Default: all outputs disabled
        analog_output_value = [0.0] * 2    # Default: output value = 0.0V
        analog_output_name = [''] * 2      # Default: empty names (will use IO pin as fallback)
        
        analog_scan_rate = 1000  # Default: 1000 seconds
        digital_scan_rate = 1000 # Default: 1000 seconds
        
        # Populate Analog config from database (if exists)
        # If config doesn't exist, defaults above will be used
        if analog_config:
            logger.info(f"✅ Loading Analog config from database for device {device_id}")
            
            # Input 4-20mA (channels 1-2)
            for channel_data in analog_config.get("input_4_20ma", []):
                ch = channel_data.get("channel", 0) - 1  # Convert to 0-based index
                if 0 <= ch < 2:
                    analog_input_enable[ch] = channel_data.get("enabled", False)
                    analog_input_div[ch] = channel_data.get("divider", 1)
                    analog_input_mul[ch] = channel_data.get("multiplier", 1)
                    analog_input_name[ch] = channel_data.get("name", "")
            
            # Input 0-10V (channels 3-4)
            for channel_data in analog_config.get("input_1_10v", []):
                ch = channel_data.get("channel", 0) - 1  # Convert to 0-based index
                if 2 <= ch < 4:
                    analog_input_enable[ch] = channel_data.get("enabled", False)
                    analog_input_div[ch] = channel_data.get("divider", 1)
                    analog_input_mul[ch] = channel_data.get("multiplier", 1)
                    analog_input_name[ch] = channel_data.get("name", "")
            
            # Output 0-10V (channels 1-2)
            for channel_data in analog_config.get("output_0_10v", []):
                ch = channel_data.get("channel", 0) - 1  # Convert to 0-based index
                if 0 <= ch < 2:
                    analog_output_enable[ch] = channel_data.get("enabled", False)
                    analog_output_value[ch] = channel_data.get("value", 0.0)
                    analog_output_name[ch] = channel_data.get("name", "")
            
            analog_scan_rate = analog_config.get("scan_rate", 1000)
        else:
            logger.info(f"ℹ️ No Analog config found in database for device {device_id}, using default values")
        
        # Populate Digital config from database (if exists)
        # If config doesn't exist, defaults above will be used
        if digital_config:
            logger.info(f"✅ Loading Digital config from database for device {device_id}")
            digital_scan_rate = digital_config.get("scan_rate", 1000)
            # TODO: Populate digital I/O fields when we have the component IDs
        else:
            logger.info(f"ℹ️ No Digital config found in database for device {device_id}, using default values")
        
        return (
            analog_input_enable,
            analog_input_div,
            analog_input_mul,
            analog_input_name,
            analog_output_enable,
            analog_output_value,
            analog_output_name,
            analog_scan_rate,
            digital_scan_rate
        )
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error loading device configuration: {e}")
        logger.exception("Full error traceback:")
        return [no_update] * 9


# Callback for save Analog configuration (inside Analog tab)
@callback(
    [
        Output('save-analog-status-message', 'children'),
        Output('save-analog-btn-spinner', 'children'),
        Output('save-analog-config-btn', 'disabled'),
        Output('config-reload-trigger', 'data', allow_duplicate=True),
        Output('save-analog-message-timer', 'data', allow_duplicate=True),
        Output('save-analog-hide-interval', 'disabled', allow_duplicate=True),
    ],
    Input('save-analog-config-btn', 'n_clicks'),
    # Analog Input States
    State({'type': 'analog-input-enable', 'index': ALL}, 'value'),
    State({'type': 'analog-input-div', 'index': ALL}, 'value'),
    State({'type': 'analog-input-mul', 'index': ALL}, 'value'),
    State({'type': 'analog-input-name', 'index': ALL}, 'value'),
    # Analog Output States
    State({'type': 'analog-output-enable', 'index': ALL}, 'value'),
    State({'type': 'analog-output-value', 'index': ALL}, 'value'),
    State({'type': 'analog-output-name', 'index': ALL}, 'value'),
    # Scan Rate States
    State('analog-scan-rate', 'value'),
    # Device Selection (Serial Number)
    State('device-selector', 'value'),
    State('device-config-session-store', 'data'),
    prevent_initial_call=True
)
def save_analog_configuration(
    n_clicks,
    analog_input_enable, analog_input_div, analog_input_mul, analog_input_name,
    analog_output_enable, analog_output_value, analog_output_name,
    analog_scan_rate,
    serial_number,
    session_data
):
    """Save device configuration with validation and ownership check"""
    if not n_clicks:
        return "", html.I(className="fas fa-save me-2"), False, no_update, no_update, True
    
    import logging
    logger = logging.getLogger(__name__)
    
    # Get logged-in user info
    username = None
    is_admin = False
    if session_data:
        username = session_data.get('username', '')
        user_type = session_data.get('user_type', 'user')
        is_admin = (username == 'admin')
    
    # Validate Serial Number is selected
    if not serial_number:
        error_msg = html.Div([
            html.Strong("Validation Error: "),
            "Please select a device (Serial Number) from the dropdown."
        ], className='text-danger')
        return error_msg, html.I(className="fas fa-save me-2"), False, no_update, no_update, True
    
    # Verify device ownership before saving (unless admin)
    if not is_admin and username and serial_number:
        from app.services.device_info_service import DeviceInfoService
        device_info_service = DeviceInfoService()
        device_info = device_info_service.get_device_info(serial_number)
        
        if device_info:
            device_owner = device_info.get('Owner', 'Unassigned')
            if device_owner != username:
                logger.warning(f"⚠️ User {username} attempted to save config for device {serial_number} owned by {device_owner} - Access denied")
                error_msg = html.Div([
                    html.Strong("Access Denied: "),
                    f"❌ You don't have permission to save configuration for device {serial_number}. This device is owned by {device_owner}."
                ], className='text-danger')
                return error_msg, html.I(className="fas fa-save me-2"), False, no_update, no_update, True
        else:
            logger.warning(f"⚠️ Device {serial_number} not found in database")
            error_msg = html.Div([
                html.Strong("Error: "),
                f"❌ Device {serial_number} not found in database."
            ], className='text-danger')
            return error_msg, html.I(className="fas fa-save me-2"), False, no_update, no_update, True, no_update, True
    
    # IMPORTANT: For immediate UI feedback, we need to return disabled/spinner state
    # However, Dash callbacks are synchronous, so UI updates only happen after callback completes
    # The button will show spinner and be disabled during the save operation
    loading_spinner = html.Span([
        dbc.Spinner(html.I(className="fas fa-save me-2"), size="sm", spinner_style={"width": "1rem", "height": "1rem"}),
    ])
    
    try:
        # Return loading state immediately (button disabled + spinner visible)
        # This will update UI after callback completes
        from app.services.config_json_builder import ConfigJSONBuilder
        from app.services.device_config import DeviceConfigService
        from app.services.device_config_db import DeviceConfigDBService
        
        builder = ConfigJSONBuilder()
        config_service = DeviceConfigService()
        db_service = DeviceConfigDBService()
        
        # Validate Scan Rate
        if analog_scan_rate is None or analog_scan_rate < 1000:
            error_msg = html.Div([
                html.Strong("Validation Error: "),
                "Analog Scan Rate must be at least 1000 seconds."
            ], className='text-danger')
            return error_msg, html.I(className="fas fa-save me-2"), False, no_update, no_update, True, no_update, True
        
        # IMPORTANT: Use ctx.states to get actual indices from pattern-matched values
        # Dash pattern matching returns values as lists, but we need to map them by actual index
        # Extract output values and names by their actual index from ctx.states
        output_value_map = {}  # {index: value}
        output_name_map = {}   # {index: name}
        output_enable_map = {} # {index: enabled}
        
        # Debug: Log ctx.states structure
        logger.info(f"🔍 DEBUG: ctx.states type: {type(ctx.states)}")
        logger.info(f"🔍 DEBUG: ctx.states keys: {list(ctx.states.keys()) if ctx.states else 'None'}")
        
        # Get all pattern-matched states for outputs
        if ctx.states:
            # ctx.states is a dict where keys are State objects (or tuples) and values are the actual values
            # When using pattern matching, keys might be tuples like (id_dict, 'value') or just the id_dict
            for state_key, state_value in ctx.states.items():
                logger.debug(f"🔍 DEBUG: state_key type: {type(state_key)}, state_key: {state_key}, state_value: {state_value}")
                
                # Handle different possible key formats
                id_dict = None
                prop = None
                
                if isinstance(state_key, dict):
                    # Key is directly the ID dict
                    id_dict = state_key
                    prop = 'value'  # Assume it's the value property
                elif isinstance(state_key, tuple) and len(state_key) == 2:
                    # Key is tuple (id_dict, property)
                    id_dict, prop = state_key
                
                if id_dict and isinstance(id_dict, dict):
                    comp_type = id_dict.get('type')
                    comp_index = id_dict.get('index')
                    
                    if comp_type == 'analog-output-value' and comp_index:
                        output_value_map[comp_index] = state_value
                        logger.info(f"✅ Found output value for index {comp_index}: {state_value}")
                    
                    elif comp_type == 'analog-output-name' and comp_index:
                        output_name_map[comp_index] = state_value
                        logger.info(f"✅ Found output name for index {comp_index}: {state_value}")
                    
                    elif comp_type == 'analog-output-enable' and comp_index:
                        output_enable_map[comp_index] = state_value
                        logger.info(f"✅ Found output enable for index {comp_index}: {state_value}")
        
        logger.info(f"✅ Output value map: {output_value_map}")
        logger.info(f"✅ Output name map: {output_name_map}")
        logger.info(f"✅ Output enable map: {output_enable_map}")
        
        # FALLBACK: If ctx.states didn't populate maps, try using the arrays directly
        # Dash ALL returns values in DOM order, and we create channels in order 1, 2
        # So array[0] should be channel 1, array[1] should be channel 2
        if not output_value_map and analog_output_value:
            logger.warning("⚠️ ctx.states didn't populate output_value_map, using array fallback")
            for idx, val in enumerate(analog_output_value):
                channel_num = idx + 1  # Channels are 1-indexed
                if channel_num <= 2:  # Only channels 1 and 2 for outputs
                    output_value_map[channel_num] = val
                    logger.info(f"✅ Fallback: Mapped array[{idx}] to channel {channel_num}: {val}")
        
        if not output_name_map and analog_output_name:
            logger.warning("⚠️ ctx.states didn't populate output_name_map, using array fallback")
            for idx, name in enumerate(analog_output_name):
                channel_num = idx + 1
                if channel_num <= 2:
                    output_name_map[channel_num] = name
                    logger.info(f"✅ Fallback: Mapped array[{idx}] to channel {channel_num}: {name}")
        
        if not output_enable_map and analog_output_enable:
            logger.warning("⚠️ ctx.states didn't populate output_enable_map, using array fallback")
            for idx, enabled in enumerate(analog_output_enable):
                channel_num = idx + 1
                if channel_num <= 2:
                    output_enable_map[channel_num] = enabled
                    logger.info(f"✅ Fallback: Mapped array[{idx}] to channel {channel_num}: {enabled}")
        
        # IO Pin mapping for channels
        io_pins = {
            1: "AIN0",
            2: "AIN1",
            3: "AIN2",
            4: "AIN3"
        }
        
        # Build Analog Config
        # 4-20mA Input (channels 1-2)
        input_4_20ma_data = []
        for idx in range(2):
            channel = idx + 1
            io_pin = io_pins[channel]
            div = analog_input_div[idx] if idx < len(analog_input_div) and analog_input_div[idx] is not None else None
            mul = analog_input_mul[idx] if idx < len(analog_input_mul) and analog_input_mul[idx] is not None else None
            name = analog_input_name[idx] if idx < len(analog_input_name) and analog_input_name[idx] else None
            
            # Set default name to IO pin if empty (before validation)
            if not name or name.strip() == '':
                name = io_pin
            
            # Validation: All parameters must be filled
            if div is None or mul is None or not name or name.strip() == '':
                error_msg = html.Div([
                    html.Strong("Validation Error: "),
                    f"Please fill all parameters for Channel {channel} (4-20mA): Divider, Multiplier, and Name/Label are required."
                ], className='text-danger')
                return error_msg, html.I(className="fas fa-save me-2"), False, no_update, no_update, True
            
            input_4_20ma_data.append({
                "channel": channel,
                "enabled": analog_input_enable[idx] if idx < len(analog_input_enable) else False,
                "divider": div,
                "multiplier": mul,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        # 0-10V Input (channels 3-4)
        input_1_10v_data = []
        for idx in range(2):
            channel = idx + 3
            io_pin = io_pins[channel]
            div = analog_input_div[idx + 2] if idx + 2 < len(analog_input_div) and analog_input_div[idx + 2] is not None else None
            mul = analog_input_mul[idx + 2] if idx + 2 < len(analog_input_mul) and analog_input_mul[idx + 2] is not None else None
            name = analog_input_name[idx + 2] if idx + 2 < len(analog_input_name) and analog_input_name[idx + 2] else None
            
            # Set default name to IO pin if empty (before validation)
            if not name or name.strip() == '':
                name = io_pin
            
            # Validation: All parameters must be filled
            if div is None or mul is None or not name or name.strip() == '':
                error_msg = html.Div([
                    html.Strong("Validation Error: "),
                    f"Please fill all parameters for Channel {channel} (0-10V): Divider, Multiplier, and Name/Label are required."
                ], className='text-danger')
                return error_msg, html.I(className="fas fa-save me-2"), False, no_update, no_update, True
            
            input_1_10v_data.append({
                "channel": channel,
                "enabled": analog_input_enable[idx + 2] if idx + 2 < len(analog_input_enable) else False,
                "divider": div,
                "multiplier": mul,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        # 0-10V Output - SIMPLIFIED APPROACH: Use arrays directly (they come in DOM order)
        # ROOT CAUSE: Dash ALL returns values in DOM order. We create rows as channel 1, then channel 2.
        # So analog_output_value[0] = channel 1, analog_output_value[1] = channel 2
        output_0_10v_data = []
        
        logger.info(f"🔍 STEP 1: Checking input arrays for outputs")
        logger.info(f"🔍 analog_output_value: {analog_output_value} (type: {type(analog_output_value)}, length: {len(analog_output_value) if analog_output_value else 0})")
        logger.info(f"🔍 analog_output_name: {analog_output_name} (type: {type(analog_output_name)}, length: {len(analog_output_name) if analog_output_name else 0})")
        logger.info(f"🔍 analog_output_enable: {analog_output_enable} (type: {type(analog_output_enable)}, length: {len(analog_output_enable) if analog_output_enable else 0})")
        
        # Process 2 output channels (channels 1 and 2, indices 1 and 2 in UI)
        # Arrays from State ALL come in DOM order, so index 0 = first row = channel 1, index 1 = second row = channel 2
        for idx in range(2):
            channel = idx + 1  # Channel number (1 or 2)
            io_pin = f"DOUT{idx}"  # DOUT0 or DOUT1
            
            logger.info(f"🔍 STEP 2: Processing output channel {channel} (array index {idx})")
            
            # Get value from array - handle bounds checking
            if not analog_output_value or idx >= len(analog_output_value):
                raw_value = None
                logger.error(f"❌ Channel {channel} - analog_output_value is None or index {idx} out of range")
            else:
                raw_value = analog_output_value[idx]
                logger.info(f"🔍 Channel {channel} - raw_value from array[{idx}]: {raw_value} (type: {type(raw_value)})")
            
            # Convert to float - handle None, empty string, and numeric values (including 0)
            if raw_value is None:
                value = None
                logger.warning(f"⚠️ Channel {channel} - raw_value is None")
            elif isinstance(raw_value, str):
                raw_value = raw_value.strip()
                if raw_value == '' or raw_value.lower() == 'none':
                    value = None
                    logger.warning(f"⚠️ Channel {channel} - raw_value is empty string or 'none'")
                else:
                    try:
                        value = float(raw_value)
                        logger.info(f"✅ Channel {channel} - converted string '{raw_value}' to float: {value}")
                    except (ValueError, TypeError) as e:
                        value = None
                        logger.error(f"❌ Channel {channel} - cannot convert '{raw_value}' to float: {e}")
            elif isinstance(raw_value, (int, float)):
                value = float(raw_value)  # Convert int/float to float
                logger.info(f"✅ Channel {channel} - converted {raw_value} (type: {type(raw_value)}) to float: {value}")
            else:
                try:
                    value = float(raw_value)
                    logger.info(f"✅ Channel {channel} - converted {raw_value} (type: {type(raw_value)}) to float: {value}")
                except (ValueError, TypeError) as e:
                    value = None
                    logger.error(f"❌ Channel {channel} - cannot convert {raw_value} (type: {type(raw_value)}) to float: {e}")
            
            # Get name from array
            if not analog_output_name or idx >= len(analog_output_name):
                raw_name = None
                logger.warning(f"⚠️ Channel {channel} - analog_output_name is None or index {idx} out of range")
            else:
                raw_name = analog_output_name[idx]
                logger.info(f"🔍 Channel {channel} - raw_name from array[{idx}]: {raw_name} (type: {type(raw_name)})")
            
            # Process name
            if raw_name is None:
                name = None
            else:
                name_str = str(raw_name).strip()
                name = name_str if name_str != '' else None
            
            # Set default name to IO pin if empty
            if not name or name.strip() == '':
                name = io_pin
                logger.info(f"✅ Channel {channel} - name was empty, set to default: {io_pin}")
            
            # Get enabled from array
            if not analog_output_enable or idx >= len(analog_output_enable):
                enabled = False
                logger.warning(f"⚠️ Channel {channel} - analog_output_enable is None or index {idx} out of range, defaulting to False")
            else:
                enabled = bool(analog_output_enable[idx])
                logger.info(f"🔍 Channel {channel} - enabled from array[{idx}]: {enabled}")
            
            logger.info(f"🔍 Channel {channel} - Final values: value={value} (type: {type(value)}), name={name}, enabled={enabled}")
            
            # Validation: Value must be provided (0.0 is a VALID value)
            # IMPORTANT: We only fail if value is None, NOT if it's 0.0
            if value is None:
                logger.error(f"❌ VALIDATION FAILED: Channel {channel} - value is None")
                logger.error(f"❌ analog_output_value array: {analog_output_value}")
                logger.error(f"❌ array index {idx} value: {analog_output_value[idx] if analog_output_value and idx < len(analog_output_value) else 'OUT_OF_RANGE'}")
                error_msg = html.Div([
                    html.Strong("Validation Error: "),
                    f"Please fill all parameters for Output Channel {channel}: Value is required (cannot be empty)."
                ], className='text-danger')
                return error_msg, html.I(className="fas fa-save me-2"), False, no_update, no_update, True
            
            # Validation: Name should be set (should have default by now, but double-check)
            if not name or name.strip() == '':
                logger.error(f"❌ VALIDATION FAILED: Channel {channel} - name is empty")
                error_msg = html.Div([
                    html.Strong("Validation Error: "),
                    f"Please fill all parameters for Output Channel {channel}: Name/Label is required."
                ], className='text-danger')
                return error_msg, html.I(className="fas fa-save me-2"), False, no_update, no_update, True
            
            # Add to output data list
            output_data = {
                "channel": channel,
                "enabled": enabled,
                "value": value,  # This is now guaranteed to be a float (not None)
                "io_pin": io_pin,
                "name": name.strip()
            }
            output_0_10v_data.append(output_data)
            logger.info(f"✅ Channel {channel} - added to output_0_10v_data: {output_data}")
        
        logger.info(f"✅ DEBUG: output_0_10v_data final list: {output_0_10v_data} (length: {len(output_0_10v_data)})")
        
        # Verify output_0_10v_data before building config
        if not output_0_10v_data:
            logger.warning(f"⚠️ WARNING: output_0_10v_data is EMPTY before building analog_config!")
        else:
            logger.info(f"✅ output_0_10v_data has {len(output_0_10v_data)} entries")
        
        analog_config = builder.build_analog_config(
            input_4_20ma_data,
            input_1_10v_data,
            output_0_10v_data,
            scan_rate=analog_scan_rate
        )
        
        # Verify output_0_10v in built config
        built_output_0_10v = analog_config.get("output_0_10v", [])
        logger.info(f"✅ DEBUG: Built analog_config has output_0_10v with {len(built_output_0_10v)} entries")
        logger.debug(f"🔍 DEBUG: Built analog_config['output_0_10v']: {built_output_0_10v}")
        
        # Build config with only analog section
        config_with_analog_only = {
            "device_id": serial_number,
            "analog": analog_config
        }
        
        # CRITICAL DEBUG: Log what we're about to save
        logger.info(f"🔍 STEP 1 PREPARATION: About to save analog config for device: {serial_number}")
        logger.info(f"🔍 config_with_analog_only keys: {list(config_with_analog_only.keys())}")
        logger.info(f"🔍 analog_config keys: {list(analog_config.keys())}")
        logger.info(f"🔍 analog_config['output_0_10v'] exists: {'output_0_10v' in analog_config}")
        if 'output_0_10v' in analog_config:
            output_list = analog_config.get('output_0_10v', [])
            logger.info(f"🔍 analog_config['output_0_10v'] length: {len(output_list)}")
            logger.info(f"🔍 analog_config['output_0_10v'] contents: {output_list}")
        else:
            logger.error(f"❌ CRITICAL: 'output_0_10v' key NOT FOUND in analog_config!")
            logger.error(f"❌ analog_config full contents: {analog_config}")
        
        # Save to database - Only Device_Config_Analog table
        if db_service.is_connected():
            # STEP 1: Save only analog section to its individual table
            # IMPORTANT: save_config_sections_only() will ONLY save sections that exist in the config dict
            # Since config_with_analog_only only contains "analog", only analog section will be saved
            logger.info(f"🔍 STEP 1: Calling save_config_sections_only() to save analog section to Device_Config_Analog table...")
            try:
                save_success = db_service.save_config_sections_only(serial_number, config_with_analog_only)
                if not save_success:
                    logger.error(f"❌ Failed to save analog config sections for device {serial_number}")
                    error_msg = html.Div([
                        html.Strong("Error: "),
                        f"❌ Failed to save analog configuration to database."
                    ], className='text-danger')
                    return error_msg, html.I(className="fas fa-save me-2"), False, no_update, no_update, True
                logger.info(f"✅ STEP 1: Successfully saved analog section to Device_Config_Analog")
            except Exception as save_error:
                logger.error(f"❌ Exception while saving analog config sections: {save_error}")
                logger.exception("Full traceback:")
                error_msg = html.Div([
                    html.Strong("Error: "),
                    f"❌ Error saving analog configuration: {str(save_error)}"
                ], className='text-danger')
                return error_msg, html.I(className="fas fa-save me-2"), False, no_update, no_update, True
            
            # STEP 2: Rebuild complete merged config from ALL tabs
            # Get latest configs from other tabs (Digital, MODBUS, CAN Bus)
            logger.info(f"🔍 STEP 2: Fetching latest configs from all tables...")
            digital_config_db = db_service.get_digital_config(serial_number)
            modbus_config_db = db_service.get_modbus_config(serial_number)
            can_bus_config_db = db_service.get_can_bus_config(serial_number)
            
            logger.info(f"🔍 DEBUG: digital_config_db exists: {digital_config_db is not None}")
            logger.info(f"🔍 DEBUG: modbus_config_db exists: {modbus_config_db is not None}")
            logger.info(f"🔍 DEBUG: can_bus_config_db exists: {can_bus_config_db is not None}")
            
            # Build ONE merged complete config combining ALL sections
            complete_config = {
                "device_id": serial_number
            }
            
            # Add new Analog config (just saved)
            complete_config["analog"] = analog_config
            
            # Add other sections if they exist (from database)
            if digital_config_db:
                complete_config["digital"] = digital_config_db
                logger.info(f"✅ Added digital config to merged config")
            else:
                logger.info(f"⚠️ No digital config found in database for device {serial_number}")
            
            if modbus_config_db:
                complete_config["rs485_modbus"] = modbus_config_db
                logger.info(f"✅ Added rs485_modbus config to merged config")
            else:
                logger.info(f"⚠️ No rs485_modbus config found in database for device {serial_number}")
            
            if can_bus_config_db:
                complete_config["can_bus"] = can_bus_config_db
                logger.info(f"✅ Added can_bus config to merged config")
            else:
                logger.info(f"⚠️ No can_bus config found in database for device {serial_number}")
            
            logger.info(f"✅ DEBUG: Complete merged config has sections: {list(complete_config.keys())}")
            logger.debug(f"🔍 DEBUG: Complete merged config: {complete_config}")
            
            # STEP 3: Save ONE merged JSON to Device_Config
            # IMPORTANT: save_device_config() ONLY saves the merged JSON, NOT individual sections
            # This ensures Device_Config always contains ONE merged JSON per device
            logger.info(f"🔍 STEP 3: Saving merged config to Device_Config table...")
            try:
                save_merged_success = db_service.save_device_config(serial_number, complete_config)
                if not save_merged_success:
                    logger.error(f"❌ Failed to save merged config to Device_Config for device {serial_number}")
                else:
                    logger.info(f"✅ STEP 3: Successfully saved merged config to Device_Config")
            except Exception as merge_error:
                logger.error(f"❌ Exception while saving merged config: {merge_error}")
                logger.exception("Full traceback:")
                # Don't fail the save, just log the error
            
            # Publish to MQTT
            try:
                from app.services.mqtt_client import MQTTClientService
                mqtt_service = MQTTClientService()
                if mqtt_service.is_connected():
                    mqtt_service.publish_config(serial_number, complete_config)
            except Exception as mqtt_error:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"MQTT publishing failed (non-critical): {mqtt_error}")
        
        # Also save to local JSON (for backup)
        success = config_service.save_device_config(serial_number, config_with_analog_only)
        
        # Success - show message, restore icon, re-enable button
        if success or db_service.is_connected():
            success_msg = html.Div([
                html.Span("✅ ", className='text-success'),
                html.Strong("Saved! ", className='text-success'),
                f"Device: {serial_number} | Complete config updated & published to MQTT"
            ], className='text-success fw-bold')
            
            # Trigger config reload by updating the store timestamp
            # Add a small delay (0.5 seconds) to ensure database write is fully flushed
            import time
            current_time = time.time()
            reload_timestamp = {'timestamp': current_time + 0.5}  # Delay reload by 0.5s to ensure DB write completes
            
            # Set timer to hide message after 1 second (1000ms)
            # Store the timestamp when message should be hidden
            message_timer = {'hide_at': current_time + 1.0}
            
            logger.info(f"✅ Save completed for device {serial_number}, reload will trigger at {reload_timestamp['timestamp']}")
            
            # Return: status message, icon (no spinner), button enabled, reload trigger, message timer, interval enabled
            return success_msg, html.I(className="fas fa-save me-2"), False, reload_timestamp, message_timer, False
        else:
            # Error - show error message, restore icon, re-enable button
            error_msg = html.Div([
                html.Strong("Error: "),
                f"❌ Error saving analog configuration for Serial Number: {serial_number}"
            ], className='text-danger')
            return error_msg, html.I(className="fas fa-save me-2"), False, no_update, no_update, True, no_update, True
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error saving analog configuration: {e}")
        logger.exception("Full error traceback:")
        error_msg = html.Div([
            html.Strong("Error: "),
            f"❌ {str(e)}"
        ], className='text-danger')
        return error_msg, html.I(className="fas fa-save me-2"), False, no_update, no_update, True


# Callback to auto-hide success message after 1 second
@callback(
    [
        Output('save-analog-status-message', 'children', allow_duplicate=True),
        Output('save-analog-hide-interval', 'disabled', allow_duplicate=True),
    ],
    Input('save-analog-hide-interval', 'n_intervals'),
    State('save-analog-message-timer', 'data'),
    State('save-analog-status-message', 'children'),
    prevent_initial_call=True
)
def auto_hide_analog_message(n_intervals, timer_data, current_message):
    """Auto-hide success message after 1 second"""
    import time
    
    # If no timer data or no message, do nothing
    if not timer_data or not current_message:
        return no_update, True  # Disable interval
    
    hide_at = timer_data.get('hide_at', 0)
    current_time = time.time()
    
    # Check if 1 second has passed
    if current_time >= hide_at:
        # Clear message and disable interval
        return "", True
    else:
        # Keep checking - interval will trigger again
        return no_update, False


# Callback for save Digital configuration (inside Digital tab)
@callback(
    [
        Output('config-save-toast', 'is_open', allow_duplicate=True),
        Output('config-save-toast', 'children', allow_duplicate=True),
        Output('config-reload-trigger', 'data', allow_duplicate=True),
    ],
    Input('save-digital-config-btn', 'n_clicks'),
    # Digital I/O States
    State({'type': 'npn-input-enable', 'index': ALL}, 'value'),
    State({'type': 'npn-input-name', 'index': ALL}, 'value'),
    State({'type': 'npn-output-enable', 'index': ALL}, 'value'),
    State({'type': 'npn-output-name', 'index': ALL}, 'value'),
    State({'type': 'pnp-input-enable', 'index': ALL}, 'value'),
    State({'type': 'pnp-input-name', 'index': ALL}, 'value'),
    State({'type': 'pnp-output-enable', 'index': ALL}, 'value'),
    State({'type': 'pnp-output-name', 'index': ALL}, 'value'),
    State({'type': 'relay-enable', 'index': ALL}, 'value'),
    State({'type': 'relay-name', 'index': ALL}, 'value'),
    # Scan Rate State
    State('digital-scan-rate', 'value'),
    # Device Selection (Serial Number)
    State('device-selector', 'value'),
    State('device-config-session-store', 'data'),
    prevent_initial_call=True
)
def save_digital_configuration(
    n_clicks,
    npn_input_enable, npn_input_name,
    npn_output_enable, npn_output_name,
    pnp_input_enable, pnp_input_name,
    pnp_output_enable, pnp_output_name,
    relay_enable, relay_name,
    digital_scan_rate,
    serial_number,
    session_data
):
    """Save Digital configuration - saves only to Device_Config_Digital table"""
    if not n_clicks:
        return False, "", no_update
    
    import logging
    logger = logging.getLogger(__name__)
    
    # Get logged-in user info
    username = None
    is_admin = False
    if session_data:
        username = session_data.get('username', '')
        user_type = session_data.get('user_type', 'user')
        is_admin = (username == 'admin')
    
    try:
        from app.services.config_json_builder import ConfigJSONBuilder
        from app.services.device_config import DeviceConfigService
        from app.services.device_config_db import DeviceConfigDBService
        
        builder = ConfigJSONBuilder()
        config_service = DeviceConfigService()
        db_service = DeviceConfigDBService()
        
        # Validate Serial Number is selected
        if not serial_number:
            return True, html.Div([
                html.Strong("Validation Error: "),
                "Please select a device (Serial Number) from the dropdown."
            ]), no_update
        
        # Verify device ownership before saving (unless admin)
        if not is_admin and username and serial_number:
            from app.services.device_info_service import DeviceInfoService
            device_info_service = DeviceInfoService()
            device_info = device_info_service.get_device_info(serial_number)
            
            if device_info:
                device_owner = device_info.get('Owner', 'Unassigned')
                if device_owner != username:
                    logger.warning(f"⚠️ User {username} attempted to save config for device {serial_number} owned by {device_owner} - Access denied")
                    return True, html.Div([
                        html.Strong("Access Denied: "),
                        f"❌ You don't have permission to save configuration for device {serial_number}. This device is owned by {device_owner}."
                    ], className='text-danger'), no_update
            else:
                logger.warning(f"⚠️ Device {serial_number} not found in database")
                return True, html.Div([
                    html.Strong("Error: "),
                    f"❌ Device {serial_number} not found in database."
                ], className='text-danger'), no_update
        
        # Validate Scan Rate
        if digital_scan_rate is None or digital_scan_rate < 1000:
            return True, html.Div([
                html.Strong("Validation Error: "),
                "Digital Scan Rate must be at least 1000 seconds."
            ]), no_update
        
        # IO Pin mappings
        digital_io_pins = {
            'npn_input': {1: "INP1H", 2: "INP2H", 3: "INP3H", 4: "INP4H"},
            'npn_output': {1: "OUTL1", 2: "OUTL2", 3: "OUTL3", 4: "OUTL4"},
            'pnp_input': {1: "INP1L", 2: "INP2L", 3: "INP3L", 4: "INP4L"},
            'pnp_output': {1: "OUTH1", 2: "OUTH2", 3: "OUTH3", 4: "OUTH4"},
            'relay': {1: "RLY1", 2: "RLY2", 3: "RLY3", 4: "RLY4"}
        }
        
        # Build Digital Config
        npn_input_data = []
        for idx in range(4):
            channel = idx + 1
            io_pin = digital_io_pins['npn_input'][channel]
            name = npn_input_name[idx] if idx < len(npn_input_name) and npn_input_name[idx] else io_pin
            if not name or name.strip() == '':
                name = io_pin
            
            npn_input_data.append({
                "channel": channel,
                "enabled": npn_input_enable[idx] if idx < len(npn_input_enable) else False,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        npn_output_data = []
        for idx in range(4):
            channel = idx + 1
            io_pin = digital_io_pins['npn_output'][channel]
            name = npn_output_name[idx] if idx < len(npn_output_name) and npn_output_name[idx] else io_pin
            if not name or name.strip() == '':
                name = io_pin
            
            npn_output_data.append({
                "channel": channel,
                "enabled": npn_output_enable[idx] if idx < len(npn_output_enable) else False,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        pnp_input_data = []
        for idx in range(4):
            channel = idx + 1
            io_pin = digital_io_pins['pnp_input'][channel]
            name = pnp_input_name[idx] if idx < len(pnp_input_name) and pnp_input_name[idx] else io_pin
            if not name or name.strip() == '':
                name = io_pin
            
            pnp_input_data.append({
                "channel": channel,
                "enabled": pnp_input_enable[idx] if idx < len(pnp_input_enable) else False,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        pnp_output_data = []
        for idx in range(4):
            channel = idx + 1
            io_pin = digital_io_pins['pnp_output'][channel]
            name = pnp_output_name[idx] if idx < len(pnp_output_name) and pnp_output_name[idx] else io_pin
            if not name or name.strip() == '':
                name = io_pin
            
            pnp_output_data.append({
                "channel": channel,
                "enabled": pnp_output_enable[idx] if idx < len(pnp_output_enable) else False,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        relay_data = []
        for idx in range(4):
            channel = idx + 1
            io_pin = digital_io_pins['relay'][channel]
            name = relay_name[idx] if idx < len(relay_name) and relay_name[idx] else io_pin
            if not name or name.strip() == '':
                name = io_pin
            
            relay_data.append({
                "channel": channel,
                "enabled": relay_enable[idx] if idx < len(relay_enable) else False,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        digital_config = builder.build_digital_config(
            npn_input_data,
            npn_output_data,
            pnp_input_data,
            pnp_output_data,
            relay_data
        )
        digital_config["scan_rate"] = digital_scan_rate
        
        # Build config with only digital section
        config_with_digital_only = {
            "device_id": serial_number,
            "digital": digital_config
        }
        
        # Save to database - Only Device_Config_Digital table
        if db_service.is_connected():
            # Save only digital section to its table
            db_service.save_config_sections_only(serial_number, config_with_digital_only)
            
            # Rebuild complete config from all tabs (new Digital + existing Analog/MODBUS/CAN Bus)
            analog_config_db = db_service.get_analog_config(serial_number)
            modbus_config_db = db_service.get_modbus_config(serial_number)
            can_bus_config_db = db_service.get_can_bus_config(serial_number)
            
            # Build complete config
            complete_config = {
                "device_id": serial_number
            }
            
            if analog_config_db:
                complete_config["analog"] = analog_config_db
            complete_config["digital"] = digital_config  # New Digital config
            if modbus_config_db:
                complete_config["rs485_modbus"] = modbus_config_db
            if can_bus_config_db:
                complete_config["can_bus"] = can_bus_config_db
            
            # Save complete config to Device_Config
            db_service.save_device_config(serial_number, complete_config)
            
            # Publish to MQTT
            try:
                from app.services.mqtt_client import MQTTClientService
                mqtt_service = MQTTClientService()
                if mqtt_service.is_connected():
                    mqtt_service.publish_config(serial_number, complete_config)
            except Exception as mqtt_error:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"MQTT publishing failed (non-critical): {mqtt_error}")
        
        # Also save to local JSON (for backup)
        success = config_service.save_device_config(serial_number, config_with_digital_only)
        
        if success or db_service.is_connected():
            success_msg = html.Div([
                html.Span("✅ ", className='text-success'),
                html.Strong("Saved! ", className='text-success'),
                f"Device: {serial_number} | Complete config updated & published to MQTT"
            ], className='text-success fw-bold')
            # Trigger config reload by updating the store timestamp
            # Add a small delay (0.5 seconds) to ensure database write is fully flushed
            import time
            current_time = time.time()
            reload_timestamp = {'timestamp': current_time + 0.5}  # Delay reload by 0.5s to ensure DB write completes
            logger.info(f"✅ Save completed for device {serial_number}, reload will trigger at {reload_timestamp['timestamp']}")
            return True, success_msg, reload_timestamp
        else:
            return True, html.Div([
                html.Strong("Error: "),
                f"❌ Error saving digital configuration for Serial Number: {serial_number}"
            ]), no_update
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error saving digital configuration: {e}")
        logger.exception("Full error traceback:")
        return True, html.Div([
            html.Strong("Error: "),
            f"❌ {str(e)}"
        ]), no_update


# Callback for save RS485 MODBUS configuration (inside RS485 MODBUS tab)
@callback(
    [
        Output('config-save-toast', 'is_open', allow_duplicate=True),
        Output('config-save-toast', 'children', allow_duplicate=True),
        Output('config-reload-trigger', 'data', allow_duplicate=True),
    ],
    Input('save-modbus-config-btn', 'n_clicks'),
    # RS485 MODBUS States
    State('modbus-baud-rate', 'value'),
    State('modbus-data-bits', 'value'),
    State('modbus-parity', 'value'),
    State('modbus-stop-bits', 'value'),
    State('modbus-mode', 'value'),
    State('modbus-role', 'value'),
    State('modbus-polling-interval', 'value'),
    State('modbus-devices-store', 'data'),
    # Device Selection (Serial Number)
    State('device-selector', 'value'),
    State('device-config-session-store', 'data'),
    prevent_initial_call=True
)
def save_modbus_configuration(
    n_clicks,
    modbus_baud_rate, modbus_data_bits, modbus_parity, modbus_stop_bits,
    modbus_mode, modbus_role, modbus_polling_interval, modbus_devices_store,
    serial_number,
    session_data
):
    """Save RS485 MODBUS configuration - saves only to Device_Config_MODBUS table"""
    if not n_clicks:
        return False, "", no_update
    
    import logging
    logger = logging.getLogger(__name__)
    
    # Get logged-in user info
    username = None
    is_admin = False
    if session_data:
        username = session_data.get('username', '')
        user_type = session_data.get('user_type', 'user')
        is_admin = (username == 'admin')
    
    try:
        from app.services.config_json_builder import ConfigJSONBuilder
        from app.services.device_config import DeviceConfigService
        from app.services.device_config_db import DeviceConfigDBService
        
        builder = ConfigJSONBuilder()
        config_service = DeviceConfigService()
        db_service = DeviceConfigDBService()
        
        # Validate Serial Number is selected
        if not serial_number:
            return True, html.Div([
                html.Strong("Validation Error: "),
                "Please select a device (Serial Number) from the dropdown."
            ]), no_update
        
        # Verify device ownership before saving (unless admin)
        if not is_admin and username and serial_number:
            from app.services.device_info_service import DeviceInfoService
            device_info_service = DeviceInfoService()
            device_info = device_info_service.get_device_info(serial_number)
            
            if device_info:
                device_owner = device_info.get('Owner', 'Unassigned')
                if device_owner != username:
                    logger.warning(f"⚠️ User {username} attempted to save config for device {serial_number} owned by {device_owner} - Access denied")
                    return True, html.Div([
                        html.Strong("Access Denied: "),
                        f"❌ You don't have permission to save configuration for device {serial_number}. This device is owned by {device_owner}."
                    ], className='text-danger'), no_update
            else:
                logger.warning(f"⚠️ Device {serial_number} not found in database")
                return True, html.Div([
                    html.Strong("Error: "),
                    f"❌ Device {serial_number} not found in database."
                ], className='text-danger'), no_update
        
        # Validate required fields
        if not modbus_baud_rate:
            return True, html.Div([
                html.Strong("Validation Error: "),
                "Please configure MODBUS communication settings."
            ])
        
        # Build RS485 MODBUS Config
        modbus_slave_devices = modbus_devices_store if modbus_devices_store else []
        modbus_config = builder.build_modbus_config(
            baud_rate=modbus_baud_rate,
            data_bits=modbus_data_bits or "8",
            parity=modbus_parity or "None",
            stop_bits=modbus_stop_bits or "1",
            mode=modbus_mode or "RTU",
            role=modbus_role or "Master",
            polling_interval=int(modbus_polling_interval) if modbus_polling_interval else 1000,
            slave_devices=modbus_slave_devices
        )
        
        # Build config with only MODBUS section
        config_with_modbus_only = {
            "device_id": serial_number,
            "rs485_modbus": modbus_config
        }
        
        # Save to database - Only Device_Config_MODBUS table
        if db_service.is_connected():
            # Save only MODBUS section to its table
            db_service.save_config_sections_only(serial_number, config_with_modbus_only)
            
            # Rebuild complete config from all tabs (new MODBUS + existing Analog/Digital/CAN Bus)
            analog_config_db = db_service.get_analog_config(serial_number)
            digital_config_db = db_service.get_digital_config(serial_number)
            can_bus_config_db = db_service.get_can_bus_config(serial_number)
            
            # Build complete config
            complete_config = {
                "device_id": serial_number
            }
            
            if analog_config_db:
                complete_config["analog"] = analog_config_db
            if digital_config_db:
                complete_config["digital"] = digital_config_db
            complete_config["rs485_modbus"] = modbus_config  # New MODBUS config
            if can_bus_config_db:
                complete_config["can_bus"] = can_bus_config_db
            
            # Save complete config to Device_Config
            db_service.save_device_config(serial_number, complete_config)
            
            # Publish to MQTT
            try:
                from app.services.mqtt_client import MQTTClientService
                mqtt_service = MQTTClientService()
                if mqtt_service.is_connected():
                    mqtt_service.publish_config(serial_number, complete_config)
            except Exception as mqtt_error:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"MQTT publishing failed (non-critical): {mqtt_error}")
        
        # Also save to local JSON (for backup)
        success = config_service.save_device_config(serial_number, config_with_modbus_only)
        
        if success or db_service.is_connected():
            success_msg = html.Div([
                html.Span("✅ ", className='text-success'),
                html.Strong("Saved! ", className='text-success'),
                f"Device: {serial_number} | Complete config updated & published to MQTT"
            ], className='text-success fw-bold')
            # Trigger config reload by updating the store timestamp
            # Add a small delay (0.5 seconds) to ensure database write is fully flushed
            import time
            current_time = time.time()
            reload_timestamp = {'timestamp': current_time + 0.5}  # Delay reload by 0.5s to ensure DB write completes
            logger.info(f"✅ Save completed for device {serial_number}, reload will trigger at {reload_timestamp['timestamp']}")
            return True, success_msg, reload_timestamp
        else:
            return True, html.Div([
                html.Strong("Error: "),
                f"❌ Error saving MODBUS configuration for Serial Number: {serial_number}"
            ]), no_update
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error saving MODBUS configuration: {e}")
        logger.exception("Full error traceback:")
        return True, html.Div([
            html.Strong("Error: "),
            f"❌ {str(e)}"
        ]), no_update


# Callback for save CAN Bus configuration (inside CAN Bus tab)
@callback(
    [
        Output('config-save-toast', 'is_open', allow_duplicate=True),
        Output('config-save-toast', 'children', allow_duplicate=True),
        Output('config-reload-trigger', 'data', allow_duplicate=True),
    ],
    Input('save-canbus-config-btn', 'n_clicks'),
    # CAN Bus States
    State('can-baud-rate', 'value'),
    State('can-identifier-length', 'value'),
    State('can-mode', 'value'),
    State('can-filter-mode', 'value'),
    State('can-filter-id', 'value'),
    State('can-filter-mask', 'value'),
    State('can-messages-store', 'data'),
    State('can-data-mapping-store', 'data'),
    # Device Selection (Serial Number)
    State('device-selector', 'value'),
    State('device-config-session-store', 'data'),
    prevent_initial_call=True
)
def save_canbus_configuration(
    n_clicks,
    can_baud_rate, can_identifier_length, can_mode, can_filter_mode,
    can_filter_id, can_filter_mask, can_messages_store, can_data_mapping_store,
    serial_number,
    session_data
):
    """Save CAN Bus configuration - saves only to Device_Config_CANBus table"""
    if not n_clicks:
        return False, "", no_update
    
    import logging
    logger = logging.getLogger(__name__)
    
    # Get logged-in user info
    username = None
    is_admin = False
    if session_data:
        username = session_data.get('username', '')
        user_type = session_data.get('user_type', 'user')
        is_admin = (username == 'admin')
    
    try:
        from app.services.config_json_builder import ConfigJSONBuilder
        from app.services.device_config import DeviceConfigService
        from app.services.device_config_db import DeviceConfigDBService
        
        builder = ConfigJSONBuilder()
        config_service = DeviceConfigService()
        db_service = DeviceConfigDBService()
        
        # Validate Serial Number is selected
        if not serial_number:
            return True, html.Div([
                html.Strong("Validation Error: "),
                "Please select a device (Serial Number) from the dropdown."
            ]), no_update
        
        # Verify device ownership before saving (unless admin)
        if not is_admin and username and serial_number:
            from app.services.device_info_service import DeviceInfoService
            device_info_service = DeviceInfoService()
            device_info = device_info_service.get_device_info(serial_number)
            
            if device_info:
                device_owner = device_info.get('Owner', 'Unassigned')
                if device_owner != username:
                    logger.warning(f"⚠️ User {username} attempted to save config for device {serial_number} owned by {device_owner} - Access denied")
                    return True, html.Div([
                        html.Strong("Access Denied: "),
                        f"❌ You don't have permission to save configuration for device {serial_number}. This device is owned by {device_owner}."
                    ], className='text-danger'), no_update
            else:
                logger.warning(f"⚠️ Device {serial_number} not found in database")
                return True, html.Div([
                    html.Strong("Error: "),
                    f"❌ Device {serial_number} not found in database."
                ], className='text-danger'), no_update
        
        # Validate required fields
        if not can_baud_rate:
            return True, html.Div([
                html.Strong("Validation Error: "),
                "Please configure CAN Bus communication settings."
            ])
        
        # Build CAN Bus Config
        can_messages = can_messages_store if can_messages_store else []
        can_data_mappings = can_data_mapping_store if can_data_mapping_store else []
        can_bus_config = builder.build_can_bus_config(
            baud_rate=can_baud_rate,
            identifier_length=can_identifier_length or "11-bit",
            can_mode=can_mode or "Normal",
            filter_mode=can_filter_mode or "None",
            filter_id=can_filter_id or "0x000",
            filter_mask=can_filter_mask or "0x000",
            can_messages=can_messages,
            data_mappings=can_data_mappings
        )
        
        # Build config with only CAN Bus section
        config_with_canbus_only = {
            "device_id": serial_number,
            "can_bus": can_bus_config
        }
        
        # Save to database - Only Device_Config_CANBus table
        if db_service.is_connected():
            # Save only CAN Bus section to its table
            db_service.save_config_sections_only(serial_number, config_with_canbus_only)
            
            # Rebuild complete config from all tabs (new CAN Bus + existing Analog/Digital/MODBUS)
            analog_config_db = db_service.get_analog_config(serial_number)
            digital_config_db = db_service.get_digital_config(serial_number)
            modbus_config_db = db_service.get_modbus_config(serial_number)
            
            # Build complete config
            complete_config = {
                "device_id": serial_number
            }
            
            if analog_config_db:
                complete_config["analog"] = analog_config_db
            if digital_config_db:
                complete_config["digital"] = digital_config_db
            if modbus_config_db:
                complete_config["rs485_modbus"] = modbus_config_db
            complete_config["can_bus"] = can_bus_config  # New CAN Bus config
            
            # Save complete config to Device_Config
            db_service.save_device_config(serial_number, complete_config)
            
            # Publish to MQTT
            try:
                from app.services.mqtt_client import MQTTClientService
                mqtt_service = MQTTClientService()
                if mqtt_service.is_connected():
                    mqtt_service.publish_config(serial_number, complete_config)
            except Exception as mqtt_error:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"MQTT publishing failed (non-critical): {mqtt_error}")
        
        # Also save to local JSON (for backup)
        success = config_service.save_device_config(serial_number, config_with_canbus_only)
        
        if success or db_service.is_connected():
            success_msg = html.Div([
                html.Span("✅ ", className='text-success'),
                html.Strong("Saved! ", className='text-success'),
                f"Device: {serial_number} | Complete config updated & published to MQTT"
            ], className='text-success fw-bold')
            # Trigger config reload by updating the store timestamp
            # Add a small delay (0.5 seconds) to ensure database write is fully flushed
            import time
            current_time = time.time()
            reload_timestamp = {'timestamp': current_time + 0.5}  # Delay reload by 0.5s to ensure DB write completes
            logger.info(f"✅ Save completed for device {serial_number}, reload will trigger at {reload_timestamp['timestamp']}")
            return True, success_msg, reload_timestamp
        else:
            return True, html.Div([
                html.Strong("Error: "),
                f"❌ Error saving CAN Bus configuration for Serial Number: {serial_number}"
            ]), no_update
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error saving CAN Bus configuration: {e}")
        logger.exception("Full error traceback:")
        return True, html.Div([
            html.Strong("Error: "),
            f"❌ {str(e)}"
        ]), no_update


# Callback for "Save All Configuration" button - saves to Device_Config table
@callback(
    [
        Output('save-all-status-message', 'children'),
        Output('save-all-btn-spinner', 'children'),
        Output('save-all-config-btn', 'disabled'),
        Output('config-save-toast', 'is_open', allow_duplicate=True),
        Output('config-save-toast', 'children', allow_duplicate=True),
        Output('config-reload-trigger', 'data', allow_duplicate=True),
    ],
    Input('save-all-config-btn', 'n_clicks'),
    # Analog Input States
    State({'type': 'analog-input-enable', 'index': ALL}, 'value'),
    State({'type': 'analog-input-div', 'index': ALL}, 'value'),
    State({'type': 'analog-input-mul', 'index': ALL}, 'value'),
    State({'type': 'analog-input-name', 'index': ALL}, 'value'),
    # Analog Output States
    State({'type': 'analog-output-enable', 'index': ALL}, 'value'),
    State({'type': 'analog-output-value', 'index': ALL}, 'value'),
    State({'type': 'analog-output-name', 'index': ALL}, 'value'),
    # Scan Rate States
    State('analog-scan-rate', 'value'),
    State('digital-scan-rate', 'value'),
    # Digital I/O States
    State({'type': 'npn-input-enable', 'index': ALL}, 'value'),
    State({'type': 'npn-input-name', 'index': ALL}, 'value'),
    State({'type': 'npn-output-enable', 'index': ALL}, 'value'),
    State({'type': 'npn-output-name', 'index': ALL}, 'value'),
    State({'type': 'pnp-input-enable', 'index': ALL}, 'value'),
    State({'type': 'pnp-input-name', 'index': ALL}, 'value'),
    State({'type': 'pnp-output-enable', 'index': ALL}, 'value'),
    State({'type': 'pnp-output-name', 'index': ALL}, 'value'),
    State({'type': 'relay-enable', 'index': ALL}, 'value'),
    State({'type': 'relay-name', 'index': ALL}, 'value'),
    # RS485 MODBUS States
    State('modbus-baud-rate', 'value'),
    State('modbus-data-bits', 'value'),
    State('modbus-parity', 'value'),
    State('modbus-stop-bits', 'value'),
    State('modbus-mode', 'value'),
    State('modbus-role', 'value'),
    State('modbus-polling-interval', 'value'),
    State('modbus-devices-store', 'data'),
    # CAN Bus States
    State('can-baud-rate', 'value'),
    State('can-identifier-length', 'value'),
    State('can-mode', 'value'),
    State('can-filter-mode', 'value'),
    State('can-filter-id', 'value'),
    State('can-filter-mask', 'value'),
    State('can-messages-store', 'data'),
    State('can-data-mapping-store', 'data'),
    # Device Selection (Serial Number)
    State('device-selector', 'value'),
    State('device-config-session-store', 'data'),
    prevent_initial_call=True
)
def save_all_configuration(
    n_clicks,
    # Analog inputs
    analog_input_enable, analog_input_div, analog_input_mul, analog_input_name,
    # Analog outputs
    analog_output_enable, analog_output_value, analog_output_name,
    # Scan rates
    analog_scan_rate, digital_scan_rate,
    # Digital I/O
    npn_input_enable, npn_input_name,
    npn_output_enable, npn_output_name,
    pnp_input_enable, pnp_input_name,
    pnp_output_enable, pnp_output_name,
    relay_enable, relay_name,
    # RS485 MODBUS
    modbus_baud_rate, modbus_data_bits, modbus_parity, modbus_stop_bits,
    modbus_mode, modbus_role, modbus_polling_interval, modbus_devices_store,
    # CAN Bus
    can_baud_rate, can_identifier_length, can_mode, can_filter_mode,
    can_filter_id, can_filter_mask, can_messages_store, can_data_mapping_store,
    # Device
    serial_number,
    session_data
):
    """Save all configurations (Analog, Digital, RS485 MODBUS, CAN Bus) to Device_Config table"""
    if not n_clicks:
        return "", html.I(className="fas fa-save me-2"), False, False, "", no_update
    
    import logging
    logger = logging.getLogger(__name__)
    
    # Get logged-in user info
    username = None
    is_admin = False
    if session_data:
        username = session_data.get('username', '')
        user_type = session_data.get('user_type', 'user')
        is_admin = (username == 'admin')
    
    try:
        from app.services.config_json_builder import ConfigJSONBuilder
        from app.services.device_config import DeviceConfigService
        from app.services.device_config_db import DeviceConfigDBService
        from app.services.mqtt_client import MQTTClientService
        
        builder = ConfigJSONBuilder()
        config_service = DeviceConfigService()
        db_service = DeviceConfigDBService()
        
        # Validate Serial Number is selected
        if not serial_number:
            error_msg = html.Div([
                html.Strong("Validation Error: "),
                "Please select a device (Serial Number) from the dropdown."
            ], className='text-danger')
            return error_msg, html.I(className="fas fa-save me-2"), False, no_update, no_update, True, no_update, True, True, error_msg, no_update
        
        # Verify device ownership before saving (unless admin)
        if not is_admin and username and serial_number:
            from app.services.device_info_service import DeviceInfoService
            device_info_service = DeviceInfoService()
            device_info = device_info_service.get_device_info(serial_number)
            
            if device_info:
                device_owner = device_info.get('Owner', 'Unassigned')
                if device_owner != username:
                    logger.warning(f"⚠️ User {username} attempted to save config for device {serial_number} owned by {device_owner} - Access denied")
                    error_msg = html.Div([
                        html.Strong("Access Denied: "),
                        f"❌ You don't have permission to save configuration for device {serial_number}. This device is owned by {device_owner}."
                    ], className='text-danger')
                    return error_msg, html.I(className="fas fa-save me-2"), False, False, "", no_update
            else:
                logger.warning(f"⚠️ Device {serial_number} not found in database")
                error_msg = html.Div([
                    html.Strong("Error: "),
                    f"❌ Device {serial_number} not found in database."
                ], className='text-danger')
                return error_msg, html.I(className="fas fa-save me-2"), False, False, "", no_update
        
        # Validate Scan Rates
        if analog_scan_rate is None or analog_scan_rate < 1000:
            error_msg = html.Div([
                html.Strong("Validation Error: "),
                "Analog Scan Rate must be at least 1000 seconds."
            ], className='text-danger')
            return error_msg, html.I(className="fas fa-save me-2"), False, True, error_msg, no_update
        
        if digital_scan_rate is None or digital_scan_rate < 1000:
            error_msg = html.Div([
                html.Strong("Validation Error: "),
                "Digital Scan Rate must be at least 1000 seconds."
            ], className='text-danger')
            return error_msg, html.I(className="fas fa-save me-2"), False, True, error_msg, no_update
        
        # Get device info for device name
        from app.services.device_info_service import DeviceInfoService
        device_info_service = DeviceInfoService()
        device_info = device_info_service.get_device_info(serial_number)
        device_name = device_info.get('Device_Name', serial_number) if device_info else serial_number
        
        # IO Pin mappings
        analog_io_pins = {1: "AIN0", 2: "AIN1", 3: "AIN2", 4: "AIN3"}
        digital_io_pins = {
            'npn_input': {1: "INP1H", 2: "INP2H", 3: "INP3H", 4: "INP4H"},
            'npn_output': {1: "OUTL1", 2: "OUTL2", 3: "OUTL3", 4: "OUTL4"},
            'pnp_input': {1: "INP1L", 2: "INP2L", 3: "INP3L", 4: "INP4L"},
            'pnp_output': {1: "OUTH1", 2: "OUTH2", 3: "OUTH3", 4: "OUTH4"},
            'relay': {1: "RLY1", 2: "RLY2", 3: "RLY3", 4: "RLY4"}
        }
        
        # Build Analog Config
        input_4_20ma_data = []
        for idx in range(2):
            channel = idx + 1
            io_pin = analog_io_pins[channel]
            div = analog_input_div[idx] if idx < len(analog_input_div) and analog_input_div[idx] is not None else 1
            mul = analog_input_mul[idx] if idx < len(analog_input_mul) and analog_input_mul[idx] is not None else 1
            name = analog_input_name[idx] if idx < len(analog_input_name) and analog_input_name[idx] else io_pin
            if not name or name.strip() == '':
                name = io_pin
            
            input_4_20ma_data.append({
                "channel": channel,
                "enabled": analog_input_enable[idx] if idx < len(analog_input_enable) else False,
                "divider": div,
                "multiplier": mul,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        input_1_10v_data = []
        for idx in range(2):
            channel = idx + 3
            io_pin = analog_io_pins[channel]
            div = analog_input_div[idx + 2] if idx + 2 < len(analog_input_div) and analog_input_div[idx + 2] is not None else 1
            mul = analog_input_mul[idx + 2] if idx + 2 < len(analog_input_mul) and analog_input_mul[idx + 2] is not None else 1
            name = analog_input_name[idx + 2] if idx + 2 < len(analog_input_name) and analog_input_name[idx + 2] else io_pin
            if not name or name.strip() == '':
                name = io_pin
            
            input_1_10v_data.append({
                "channel": channel,
                "enabled": analog_input_enable[idx + 2] if idx + 2 < len(analog_input_enable) else False,
                "divider": div,
                "multiplier": mul,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        output_0_10v_data = []
        for idx in range(2):
            channel = idx + 1
            io_pin = f"DOUT{idx}"
            value = analog_output_value[idx] if idx < len(analog_output_value) and analog_output_value[idx] is not None else 0.0
            name = analog_output_name[idx] if idx < len(analog_output_name) and analog_output_name[idx] else io_pin
            if not name or name.strip() == '':
                name = io_pin
            
            output_0_10v_data.append({
                "channel": channel,
                "enabled": analog_output_enable[idx] if idx < len(analog_output_enable) else False,
                "value": value,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        analog_config = builder.build_analog_config(
            input_4_20ma_data,
            input_1_10v_data,
            output_0_10v_data,
            scan_rate=analog_scan_rate
        )
        
        # Build Digital Config
        npn_input_data = []
        for idx in range(4):
            channel = idx + 1
            io_pin = digital_io_pins['npn_input'][channel]
            name = npn_input_name[idx] if idx < len(npn_input_name) and npn_input_name[idx] else io_pin
            if not name or name.strip() == '':
                name = io_pin
            
            npn_input_data.append({
                "channel": channel,
                "enabled": npn_input_enable[idx] if idx < len(npn_input_enable) else False,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        npn_output_data = []
        for idx in range(4):
            channel = idx + 1
            io_pin = digital_io_pins['npn_output'][channel]
            name = npn_output_name[idx] if idx < len(npn_output_name) and npn_output_name[idx] else io_pin
            if not name or name.strip() == '':
                name = io_pin
            
            npn_output_data.append({
                "channel": channel,
                "enabled": npn_output_enable[idx] if idx < len(npn_output_enable) else False,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        pnp_input_data = []
        for idx in range(4):
            channel = idx + 1
            io_pin = digital_io_pins['pnp_input'][channel]
            name = pnp_input_name[idx] if idx < len(pnp_input_name) and pnp_input_name[idx] else io_pin
            if not name or name.strip() == '':
                name = io_pin
            
            pnp_input_data.append({
                "channel": channel,
                "enabled": pnp_input_enable[idx] if idx < len(pnp_input_enable) else False,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        pnp_output_data = []
        for idx in range(4):
            channel = idx + 1
            io_pin = digital_io_pins['pnp_output'][channel]
            name = pnp_output_name[idx] if idx < len(pnp_output_name) and pnp_output_name[idx] else io_pin
            if not name or name.strip() == '':
                name = io_pin
            
            pnp_output_data.append({
                "channel": channel,
                "enabled": pnp_output_enable[idx] if idx < len(pnp_output_enable) else False,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        relay_data = []
        for idx in range(4):
            channel = idx + 1
            io_pin = digital_io_pins['relay'][channel]
            name = relay_name[idx] if idx < len(relay_name) and relay_name[idx] else io_pin
            if not name or name.strip() == '':
                name = io_pin
            
            relay_data.append({
                "channel": channel,
                "enabled": relay_enable[idx] if idx < len(relay_enable) else False,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        digital_config = builder.build_digital_config(
            npn_input_data,
            npn_output_data,
            pnp_input_data,
            pnp_output_data,
            relay_data
        )
        digital_config["scan_rate"] = digital_scan_rate
        
        # Build RS485 MODBUS Config
        modbus_config = None
        if modbus_baud_rate and modbus_polling_interval:
            modbus_slave_devices = modbus_devices_store if modbus_devices_store else []
            modbus_config = builder.build_modbus_config(
                baud_rate=modbus_baud_rate,
                data_bits=modbus_data_bits or "8",
                parity=modbus_parity or "None",
                stop_bits=modbus_stop_bits or "1",
                mode=modbus_mode or "RTU",
                role=modbus_role or "Master",
                polling_interval=int(modbus_polling_interval) if modbus_polling_interval else 1000,
                slave_devices=modbus_slave_devices
            )
        
        # Build CAN Bus Config
        can_bus_config = None
        if can_baud_rate:
            can_messages = can_messages_store if can_messages_store else []
            can_data_mappings = can_data_mapping_store if can_data_mapping_store else []
            can_bus_config = builder.build_can_bus_config(
                baud_rate=can_baud_rate,
                identifier_length=can_identifier_length or "11-bit",
                can_mode=can_mode or "Normal",
                filter_mode=can_filter_mode or "None",
                filter_id=can_filter_id or "0x000",
                filter_mask=can_filter_mask or "0x000",
                can_messages=can_messages,
                data_mappings=can_data_mappings
            )
        
        # Build complete config (without mqtt and network sections, as per documentation)
        complete_config = builder.build_complete_config(
            device_id=serial_number,
            device_name=device_name,
            analog_config=analog_config,
            digital_config=digital_config,
            modbus_config=modbus_config,
            can_bus_config=can_bus_config,
            mqtt_config=None,  # Not included
            network_config=None  # Not included
        )
        
        # Remove mqtt and network from config (as per documentation requirements)
        complete_config.pop('mqtt', None)
        complete_config.pop('network', None)
        
        # Also remove metadata wrapper - move fields to top level (as per documentation)
        if 'metadata' in complete_config:
            metadata = complete_config.pop('metadata')
            # We only keep device_id at top level (no device_name, created_at, updated_at)
            # These were already in metadata, so we just remove it
        
        # Save to local JSON file
        success = config_service.save_device_config(serial_number, complete_config)
        
        # Save to database - this will save to Device_Config AND individual tables
        if db_service.is_connected():
            db_service.save_device_config(serial_number, complete_config)
        
        # Publish to MQTT (if MQTT service is available)
        try:
            mqtt_service = MQTTClientService()
            if mqtt_service.is_connected():
                mqtt_service.publish_config(serial_number, complete_config)
        except Exception as mqtt_error:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"MQTT publishing failed (non-critical): {mqtt_error}")
        
        if success:
            success_msg = html.Div([
                html.Span("✅ ", className='text-success'),
                html.Strong("All configurations saved! ", className='text-success'),
                f"Device: {serial_number} | Published to MQTT"
            ], className='text-success fw-bold')
            # Trigger config reload by updating the store timestamp
            import time
            # Trigger config reload by updating the store timestamp
            # Add a small delay (0.5 seconds) to ensure database write is fully flushed
            import time
            import logging
            logger = logging.getLogger(__name__)
            current_time = time.time()
            reload_timestamp = {'timestamp': current_time + 0.5}  # Delay reload by 0.5s to ensure DB write completes
            logger.info(f"✅ Save completed for device {serial_number}, reload will trigger at {reload_timestamp['timestamp']}")
            return success_msg, html.I(className="fas fa-save me-2"), False, True, success_msg, reload_timestamp
        else:
            error_msg = html.Div([
                html.Strong("Error: "),
                f"❌ Error saving all configurations for Serial Number: {serial_number}"
            ], className='text-danger')
            return error_msg, html.I(className="fas fa-save me-2"), False, True, error_msg, no_update
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error saving all configurations: {e}")
        logger.exception("Full error traceback:")
        error_msg = html.Div([
            html.Strong("Error: "),
            f"❌ {str(e)}"
        ], className='text-danger')
        return error_msg, html.I(className="fas fa-save me-2"), False, True, error_msg, no_update

