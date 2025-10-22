"""
Device Configuration Page
Configure Analog, Digital, and Communication settings for IoT devices
"""
from dash import html, dcc, Input, Output, State, ALL, callback
import dash_bootstrap_components as dbc


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
                        options=[
                            {'label': '🔌 ESP32-Gateway-01 (192.168.1.100)', 'value': 'esp32_gw_01'},
                            {'label': '🔌 ESP32-Gateway-02 (192.168.1.101)', 'value': 'esp32_gw_02'},
                            {'label': '🔌 ESP32-Gateway-03 (192.168.1.102)', 'value': 'esp32_gw_03'},
                        ],
                        value='esp32_gw_01',
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
                
                # Communication Tab
                dbc.Tab(
                    create_communication_config_tab(),
                    label="📡 Communication",
                    tab_id='tab-communication',
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
            header="Configuration Saved",
            icon="success",
            duration=4000,
            is_open=False,
            dismissable=True,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 9999},
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
        
        # 1-10V Input Section
        html.H5([
            html.I(className="fas fa-plug me-2", style={'color': '#667eea'}),
            "1 to 10V Input"
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
        ], className='config-table'),
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
                style={'width': '100px'}
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
                style={'width': '100px'}
            )
        ),
        html.Td(
            html.Code(io_pin, className='badge bg-secondary')
        ),
        html.Td(
            dbc.Input(
                id={'type': 'analog-input-name', 'index': channel},
                type='text',
                placeholder='Enter name...',
                value='-',
                size='sm'
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
                style={'width': '100px'}
            )
        ),
        html.Td(
            html.Code(io_pin, className='badge bg-secondary')
        ),
        html.Td(
            dbc.Input(
                id={'type': 'analog-output-name', 'index': channel},
                type='text',
                placeholder='Enter name...',
                value='-',
                size='sm'
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
        ], className='config-table'),
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


def create_communication_config_tab():
    """Create communication configuration tab content"""
    
    return html.Div([
        dbc.Row([
            # Network Settings
            dbc.Col([
                html.Div([
                    html.H5([
                        html.I(className="fas fa-wifi me-2", style={'color': '#667eea'}),
                        "Network Settings"
                    ], className='fw-bold mb-3'),
                    
                    dbc.Form([
                        dbc.Row([
                            dbc.Label("WiFi SSID", md=4, className='fw-bold'),
                            dbc.Col([
                                dbc.Input(
                                    id='wifi-ssid',
                                    type='text',
                                    placeholder='Enter WiFi SSID',
                                    value=''
                                ),
                            ], md=8),
                        ], className='mb-3'),
                        
                        dbc.Row([
                            dbc.Label("WiFi Password", md=4, className='fw-bold'),
                            dbc.Col([
                                dbc.Input(
                                    id='wifi-password',
                                    type='password',
                                    placeholder='Enter password',
                                    value=''
                                ),
                            ], md=8),
                        ], className='mb-3'),
                        
                        dbc.Row([
                            dbc.Label("IP Mode", md=4, className='fw-bold'),
                            dbc.Col([
                                dcc.Dropdown(
                                    id='ip-mode',
                                    options=[
                                        {'label': 'DHCP (Automatic)', 'value': 'dhcp'},
                                        {'label': 'Static IP', 'value': 'static'},
                                    ],
                                    value='dhcp'
                                ),
                            ], md=8),
                        ], className='mb-3'),
                        
                        dbc.Row([
                            dbc.Label("Static IP", md=4, className='fw-bold'),
                            dbc.Col([
                                dbc.Input(
                                    id='static-ip',
                                    type='text',
                                    placeholder='192.168.1.100',
                                    disabled=True
                                ),
                            ], md=8),
                        ], className='mb-3'),
                    ]),
                ], className='stat-card p-4'),
            ], md=6),
            
            # MQTT Settings
            dbc.Col([
                html.Div([
                    html.H5([
                        html.I(className="fas fa-exchange-alt me-2", style={'color': '#667eea'}),
                        "MQTT Settings"
                    ], className='fw-bold mb-3'),
                    
                    dbc.Form([
                        dbc.Row([
                            dbc.Label("MQTT Broker", md=4, className='fw-bold'),
                            dbc.Col([
                                dbc.Input(
                                    id='mqtt-broker',
                                    type='text',
                                    placeholder='mqtt.example.com',
                                    value='mqtt'
                                ),
                            ], md=8),
                        ], className='mb-3'),
                        
                        dbc.Row([
                            dbc.Label("MQTT Port", md=4, className='fw-bold'),
                            dbc.Col([
                                dbc.Input(
                                    id='mqtt-port',
                                    type='number',
                                    value=1883
                                ),
                            ], md=8),
                        ], className='mb-3'),
                        
                        dbc.Row([
                            dbc.Label("Device Topic", md=4, className='fw-bold'),
                            dbc.Col([
                                dbc.Input(
                                    id='mqtt-topic',
                                    type='text',
                                    placeholder='iotnarad/devices/esp32_01',
                                    value=''
                                ),
                            ], md=8),
                        ], className='mb-3'),
                        
                        dbc.Row([
                            dbc.Label("Publish Interval", md=4, className='fw-bold'),
                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.Input(
                                        id='publish-interval',
                                        type='number',
                                        value=5,
                                        min=1
                                    ),
                                    dbc.InputGroupText("seconds"),
                                ]),
                            ], md=8),
                        ], className='mb-3'),
                    ]),
                ], className='stat-card p-4'),
            ], md=6),
        ], className='mb-4'),
        
        dbc.Row([
            # Modbus Settings
            dbc.Col([
                html.Div([
                    html.H5([
                        html.I(className="fas fa-network-wired me-2", style={'color': '#667eea'}),
                        "Modbus RTU Settings"
                    ], className='fw-bold mb-3'),
                    
                    dbc.Form([
                        dbc.Row([
                            dbc.Label("Enable Modbus", md=4, className='fw-bold'),
                            dbc.Col([
                                dbc.Switch(
                                    id='modbus-enable',
                                    value=False,
                                    className='mt-1'
                                ),
                            ], md=8),
                        ], className='mb-3'),
                        
                        dbc.Row([
                            dbc.Label("Baud Rate", md=4, className='fw-bold'),
                            dbc.Col([
                                dcc.Dropdown(
                                    id='modbus-baudrate',
                                    options=[
                                        {'label': '9600', 'value': 9600},
                                        {'label': '19200', 'value': 19200},
                                        {'label': '38400', 'value': 38400},
                                        {'label': '115200', 'value': 115200},
                                    ],
                                    value=9600
                                ),
                            ], md=8),
                        ], className='mb-3'),
                        
                        dbc.Row([
                            dbc.Label("Slave Address", md=4, className='fw-bold'),
                            dbc.Col([
                                dbc.Input(
                                    id='modbus-slave-addr',
                                    type='number',
                                    value=1,
                                    min=1,
                                    max=247
                                ),
                            ], md=8),
                        ], className='mb-3'),
                    ]),
                ], className='stat-card p-4'),
            ], md=6),
            
            # CAN Bus Settings
            dbc.Col([
                html.Div([
                    html.H5([
                        html.I(className="fas fa-bus me-2", style={'color': '#667eea'}),
                        "CAN Bus Settings"
                    ], className='fw-bold mb-3'),
                    
                    dbc.Form([
                        dbc.Row([
                            dbc.Label("Enable CAN Bus", md=4, className='fw-bold'),
                            dbc.Col([
                                dbc.Switch(
                                    id='canbus-enable',
                                    value=False,
                                    className='mt-1'
                                ),
                            ], md=8),
                        ], className='mb-3'),
                        
                        dbc.Row([
                            dbc.Label("CAN Speed", md=4, className='fw-bold'),
                            dbc.Col([
                                dcc.Dropdown(
                                    id='canbus-speed',
                                    options=[
                                        {'label': '125 Kbps', 'value': 125},
                                        {'label': '250 Kbps', 'value': 250},
                                        {'label': '500 Kbps', 'value': 500},
                                        {'label': '1 Mbps', 'value': 1000},
                                    ],
                                    value=500
                                ),
                            ], md=8),
                        ], className='mb-3'),
                        
                        dbc.Row([
                            dbc.Label("CAN ID Filter", md=4, className='fw-bold'),
                            dbc.Col([
                                dbc.Input(
                                    id='canbus-filter',
                                    type='text',
                                    placeholder='0x100-0x200',
                                    value=''
                                ),
                            ], md=8),
                        ], className='mb-3'),
                    ]),
                ], className='stat-card p-4'),
            ], md=6),
        ]),
    ])


# Callback for save configuration
@callback(
    Output('config-save-toast', 'is_open'),
    Input('save-config-btn', 'n_clicks'),
    prevent_initial_call=True
)
def save_configuration(n_clicks):
    """Save device configuration"""
    if n_clicks:
        # Here you would collect all the form values and save them
        # For now, just show success message
        return True
    return False

