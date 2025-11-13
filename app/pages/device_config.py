"""
Device Configuration Page
Configure Analog, Digital, and Communication settings for IoT devices
"""
from dash import html, dcc, Input, Output, State, ALL, callback, ctx
import dash_bootstrap_components as dbc
import time

# Module-level cache for device list (refreshes every 30 seconds)
_device_list_cache = None
_cache_timestamp = 0
_cache_ttl = 30  # Cache for 30 seconds


def create_device_config_layout():
    """Create device configuration page with tabs"""
    
    return html.Div([
        # Device Selection
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Label("Select Device", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='device-selector',
                        options=[],
                        value=None,
                        placeholder='Loading devices...',
                        className='mb-3',
                        style={'borderRadius': '8px'}
                    ),
                ], className='stat-card p-3'),
            ], md=6),
            
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Span("Device Status: ", className='fw-bold'),
                        html.Span([
                            html.I(className="fas fa-circle me-2",
                                   style={'color': '#4ade80', 'fontSize': '0.7rem'}),
                            "Online"
                        ], id='device-status-badge',
                           className='badge bg-light text-success ms-2 px-3 py-2'),
                    ], className='mb-2'),
                    html.Small("Last seen: 2 seconds ago", 
                              id='device-last-seen',
                              className='text-muted'),
                ], className='stat-card p-3'),
            ], md=6),
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
        
        # Action Buttons
        html.Div([
            dbc.Button([
                html.I(className="fas fa-save me-2"),
                "Save Configuration"
            ], id='save-config-btn', color='primary', size='lg', className='me-2'),
            
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


# Callback to load device list (Serial Numbers) from Device_info on page load
# Uses multiple triggers to ensure it runs immediately when the page loads
@callback(
    Output('device-selector', 'options'),
    Output('device-selector', 'value'),
    Input('url', 'pathname'),
    Input('device-selector', 'id'),
    prevent_initial_call=False
)
def load_device_list(pathname, _):
    """Load Serial Numbers from Device_info measurement (optimized - single query with caching)"""
    global _device_list_cache, _cache_timestamp
    
    try:
        # Only run if we're on a devices-related page (or if triggered by device-selector)
        if pathname and '/devices' not in pathname and ctx.triggered_id == 'url':
            # Not on devices page, don't load
            if _device_list_cache:
                return _device_list_cache
            return [], None
        
        # Check cache first - return immediately if available and fresh
        current_time = time.time()
        if _device_list_cache and (current_time - _cache_timestamp) < _cache_ttl:
            # Return cached data immediately (no database query needed)
            return _device_list_cache
        
        # Cache expired or not available, fetch from database
        from app.services.device_info_service import DeviceInfoService
        device_info_service = DeviceInfoService()
        
        if not device_info_service.is_connected():
            error_options = (
                [{'label': '⚠️ Database not connected', 'value': None, 'disabled': True}], 
                None
            )
            _device_list_cache = error_options
            _cache_timestamp = current_time
            return error_options
        
        # Get all devices with their info in a single optimized query
        all_devices_info = device_info_service.get_all_devices_info()
        
        if not all_devices_info:
            no_devices_options = (
                [{'label': '⚠️ No devices found', 'value': None, 'disabled': True}], 
                None
            )
            _device_list_cache = no_devices_options
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
        
        # Set default value to first device
        default_value = all_devices_info[0].get('Sr_No') if all_devices_info else None
        
        # Cache the results
        result = (options, default_value)
        _device_list_cache = result
        _cache_timestamp = current_time
        
        return result
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error loading device list: {e}")
        logger.exception("Full error traceback:")
        error_result = (
            [{'label': '⚠️ Error loading devices', 'value': None, 'disabled': True}], 
            None
        )
        # Don't cache errors
        return error_result


# Callback for save configuration
@callback(
    Output('config-save-toast', 'is_open'),
    Output('config-save-toast', 'children'),
    Input('save-config-btn', 'n_clicks'),
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
    # Device Selection (Serial Number)
    State('device-selector', 'value'),
    prevent_initial_call=True
)
def save_configuration(
    n_clicks,
    analog_input_enable, analog_input_div, analog_input_mul, analog_input_name,
    analog_output_enable, analog_output_value, analog_output_name,
    analog_scan_rate, digital_scan_rate,
    serial_number
):
    """Save device configuration with validation"""
    if not n_clicks:
        return False, ""
    
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
            ])
        
        # Validate Scan Rates
        if analog_scan_rate is None or analog_scan_rate < 1000:
            return True, html.Div([
                html.Strong("Validation Error: "),
                "Analog Scan Rate must be at least 1000 seconds."
            ])
        
        if digital_scan_rate is None or digital_scan_rate < 1000:
            return True, html.Div([
                html.Strong("Validation Error: "),
                "Digital Scan Rate must be at least 1000 seconds."
            ])
        
        # Get device info for device name
        from app.services.device_info_service import DeviceInfoService
        device_info_service = DeviceInfoService()
        device_info = device_info_service.get_device_info(serial_number)
        device_name = device_info.get('Device_Name', serial_number) if device_info else serial_number
        
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
                return True, html.Div([
                    html.Strong("Validation Error: "),
                    f"Please fill all parameters for Channel {channel} (4-20mA): Divider, Multiplier, and Name/Label are required."
                ])
            
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
                return True, html.Div([
                    html.Strong("Validation Error: "),
                    f"Please fill all parameters for Channel {channel} (0-10V): Divider, Multiplier, and Name/Label are required."
                ])
            
            input_1_10v_data.append({
                "channel": channel,
                "enabled": analog_input_enable[idx + 2] if idx + 2 < len(analog_input_enable) else False,
                "divider": div,
                "multiplier": mul,
                "io_pin": io_pin,
                "name": name.strip()
            })
        
        # 0-10V Output
        output_0_10v_data = []
        for idx in range(2):
            channel = idx + 1
            io_pin = f"DOUT{idx}"
            value = analog_output_value[idx] if idx < len(analog_output_value) and analog_output_value[idx] is not None else None
            name = analog_output_name[idx] if idx < len(analog_output_name) and analog_output_name[idx] else None
            
            # Set default name to IO pin if empty (before validation)
            if not name or name.strip() == '':
                name = io_pin
            
            # Validation: All parameters must be filled
            if value is None or not name or name.strip() == '':
                return True, html.Div([
                    html.Strong("Validation Error: "),
                    f"Please fill all parameters for Output Channel {channel}: Value and Name/Label are required."
                ])
            
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
        
        # Build digital config (for now empty, but include scan_rate)
        digital_config = {
            "npn_input": [],
            "npn_output": [],
            "pnp_input": [],
            "pnp_output": [],
            "relay": [],
            "scan_rate": digital_scan_rate
        }
        
        # Build complete config
        complete_config = builder.build_complete_config(
            device_id=serial_number,
            device_name=device_name,
            analog_config=analog_config,
            digital_config=digital_config
        )
        
        # Save Configuration (using Serial Number)
        success = config_service.save_device_config(serial_number, complete_config)
        
        # Also save to database (using Serial Number)
        if db_service.is_connected():
            db_service.save_device_config(serial_number, complete_config)
        
        if success:
            return True, html.Div([
                html.Strong("Success: "),
                f"✅ Configuration saved successfully for Serial Number: {serial_number}"
            ])
        else:
            return True, html.Div([
                html.Strong("Error: "),
                f"❌ Error saving configuration for Serial Number: {serial_number}"
            ])
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error saving configuration: {e}")
        logger.exception("Full error traceback:")
        return True, html.Div([
            html.Strong("Error: "),
            f"❌ {str(e)}"
        ])

