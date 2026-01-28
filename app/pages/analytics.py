"""
Analytics Page Layout
Real-time data visualization and insights
"""
from dash import html, dcc, Input, Output, State, callback, ALL, no_update, clientside_callback, ClientsideFunction
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from datetime import datetime, timedelta, timezone
import logging
import json

logger = logging.getLogger(__name__)


def create_analytics_layout():
    """Create analytics page with real-time charts"""
    
    return html.Div([
        # Hidden stores
        dcc.Store(id='analytics-device-store', data=None),
        dcc.Store(id='analytics-params-store', data={}),
        dcc.Store(id='analytics-latest-values-store', data={}),
        # Socket.IO RTD update trigger store (updated by clientside callback)
        dcc.Store(id='analytics-rtd-trigger-store', data={'timestamp': None, 'device_id': None, 'trigger_count': 0}),
        
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
        
        # Auto-refresh interval (30 seconds - fallback only, Socket.IO is primary)
        dcc.Interval(id='analytics-refresh-interval', interval=30000, n_intervals=0),
        
        # Analytics Socket.IO client script loader
        # Socket.IO library is loaded in <head> via app.index_string in main.py
        # This script waits for Socket.IO to be available, then loads our custom client
        html.Script('''
            (function() {
                console.log('📦 Analytics page: Initializing Socket.IO client loader...');
                
                // Wait for Socket.IO library to load (it's in <head> section)
                function waitForSocketIOAndLoadClient() {
                    if (typeof io !== 'undefined') {
                        console.log('✅ Socket.IO library confirmed available');
                        loadAnalyticsClient();
                    } else {
                        // Socket.IO should be in <head>, but wait a bit if it's still loading
                        console.log('⏳ Waiting for Socket.IO library to load...');
                        setTimeout(waitForSocketIOAndLoadClient, 100);
                    }
                }
                
                function loadAnalyticsClient() {
                    // Prevent duplicate initialization
                    if (window.analyticsSocketIOInitialized) {
                        console.log('⚠️ Analytics Socket.IO client already initialized');
                        return;
                    }
                    
                    // Double-check Socket.IO is available
                    if (typeof io === 'undefined') {
                        console.error('❌ Socket.IO library still not available after wait');
                        return;
                    }
                    
                    console.log('✅ Loading analytics Socket.IO client script...');
                    
                    // Load our custom analytics client script
                    const script = document.createElement('script');
                    script.src = '/assets/z_analytics_socket_client.js';
                    script.type = 'text/javascript';
                    script.async = false;
                    script.onload = function() {
                        console.log('✅ Analytics Socket.IO client script loaded successfully');
                    };
                    script.onerror = function() {
                        console.error('❌ Failed to load analytics Socket.IO client script');
                        console.error('   URL: /assets/z_analytics_socket_client.js');
                        console.error('   Check Network tab in DevTools');
                    };
                    document.head.appendChild(script);
                }
                
                // Start waiting for Socket.IO (should be quick since it's in <head>)
                waitForSocketIOAndLoadClient();
            })();
        ''', type='text/javascript'),
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
    """Convert timestamp (datetime or ISO string) to timezone-aware datetime object (UTC)"""
    from datetime import timezone
    
    if isinstance(timestamp, datetime):
        # If already datetime, ensure it's timezone-aware (UTC)
        if timestamp.tzinfo is None:
            # Timezone-naive, assume UTC
            return timestamp.replace(tzinfo=timezone.utc)
        else:
            # Already timezone-aware, convert to UTC if needed
            return timestamp.astimezone(timezone.utc)
    elif isinstance(timestamp, str):
        try:
            # Try ISO format first
            if 'T' in timestamp or '+' in timestamp or timestamp.endswith('Z'):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                # Ensure timezone-aware
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            else:
                # Try other formats - assume UTC
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                return dt.replace(tzinfo=timezone.utc)
        except (ValueError, AttributeError) as e:
            logger.warning(f"⚠️ Could not parse timestamp: {timestamp}, error: {e}")
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


def get_xaxis_tick_interval(time_range: str):
    """
    Get appropriate tick interval for X-axis based on selected time range
    
    Args:
        time_range: Time range string ('1h', '6h', '24h', '7d', '30d', '6m', '1y')
    
    Returns:
        Tuple of (dtick_value, tick_format)
        - dtick_value: Plotly date tick value (milliseconds for minutes, or string like 'H2', 'D1', 'M1')
        - tick_format: Format string for displaying time
    """
    if time_range == '1h':
        # Last 1 Hour: 10-minute intervals (10 * 60 * 1000 = 600000 ms)
        return 600000, '%H:%M'
    elif time_range == '6h':
        # Last 6 Hours: 30-minute intervals (30 * 60 * 1000 = 1800000 ms)
        return 1800000, '%H:%M'
    elif time_range == '24h':
        # Last 24 Hours: 2-hour intervals
        return 'H2', '%H:%M'
    elif time_range == '7d':
        # Last 7 Days: 12-hour intervals
        return 'H12', '%m/%d %H:%M'
    elif time_range == '30d':
        # Last 30 Days: 2-day intervals
        return 'D2', '%m/%d'
    elif time_range == '6m':
        # Last 6 Months: 1-week intervals
        return 'W1', '%m/%d'
    elif time_range == '1y':
        # Last 1 Year: 1-month intervals
        return 'M1', '%m/%Y'
    else:
        # Default: 10-minute intervals
        return 600000, '%H:%M'


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
        logger.info(f"   Parameter details: {[(name, info['data_type'], len(info['active_periods'])) for name, info in param_metadata.items()]}")
        
        # DEBUG: Log active periods for each parameter
        for param_name, info in param_metadata.items():
            periods = info['active_periods']
            logger.debug(f"   '{param_name}' ({info['data_type']}): {len(periods)} active period(s)")
            for i, (p_start, p_end) in enumerate(periods):
                logger.debug(f"      Period {i+1}: {p_start} to {p_end}")
        
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
        Input('analytics-rtd-trigger-store', 'data'),  # Socket.IO event trigger (store update via clientside callback)
        Input('analytics-time-range-selector', 'value'),
        Input('analytics-device-store', 'data'),
        Input('analytics-params-store', 'data'),
    ],
    prevent_initial_call=False  # Allow initial call to load data immediately
)
def update_analytics_charts(n_intervals, rtd_trigger_data, time_range, device_id, enabled_params):
    """Update all charts with real-time data"""
    
    try:
        # Determine trigger source
        from dash import ctx
        
        # Handle initial load case (when ctx.triggered might be empty)
        if not ctx.triggered or len(ctx.triggered) == 0:
            # On initial load, use default values
            trigger_id = 'analytics-refresh-interval'  # Default to interval trigger
            logger.info("🔄 Analytics callback triggered: Initial load")
        else:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
        
        # Only process if triggered by valid sources
        valid_triggers = ['analytics-refresh-interval', 'analytics-rtd-trigger-store', 'analytics-time-range-selector', 'analytics-device-store', 'analytics-params-store']
        if trigger_id not in valid_triggers:
            logger.warning(f"⚠️ Unknown trigger: {trigger_id} - ignoring (valid: {valid_triggers})")
            # For ALL outputs, we need to return correct count - try to get from enabled_params
            param_count = 0
            if enabled_params and isinstance(enabled_params, dict):
                param_metadata = enabled_params.get('_metadata', {})
                param_names = [k for k in enabled_params.keys() if k != '_metadata']
                param_count = len(param_names)
            if param_count > 0:
                return [go.Figure() for _ in range(param_count)], [[html.Span("No data", className='fw-bold fs-5')] for _ in range(param_count)]
            return [], []
        
        # Determine trigger source for logging
        if trigger_id == 'analytics-rtd-trigger-store' and rtd_trigger_data and rtd_trigger_data.get('timestamp'):
            trigger_source = f"Socket.IO RTD event (device: {rtd_trigger_data.get('device_id', 'unknown')}, timestamp: {rtd_trigger_data.get('timestamp')})"
            
            # ========== DETAILED CONSOLE LOGGING FOR DEBUGGING ==========
            logger.info("=" * 80)
            logger.info("🟢 [DASH STORE → ANALYTICS CALLBACK] Step 6/6: ANALYTICS CALLBACK TRIGGERED!")
            logger.info("=" * 80)
            logger.info(f"   🎯 Trigger Source: Socket.IO RTD event (Real-time data from hardware)")
            logger.info(f"   🏭 Device ID: {rtd_trigger_data.get('device_id', 'unknown')}")
            logger.info(f"   📅 Event Timestamp: {rtd_trigger_data.get('timestamp')}")
            logger.info(f"   📊 Trigger Data: {json.dumps(rtd_trigger_data, indent=2)}")
            logger.info(f"   ⏱️ Callback Trigger Time: {datetime.utcnow().isoformat()}")
            logger.info("=" * 80)
            # ========== END DETAILED LOGGING ==========
        else:
            trigger_source = f"Interval (n_intervals={n_intervals})"
            logger.info(f"🔄 Analytics callback triggered: {trigger_source}")
        
        logger.info(f"   📊 Device ID: {device_id}, Enabled Params: {len(enabled_params) if enabled_params else 0}")
        
        if not device_id or not enabled_params:
            logger.warning(f"⚠️ Missing device_id or enabled_params: device_id={device_id}, enabled_params={enabled_params}")
            # Try to get parameter count even if enabled_params is partial
            param_count = 0
            if enabled_params and isinstance(enabled_params, dict):
                param_metadata = enabled_params.get('_metadata', {})
                param_names = [k for k in enabled_params.keys() if k != '_metadata']
                param_count = len(param_names)
            if param_count > 0:
                return [go.Figure() for _ in range(param_count)], [[html.Span("No data", className='fw-bold fs-5')] for _ in range(param_count)]
            return [], []  # Return empty lists for ALL outputs
        from app.services.realtime_data_db import RealtimeDataDBService
        
        db_service = RealtimeDataDBService()
        
        if not db_service.is_connected():
            logger.warning("⚠️ Real-time data DB not connected")
            # Get parameter count from enabled_params
            param_count = 0
            if enabled_params and isinstance(enabled_params, dict):
                param_metadata = enabled_params.get('_metadata', {})
                param_names = [k for k in enabled_params.keys() if k != '_metadata']
                param_count = len(param_names)
            if param_count > 0:
                return [go.Figure() for _ in range(param_count)], [[html.Span("DB Error", className='fw-bold fs-5', style={'color': '#ef4444'})] for _ in range(param_count)]
            return [], []  # Return empty lists for ALL outputs
        
        # Calculate time range
        from datetime import timezone
        import pytz
        
        # Get current time in UTC (for database queries)
        end_time_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
        # Add small buffer (5 seconds) to ensure we capture the latest data point
        # This is important because data might be saved just before the query executes
        end_time_utc_with_buffer = end_time_utc + timedelta(seconds=5)
        
        if time_range == '1h':
            start_time_utc = end_time_utc - timedelta(hours=1)
        elif time_range == '6h':
            start_time_utc = end_time_utc - timedelta(hours=6)
        elif time_range == '24h':
            start_time_utc = end_time_utc - timedelta(hours=24)
        elif time_range == '7d':
            start_time_utc = end_time_utc - timedelta(days=7)
        elif time_range == '30d':
            start_time_utc = end_time_utc - timedelta(days=30)
        elif time_range == '6m':
            start_time_utc = end_time_utc - timedelta(days=180)
        elif time_range == '1y':
            start_time_utc = end_time_utc - timedelta(days=365)
        else:
            start_time_utc = end_time_utc - timedelta(hours=1)
        
        # Ensure both are timezone-aware (UTC) - critical for datetime comparisons
        if start_time_utc.tzinfo is None:
            start_time_utc = start_time_utc.replace(tzinfo=timezone.utc)
        if end_time_utc.tzinfo is None:
            end_time_utc = end_time_utc.replace(tzinfo=timezone.utc)
        if end_time_utc_with_buffer.tzinfo is None:
            end_time_utc_with_buffer = end_time_utc_with_buffer.replace(tzinfo=timezone.utc)
        
        # Convert to IST (Asia/Kolkata) for X-axis display
        ist = pytz.timezone('Asia/Kolkata')
        start_time = start_time_utc.astimezone(ist)  # Convert to IST for display
        end_time = end_time_utc.astimezone(ist)  # Convert to IST for display
        
        # Keep UTC versions for database queries
        # Use start_time_utc and end_time_utc for database queries
        # Use start_time and end_time (IST) for X-axis display
        
        # Extract metadata and filter out metadata key
        param_metadata = enabled_params.get('_metadata', {})
        param_names = [k for k in enabled_params.keys() if k != '_metadata']
        
        # Auto-removal: Filter parameters that have no data in the current time range
        # Check if parameter has any active period that overlaps with current time range
        valid_param_names = []
        logger.info(f"🔍 Checking {len(param_names)} parameter(s) for active periods in time range ({start_time} to {end_time})")
        
        for param_name in param_names:
            if param_name in param_metadata:
                active_periods_raw = param_metadata[param_name].get('active_periods', [])
                # Convert string timestamps to datetime objects
                active_periods = convert_active_periods_to_datetime(active_periods_raw)
                
                logger.debug(f"   Parameter '{param_name}': {len(active_periods)} active period(s)")
                
                # Check if any active period overlaps with current time range
                # Note: start_time and end_time are already timezone-aware (set at function start)
                has_overlap = False
                for period_start, period_end in active_periods:
                    # Ensure period timestamps are timezone-aware (UTC)
                    period_start = convert_timestamp_to_datetime(period_start) if period_start else None
                    period_end = convert_timestamp_to_datetime(period_end) if period_end else None
                    
                    if period_start and period_end:
                        # Check if period overlaps with current range
                        overlap_check = period_start <= end_time and period_end >= start_time
                        logger.debug(f"      Period ({period_start} to {period_end}): overlap={overlap_check}")
                        if overlap_check:
                            has_overlap = True
                            break
                
                if has_overlap:
                    valid_param_names.append(param_name)
                    logger.debug(f"   ✅ Parameter '{param_name}' is valid (has overlapping active period)")
                else:
                    logger.warning(f"   ⏭️ Skipping parameter '{param_name}' - no active period overlaps with current time range")
                    logger.warning(f"      Time range: {start_time} to {end_time}")
                    logger.warning(f"      Active periods: {active_periods}")
            else:
                # No metadata - include it (backward compatibility)
                logger.debug(f"   ✅ Parameter '{param_name}' included (no metadata - backward compatibility)")
                valid_param_names.append(param_name)
        
        logger.info(f"✅ Filtered to {len(valid_param_names)} valid parameter(s) out of {len(param_names)} total")
        
        param_names = valid_param_names
        param_types = [enabled_params[name] for name in param_names]
        
        # If no valid parameters, return empty lists
        if not param_names:
            logger.info("   ⚠️ No valid parameters found in time range")
            # Return empty outputs matching expected count (should be 0, but handle edge case)
            return [], []
        
        # Get data for all parameters at once (more efficient)
        # Use UTC times for database queries
        logger.info(f"🔍 Querying data for {len(param_names)} parameter(s): {param_names[:5]}...")
        logger.info(f"   Database query range (UTC): {start_time_utc.strftime('%Y-%m-%d %H:%M:%S')} to {end_time_utc_with_buffer.strftime('%Y-%m-%d %H:%M:%S')} (with 5s buffer)")
        all_data = db_service.get_realtime_data_multiple_params(
            device_id=device_id,
            parameter_names=param_names,
            start_time=start_time_utc,  # Use UTC for database queries
            end_time=end_time_utc_with_buffer  # Use UTC with buffer to ensure latest data is captured
        )
        
        logger.info(f"📊 Data query result: {len(all_data)} parameter(s) have data")
        for param_name, data_points in all_data.items():
            if data_points:
                first_dp = data_points[0]
                last_dp = data_points[-1]
                logger.info(f"   '{param_name}': {len(data_points)} data point(s) | First: {first_dp.get('timestamp')} | Last: {last_dp.get('timestamp')}")
            else:
                logger.info(f"   '{param_name}': 0 data point(s)")
        
        # Create figures and live values for each parameter
        figures = []
        live_values = []
        
        for param_name, param_type in zip(param_names, param_types):
            # Clean parameter name (remove extra spaces)
            clean_param_name = param_name.strip()
            
            logger.info(f"🔍 Processing parameter: '{clean_param_name}' (device: {device_id}, type: {param_type})")
            
            # Get data from batch query result
            data_points = all_data.get(clean_param_name, [])
            logger.info(f"   📥 Retrieved {len(data_points)} data point(s) for '{clean_param_name}'")
            
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
                        # Ensure dp_time is timezone-aware datetime (UTC)
                        if isinstance(dp_time, str):
                            dp_time = convert_timestamp_to_datetime(dp_time)
                            if not dp_time:
                                continue
                        elif isinstance(dp_time, datetime):
                            # Ensure timezone-aware
                            dp_time = convert_timestamp_to_datetime(dp_time)
                            if not dp_time:
                                continue
                        
                        # Check if data point is within any active period
                        for period_start, period_end in active_periods:
                            # Ensure both period timestamps are timezone-aware
                            period_start = convert_timestamp_to_datetime(period_start) if period_start else None
                            period_end = convert_timestamp_to_datetime(period_end) if period_end else None
                            
                            if period_start and period_end and period_start <= dp_time <= period_end:
                                filtered_data_points.append(dp)
                                break
                    data_points = filtered_data_points
                    logger.info(f"   Filtered to {len(data_points)} data points within active periods")
            
            logger.info(f"   Historical data points: {len(data_points)}")
            if len(data_points) > 0:
                logger.info(f"   First data point: timestamp={data_points[0].get('timestamp')}, value={data_points[0].get('value')}")
                logger.info(f"   Last data point: timestamp={data_points[-1].get('timestamp')}, value={data_points[-1].get('value')}")
            
            # Get latest value - prefer using data_points we already fetched
            latest_value = None
            
            # First, try to get latest value from data_points we already fetched
            if len(data_points) > 0:
                # Ensure data points are sorted by timestamp (most recent last)
                # Convert timestamps to datetime for proper sorting
                def get_timestamp_for_sort(dp):
                    ts = dp.get('timestamp')
                    if isinstance(ts, datetime):
                        return ts
                    elif isinstance(ts, str):
                        return convert_timestamp_to_datetime(ts) or datetime.min.replace(tzinfo=timezone.utc)
                    else:
                        return datetime.min.replace(tzinfo=timezone.utc)
                
                sorted_data_points = sorted(data_points, key=get_timestamp_for_sort)
                latest_dp = sorted_data_points[-1]
                latest_value = latest_dp.get('value')
                latest_timestamp = latest_dp.get('timestamp')
                logger.info(f"   ✅ Latest value from data_points: {latest_value} (timestamp: {latest_timestamp}, type: {type(latest_value)})")
            else:
                # If no data points in time range, check if parameter is currently active and fetch latest value
                is_currently_active = False
                if clean_param_name in param_metadata:
                    active_periods_raw = param_metadata[clean_param_name].get('active_periods', [])
                    active_periods = convert_active_periods_to_datetime(active_periods_raw)
                    
                    # Check if parameter is currently active (has period that includes end_time)
                    # Note: end_time is already timezone-aware (set at function start)
                    for period_start, period_end in active_periods:
                        period_start = convert_timestamp_to_datetime(period_start) if period_start else None
                        period_end = convert_timestamp_to_datetime(period_end) if period_end else None
                        if period_start and period_end and period_start <= end_time <= period_end:
                            is_currently_active = True
                            break
                else:
                    # No metadata - assume currently active (backward compatibility)
                    is_currently_active = True
                
                if is_currently_active:
                    # Fetch latest value from database (last 7 days)
                    latest_value = db_service.get_latest_value(
                        device_id=device_id,
                        parameter_name=clean_param_name
                    )
                    if latest_value is not None:
                        logger.info(f"   ✅ Latest value from database: {latest_value} (type: {type(latest_value)})")
                    else:
                        logger.info(f"   ⚠️ No latest value found in database for {clean_param_name}")
                else:
                    logger.info(f"   ⚠️ Parameter '{clean_param_name}' is not currently active, skipping latest value fetch")
            
            logger.info(f"   Final latest value: {latest_value} (type: {type(latest_value)})")
            
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
                # Ensure timestamps are datetime objects and convert to IST for display
                timestamps = []
                values = []
                for dp in data_points:
                    ts = dp['timestamp']
                    # Convert to datetime if it's a string
                    if isinstance(ts, str):
                        ts = convert_timestamp_to_datetime(ts)
                    elif isinstance(ts, datetime) and ts.tzinfo is None:
                        # Make timezone-aware if naive (assume UTC)
                        ts = ts.replace(tzinfo=timezone.utc)
                    
                    # Convert UTC timestamp to IST for display
                    if isinstance(ts, datetime) and ts.tzinfo:
                        ts = ts.astimezone(ist)
                    
                    timestamps.append(ts)
                    values.append(dp['value'])
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
                
                # Add trace with explicit metadata to ensure updates
                # Add trace with explicit metadata to ensure updates
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=plot_values,
                    mode='lines+markers',
                    name=param_name,
                    line=dict(color=color, width=3),
                    marker=dict(size=4),
                    fill='tozeroy',
                    fillcolor=fill_color,
                    # Add metadata to help Dash detect changes
                    meta={'update_time': end_time.isoformat(), 'data_points': len(plot_values)}
                ))
                
                logger.info(f"   ✅ Added trace for '{clean_param_name}': {len(plot_values)} points, range: {min(plot_values) if plot_values else 'N/A'} to {max(plot_values) if plot_values else 'N/A'}")
                
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
            
            # Get tick interval and format based on time range
            dtick_string, tick_format = get_xaxis_tick_interval(time_range)
            
            # Ensure start_time and end_time are datetime objects (not strings)
            # They should already be datetime objects, but double-check
            if isinstance(start_time, str):
                start_time = convert_timestamp_to_datetime(start_time)
            if isinstance(end_time, str):
                end_time = convert_timestamp_to_datetime(end_time)
            
            # Log time range for debugging
            logger.info(f"   📊 X-axis range for '{clean_param_name}': {start_time.strftime('%Y-%m-%d %H:%M:%S')} IST to {end_time.strftime('%Y-%m-%d %H:%M:%S')} IST (time_range: {time_range})")
            if timestamps:
                first_ts = timestamps[0] if timestamps else None
                last_ts = timestamps[-1] if timestamps else None
                if isinstance(first_ts, datetime):
                    logger.info(f"   📊 Data points range: {first_ts.strftime('%Y-%m-%d %H:%M:%S')} to {last_ts.strftime('%Y-%m-%d %H:%M:%S')} ({len(timestamps)} points)")
                else:
                    logger.info(f"   📊 Data points range: {first_ts} to {last_ts} ({len(timestamps)} points)")
            
            # Update layout with basic settings first
            fig.update_layout(
                margin=dict(l=60, r=20, t=20, b=50),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                hovermode='x unified',
                showlegend=False
            )
            
            # CRITICAL: Set X-axis range BEFORE updating axes (Plotly needs this order)
            # Use datetime objects directly - Plotly date axes accept datetime objects
            fig.update_layout(
                xaxis=dict(
                    range=[start_time, end_time],
                    autorange=False
                )
            )
            
            # Then update X-axis with all other settings
            fig.update_xaxes(
                showgrid=True,
                gridcolor='#e9ecef',
                title="Time",
                titlefont=dict(size=12),
                tickfont=dict(size=10),
                # Set tick interval
                dtick=dtick_string,
                # Format time display
                tickformat=tick_format,
                # Ensure timezone is handled correctly
                type='date',
                # Force autorange to False to enforce our range (redundant but ensures it's set)
                autorange=False
            )
            
            # Update Y-axis
            fig.update_yaxes(
                showgrid=True,
                gridcolor='#e9ecef',
                title="Value",
                titlefont=dict(size=12),
                tickfont=dict(size=10),
                range=[y_min, y_max] if y_min is not None and y_max is not None else None
            )
            
            # Add a unique identifier to force Dash to recognize this as a new figure
            # This ensures Dash updates the graph even if data structure is similar
            fig.update_layout(
                uirevision=False  # Disable UI revision to force updates
            )
            
            figures.append(fig)
        
        # ========== DETAILED CONSOLE LOGGING FOR DEBUGGING ==========
        logger.info("=" * 80)
        logger.info("✅ [ANALYTICS CALLBACK → UI] Step 7/7: CHARTS UPDATED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info(f"   📊 Updated Charts Count: {len(figures)}")
        logger.info(f"   📈 Live Values Count: {len(live_values)}")
        logger.info(f"   🏭 Device ID: {device_id}")
        logger.info(f"   📅 Current Time (IST): {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Ensure we return the correct number of outputs
        if len(figures) != len(live_values):
            logger.warning(f"   ⚠️ Mismatch: {len(figures)} figures but {len(live_values)} live values")
        
        # Log summary of data points for debugging
        total_data_points = sum(len(all_data.get(name, [])) for name in param_names)
        logger.info(f"   📊 Total Data Points: {total_data_points}")
        
        # Log live values for debugging
        if live_values:
            logger.info(f"   📋 Live Values Count: {len(live_values)}")
            # live_values is a list of HTML components, not a dictionary
            # Log parameter names alongside their values
            if param_names and len(param_names) == len(live_values):
                for i, param_name in enumerate(param_names):
                    logger.info(f"      • {param_name}: Live value component created")
            else:
                logger.info(f"      • {len(live_values)} live value component(s) created")
        
        # Final success log
        if trigger_id == 'analytics-rtd-trigger-store':
            logger.info("=" * 80)
            logger.info("🎉 [RTD FLOW COMPLETE] REAL-TIME UPDATE SUCCESSFUL!")
            logger.info("=" * 80)
            logger.info("   ✅ Complete Flow:")
            logger.info("      1️⃣ Hardware → MQTT (RTD/# topic)")
            logger.info("      2️⃣ MQTT → Database (InfluxDB save)")
            logger.info("      3️⃣ Database → Socket.IO (emit event)")
            logger.info("      4️⃣ Socket.IO → Client (receive event)")
            logger.info("      5️⃣ Client → Dash Store (set_props)")
            logger.info("      6️⃣ Dash Store → Analytics Callback (trigger)")
            logger.info("      7️⃣ Analytics Callback → UI (charts updated)")
            logger.info("   📈 Graphs and values should now be visible with latest data!")
            logger.info("=" * 80)
        else:
            logger.info("=" * 80)
        # ========== END DETAILED LOGGING ==========
        
        return figures, live_values
        
    except Exception as e:
        logger.error(f"❌ Error updating charts: {e}")
        logger.exception("Full error traceback:")
        
        # For ALL outputs, we need to return the correct number of empty outputs
        # Get parameter count from enabled_params if available
        param_count = 0
        if enabled_params and isinstance(enabled_params, dict):
            # Extract metadata and filter out metadata key
            param_metadata = enabled_params.get('_metadata', {})
            param_names = [k for k in enabled_params.keys() if k != '_metadata']
            param_count = len(param_names)
        
        # If we can't determine count, try to get from device config
        if param_count == 0 and device_id:
            try:
                from app.services.device_config_db import DeviceConfigDBService
                db_service = DeviceConfigDBService()
                # Get enabled parameters for this device
                device_config = db_service.get_device_config(device_id)
                if device_config and 'enabled_parameters' in device_config:
                    enabled_params_from_db = device_config.get('enabled_parameters', {})
                    param_metadata = enabled_params_from_db.get('_metadata', {})
                    param_names = [k for k in enabled_params_from_db.keys() if k != '_metadata']
                    param_count = len(param_names)
            except Exception as db_error:
                logger.error(f"❌ Error getting parameter count from DB: {db_error}")
        
        # Return empty outputs matching the expected count
        # Each parameter needs: 1 figure + 1 live value = 2 outputs per parameter
        if param_count > 0:
            logger.warning(f"⚠️ Returning {param_count} empty figure(s) and {param_count} empty live value(s) due to error")
            empty_figures = [go.Figure() for _ in range(param_count)]
            empty_live_values = [[html.Span("Error", className='fw-bold fs-5', style={'color': '#ef4444'})] for _ in range(param_count)]
            return empty_figures, empty_live_values
        else:
            # If we can't determine count, return empty lists (Dash will handle it)
            logger.warning(f"⚠️ Cannot determine parameter count, returning empty lists")
            return [], []
