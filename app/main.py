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
import time
from datetime import datetime
from typing import Dict, Any
from threading import Lock

# Load environment variables
load_dotenv()

# Import services
from app.services.mqtt_client import MQTTClientService
from app.services.influx import InfluxDBService
from app.services.device_config import DeviceConfigService
from app.services.user_service import UserService
from app.services.email_service import EmailService
from app.services.device_info_service import DeviceInfoService
from app.services.device_config_provider import DeviceConfigProviderService
from app.services.device_config_db import DeviceConfigDBService
from app.services.realtime_data_db import RealtimeDataDBService

# Import pages
from app.pages.login import create_login_layout
from app.pages.dashboard import create_dashboard_layout
from app.pages.device_config import create_device_config_layout
from app.pages.analytics import create_analytics_layout
from app.pages.create_user import create_user_form_layout
from app.pages.change_password import create_change_password_layout
# Import change_password module to register callbacks
import app.pages.change_password
# Import rs485_modbus and can_bus modules to register callbacks
import app.pages.rs485_modbus
import app.pages.can_bus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask server
server = Flask(__name__, static_folder='../assets', static_url_path='/assets')
server.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY', 'dev-secret-key-change-me')
# Configure session to work reliably across different domains/IPs
server.config['SESSION_COOKIE_HTTPONLY'] = True
server.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
server.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Initialize SocketIO
socketio = SocketIO(
    server,
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=True,
    engineio_logger=True
)

# Initialize Dash app with modern theme
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    assets_folder='../assets',  # Point to assets folder for CSS files
    suppress_callback_exceptions=True,
    title="IOTNarad Dashboard",
    update_title=None
)

# Initialize services
mqtt_service = MQTTClientService()
influx_service = InfluxDBService()
config_service = DeviceConfigService()
user_service = UserService()
email_service = EmailService()
device_info_service = DeviceInfoService()
device_config_db_service = DeviceConfigDBService()
realtime_data_db_service = RealtimeDataDBService()
device_config_provider_service = DeviceConfigProviderService(mqtt_service, device_config_db_service)

# Admin credentials from environment
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'iotnarad@2025')

# Server-side session storage (fallback when browser sessionStorage fails)
# Key: session_id (from Flask session), Value: session data dict
_server_sessions: Dict[str, Dict[str, Any]] = {}

def invalidate_user_sessions(user_id: str, reason: str = "User data changed"):
    """Invalidate all sessions for a specific user ID
    
    This function should be called whenever user data is modified or deleted
    to ensure old sessions become invalid immediately.
    
    Args:
        user_id: The User ID whose sessions should be invalidated
        reason: Reason for invalidation (for logging)
    
    Returns:
        int: Number of sessions invalidated
    """
    global _server_sessions
    from flask import session as flask_session, has_request_context
    
    sessions_invalidated = 0
    
    # Clear all server-side sessions for this user
    sessions_to_delete = [
        k for k, v in _server_sessions.items() 
        if v.get('username') == user_id
    ]
    
    for key in sessions_to_delete:
        del _server_sessions[key]
        sessions_invalidated += 1
        logger.info(f"🔒 Invalidated session: {key[:20]}... for user '{user_id}' - Reason: {reason}")
    
    if has_request_context():
        # If current request is from this user, clear their Flask session too
        current_user = flask_session.get('username')
        if current_user == user_id:
            flask_session.clear()
            flask_session.permanent = False
            flask_session.modified = True
            logger.info(f"🔒 Cleared Flask session for current user '{user_id}' - Reason: {reason}")
    
    if sessions_invalidated > 0:
        logger.warning(f"🚨 Invalidated {sessions_invalidated} session(s) for user '{user_id}' - Reason: {reason}")
    else:
        logger.debug(f"ℹ️ No active sessions found for user '{user_id}' to invalidate")
    
    return sessions_invalidated

# ==================== LAYOUT ====================
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False, pathname='/'),
    dcc.Store(id='session-store', storage_type='session'),
    dcc.Store(id='device-data-store', storage_type='memory'),
    dcc.Interval(id='data-update-interval', interval=2000, n_intervals=0),
    html.Div(id='page-content'),
    # SocketIO client library - loaded globally for all pages
    html.Script(src="https://cdn.socket.io/4.5.4/socket.io.min.js"),
    # Client-side script to sync Flask session with Dash store on page load
    html.Script("""
        // Sync Flask session with Dash session store on page load
        (function() {
            fetch('/api/session/status')
                .then(response => response.json())
                .then(data => {
                    if (data.authenticated) {
                        // Update session store if authenticated
                        const event = new CustomEvent('flask-session-sync', {
                            detail: {
                                authenticated: data.authenticated,
                                username: data.username,
                                user_type: data.user_type
                            }
                        });
                        window.dispatchEvent(event);
                    }
                })
                .catch(err => console.log('Session sync error:', err));
        })();
    """),
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
    from flask import session as flask_session, has_request_context
    
    global _server_sessions
    
    session_data = session_data or {}
    pathname = pathname or '/'
    
    # CRITICAL: Check Flask server-side session first (more reliable than client-side storage)
    # This ensures authentication works even if browser sessionStorage fails
    flask_authenticated = False
    flask_user_type = 'user'
    flask_username = ''
    server_session_id = None
    recent_failed_login = False  # Initialize outside try block so it's accessible later
    
    # CRITICAL FIX: Access Flask session using request context
    # Dash callbacks run in Flask request context, so we can access session directly
    try:
        # Get Flask session cookie from request
        session_cookie = request.cookies.get('session', '')
        
        # CRITICAL: Check for failed login flag FIRST - if login just failed, ignore any old session
        # This MUST be checked before reading any other session data
        recent_failed_login = flask_session.get('_login_failed', False)
        if recent_failed_login:
            failed_user = flask_session.get('_failed_login_user', 'unknown')
            logger.warning(f"🚫 Recent failed login detected for user '{failed_user}' - Ignoring old session cookie for security")
            # Clear the failed login flag after using it (but keep session cleared)
            flask_session.pop('_login_failed', None)
            flask_session.pop('_failed_login_user', None)
            flask_session.modified = True
            # Don't read any other session data if login failed
            flask_authenticated = False
            flask_username = ''
            flask_user_type = 'user'
        else:
            # Only read session data if no failed login flag
            # Check Flask session directly
            flask_authenticated = flask_session.get('authenticated', False)
            flask_user_type = flask_session.get('user_type', 'user')
            flask_username = flask_session.get('username', '')
            
            # Also check server-side session storage (backup for IP address access)
            if session_cookie and session_cookie in _server_sessions:
                server_session = _server_sessions[session_cookie]
                if not flask_authenticated and server_session.get('authenticated'):
                    flask_authenticated = True
                    flask_user_type = server_session.get('user_type', 'user')
                    flask_username = server_session.get('username', '')
                    logger.info(f"✅ Using server-side session backup - User: {flask_username}, Type: {flask_user_type}")
        
        logger.info(f"🔐 Flask session check - Cookie: {session_cookie[:20] if session_cookie else 'None'}..., Auth: {flask_authenticated}, User: {flask_username}, Type: {flask_user_type}, Failed Login: {recent_failed_login}")
        
        # CRITICAL: Verify user exists in database if session says authenticated
        # This prevents access with old/invalid session cookies
        if flask_authenticated and flask_username:
            # Log that we're using an existing session (user didn't explicitly login just now)
            session_created_at = flask_session.get('session_created_at')
            if session_created_at:
                session_age_seconds = time.time() - session_created_at
                session_age_hours = session_age_seconds / 3600
                logger.info(f"📝 Using existing session cookie (Age: {session_age_hours:.2f} hours) - User didn't login in this request")
            
            # CRITICAL: Expire very old sessions (e.g., older than 30 days) for security
            # This prevents indefinitely stale sessions
            SESSION_MAX_AGE_HOURS = 30 * 24  # 30 days
            if session_created_at:
                session_age_seconds = time.time() - session_created_at
                session_age_hours = session_age_seconds / 3600
                if session_age_hours > SESSION_MAX_AGE_HOURS:
                    logger.warning(f"⏰ Session expired due to age ({session_age_hours:.2f} hours > {SESSION_MAX_AGE_HOURS} hours) - Clearing old session")
                    flask_authenticated = False
                    flask_username = ''
                    flask_user_type = 'user'
                    flask_session.clear()
                    flask_session.permanent = False
                    flask_session.modified = True
                    if session_cookie and session_cookie in _server_sessions:
                        del _server_sessions[session_cookie]
                    logger.info(f"🔒 Old session cleared - User must login again")
            
            if flask_authenticated:  # Only continue validation if session not expired
                try:
                    db_user = user_service.get_user_by_id(flask_username)
                    logger.info(f"🔍 Database verification for session user '{flask_username}': user_service returned: {type(db_user)}, exists: {db_user is not None}")
                    
                    if db_user is None or not isinstance(db_user, dict) or db_user.get('User_Id') != flask_username:
                        logger.warning(f"❌ Session user '{flask_username}' not found in database - Invalidating session")
                        logger.warning(f"   db_user type: {type(db_user)}, value: {db_user}")
                        flask_authenticated = False
                        flask_username = ''
                        flask_user_type = 'user'
                        # Clear invalid session completely
                        flask_session.clear()
                        flask_session.permanent = False
                        flask_session.modified = True
                        # Clear server-side storage
                        if session_cookie and session_cookie in _server_sessions:
                            del _server_sessions[session_cookie]
                        # Also clear any matching sessions
                        cookie_prefix = session_cookie[:20] if session_cookie else ''
                        sessions_to_delete = [k for k in list(_server_sessions.keys()) if k.startswith(cookie_prefix) or cookie_prefix in k]
                        for key in sessions_to_delete:
                            del _server_sessions[key]
                    else:
                        # CRITICAL: Check if user data was changed after session was created
                        # This invalidates sessions when ANY user data changes (password, permissions, deletion, etc.)
                        db_user_updated_at = db_user.get('User_Updated_At')
                        session_user_updated_at = flask_session.get('user_updated_at')
                        
                        # Also check password changed timestamp for backward compatibility
                        db_password_changed_at = db_user.get('Password_Changed_At')
                        session_password_changed_at = flask_session.get('password_changed_at')
                        
                        # Priority: User_Updated_At > Password_Changed_At (User_Updated_At is more comprehensive)
                        user_data_changed = False
                        reason = ""
                        
                        if db_user_updated_at is not None:
                            # Use User_Updated_At (tracks ALL user data changes)
                            if session_user_updated_at is None or session_user_updated_at != db_user_updated_at:
                                user_data_changed = True
                                reason = f"User data changed (DB User_Updated_At: {db_user_updated_at}, Session: {session_user_updated_at})"
                        elif db_password_changed_at is not None:
                            # Fallback to Password_Changed_At for older records
                            if session_password_changed_at is None or session_password_changed_at != db_password_changed_at:
                                user_data_changed = True
                                reason = f"Password changed (DB Password_Changed_At: {db_password_changed_at}, Session: {session_password_changed_at})"
                        
                        if user_data_changed:
                            # User data was changed after session was created, invalidate ALL sessions for this user
                            logger.warning(f"🔒 User data changed for user '{flask_username}' - Invalidating old session")
                            logger.warning(f"   Reason: {reason}")
                            
                            flask_authenticated = False
                            flask_username = ''
                            flask_user_type = 'user'
                            
                            # Clear invalid session completely
                            flask_session.clear()
                            flask_session.permanent = False
                            flask_session.modified = True
                            
                            # Clear ALL server-side sessions for this user (not just current cookie)
                            if session_cookie and session_cookie in _server_sessions:
                                del _server_sessions[session_cookie]
                            
                            # Clear all sessions matching this user ID
                            user_sessions_to_delete = [
                                k for k, v in _server_sessions.items() 
                                if v.get('username') == flask_username
                            ]
                            for key in user_sessions_to_delete:
                                del _server_sessions[key]
                                logger.info(f"   🗑️ Deleted session: {key[:20]}...")
                            
                            # Also clear any matching sessions by cookie prefix
                            cookie_prefix = session_cookie[:20] if session_cookie else ''
                            if cookie_prefix:
                                sessions_to_delete = [k for k in list(_server_sessions.keys()) if k.startswith(cookie_prefix) or cookie_prefix in k]
                                for key in sessions_to_delete:
                                    del _server_sessions[key]
                        else:
                            logger.info(f"✅ Session validated - User '{flask_username}' exists and data unchanged (User_Id: {db_user.get('User_Id')}, User_Updated_At: {db_user_updated_at})")
                except Exception as e:
                    logger.error(f"❌ Error verifying session user in database: {e}")
                    # On error, invalidate session for security
                    flask_authenticated = False
                    flask_username = ''
                    flask_user_type = 'user'
                    flask_session.clear()
                    if session_cookie and session_cookie in _server_sessions:
                        del _server_sessions[session_cookie]
    except Exception as e:
        logger.error(f"❌ Error accessing Flask session: {e}", exc_info=True)
        flask_authenticated = False
        flask_user_type = 'user'
        flask_username = ''
    
    # Sync Flask session with client-side store (only if validated and not failed login)
    # Note: recent_failed_login is already checked above, and flask_authenticated is set to False if it was True
    if flask_authenticated and flask_username and not recent_failed_login:
        session_data['authenticated'] = True
        session_data['username'] = flask_username
        session_data['user_type'] = flask_user_type
        if has_request_context() and flask_session.get('user_data'):
            session_data['user_data'] = flask_session.get('user_data')
    else:
        # Clear invalid session data from client store
        session_data.pop('authenticated', None)
        session_data.pop('username', None)
        session_data.pop('user_type', None)
        session_data.pop('user_data', None)
        session_data.pop('_login_failed', None)  # Also remove failed login flag from client store
    
    # Check if user is logged in (prefer Flask session, fallback to client store)
    # But only trust client store if we don't have Flask session (for initial login)
    # AND ensure we don't use old session if login just failed
    is_authenticated = (flask_authenticated and not recent_failed_login) or (not flask_username and session_data.get('authenticated', False) and not session_data.get('_login_failed', False))
    user_type = flask_user_type if (flask_authenticated and not recent_failed_login) else session_data.get('user_type', 'user')
    
    logger.info(f"🔍 Page routing - Path: {pathname}, Flask Auth: {flask_authenticated}, Client Auth: {session_data.get('authenticated', False)}, Failed Login Flag: {recent_failed_login}, User Type: {user_type}, Username: {flask_username or session_data.get('username', 'N/A')}")
    
    # Handle logout
    if pathname == '/logout':
        logger.info("User logging out")
        from flask import session as flask_session
        flask_session.clear()
        return create_login_layout(), {}
    
    # Protected routes - require authentication
    if pathname == '/dashboard':
        if is_authenticated:
            logger.info(f"Loading dashboard for user: {session_data.get('username', 'unknown')}")
            return create_dashboard_layout(), session_data
        else:
            logger.warning("Unauthenticated access attempt to dashboard")
            return create_login_layout(), session_data
    
    if pathname == '/create-user':
        # Get username (User_Id) from session
        username = flask_username or session_data.get('username', '')
        # Check if User_Id is admin (only check username/User_Id == 'admin')
        is_admin = (is_authenticated and username == 'admin')
        
        logger.info(f"🔐 Create-user access check - Authenticated: {is_authenticated}, User_Id: {username}, Is Admin: {is_admin}, Flask Session: {flask_authenticated}")
        
        if is_admin:
            logger.info(f"✅ Loading create user page for admin User_Id: {username}")
            return create_user_form_layout(), session_data
        elif not is_authenticated:
            logger.warning(f"❌ Unauthenticated access attempt to create-user - Flask: {flask_authenticated}, Client: {session_data.get('authenticated', False)}")
            return create_login_layout(), session_data
        else:
            logger.warning(f"❌ Non-admin User_Id ({username}) attempted to access create-user")
            return create_login_layout(), session_data
    
    if pathname == '/change-password':
        if is_authenticated:
            logger.info(f"Loading change password page for user: {session_data.get('username', 'unknown')}")
            return create_change_password_layout(), session_data
        else:
            logger.warning("Unauthenticated access attempt to change-password")
            return create_login_layout(), session_data
    
    # Root path (/) - show login if not authenticated
    if pathname == '/':
        if not is_authenticated:
            logger.info("Showing login page at root path")
            return create_login_layout(), session_data
        else:
            # Authenticated user at root - redirect callback will handle, but show login temporarily
            # (redirect callback will change pathname to /dashboard)
            logger.info("Authenticated user at root - redirect callback will handle")
            return create_login_layout(), session_data
    
    # Any other path - if authenticated show dashboard, else show login
    if not is_authenticated:
        logger.info(f"Unauthenticated access to {pathname}, showing login")
        return create_login_layout(), session_data
    else:
        # Authenticated but unknown path - show dashboard
        logger.info(f"Authenticated user on unknown path {pathname}, showing dashboard")
        return create_dashboard_layout(), session_data


@app.callback(
    Output('session-store', 'data', allow_duplicate=True),
    Output('login-message', 'children'),
    Output('url', 'pathname', allow_duplicate=True),
    Input('login-button', 'n_clicks'),
    State('username-input', 'value'),
    State('password-input', 'value'),
    State('session-store', 'data'),
    State('url', 'pathname'),
    prevent_initial_call=True
)
def login_user(n_clicks, username, password, session_data, current_path):
    """Handle user login - Database authentication only"""
    global _server_sessions  # Declare global at the start of the function
    
    if not n_clicks:
        return session_data or {}, '', current_path or '/'
    
    session_data = session_data or {}
    
    # Validate input - strict validation
    if not username or not password:
        logger.warning(f"Login attempt with empty fields - Username: {bool(username)}, Password: {bool(password)}")
        return session_data, dbc.Alert(
            "Please enter User ID and Password!",
            color="warning",
            dismissable=True,
            className="mt-3"
        ), current_path or '/'
    
    # Trim and validate again
    username = username.strip() if username else ''
    password = password.strip() if password else ''
    
    if not username or not password:
        logger.warning(f"Login attempt with empty fields after trimming - Username: '{username}', Password: '{password}'")
        return session_data, dbc.Alert(
            "Please enter User ID and Password!",
            color="warning",
            dismissable=True,
            className="mt-3"
        ), current_path or '/'
    
    # Check user credentials in InfluxDB
    user = None
    try:
        user = user_service.authenticate_user(username, password)
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        logger.exception("Full error traceback:")
        # On any error, authentication fails
        user = None
    
    # CRITICAL STRICT CHECK: Only set authenticated if user is valid and returned from database
    # User must be a dict with all required fields
    if (user is not None and 
        isinstance(user, dict) and 
        user.get('User_Id') is not None and
        user.get('User_Id') == username and
        len(str(user.get('User_Id', ''))) > 0):
        
        # Additional validation: Ensure user has required fields
        required_fields = ['User_Id', 'User_Type']
        has_all_fields = all(user.get(field) is not None for field in required_fields)
        
        if has_all_fields:
            logger.info(f"✅ User {username} authenticated successfully (Type: {user.get('User_Type', 'user')})")
            
            # CRITICAL: Store in Flask server-side session (more reliable)
            from flask import session as flask_session, has_request_context
            
            if has_request_context():
                flask_session.permanent = True
                flask_session['authenticated'] = True
                flask_session['username'] = username
                flask_session['user_type'] = user.get('User_Type', 'user')
                flask_session['user_data'] = user
                
                # CRITICAL: Store user updated timestamp in session
                # This allows us to verify if user data was changed after session creation
                # Priority: User_Updated_At > Password_Changed_At (User_Updated_At tracks ALL changes)
                user_updated_at = user.get('User_Updated_At')
                password_changed_at = user.get('Password_Changed_At')
                
                if user_updated_at is not None:
                    flask_session['user_updated_at'] = user_updated_at
                elif password_changed_at is not None:
                    # Fallback for older records without User_Updated_At
                    flask_session['password_changed_at'] = password_changed_at
                
                flask_session['session_created_at'] = datetime.utcnow().timestamp()
                
                # Also store in server-side backup storage (keyed by session cookie)
                # This ensures session works even when browser sessionStorage fails on IP addresses
                session_cookie = request.cookies.get('session') or flask_session.get('_id') or str(id(flask_session))
                _server_sessions[session_cookie] = {
                    'authenticated': True,
                    'username': username,
                    'user_type': user.get('User_Type', 'user'),
                    'user_data': user,
                    'user_updated_at': user_updated_at,
                    'password_changed_at': password_changed_at,
                    'session_created_at': datetime.utcnow().timestamp()
                }
                logger.info(f"💾 Stored session in server-side storage: {session_cookie[:20]}... (User: {username}, Type: {user.get('User_Type', 'user')}, User_Updated_At: {user_updated_at}, Password_Changed_At: {password_changed_at})")
            
            # Also update client-side store
            session_data['authenticated'] = True
            session_data['username'] = username
            session_data['user_type'] = user.get('User_Type', 'user')
            session_data['user_data'] = user
            
            # Redirect to dashboard after successful login
            return session_data, '', '/dashboard'
        else:
            logger.warning(f"❌ Authentication failed - User object missing required fields: {user}")
    else:
        logger.warning(f"❌ Authentication failed - Invalid user object for User ID: '{username}' - User: {user}")
    
    # Authentication failed - log and return error
    # CRITICAL: Clear Flask session and server-side session storage on failed login
    # This prevents old session cookies from being used after failed login
    from flask import session as flask_session, has_request_context
    from flask import session as flask_session_modify
    
    if has_request_context():
        # Get session cookie BEFORE clearing (to identify which session to remove)
        session_cookie = request.cookies.get('session', '') or flask_session.get('_id', '') or str(id(flask_session))
        
        # Clear Flask session completely BUT keep a flag to indicate failed login
        # This flag prevents old sessions from being used after failed login
        old_session_data = dict(flask_session)  # Save old data to clear selectively
        flask_session.clear()
        flask_session.permanent = False  # Disable permanent session
        
        # Set a flag to indicate login failed (prevents using old session on next request)
        # This MUST be set after clear() so it persists
        flask_session['_login_failed'] = True
        flask_session['_failed_login_user'] = username  # Store which user failed for logging
        flask_session.modified = True  # Mark as modified to ensure cookie is updated
        
        # Clear server-side session storage
        if session_cookie and session_cookie in _server_sessions:
            del _server_sessions[session_cookie]
            logger.info(f"🔒 Cleared server-side session storage for cookie: {session_cookie[:20]}...")
        
        # Also clear any sessions that might match the current cookie pattern
        cookie_prefix = session_cookie[:20] if session_cookie else ''
        sessions_to_delete = [k for k in list(_server_sessions.keys()) if k.startswith(cookie_prefix) or cookie_prefix in k]
        for key in sessions_to_delete:
            del _server_sessions[key]
        
        logger.info("🔒 Cleared Flask session due to failed login and set failed login flag")
    
    # Clear any existing authentication state to prevent session hijacking
    session_data = {}  # Reset to empty dict instead of just clearing fields
    session_data['authenticated'] = False
    session_data['_login_failed'] = True  # Set flag in client store too
    
    logger.warning(f"❌ Login failed for User ID: '{username}' - All sessions cleared and failed login flag set")
    
    return session_data, dbc.Alert(
        "Invalid User ID or Password!",
        color="danger",
        dismissable=True,
        className="mt-3"
    ), current_path or '/'


@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('session-store', 'data'),
    State('url', 'pathname'),
    prevent_initial_call=True
)
def redirect_after_login(session_data, current_path):
    """Redirect to dashboard after successful login - backup redirect"""
    current_path = current_path or '/'
    
    if session_data and session_data.get('authenticated'):
        # If authenticated and on root path, redirect to dashboard
        if current_path == '/':
            logger.info("Redirecting authenticated user from root to dashboard")
            return '/dashboard'
        # If authenticated but not on dashboard or create-user, redirect to dashboard
        elif current_path not in ['/dashboard', '/create-user']:
            logger.info(f"Redirecting authenticated user to dashboard from {current_path}")
            return '/dashboard'
    elif not session_data or not session_data.get('authenticated'):
        # If not authenticated and trying to access protected routes, redirect to root
        if current_path in ['/dashboard', '/create-user']:
            logger.info(f"Unauthenticated access to {current_path}, redirecting to root")
            return '/'
    
    return current_path


# ==================== FORGOT PASSWORD CALLBACKS ====================

@app.callback(
    Output('forgot-password-modal', 'is_open'),
    [Input('forgot-password-link', 'n_clicks'),
     Input('forgot-password-cancel', 'n_clicks'),
     Input('forgot-password-submit', 'n_clicks')],
    [State('forgot-password-modal', 'is_open')],
    prevent_initial_call=True
)
def toggle_forgot_password_modal(link_clicks, cancel_clicks, submit_clicks, is_open):
    """Toggle forgot password modal"""
    from dash import ctx
    if ctx.triggered_id == 'forgot-password-link':
        return True
    elif ctx.triggered_id in ['forgot-password-cancel', 'forgot-password-submit']:
        return False
    return is_open


@app.callback(
    Output('forgot-password-message', 'children'),
    Output('forgot-user-id', 'value'),
    Output('forgot-phone-no', 'value'),
    Input('forgot-password-submit', 'n_clicks'),
    [State('forgot-user-id', 'value'),
     State('forgot-phone-no', 'value')],
    prevent_initial_call=True
)
def handle_forgot_password(n_clicks, user_id, phone_no):
    """Handle forgot password request"""
    import secrets
    import string
    
    if not n_clicks or n_clicks == 0:
        return '', '', ''
    
    # Validate input
    if not user_id or not phone_no:
        return dbc.Alert(
            "Please enter User ID and Phone Number!",
            color="warning",
            dismissable=True
        ), user_id or '', phone_no or ''
    
    # Clean phone number (remove spaces, dashes)
    phone_no_clean = phone_no.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    try:
        # Generate new password
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        new_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        # Reset password in database
        success = user_service.reset_password(user_id, phone_no_clean, new_password)
        
        if success:
            # Get user email for sending
            user = user_service.get_user_by_id_and_phone(user_id, phone_no_clean)
            if user:
                email = user.get('Email_Id')
                
                # Send email with new password
                email_data = {
                    'User_Id': user_id,
                    'Email_Id': email,
                    'Password': new_password,
                    'Company_Name': user.get('Company_Name', 'User'),
                    'User_Type': user.get('User_Type', 'user'),
                    'Status': user.get('status', 'active')
                }
                
                email_sent = email_service.send_user_credentials(email_data)
                
                if email_sent:
                    logger.info(f"Password reset successful for {user_id}. Email sent to {email}")
                    return dbc.Alert([
                        html.H4([
                            html.I(className="fas fa-check-circle me-2"),
                            "Password Reset Successful!"
                        ], className='fw-bold'),
                        html.P([
                            f"New password has been sent to your registered email: {email}",
                            html.Br(),
                            html.Small("Please check your inbox and spam folder.", className='text-muted')
                        ])
                    ], color="success", dismissable=True), '', ''
                else:
                    logger.warning(f"Password reset successful but email sending failed for {user_id}")
                    return dbc.Alert([
                        html.H4([
                            html.I(className="fas fa-exclamation-triangle me-2"),
                            "Password Reset Successful"
                        ], className='fw-bold'),
                        html.P([
                            "Your password has been reset, but email sending failed.",
                            html.Br(),
                            html.Strong(f"New Password: "),
                            html.Code(new_password, style={'background': '#f8f9fa', 'padding': '4px 8px', 'borderRadius': '4px'})
                        ])
                    ], color="warning", dismissable=True), '', ''
            else:
                return dbc.Alert(
                    "Password reset successful but could not retrieve user email.",
                    color="warning",
                    dismissable=True
                ), '', ''
        else:
            logger.warning(f"Password reset failed for User ID: {user_id}, Phone: {phone_no_clean}")
            return dbc.Alert([
                html.H4([
                    html.I(className="fas fa-times-circle me-2"),
                    "Password Reset Failed"
                ], className='fw-bold'),
                html.P("Invalid User ID or Phone Number. Please check your details and try again.")
            ], color="danger", dismissable=True), user_id or '', phone_no or ''
            
    except Exception as e:
        logger.error(f"Error in forgot password: {e}")
        logger.exception("Full error traceback:")
        return dbc.Alert([
            html.H4([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "Error"
            ], className='fw-bold'),
            html.P(f"An error occurred: {str(e)}")
        ], color="danger", dismissable=True), user_id or '', phone_no or ''


# ==================== FLASK ROUTES FOR SESSION MANAGEMENT ====================

@server.route('/api/session/status', methods=['GET'])
def get_session_status():
    """API endpoint to get current session status - helps with authentication across different domains"""
    from flask import jsonify
    try:
        auth_status = {
            'authenticated': session.get('authenticated', False),
            'username': session.get('username', ''),
            'user_type': session.get('user_type', 'user'),
            'has_session': bool(session)
        }
        logger.debug(f"Session status API called: {auth_status}")
        return jsonify(auth_status), 200
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        return jsonify({'authenticated': False, 'error': str(e)}), 500


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
        logger.info(f"Received create_user request: {data}")
        
        # Validate required fields
        required_fields = ['User_Id', 'Company_Name', 'Email_Id', 'Phone_No', 'User_Type', 'Password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            emit('user_creation_error', {
                'status': 'error',
                'message': f"Missing required fields: {', '.join(missing_fields)}"
            })
            return
        
        # Check if user ID already exists
        existing_user = user_service.get_user_by_id(data.get('User_Id'))
        if existing_user:
            logger.warning(f"User ID '{data.get('User_Id')}' already exists")
            emit('user_creation_error', {
                'status': 'error',
                'message': f"User ID '{data.get('User_Id')}' already exists. Please choose a different User ID."
            })
            return
        
        # Create user using user service
        logger.info(f"Attempting to create user: {data.get('User_Id')}")
        success = user_service.create_user(data)
        
        if success:
            # Send email with credentials
            email_sent = email_service.send_user_credentials(data)
            
            logger.info(f"✅ User created successfully: {data.get('User_Id')}")
            logger.info(f"   Generated password: {data.get('Password')}")
            logger.info(f"   Email sent to: {data.get('Email_Id')} - Status: {'Success' if email_sent else 'Failed'}")
            
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
            logger.error(f"Failed to create user: {data.get('User_Id')}")
            emit('user_creation_error', {
                'status': 'error',
                'message': 'Failed to create user in database. Please check server logs for details.'
            })
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        logger.exception("Full error traceback:")
        emit('user_creation_error', {
            'status': 'error',
            'message': f"An error occurred: {str(e)}"
        })


# In-memory deduplication: Track recently processed serial numbers
# Prevents duplicate processing of the same serial number within 5 seconds
# Format: {serial_number: (timestamp, is_processing)}
_recently_processed: Dict[str, tuple] = {}
# Set to track currently processing serial numbers (for immediate duplicate rejection)
_currently_processing: set = set()
_processing_lock = Lock()
_DEDUP_WINDOW_SECONDS = 5.0  # Ignore same serial number if processed within last 5 seconds


# MQTT callback for device initialization
def on_device_init_received(topic: str, data: Dict[str, Any]):
    """
    Callback when MQTT receives device initialization message
    Handles device registration on topic: Dev/Init/#
    """
    # Declare global at the start of function
    global _recently_processed, _currently_processing
    
    try:
        logger.info(f"📨 Device initialization message received on topic: {topic}")
        logger.info(f"   Payload: {data}")
        logger.info(f"   Payload type: {type(data)}")
        
        # Process Dev/Init/<SerialNumber> messages
        # Acknowledgments are published to Dev/Ack/<SerialNumber> (separate topic)
        
        # Extract serial number from payload
        serial_number = data.get('SerialNumber')
        if not serial_number:
            logger.warning("⚠️ SerialNumber not found in payload")
            # Try to extract from topic if not in payload
            # Topic format: Dev/Init/<SerialNumber>
            topic_parts = topic.split('/')
            if len(topic_parts) >= 3:
                serial_number = topic_parts[2]
            else:
                logger.error(f"❌ Cannot extract serial number from topic: {topic}")
                return
        
        serial_number = str(serial_number).strip()
        logger.info(f"🔍 Processing serial number: {serial_number}")
        
        # Validate serial number - reject invalid values
        if not serial_number or serial_number.upper() == "ACK" or len(serial_number) < 3:
            logger.warning(f"⚠️ Invalid serial number rejected: '{serial_number}'")
            return
        
        # In-memory deduplication: Check if this serial number is being processed or was recently processed
        # Use atomic check-and-set pattern to prevent race conditions
        current_time = time.time()
        
        # CRITICAL: Use a set for immediate duplicate detection (faster than dict lookup)
        is_duplicate = False
        should_send_ack = False
        
        with _processing_lock:
            # First check: Is it currently being processed? (fastest check)
            if serial_number in _currently_processing:
                logger.warning(f"⚠️ Serial number '{serial_number}' is currently being processed. Ignoring duplicate message.")
                is_duplicate = True
                should_send_ack = True  # Always send ACK for duplicates
                # Don't return yet - send ACK first
            # Second check: Was it recently processed?
            elif serial_number in _recently_processed:
                last_timestamp, is_processing = _recently_processed[serial_number]
                time_since_last = current_time - last_timestamp
                
                # If processed recently (within dedup window), reject but send ACK if exists
                if time_since_last < _DEDUP_WINDOW_SECONDS:
                    logger.warning(f"⚠️ Serial number '{serial_number}' was processed {time_since_last:.2f}s ago. Ignoring duplicate message.")
                    is_duplicate = True
                    should_send_ack = True  # Always send ACK for duplicates
                    # Don't return yet - send ACK first
                else:
                    # Processed more than 5 seconds ago - allow reprocessing
                    # Remove from history to allow new processing
                    logger.info(f"ℹ️ Serial number '{serial_number}' was processed {time_since_last:.2f}s ago (>5s). Allowing reprocessing.")
                    _recently_processed.pop(serial_number, None)
                    _currently_processing.discard(serial_number)
            
            # Only mark as processing if NOT a duplicate
            if not is_duplicate:
                # ATOMIC: Mark as being processed NOW (before releasing lock)
                # Add to both sets for fast lookup
                _currently_processing.add(serial_number)
                _recently_processed[serial_number] = (current_time, True)
                
                # Clean up old entries (older than dedup window) - modify in place
                keys_to_remove = [k for k, (ts, _) in _recently_processed.items() 
                                 if current_time - ts >= _DEDUP_WINDOW_SECONDS * 2]
                for key in keys_to_remove:
                    _recently_processed.pop(key, None)
                    _currently_processing.discard(key)
        
        # CRITICAL: Send ACK for duplicates OUTSIDE the lock to avoid deadlocks
        # and ensure it always happens, even if there's an exception
        if is_duplicate and should_send_ack:
            logger.info(f"🔄 Duplicate message detected for '{serial_number}'. Sending ACK...")
            try:
                exists = device_info_service.check_serial_number_exists(serial_number)
                if exists:
                    logger.info(f"ℹ️ Device already registered (duplicate message): {serial_number}")
                    # Wait 3 seconds to ensure hardware has time to subscribe to ACK topic
                    time.sleep(3.0)
                    mqtt_service.publish_ack(
                        serial_number,
                        status="success",
                        message="Device already registered"
                    )
                    logger.info(f"✅ ACK sent for duplicate message: {serial_number}")
                else:
                    # Device doesn't exist yet - might be processing first message
                    # Still send ACK to acknowledge receipt
                    logger.warning(f"⚠️ Duplicate message for unknown device '{serial_number}'. Sending acknowledgment anyway.")
                    # Wait 3 seconds to ensure hardware has time to subscribe to ACK topic
                    time.sleep(3.0)
                    mqtt_service.publish_ack(
                        serial_number,
                        status="success",
                        message="Message received (processing)"
                    )
            except Exception as ack_error:
                logger.error(f"❌ Failed to send ACK for duplicate message '{serial_number}': {ack_error}")
                logger.exception("Full traceback:")
                # Try one more time with error ACK
                try:
                    # Wait 3 seconds to ensure hardware has time to subscribe to ACK topic
                    time.sleep(3.0)
                    mqtt_service.publish_ack(
                        serial_number,
                        status="error",
                        message="Server error processing duplicate message"
                    )
                except:
                    logger.error(f"❌ Critical: Cannot send ACK for '{serial_number}'")
            return  # Exit early for duplicates
        
        # Lock is released here - serial_number is already marked as processing (if not duplicate)
        # So any concurrent message will see it as "processing" and be rejected
        
        try:
            logger.info(f"🔍 Processing serial number (normal flow): {serial_number}")
            # Check if serial number already exists
            try:
                exists = device_info_service.check_serial_number_exists(serial_number)
                logger.info(f"   Serial number exists check result: {exists}")
            except Exception as check_error:
                logger.error(f"❌ Error checking serial number existence: {check_error}")
                logger.exception("Full traceback:")
                # If check fails, assume it doesn't exist and try to register
                exists = False
            
            if not exists:
                # Register new device
                logger.info(f"🆕 New device detected. Registering serial number: {serial_number}")
                try:
                    success = device_info_service.register_device(serial_number)
                    
                    if success:
                        logger.info(f"✅ Device registered successfully: {serial_number}")
                        # Send acknowledgment
                        try:
                            # Wait 3 seconds to ensure hardware has time to subscribe to ACK topic
                            time.sleep(3.0)
                            mqtt_service.publish_ack(
                                serial_number,
                                status="success",
                                message="Device registered successfully"
                            )
                            logger.info(f"✅ ACK sent for new device: {serial_number}")
                        except Exception as ack_error:
                            logger.error(f"❌ Failed to send ACK for new device '{serial_number}': {ack_error}")
                            logger.exception("Full traceback:")
                    else:
                        logger.error(f"❌ Failed to register device: {serial_number}")
                        # Send error acknowledgment
                        try:
                            # Wait 3 seconds to ensure hardware has time to subscribe to ACK topic
                            time.sleep(3.0)
                            mqtt_service.publish_ack(
                                serial_number,
                                status="error",
                                message="Failed to register device"
                            )
                            logger.info(f"✅ Error ACK sent for failed registration: {serial_number}")
                        except Exception as ack_error:
                            logger.error(f"❌ Failed to send error ACK for failed registration '{serial_number}': {ack_error}")
                            logger.exception("Full traceback:")
                except Exception as reg_error:
                    logger.error(f"❌ Exception during device registration: {reg_error}")
                    logger.exception("Full traceback:")
                    # Send error acknowledgment
                    try:
                        # Wait 3 seconds to ensure hardware has time to subscribe to ACK topic
                        time.sleep(3.0)
                        mqtt_service.publish_ack(
                            serial_number,
                            status="error",
                            message=f"Server error during registration: {str(reg_error)}"
                        )
                        logger.info(f"✅ Error ACK sent for registration exception: {serial_number}")
                    except Exception as ack_error:
                        logger.error(f"❌ Failed to send error ACK for registration exception '{serial_number}': {ack_error}")
            else:
                # Device already exists
                logger.info(f"ℹ️ Device already registered: {serial_number}")
                # Send acknowledgment
                try:
                    # Wait 3 seconds to ensure hardware has time to subscribe to ACK topic
                    time.sleep(3.0)
                    mqtt_service.publish_ack(
                        serial_number,
                        status="success",
                        message="Device already registered"
                    )
                    logger.info(f"✅ ACK sent for existing device: {serial_number}")
                except Exception as ack_error:
                    logger.error(f"❌ Failed to send ACK for existing device '{serial_number}': {ack_error}")
                    logger.exception("Full traceback:")
                    # Try one more time with error ACK
                    try:
                        # Wait 3 seconds to ensure hardware has time to subscribe to ACK topic
                        time.sleep(3.0)
                        mqtt_service.publish_ack(
                            serial_number,
                            status="error",
                            message="Server error sending acknowledgment"
                        )
                    except:
                        logger.error(f"❌ Critical: Cannot send any ACK for '{serial_number}'")
        finally:
            # Mark as completed (not processing anymore, but keep timestamp for dedup)
            with _processing_lock:
                _currently_processing.discard(serial_number)  # Remove from processing set
                _recently_processed[serial_number] = (current_time, False)  # Keep in history
            
    except Exception as e:
        logger.error(f"❌ Error processing device initialization: {e}")
        logger.exception("Full error traceback:")
        # Try to send error acknowledgment if we have serial number
        try:
            serial_number = data.get('SerialNumber', 'unknown')
                            # Wait 3 seconds to ensure hardware has time to subscribe to ACK topic
            time.sleep(3.0)
            mqtt_service.publish_ack(
                serial_number,
                status="error",
                message=f"Error processing request: {str(e)}"
            )
        except:
            pass


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


# MQTT callback for device configuration requests
def on_device_config_request(topic: str, data: Dict[str, Any], device_id: str):
    """
    Callback when device requests configuration via MQTT
    Handles requests on topic: Cmd/DConfig/<Device ID>
    """
    try:
        logger.info(f"📥 Device config request received on topic: {topic}")
        logger.info(f"   Device ID: {device_id}, Payload: {data}")
        
        # Extract command from payload
        command = data.get('command')
        if not command:
            logger.error(f"❌ No 'command' field in payload from device {device_id}")
            return
        
        # Handle the config request
        device_config_provider_service.handle_config_request(device_id, command)
        
    except Exception as e:
        logger.error(f"❌ Error processing device config request: {e}")
        logger.exception("Full error traceback:")


# MQTT callback for real-time data (RTD/#)
def on_realtime_data_received(device_id: str, data: Dict[str, Any]):
    """
    Callback when device sends real-time data via MQTT
    Handles data on topic: RTD/<Device ID>
    
    Expected payload format:
    {
        "type": "Analog" | "Digital" | "Modbus" | "Canbus",
        "value": {
            "parameter_name1": value1,
            "parameter_name2": value2,
            ...
        }
    }
    """
    try:
        logger.info(f"📊 Real-time data received from device: {device_id}")
        logger.debug(f"   Payload: {data}")
        
        # Extract data type and values
        data_type = data.get('type', 'Unknown')
        values = data.get('value', {})
        
        if not values:
            logger.warning(f"⚠️ No 'value' field in RTD payload from device {device_id}")
            return
        
        # Get current timestamp
        from datetime import datetime
        timestamp = datetime.utcnow()
        
        # Save each parameter to database
        for parameter_name, parameter_value in values.items():
            if parameter_name and parameter_name.strip():
                # Clean parameter name (remove extra spaces)
                clean_param_name = parameter_name.strip()
                
                # Normalize data type name (Modbus -> Modbus, Canbus -> Canbus, etc.)
                normalized_type = data_type
                if normalized_type.lower() == 'canbus':
                    normalized_type = 'Canbus'
                elif normalized_type.lower() == 'modbus':
                    normalized_type = 'Modbus'
                
                logger.info(f"💾 Saving RTD: device={device_id}, type={normalized_type}, param='{clean_param_name}', value={parameter_value}")
                
                # Save to database
                success = realtime_data_db_service.save_realtime_data(
                    device_id=device_id,
                    data_type=normalized_type,
                    parameter_name=clean_param_name,
                    parameter_value=parameter_value,
                    timestamp=timestamp
                )
                
                if success:
                    logger.info(f"✅ Saved RTD: {device_id}/{normalized_type}/{clean_param_name} = {parameter_value}")
                else:
                    logger.warning(f"⚠️ Failed to save RTD: {device_id}/{normalized_type}/{clean_param_name}")
        
        logger.info(f"✅ Processed {len(values)} real-time data parameters from device {device_id}")
        
    except Exception as e:
        logger.error(f"❌ Error processing real-time data: {e}")
        logger.exception("Full error traceback:")


# Set MQTT callbacks
mqtt_service.set_data_callback(on_device_data_received)
mqtt_service.set_init_callback(on_device_init_received)
mqtt_service.set_config_request_callback(on_device_config_request)
mqtt_service.set_realtime_data_callback(on_realtime_data_received)


# ==================== MAIN ====================

if __name__ == '__main__':
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8050))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # CRITICAL: Only start MQTT client in the actual app process, not in reloader parent process
    # When use_reloader=True, Werkzeug creates a parent process (watcher) and child process (app)
    # The child process sets WERKZEUG_RUN_MAIN='true'
    # We only want ONE MQTT client running, so start it only in the child process
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not DEBUG:
        # This is the actual app process (child process when reloader is on, or main process when reloader is off)
        logger.info("🚀 Starting MQTT client...")
        mqtt_service.start()
    else:
        # This is the reloader parent process (watcher) - don't start MQTT client here
        logger.info("⚠️ Reloader parent process detected - skipping MQTT client start")
    
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
