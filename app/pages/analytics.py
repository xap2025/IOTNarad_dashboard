"""
Analytics Page Layout
Real-time data visualization and insights
"""
from dash import html, dcc, Input, Output, State, callback, ALL, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def create_analytics_layout():
    """Create analytics page with real-time charts"""
    
    return html.Div([
        # Hidden stores
        dcc.Store(id='analytics-device-store', data=None),
        dcc.Store(id='analytics-params-store', data={}),
        dcc.Store(id='analytics-latest-values-store', data={}),
        
        # Device Selection and Time Range
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Label("Select Device", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='analytics-device-selector',
                        options=[],
                        value=None,
                        placeholder='Select a device...',
                        className='mb-3',
                        style={'borderRadius': '8px', 'minWidth': '300px', 'width': '100%'}
                    ),
                ], className='stat-card p-3'),
            ], md=6),
            
            dbc.Col([
                html.Div([
                    html.Label("Time Range", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='analytics-time-range-selector',
                        options=[
                            {'label': '⏱️ Last 1 Hour', 'value': '1h'},
                            {'label': '⏱️ Last 6 Hours', 'value': '6h'},
                            {'label': '⏱️ Last 24 Hours', 'value': '24h'},
                            {'label': '⏱️ Last 7 Days', 'value': '7d'},
                            {'label': '⏱️ Last 30 Days', 'value': '30d'},
                            {'label': '⏱️ Last 6 Months', 'value': '6m'},
                            {'label': '⏱️ Last 1 Year', 'value': '1y'},
                        ],
                        value='1h',
                        className='mb-3',
                        style={'borderRadius': '8px', 'width': '100%'}
                    ),
                ], className='stat-card p-3'),
            ], md=6),
        ], className='mb-4'),
        
        # Dynamic Charts Container
        html.Div(id='analytics-charts-container', children=[]),
        
        # Auto-refresh interval (5 seconds)
        dcc.Interval(id='analytics-refresh-interval', interval=5000, n_intervals=0),
    ])


def create_parameter_chart(parameter_name: str, data_type: str, chart_id: str):
    """Create a chart card for a parameter"""
    
    # Determine icon and color based on data type
    icon_map = {
        'Analog': ('fas fa-bolt', '#8b5cf6'),
        'Digital': ('fas fa-toggle-on', '#10b981'),
        'Modbus': ('fas fa-network-wired', '#3b82f6'),
        'Canbus': ('fas fa-bus', '#f59e0b'),
    }
    
    icon_class, color = icon_map.get(data_type, ('fas fa-chart-line', '#667eea'))
    
    return dbc.Col([
        html.Div([
            html.Div([
                html.H6([
                    html.I(className=f"{icon_class} me-2", style={'color': color}),
                    parameter_name
                ], className='fw-bold mb-2'),
                # Live value display
                html.Div([
                    html.Span("Current: ", className='text-muted small'),
                    html.Span(id={'type': 'live-value', 'parameter': parameter_name}, 
                             children="--", 
                             className='fw-bold fs-5',
                             style={'color': color})
                ], className='mb-2'),
            ], className='d-flex justify-content-between align-items-center'),
            
            dcc.Graph(
                id={'type': 'analytics-chart', 'parameter': parameter_name},
                config={'displayModeBar': False},
                style={'height': '250px'}
            ),
        ], className='stat-card p-3'),
    ], md=4, className='mb-4')


# Callback to load device list
@callback(
    [
        Output('analytics-device-selector', 'options'),
        Output('analytics-device-selector', 'value'),
    ],
    [
        Input('url', 'pathname'),
    ],
    prevent_initial_call=False
)
def load_analytics_device_list(pathname):
    """Load device list for analytics page"""
    try:
        from app.services.device_info_service import DeviceInfoService
        
        device_info_service = DeviceInfoService()
        
        if not device_info_service.is_connected():
            logger.error("❌ Device Info Service not connected")
            return (
                [{'label': '⚠️ Database not connected', 'value': None, 'disabled': True}],
                None
            )
        
        # Get all devices
        all_devices = device_info_service.get_all_devices_info(owner_filter=None, is_admin=True)
        
        if not all_devices:
            return (
                [{'label': 'No devices found', 'value': None, 'disabled': True}],
                None
            )
        
        # Create options
        options = [
            {
                'label': f"{device.get('Sr_No')} - {device.get('Device_Name', 'Unnamed')}",
                'value': device.get('Sr_No')
            }
            for device in all_devices
        ]
        
        # Set default to first device if available
        default_value = options[0]['value'] if options else None
        
        logger.info(f"✅ Loaded {len(options)} devices for analytics")
        return options, default_value
        
    except Exception as e:
        logger.error(f"❌ Error loading device list: {e}")
        logger.exception("Full error traceback:")
        return (
            [{'label': f'⚠️ Error: {str(e)}', 'value': None, 'disabled': True}],
            None
        )


# Callback to load enabled parameters from device config
@callback(
    [
        Output('analytics-device-store', 'data'),
        Output('analytics-params-store', 'data'),
        Output('analytics-charts-container', 'children'),
    ],
    [
        Input('analytics-device-selector', 'value'),
    ],
    prevent_initial_call=True
)
def load_enabled_parameters(device_id):
    """Load enabled parameters from device configuration"""
    if not device_id:
        return None, {}, []
    
    try:
        from app.services.device_config_db import DeviceConfigDBService
        
        db_service = DeviceConfigDBService()
        
        # Get all config types
        analog_config = db_service.get_analog_config(device_id)
        digital_config = db_service.get_digital_config(device_id)
        modbus_config = db_service.get_modbus_config(device_id)
        can_bus_config = db_service.get_can_bus_config(device_id)
        
        # Collect enabled parameters
        enabled_params = {}
        
        # Analog parameters
        if analog_config:
            # 4-20mA inputs
            for channel in analog_config.get('input_4_20ma', []):
                if channel.get('enabled', False):
                    name = channel.get('name', f"Channel {channel.get('channel', '?')}")
                    enabled_params[name] = 'Analog'
            
            # 0-10V inputs
            for channel in analog_config.get('input_0_10v', []):
                if channel.get('enabled', False):
                    name = channel.get('name', f"Channel {channel.get('channel', '?')}")
                    enabled_params[name] = 'Analog'
        
        # Digital parameters
        if digital_config:
            # NPN inputs
            for channel in digital_config.get('npn_input', []):
                if channel.get('enabled', False):
                    name = channel.get('name', f"NPN_IN_{channel.get('channel', '?')}")
                    enabled_params[name] = 'Digital'
            
            # NPN outputs
            for channel in digital_config.get('npn_output', []):
                if channel.get('enabled', False):
                    name = channel.get('name', f"NPN_OUT_{channel.get('channel', '?')}")
                    enabled_params[name] = 'Digital'
            
            # PNP inputs
            for channel in digital_config.get('pnp_input', []):
                if channel.get('enabled', False):
                    name = channel.get('name', f"PNP_IN_{channel.get('channel', '?')}")
                    enabled_params[name] = 'Digital'
            
            # PNP outputs
            for channel in digital_config.get('pnp_output', []):
                if channel.get('enabled', False):
                    name = channel.get('name', f"PNP_OUT_{channel.get('channel', '?')}")
                    enabled_params[name] = 'Digital'
            
            # Relays
            for relay in digital_config.get('relay', []):
                if relay.get('enabled', False):
                    name = relay.get('name', f"Relay {relay.get('channel', '?')}")
                    enabled_params[name] = 'Digital'
        
        # Modbus parameters
        if modbus_config:
            slave_devices = modbus_config.get('slave_devices', [])
            for slave in slave_devices:
                var_name = slave.get('variable_name', '')
                if var_name:
                    enabled_params[var_name] = 'Modbus'
        
        # CAN Bus parameters
        if can_bus_config:
            can_messages = can_bus_config.get('can_messages', [])
            for msg in can_messages:
                var_name = msg.get('variable_name', '')
                if var_name:
                    enabled_params[var_name] = 'Canbus'
        
        logger.info(f"✅ Loaded {len(enabled_params)} enabled parameters for device {device_id}")
        logger.debug(f"   Parameters: {list(enabled_params.keys())}")
        
        # Create chart components
        charts = []
        if enabled_params:
            # Group parameters by type for better layout
            rows = []
            current_row = []
            
            for idx, (param_name, param_type) in enumerate(enabled_params.items()):
                chart_id = f"chart-{param_name}"
                chart_col = create_parameter_chart(param_name, param_type, chart_id)
                current_row.append(chart_col)
                
                # Create row every 3 charts
                if len(current_row) == 3 or idx == len(enabled_params) - 1:
                    rows.append(dbc.Row(current_row, className='mb-4'))
                    current_row = []
            
            charts = rows
        else:
            charts = [
                dbc.Alert(
                    [
                        html.I(className="fas fa-info-circle me-2"),
                        "No enabled parameters found for this device. Please configure the device in the Devices tab."
                    ],
                    color="info",
                    className="mt-4"
                )
            ]
        
        return device_id, enabled_params, charts
        
    except Exception as e:
        logger.error(f"❌ Error loading enabled parameters: {e}")
        logger.exception("Full error traceback:")
        return device_id, {}, [
            dbc.Alert(
                [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"Error loading parameters: {str(e)}"
                ],
                color="danger",
                className="mt-4"
            )
        ]


# Callback to update charts with real-time data
@callback(
    [
        Output({'type': 'analytics-chart', 'parameter': ALL}, 'figure'),
        Output({'type': 'live-value', 'parameter': ALL}, 'children'),
    ],
    [
        Input('analytics-refresh-interval', 'n_intervals'),
        Input('analytics-time-range-selector', 'value'),
        Input('analytics-device-store', 'data'),
        Input('analytics-params-store', 'data'),
    ],
    prevent_initial_call=True
)
def update_analytics_charts(n_intervals, time_range, device_id, enabled_params):
    """Update all charts with real-time data"""
    
    if not device_id or not enabled_params:
        return no_update, no_update
    
    try:
        from app.services.realtime_data_db import RealtimeDataDBService
        
        db_service = RealtimeDataDBService()
        
        if not db_service.is_connected():
            logger.warning("⚠️ Real-time data DB not connected")
            return no_update, no_update
        
        # Calculate time range
        end_time = datetime.utcnow()
        if time_range == '1h':
            start_time = end_time - timedelta(hours=1)
        elif time_range == '6h':
            start_time = end_time - timedelta(hours=6)
        elif time_range == '24h':
            start_time = end_time - timedelta(hours=24)
        elif time_range == '7d':
            start_time = end_time - timedelta(days=7)
        elif time_range == '30d':
            start_time = end_time - timedelta(days=30)
        elif time_range == '6m':
            start_time = end_time - timedelta(days=180)
        elif time_range == '1y':
            start_time = end_time - timedelta(days=365)
        else:
            start_time = end_time - timedelta(hours=1)
        
        # Get parameter names in order
        param_names = list(enabled_params.keys())
        param_types = [enabled_params[name] for name in param_names]
        
        # Create figures and live values for each parameter
        figures = []
        live_values = []
        
        for param_name, param_type in zip(param_names, param_types):
            # Get historical data
            data_points = db_service.get_realtime_data(
                device_id=device_id,
                parameter_name=param_name,
                start_time=start_time,
                end_time=end_time
            )
            
            # Get latest value
            latest_value = db_service.get_latest_value(
                device_id=device_id,
                parameter_name=param_name
            )
            
            # Format latest value for display
            if latest_value is not None:
                if isinstance(latest_value, (int, float)):
                    live_value = f"{latest_value:.2f}" if isinstance(latest_value, float) else str(latest_value)
                else:
                    live_value = str(latest_value)
            else:
                live_value = "--"
            
            live_values.append(live_value)
            
            # Create figure
            if data_points:
                timestamps = [dp['timestamp'] for dp in data_points]
                values = [dp['value'] for dp in data_points]
            else:
                timestamps = []
                values = []
            
            # Determine color based on type
            color_map = {
                'Analog': ('#8b5cf6', 'rgba(139, 92, 246, 0.1)'),
                'Digital': ('#10b981', 'rgba(16, 185, 129, 0.1)'),
                'Modbus': ('#3b82f6', 'rgba(59, 130, 246, 0.1)'),
                'Canbus': ('#f59e0b', 'rgba(245, 158, 11, 0.1)'),
            }
            color, fill_color = color_map.get(param_type, ('#667eea', 'rgba(102, 126, 234, 0.1)'))
            
            fig = go.Figure()
            
            if timestamps and values:
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=values,
                    mode='lines+markers',
                    name=param_name,
                    line=dict(color=color, width=3),
                    marker=dict(size=4),
                    fill='tozeroy',
                    fillcolor=fill_color
                ))
            
            fig.update_layout(
                margin=dict(l=40, r=20, t=20, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='#e9ecef'),
                yaxis=dict(showgrid=True, gridcolor='#e9ecef'),
                hovermode='x unified',
                showlegend=False
            )
            
            figures.append(fig)
        
        logger.debug(f"✅ Updated {len(figures)} charts for device {device_id}")
        return figures, live_values
        
    except Exception as e:
        logger.error(f"❌ Error updating charts: {e}")
        logger.exception("Full error traceback:")
        return no_update, no_update
