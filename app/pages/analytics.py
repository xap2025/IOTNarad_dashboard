"""
Analytics Page Layout
Real-time data visualization and insights
"""
from dash import html, dcc, Input, Output, State, callback, ALL, no_update, ctx
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
        # RTD update trigger - gets updated when MQTT data arrives
        dcc.Store(id='analytics-rtd-update-trigger', data={'timestamp': None, 'device_id': None}),
        
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
                        className='mb-2',
                        style={'borderRadius': '8px', 'minWidth': '300px', 'width': '100%'}
                    ),
                    # Device Status Badge
                    html.Div(id='device-status-container', children=[]),
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
        
        # Fallback refresh interval (30 seconds) - only used if no MQTT data arrives
        dcc.Interval(id='analytics-refresh-interval', interval=30000, n_intervals=0),
        
        # Client-side script to listen to SocketIO RTD events and trigger Store update
        html.Script("""
            (function() {
                // Wait for SocketIO to load
                function initRTDListener() {
                    if (typeof io === 'undefined') {
                        console.warn('⚠️ Analytics: SocketIO not loaded, retrying...');
                        setTimeout(initRTDListener, 500);
                        return;
                    }
                    
                    const socket = io();
                    
                    socket.on('rtd_data_update', function(data) {
                        console.log('📊 RTD data update received:', data);
                        
                        // Trigger Store update by dispatching custom event
                        // The Store will be updated via a callback that listens to this
                        const event = new CustomEvent('rtd-data-received', {
                            detail: {
                                device_id: data.device_id,
                                timestamp: data.timestamp || new Date().toISOString()
                            }
                        });
                        window.dispatchEvent(event);
                        
                        // Also trigger a click on hidden button to trigger callback
                        const triggerBtn = document.getElementById('analytics-rtd-trigger-btn');
                        if (triggerBtn) {
                            triggerBtn.click();
                        }
                    });
                    
                    console.log('✅ Analytics: SocketIO RTD listener initialized');
                }
                
                // Start initialization
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', initRTDListener);
                } else {
                    initRTDListener();
                }
            })();
        """),
        # Hidden button to trigger callback when RTD data arrives
        html.Button(id='analytics-rtd-trigger-btn', style={'display': 'none'}, n_clicks=0),
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
                # Live value display (will be updated by callback)
                html.Div(id={'type': 'live-value-container', 'parameter': parameter_name}, 
                        children=[
                            html.Span("No value", className='fw-bold fs-5', style={'color': color})
                        ], 
                        className='mb-2'),
            ], className='d-flex justify-content-between align-items-center'),
            
            dcc.Graph(
                id={'type': 'analytics-chart', 'parameter': parameter_name},
                config={'displayModeBar': False},
                style={'height': '250px'}
            ),
        ], className='stat-card p-3'),
    ], md=4, className='mb-4')


def create_device_status_badge(device_id: str):
    """Create device status badge (Running/Not Running)"""
    return html.Div([
        html.Span(id='device-status-badge', className='badge bg-secondary')
    ], className='mb-2')


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
        # IMPORTANT: Only check Input channels (4-20mA Input and 0-10V Input)
        # Output channels are ignored for Analytics
        if analog_config:
            logger.info(f"📊 ANALOG: Loading analog config for device {device_id}")
            
            # 4-20mA inputs (ONLY INPUTS)
            input_4_20ma_list = analog_config.get('input_4_20ma', [])
            logger.info(f"📊 ANALOG: Found {len(input_4_20ma_list)} input_4_20ma channel(s)")
            for channel in input_4_20ma_list:
                if channel.get('enabled', False):
                    name = channel.get('name', f"Channel {channel.get('channel', '?')}")
                    enabled_params[name] = 'Analog'
                    logger.debug(f"   Added Analog parameter (4-20mA Input): '{name}'")
            
            # 0-10V inputs (ONLY INPUTS) - Note: Database uses 'input_1_10v' but it's 0-10V range
            input_1_10v_list = analog_config.get('input_1_10v', [])
            logger.info(f"📊 ANALOG: Found {len(input_1_10v_list)} input_1_10v channel(s)")
            for channel in input_1_10v_list:
                if channel.get('enabled', False):
                    name = channel.get('name', f"Channel {channel.get('channel', '?')}")
                    enabled_params[name] = 'Analog'
                    logger.debug(f"   Added Analog parameter (0-10V Input): '{name}'")
            
            # NOTE: Output channels (output_0_10v) are IGNORED for Analytics
            logger.debug(f"   Skipping Analog output channels (not shown in Analytics)")
        
        # Digital parameters
        # IMPORTANT: Only check Input channels (NPN Input and PNP Input)
        # Output channels and Relays are ignored for Analytics
        if digital_config:
            logger.info(f"📊 DIGITAL: Loading digital config for device {device_id}")
            
            # NPN inputs (ONLY INPUTS)
            npn_input_list = digital_config.get('npn_input', [])
            logger.info(f"📊 DIGITAL: Found {len(npn_input_list)} NPN input channel(s)")
            for channel in npn_input_list:
                if channel.get('enabled', False):
                    name = channel.get('name', f"NPN_IN_{channel.get('channel', '?')}")
                    enabled_params[name] = 'Digital'
                    logger.debug(f"   Added Digital parameter (NPN Input): '{name}'")
            
            # PNP inputs (ONLY INPUTS)
            pnp_input_list = digital_config.get('pnp_input', [])
            logger.info(f"📊 DIGITAL: Found {len(pnp_input_list)} PNP input channel(s)")
            for channel in pnp_input_list:
                if channel.get('enabled', False):
                    name = channel.get('name', f"PNP_IN_{channel.get('channel', '?')}")
                    enabled_params[name] = 'Digital'
                    logger.debug(f"   Added Digital parameter (PNP Input): '{name}'")
            
            # NOTE: NPN outputs, PNP outputs, and Relays are IGNORED for Analytics
            logger.debug(f"   Skipping Digital outputs and Relays (not shown in Analytics)")
        
        # Modbus parameters
        if modbus_config:
            slave_devices = modbus_config.get('slave_devices', [])
            logger.info(f"📊 MODBUS: Found {len(slave_devices)} slave device(s) in config")
            for slave in slave_devices:
                var_name = slave.get('variable_name', '')
                if var_name:
                    # Clean variable name (remove extra spaces)
                    clean_var_name = var_name.strip()
                    enabled_params[clean_var_name] = 'Modbus'
                    logger.debug(f"   Added Modbus parameter: '{clean_var_name}'")
                else:
                    logger.warning(f"   ⚠️ Modbus slave device has empty variable_name: {slave}")
        
        # CAN Bus parameters
        if can_bus_config:
            can_messages = can_bus_config.get('can_messages', [])
            for msg in can_messages:
                var_name = msg.get('variable_name', '')
                if var_name:
                    enabled_params[var_name] = 'Canbus'
        
        logger.info(f"✅ Loaded {len(enabled_params)} enabled parameters for device {device_id}")
        logger.info(f"   Parameter list: {list(enabled_params.keys())}")
        logger.info(f"   Parameter details: {enabled_params}")
        
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


# Callback to check device status (Running/Not Running)
@callback(
    Output('device-status-container', 'children'),
    [
        Input('analytics-refresh-interval', 'n_intervals'),
        Input('analytics-rtd-update-trigger', 'data'),  # Also update on RTD data
        Input('analytics-device-store', 'data'),
    ],
    prevent_initial_call=False  # Allow initial call
)
def update_device_status(n_intervals, rtd_trigger, device_id):
    """Check if device is running (has data in last 1 hour)"""
    if not device_id:
        return []
    
    try:
        from app.services.realtime_data_db import RealtimeDataDBService
        
        db_service = RealtimeDataDBService()
        
        if not db_service.is_connected():
            return []
        
        # Check if device has sent data in last 1 hour
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        # Query for any data from this device in last 1 hour
        escaped_device_id = device_id.replace('\\', '\\\\').replace('"', '\\"')
        
        query = f'''
            from(bucket: "{db_service.bucket}")
            |> range(start: -1h)
            |> filter(fn: (r) => r._measurement == "Realtime_Data")
            |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
            |> limit(n: 1)
        '''
        
        result = db_service.query_api.query(org=db_service.org, query=query)
        
        has_data = False
        for table in result:
            for record in table.records:
                has_data = True
                break
            if has_data:
                break
        
        # Create status badge
        if has_data:
            status_badge = dbc.Badge(
                [
                    html.I(className="fas fa-circle me-1", style={'fontSize': '0.6rem'}),
                    "Running"
                ],
                color="success",
                className="px-3 py-2"
            )
        else:
            status_badge = dbc.Badge(
                [
                    html.I(className="fas fa-circle me-1", style={'fontSize': '0.6rem'}),
                    "Not Running"
                ],
                color="secondary",
                className="px-3 py-2"
            )
        
        return [status_badge]
        
    except Exception as e:
        logger.error(f"❌ Error checking device status: {e}")
        return []


# Callback to update RTD trigger Store when button is clicked (triggered by SocketIO)
@callback(
    Output('analytics-rtd-update-trigger', 'data'),
    Input('analytics-rtd-trigger-btn', 'n_clicks'),
    State('analytics-device-store', 'data'),
    prevent_initial_call=True
)
def update_rtd_trigger(n_clicks, device_id):
    """Update RTD trigger Store when SocketIO event is received"""
    if n_clicks and n_clicks > 0:
        logger.info(f"🔄 RTD update trigger activated (clicks: {n_clicks})")
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'device_id': device_id
        }
    return no_update


# Callback to update charts with real-time data
@callback(
    [
        Output({'type': 'analytics-chart', 'parameter': ALL}, 'figure'),
        Output({'type': 'live-value-container', 'parameter': ALL}, 'children'),
    ],
    [
        Input('analytics-refresh-interval', 'n_intervals'),  # Fallback interval (30s)
        Input('analytics-rtd-update-trigger', 'data'),  # Event-based trigger from MQTT
        Input('analytics-time-range-selector', 'value'),
        Input('analytics-device-store', 'data'),
        Input('analytics-params-store', 'data'),
    ],
    prevent_initial_call=False  # Allow initial call to load data immediately
)
def update_analytics_charts(n_intervals, rtd_trigger, time_range, device_id, enabled_params):
    """Update all charts with real-time data"""
    
    # Check what triggered this callback
    triggered_id = ctx.triggered[0]['prop_id'] if ctx.triggered else 'initial'
    
    if 'analytics-rtd-update-trigger' in triggered_id:
        logger.info(f"⚡ Analytics callback triggered by RTD MQTT data: device_id={device_id}")
    elif 'analytics-refresh-interval' in triggered_id:
        logger.info(f"⏱️ Analytics callback triggered by fallback interval: n_intervals={n_intervals}")
    else:
        logger.info(f"🔄 Analytics callback triggered: {triggered_id}, device_id={device_id}, enabled_params_count={len(enabled_params) if enabled_params else 0}")
    
    if not device_id or not enabled_params:
        logger.warning(f"⚠️ Missing device_id or enabled_params: device_id={device_id}, enabled_params={enabled_params}")
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
            # Clean parameter name (remove extra spaces)
            clean_param_name = param_name.strip()
            
            logger.info(f"🔍 Fetching data for parameter: '{clean_param_name}' (device: {device_id}, type: {param_type})")
            
            # Get historical data
            data_points = db_service.get_realtime_data(
                device_id=device_id,
                parameter_name=clean_param_name,
                start_time=start_time,
                end_time=end_time
            )
            
            logger.info(f"   Historical data points: {len(data_points)}")
            if len(data_points) > 0:
                logger.info(f"   First data point: timestamp={data_points[0].get('timestamp')}, value={data_points[0].get('value')}")
                logger.info(f"   Last data point: timestamp={data_points[-1].get('timestamp')}, value={data_points[-1].get('value')}")
            
            # Get latest value (check last 24 hours for latest value)
            latest_value = db_service.get_latest_value(
                device_id=device_id,
                parameter_name=clean_param_name
            )
            
            logger.info(f"   Latest value: {latest_value} (type: {type(latest_value)})")
            
            # Determine color based on type (MUST be before using color variable)
            color_map = {
                'Analog': ('#8b5cf6', 'rgba(139, 92, 246, 0.1)'),
                'Digital': ('#10b981', 'rgba(16, 185, 129, 0.1)'),
                'Modbus': ('#3b82f6', 'rgba(59, 130, 246, 0.1)'),
                'Canbus': ('#f59e0b', 'rgba(245, 158, 11, 0.1)'),
            }
            color, fill_color = color_map.get(param_type, ('#667eea', 'rgba(102, 126, 234, 0.1)'))
            
            # Format latest value for display (without "Current:" prefix)
            if latest_value is not None:
                # Handle Digital data: values are stored as integers (1/0) but should display as ON/OFF
                if param_type == 'Digital':
                    # Digital values are stored as integers: 1 = true/ON, 0 = false/OFF
                    if isinstance(latest_value, (int, float)):
                        int_value = int(latest_value)
                        value_text = "ON" if int_value == 1 else "OFF"
                        logger.info(f"   ✅ Digital value converted: {latest_value} → {value_text}")
                    elif isinstance(latest_value, bool):
                        value_text = "ON" if latest_value else "OFF"
                        logger.info(f"   ✅ Digital boolean value: {latest_value} → {value_text}")
                    else:
                        value_text = str(latest_value)
                        logger.warning(f"   ⚠️ Unexpected Digital value type: {type(latest_value)} = {latest_value}")
                elif isinstance(latest_value, (int, float)):
                    # Show integers without decimals, floats with 2 decimals
                    if isinstance(latest_value, float) and latest_value.is_integer():
                        value_text = str(int(latest_value))
                    elif isinstance(latest_value, float):
                        value_text = f"{latest_value:.2f}"
                    else:
                        value_text = str(latest_value)
                else:
                    value_text = str(latest_value)
                
                # Show only value (no "Current:" prefix)
                live_value_display = [
                    html.Span(value_text, className='fw-bold fs-5', style={'color': color})
                ]
            else:
                # Show only "No value" when no value is available
                logger.warning(f"   ⚠️ No latest value found for parameter '{clean_param_name}'")
                live_value_display = [
                    html.Span("No value", className='fw-bold fs-5', style={'color': color})
                ]
            
            live_values.append(live_value_display)
            
            # Create figure
            if data_points:
                timestamps = [dp['timestamp'] for dp in data_points]
                values = [dp['value'] for dp in data_points]
            else:
                timestamps = []
                values = []
            
            fig = go.Figure()
            
            if timestamps and values:
                # Values are already stored as integers in database
                # Digital: 1 = ON, 0 = OFF
                # Other types: numeric values as-is
                plot_values = []
                for v in values:
                    if isinstance(v, bool):
                        # Handle boolean (shouldn't happen after fix, but keep for safety)
                        plot_values.append(1 if v else 0)
                    elif isinstance(v, (int, float)):
                        plot_values.append(v)
                    else:
                        # Try to convert to number
                        try:
                            plot_values.append(float(v))
                        except (ValueError, TypeError):
                            plot_values.append(0)
                
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=plot_values,
                    mode='lines+markers',
                    name=param_name,
                    line=dict(color=color, width=3),
                    marker=dict(size=4),
                    fill='tozeroy',
                    fillcolor=fill_color
                ))
                
                # Auto-scale Y-axis based on data range
                if plot_values:
                    min_val = min(plot_values)
                    max_val = max(plot_values)
                    # Add padding (10% on each side)
                    range_val = max_val - min_val
                    if range_val == 0:
                        # If all values are same, add some padding
                        y_min = min_val - abs(min_val * 0.1) if min_val != 0 else -1
                        y_max = max_val + abs(max_val * 0.1) if max_val != 0 else 1
                    else:
                        y_min = min_val - (range_val * 0.1)
                        y_max = max_val + (range_val * 0.1)
                else:
                    y_min = None
                    y_max = None
            else:
                y_min = None
                y_max = None
            
            # Update layout with proper axis labels
            fig.update_layout(
                margin=dict(l=60, r=20, t=20, b=50),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=True, 
                    gridcolor='#e9ecef',
                    title="Time",
                    titlefont=dict(size=12),
                    tickfont=dict(size=10)
                ),
                yaxis=dict(
                    showgrid=True, 
                    gridcolor='#e9ecef',
                    title="Value",
                    titlefont=dict(size=12),
                    tickfont=dict(size=10),
                    range=[y_min, y_max] if y_min is not None and y_max is not None else None
                ),
                hovermode='x unified',
                showlegend=False
            )
            
            figures.append(fig)
        
        logger.debug(f"✅ Updated {len(figures)} charts for device {device_id}")
        logger.debug(f"   Live values: {live_values}")
        return figures, live_values
        
    except Exception as e:
        logger.error(f"❌ Error updating charts: {e}")
        logger.exception("Full error traceback:")
        return no_update, no_update
