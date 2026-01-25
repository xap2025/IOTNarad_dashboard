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


def convert_timestamp_to_datetime(timestamp):
    """Convert timestamp (datetime or ISO string) to datetime object"""
    if isinstance(timestamp, datetime):
        return timestamp
    elif isinstance(timestamp, str):
        try:
            # Try ISO format first
            if 'T' in timestamp or '+' in timestamp or timestamp.endswith('Z'):
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                # Try other formats
                return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        except (ValueError, AttributeError):
            logger.warning(f"⚠️ Could not parse timestamp: {timestamp}")
            return None
    return None


def convert_active_periods_to_datetime(active_periods):
    """Convert active_periods list (which may contain string timestamps) to datetime objects"""
    if not active_periods:
        return []
    
    converted_periods = []
    for period_start, period_end in active_periods:
        start_dt = convert_timestamp_to_datetime(period_start)
        end_dt = convert_timestamp_to_datetime(period_end)
        if start_dt and end_dt:
            converted_periods.append((start_dt, end_dt))
    
    return converted_periods


# Callback to load enabled parameters from device config (with historical support)
@callback(
    [
        Output('analytics-device-store', 'data'),
        Output('analytics-params-store', 'data'),
        Output('analytics-charts-container', 'children'),
    ],
    [
        Input('analytics-device-selector', 'value'),
        Input('analytics-time-range-selector', 'value'),
    ],
    prevent_initial_call=True
)
def load_enabled_parameters(device_id, time_range):
    """Load enabled parameters from device configuration (including historical parameters in time range)"""
    if not device_id:
        return None, {}, []
    
    try:
        from app.services.device_config_db import DeviceConfigDBService
        
        db_service = DeviceConfigDBService()
        
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
        
        # Get historical parameter names in time range
        logger.info(f"📊 Loading historical parameters for device {device_id} in time range {time_range} ({start_time} to {end_time})")
        parameter_map = db_service.get_parameter_names_in_time_range(device_id, start_time, end_time)
        
        # Build enabled_params dict with data_type
        enabled_params = {}
        param_metadata = {}  # Store metadata for each parameter
        
        for param_name, param_info in parameter_map.items():
            enabled_params[param_name] = param_info['data_type']
            param_metadata[param_name] = {
                'data_type': param_info['data_type'],
                'active_periods': param_info['active_periods'],
                'channel_info': param_info.get('channel_info', {})
            }
        
        logger.info(f"✅ Loaded {len(enabled_params)} parameter(s) (including historical) for device {device_id}")
        logger.info(f"   Parameter list: {list(enabled_params.keys())}")
        
        # Store metadata in params store (we'll encode it in the dict)
        # Add metadata as a special key that won't conflict with parameter names
        enabled_params['_metadata'] = param_metadata
        
        # Create chart components
        charts = []
        if enabled_params and len([k for k in enabled_params.keys() if k != '_metadata']) > 0:
            # Group parameters by type for better layout
            rows = []
            current_row = []
            
            # Filter out metadata key
            param_items = [(k, v) for k, v in enabled_params.items() if k != '_metadata']
            
            for idx, (param_name, param_type) in enumerate(param_items):
                chart_id = f"chart-{param_name}"
                chart_col = create_parameter_chart(param_name, param_type, chart_id)
                current_row.append(chart_col)
                
                # Create row every 3 charts
                if len(current_row) == 3 or idx == len(param_items) - 1:
                    rows.append(dbc.Row(current_row, className='mb-4'))
                    current_row = []
            
            charts = rows
        else:
            charts = [
                dbc.Alert(
                    [
                        html.I(className="fas fa-info-circle me-2"),
                        "No enabled parameters found for this device in the selected time range. Please configure the device in the Devices tab."
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
        Input('analytics-device-store', 'data'),
    ],
    prevent_initial_call=False  # Allow initial call
)
def update_device_status(n_intervals, device_id):
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


# Callback to update charts with real-time data
@callback(
    [
        Output({'type': 'analytics-chart', 'parameter': ALL}, 'figure'),
        Output({'type': 'live-value-container', 'parameter': ALL}, 'children'),
    ],
    [
        Input('analytics-refresh-interval', 'n_intervals'),
        Input('analytics-time-range-selector', 'value'),
        Input('analytics-device-store', 'data'),
        Input('analytics-params-store', 'data'),
    ],
    prevent_initial_call=False  # Allow initial call to load data immediately
)
def update_analytics_charts(n_intervals, time_range, device_id, enabled_params):
    """Update all charts with real-time data"""
    
    logger.info(f"🔄 Analytics callback triggered: n_intervals={n_intervals}, device_id={device_id}, enabled_params_count={len(enabled_params) if enabled_params else 0}")
    
    if not device_id or not enabled_params:
        logger.warning(f"⚠️ Missing device_id or enabled_params: device_id={device_id}, enabled_params={enabled_params}")
        return [], []  # Return empty lists for ALL outputs
    
    try:
        from app.services.realtime_data_db import RealtimeDataDBService
        
        db_service = RealtimeDataDBService()
        
        if not db_service.is_connected():
            logger.warning("⚠️ Real-time data DB not connected")
            return [], []  # Return empty lists for ALL outputs
        
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
        
        # Extract metadata and filter out metadata key
        param_metadata = enabled_params.get('_metadata', {})
        param_names = [k for k in enabled_params.keys() if k != '_metadata']
        
        # Auto-removal: Filter parameters that have no data in the current time range
        # Check if parameter has any active period that overlaps with current time range
        valid_param_names = []
        for param_name in param_names:
            if param_name in param_metadata:
                active_periods_raw = param_metadata[param_name].get('active_periods', [])
                # Convert string timestamps to datetime objects
                active_periods = convert_active_periods_to_datetime(active_periods_raw)
                
                # Check if any active period overlaps with current time range
                has_overlap = False
                for period_start, period_end in active_periods:
                    # Check if period overlaps with current range
                    if period_start <= end_time and period_end >= start_time:
                        has_overlap = True
                        break
                
                if has_overlap:
                    valid_param_names.append(param_name)
                else:
                    logger.info(f"   ⏭️ Skipping parameter '{param_name}' - no active period in current time range")
            else:
                # No metadata - include it (backward compatibility)
                valid_param_names.append(param_name)
        
        param_names = valid_param_names
        param_types = [enabled_params[name] for name in param_names]
        
        # If no valid parameters, return empty lists
        if not param_names:
            logger.info("   ⚠️ No valid parameters found in time range")
            return [], []
        
        # Get data for all parameters at once (more efficient)
        all_data = db_service.get_realtime_data_multiple_params(
            device_id=device_id,
            parameter_names=param_names,
            start_time=start_time,
            end_time=end_time
        )
        
        # Create figures and live values for each parameter
        figures = []
        live_values = []
        
        for param_name, param_type in zip(param_names, param_types):
            # Clean parameter name (remove extra spaces)
            clean_param_name = param_name.strip()
            
            logger.info(f"🔍 Processing parameter: '{clean_param_name}' (device: {device_id}, type: {param_type})")
            
            # Get data from batch query result
            data_points = all_data.get(clean_param_name, [])
            
            # Filter data based on active periods (if metadata available)
            if clean_param_name in param_metadata:
                active_periods_raw = param_metadata[clean_param_name].get('active_periods', [])
                # Convert string timestamps to datetime objects
                active_periods = convert_active_periods_to_datetime(active_periods_raw)
                
                if active_periods:
                    # Filter data points to only include those within active periods
                    filtered_data_points = []
                    for dp in data_points:
                        dp_time = dp['timestamp']
                        # Ensure dp_time is datetime
                        if isinstance(dp_time, str):
                            dp_time = convert_timestamp_to_datetime(dp_time)
                            if not dp_time:
                                continue
                        
                        # Check if data point is within any active period
                        for period_start, period_end in active_periods:
                            if period_start <= dp_time <= period_end:
                                filtered_data_points.append(dp)
                                break
                    data_points = filtered_data_points
                    logger.info(f"   Filtered to {len(data_points)} data points within active periods")
            
            logger.info(f"   Historical data points: {len(data_points)}")
            if len(data_points) > 0:
                logger.info(f"   First data point: timestamp={data_points[0].get('timestamp')}, value={data_points[0].get('value')}")
                logger.info(f"   Last data point: timestamp={data_points[-1].get('timestamp')}, value={data_points[-1].get('value')}")
            
            # Get latest value (check last 24 hours for latest value)
            # Only show latest value if parameter is currently active
            latest_value = None
            if clean_param_name in param_metadata:
                active_periods_raw = param_metadata[clean_param_name].get('active_periods', [])
                # Convert string timestamps to datetime objects
                active_periods = convert_active_periods_to_datetime(active_periods_raw)
                
                # Check if parameter is currently active (has period that includes end_time)
                is_currently_active = any(period_start <= end_time <= period_end for period_start, period_end in active_periods)
                if is_currently_active:
                    latest_value = db_service.get_latest_value(
                        device_id=device_id,
                        parameter_name=clean_param_name
                    )
            else:
                # No metadata - get latest value (backward compatibility)
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
            
            # Format latest value for display
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
                # Show "No value" when parameter name changed or no current data
                logger.warning(f"   ⚠️ No latest value found for parameter '{clean_param_name}' (may be old name)")
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
        # Return empty lists for ALL outputs (not no_update for multi-output with ALL)
        return [], []
