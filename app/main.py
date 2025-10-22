"""
Main Application Entry Point
IOTNarad Dashboard with Dash + Flask-SocketIO
"""
import os
from dotenv import load_dotenv
import dash
from dash import dcc, html, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
from flask import Flask, session, request
from flask_socketio import SocketIO, emit
import logging

# Load environment variables
load_dotenv()

# Import services
from app.services.mqtt_client import MQTTClientService
from app.services.influx import InfluxDBService
from app.services.device_config import DeviceConfigService
from app.services.user_service import UserService
from app.services.email_service import EmailService

# Import pages
from app.pages.login import create_login_layout
from app.pages.dashboard import create_dashboard_layout
from app.pages.device_config import create_device_config_layout
from app.pages.analytics import create_analytics_layout
from app.pages.create_user import create_user_form_layout

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask server
server = Flask(__name__, static_folder='/app/assets', static_url_path='/assets')
server.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY', 'dev-secret-key-change-me')

# Initialize SocketIO
socketio = SocketIO(
    server,
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=True,
    engineio_logger=True
)

# Add route to serve logo directly
@server.route('/logo')
def serve_logo():
    return server.send_static_file('images/xaptronics-logo.png')

# Initialize Dash app with modern theme
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True,
    title="IOTNarad Dashboard",
    update_title=None
)

# Add custom CSS for navigation styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .sidebar .nav-item-custom {
                color: white !important;
                text-align: center !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                padding: 12px 20px !important;
            }
            .sidebar .nav-item-custom:hover {
                color: white !important;
                background-color: rgba(255,255,255,0.1) !important;
            }
            .sidebar .nav-item-custom.active {
                color: white !important;
                background-color: rgba(255,255,255,0.2) !important;
            }
            .sidebar .nav-item-custom span {
                color: white !important;
            }
            .sidebar .nav-item-custom i {
                color: white !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Initialize services
mqtt_service = MQTTClientService()
influx_service = InfluxDBService()
config_service = DeviceConfigService()
user_service = UserService()
email_service = EmailService()

# Admin credentials from environment
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'iotnarad@2025')

# ==================== LAYOUT ====================
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-store', storage_type='session'),
    dcc.Store(id='device-data-store', storage_type='memory'),
    dcc.Interval(id='data-update-interval', interval=2000, n_intervals=0),
    html.Div(id='page-content')
], fluid=True, className='p-0 m-0')


# ==================== CALLBACKS ====================

@app.callback(
    Output('page-content', 'children'),
    Output('session-store', 'data'),
    Input('url', 'pathname'),
    State('session-store', 'data')
)
def display_page(pathname, session_data):
    """Handle page routing and authentication"""
    session_data = session_data or {}
    
    # Check if user is logged in
    is_authenticated = session_data.get('authenticated', False)
    user_type = session_data.get('user_type', 'user')
    
    if pathname == '/dashboard' and is_authenticated:
        return create_dashboard_layout(), session_data
    elif pathname == '/create-user' and is_authenticated and user_type == 'admin':
        return create_user_form_layout(), session_data
    elif pathname == '/logout':
        # Clear session
        return create_login_layout(), {}
    elif not is_authenticated:
        # Redirect to login
        return create_login_layout(), session_data
    else:
        # Default to login
        return create_login_layout(), session_data


@app.callback(
    Output('session-store', 'data', allow_duplicate=True),
    Output('login-message', 'children'),
    Input('login-button', 'n_clicks'),
    State('username-input', 'value'),
    State('password-input', 'value'),
    State('session-store', 'data'),
    prevent_initial_call=True
)
def login_user(n_clicks, username, password, session_data):
    """Handle user login"""
    if not n_clicks:
        return session_data or {}, ''
    
    session_data = session_data or {}
    
    # Check admin credentials first
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session_data['authenticated'] = True
        session_data['username'] = username
        session_data['user_type'] = 'admin'
        logger.info(f"Admin {username} logged in successfully")
        return session_data, ''
    
    # Check user credentials in InfluxDB
    try:
        user = user_service.authenticate_user(username, password)
        if user:
            session_data['authenticated'] = True
            session_data['username'] = username
            session_data['user_type'] = user.get('User_Type', 'user')
            session_data['user_data'] = user
            logger.info(f"User {username} logged in successfully")
            return session_data, ''
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
    
    # Failed login
    logger.warning(f"Failed login attempt for username: {username}")
    return session_data, dbc.Alert(
        "Invalid username or password!",
        color="danger",
        dismissable=True,
        className="mt-3"
    )


@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('session-store', 'data'),
    State('url', 'pathname'),
    prevent_initial_call=True
)
def redirect_after_login(session_data, current_path):
    """Redirect to dashboard after successful login"""
    if session_data and session_data.get('authenticated') and current_path == '/':
        return '/dashboard'
    return current_path


# ==================== SOCKETIO EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connection_response', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('device_config_update')
def handle_device_config_update(data):
    """Handle device configuration updates from clients"""
    try:
        device_id = data.get('device_id')
        config = data.get('config')
        
        # Save configuration
        config_service.save_device_config(device_id, config)
        
        # Publish to MQTT for device to receive
        mqtt_service.publish_config(device_id, config)
        
        # Broadcast to all connected clients
        socketio.emit('config_updated', {
            'device_id': device_id,
            'config': config,
            'status': 'success'
        })
        
        logger.info(f"Configuration updated for device: {device_id}")
    except Exception as e:
        logger.error(f"Error updating device config: {e}")
        emit('config_update_error', {'error': str(e)})


@socketio.on('request_device_data')
def handle_device_data_request(data):
    """Handle request for device data"""
    try:
        device_id = data.get('device_id')
        time_range = data.get('time_range', '1h')
        
        # Fetch data from InfluxDB
        device_data = influx_service.get_device_data(device_id, time_range)
        
        emit('device_data_response', {
            'device_id': device_id,
            'data': device_data
        })
    except Exception as e:
        logger.error(f"Error fetching device data: {e}")
        emit('device_data_error', {'error': str(e)})


@socketio.on('create_user')
def handle_create_user(data):
    """Handle user creation from create user page"""
    try:
        # Check if user ID already exists
        existing_user = user_service.get_user_by_id(data.get('User_Id'))
        if existing_user:
            emit('user_creation_error', {
                'status': 'error',
                'message': f"User ID '{data.get('User_Id')}' already exists. Please choose a different User ID."
            })
            return
        
        # Create user using user service
        success = user_service.create_user(data)
        
        if success:
            # Send email with credentials
            email_sent = email_service.send_user_credentials(data)
            
            logger.info(f"User created successfully: {data.get('User_Id')}")
            logger.info(f"Generated password: {data.get('Password')}")
            logger.info(f"Email sent to: {data.get('Email_Id')} - Status: {'Success' if email_sent else 'Failed'}")
            
            emit('user_created', {
                'status': 'success',
                'message': f"User {data.get('User_Id')} created successfully" + 
                          (" and credentials sent via email" if email_sent else " but email sending failed"),
                'user_id': data.get('User_Id'),
                'email': data.get('Email_Id'),
                'password': data.get('Password'),
                'email_sent': email_sent
            })
        else:
            emit('user_creation_error', {
                'status': 'error',
                'message': 'Failed to create user in database'
            })
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        emit('user_creation_error', {
            'status': 'error',
            'message': str(e)
        })


# MQTT callback to forward data to WebSocket clients
def on_device_data_received(device_id, data):
    """Callback when MQTT receives device data"""
    try:
        # Store in InfluxDB
        influx_service.write_device_data(device_id, data)
        
        # Broadcast to WebSocket clients
        socketio.emit('device_data_update', {
            'device_id': device_id,
            'data': data,
            'timestamp': data.get('timestamp')
        })
        
        logger.debug(f"Data received from device {device_id}: {data}")
    except Exception as e:
        logger.error(f"Error processing device data: {e}")


# Set MQTT callback
mqtt_service.set_data_callback(on_device_data_received)


# ==================== MAIN ====================

if __name__ == '__main__':
    # Start MQTT client
    mqtt_service.start()
    
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8050))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting IOTNarad Dashboard on {HOST}:{PORT}")
    logger.info(f"Admin Username: {ADMIN_USERNAME}")
    
    # Run with SocketIO
    socketio.run(
        server,
        host=HOST,
        port=PORT,
        debug=DEBUG,
        use_reloader=DEBUG
    )
