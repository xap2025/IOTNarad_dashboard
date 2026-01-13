"""
Dashboard Page Layout
Main dashboard with sidebar navigation and content area
"""
from dash import html, dcc, Input, Output, State, callback, no_update, ALL
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import pytz
import plotly.graph_objs as go
import random
import logging

logger = logging.getLogger(__name__)

def create_dashboard_layout():
    """Create the main dashboard layout with sidebar navigation"""
    
    return html.Div([
        # Sidebar
        html.Div([
            # Logo Section
            html.Div([
                # Username display
                html.Div([
                    html.H6(id='sidebar-username', className='fw-bold',
                            style={'color': 'white', 'textAlign': 'center', 'fontSize': '0.9rem', 'marginBottom': '0'}),
                ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginBottom': '1rem', 'paddingTop': '0.75rem'}),
                
                # Xaptronics Logo Section
                html.Div([
                    html.Div([
                        # Xaptronics Logo Image
                        html.Div([
                            html.Img(
                                src='/assets/images/xaptronics-logo.png',
                                alt='Xaptronics Logo',
                                className='img-fluid',
                                style={
                                    'width': '100%',
                                    'maxWidth': '110px',
                                    'height': 'auto',
                                    'maxHeight': '110px',
                                    'objectFit': 'contain',
                                    'margin': '0 auto',
                                    'display': 'block',
                                    'paddingTop': '8px',
                                    'paddingBottom': '8px'
                                }
                            ),
                        ], className='mb-2', style={
                            'display': 'flex',
                            'justifyContent': 'center',
                            'alignItems': 'center',
                            'width': '100%',
                            'paddingTop': '8px',
                            'paddingBottom': '0px'
                        }),
                        
                        # Company Name
                        
                        # Product Name
                        html.Div([
                            html.H4("IOTNarad", className='mb-1 fw-bold text-center',
                                    style={'color': 'white', 'letterSpacing': '1px', 'fontSize': '1.2rem', 'textShadow': '0 0 10px rgba(255,255,255,0.3)', 'wordWrap': 'break-word', 'overflowWrap': 'break-word'}),
                            html.P("IoT Dashboard", className='mb-0 text-center mt-1',
                                   style={'color': 'rgba(255,255,255,0.7)', 'fontSize': '0.75rem', 'fontWeight': '300', 'wordWrap': 'break-word', 'lineHeight': '1.4'}),
                        ], style={'marginTop': '6px', 'marginBottom': '2px'}),
                    ], className='text-center'),
                ], style={
                    'border': '1px solid rgba(255,255,255,0.1)',
                    'borderRadius': '12px',
                    'borderTopLeftRadius': '12px',
                    'borderTopRightRadius': '12px',
                    'borderBottomLeftRadius': '12px',
                    'borderBottomRightRadius': '12px',
                    'backgroundColor': 'rgba(255,255,255,0.05)',
                    'backdropFilter': 'blur(5px)',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'width': '100%',
                    'maxWidth': '100%',
                    'boxSizing': 'border-box',
                    'padding': '0.75rem 0.75rem',
                    'paddingTop': '0.875rem',
                    'paddingBottom': '1rem',
                    'overflow': 'visible',
                    'minHeight': 'auto',
                    'marginBottom': '1rem'
                }),
                
                html.Hr(style={'borderColor': 'rgba(255,255,255,0.1)', 'margin': '0 0 1rem 0', 'width': '100%'}),
            ], className='p-2', style={
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'justifyContent': 'flex-start',
                'width': '100%',
                'boxSizing': 'border-box',
                'overflow': 'hidden',
                'flexShrink': '0',
                'paddingTop': '0.75rem',
                'paddingBottom': '0.75rem'
            }),
            
            # Navigation Menu
            html.Nav([
                dbc.Nav([
                    # Home
                    dbc.NavLink([
                        html.I(className="fas fa-home me-3", style={'color': 'white'}),
                        html.Span("Home", style={'color': 'white'})
                    ], id='nav-home', href='#', className='nav-item-custom active',
                       n_clicks=0, style={'color': 'white'}),
                    
                    # Analytics
                    dbc.NavLink([
                        html.I(className="fas fa-chart-line me-3", style={'color': 'white'}),
                        html.Span("Analytics", style={'color': 'white'})
                    ], id='nav-analytics', href='#', className='nav-item-custom',
                       n_clicks=0, style={'color': 'white'}),
                    
                    # OEE Dashboard
                    dbc.NavLink([
                        html.I(className="fas fa-industry me-3", style={'color': 'white'}),
                        html.Span("OEE Dashboard", style={'color': 'white'})
                    ], id='nav-oee', href='#', className='nav-item-custom',
                       n_clicks=0, style={'color': 'white'}),
                    
                    # Devices
                    dbc.NavLink([
                        html.I(className="fas fa-microchip me-3", style={'color': 'white'}),
                        html.Span("Devices", style={'color': 'white'})
                    ], id='nav-devices', href='#', className='nav-item-custom',
                       n_clicks=0, style={'color': 'white'}),
                    
                    # Profile (visible for all users - admin and regular users)
                    dbc.NavLink([
                        html.I(className="fas fa-user me-3", style={'color': 'white'}),
                        html.Span("Profile", style={'color': 'white'})
                    ], id='nav-profile', href='#', className='nav-item-custom',
                       n_clicks=0, style={'color': 'white'}),
                    
                    # Settings (for admin users only - hidden by default, shown only for admin)
                    dbc.NavLink([
                        html.I(className="fas fa-cog me-3", style={'color': 'white'}),
                        html.Span("Settings", style={'color': 'white'})
                    ], id='nav-settings', href='#', className='nav-item-custom nav-hidden',
                       n_clicks=0, style={'color': 'white'}),
                    
                    # Help
                    dbc.NavLink([
                        html.I(className="fas fa-question-circle me-3", style={'color': 'white'}),
                        html.Span("Help", style={'color': 'white'})
                    ], id='nav-help', href='#', className='nav-item-custom',
                       n_clicks=0, style={'color': 'white'}),
                    
                ], vertical=True, className='flex-column'),
            ], className='px-3', style={'flexShrink': '1', 'overflow': 'hidden', 'minHeight': '0'}),
            
            # Bottom Section
            html.Div([
                html.Hr(style={'borderColor': 'rgba(255,255,255,0.1)', 'margin': '0.5rem 0'}),
                dbc.NavLink([
                    html.I(className="fas fa-sign-out-alt me-3", style={'color': 'white'}),
                    html.Span("Logout", style={'color': 'white'})
                ], href='/logout', className='nav-item-custom',
                   style={'color': 'white !important'}),
            ], className='px-3', style={'marginTop': 'auto', 'flexShrink': '0', 'paddingBottom': '1rem'}),
            
        ], className='sidebar', style={
            'position': 'fixed',
            'left': '0',
            'top': '0',
            'height': '100vh',
            'maxHeight': '100vh',
            'background': 'linear-gradient(180deg, #1a1a2e 0%, #16213e 100%)',
            'display': 'flex',
            'flexDirection': 'column',
            'boxShadow': '4px 0 10px rgba(0,0,0,0.1)',
            'zIndex': '1000',
            'overflowY': 'hidden',
            'overflowX': 'hidden'
        }),
        
        # Main Content Area
        html.Div([
            # Top Header Bar
            html.Div([
                html.Div([
                    html.Div([
                        html.H4(id='page-title', children='Home', 
                                className='mb-0 fw-bold',
                                style={'color': '#1a1a2e'}),
                        html.P(id='page-subtitle', 
                               children='Welcome to IOTNarad Dashboard',
                               className='mb-0 text-muted',
                               style={'fontSize': '0.9rem'}),
                    ]),
                    
                    html.Div([
                        # Date Display
                        html.Div(id='current-date', className='text-muted me-4',
                                style={'fontSize': '0.9rem', 'fontWeight': '500'}),
                        
                        # Clock
                        html.Div([
                            html.I(className="fas fa-clock me-2", style={'color': '#667eea'}),
                            html.Span(id='current-time', className='fw-bold',
                                    style={'fontSize': '0.95rem', 'color': '#1a1a2e', 'fontFamily': 'monospace'})
                        ], className='d-flex align-items-center'),
                    ], className='d-flex align-items-center'),
                ], className='d-flex justify-content-between align-items-center'),
            ], className='header-bar', style={
                'background': 'white',
                'padding': '1.5rem 2rem',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.05)',
                'borderBottom': '1px solid #e9ecef'
            }),
            
            # Page Content
            html.Div(id='dashboard-content', className='content-area', style={
                'padding': '2rem'
            }),
            
        ], className='main-content', style={
            'minHeight': '100vh',
            'background': '#f8f9fa'
        }),
        
        # Interval for clock and date update
        dcc.Interval(id='clock-interval', interval=1000, n_intervals=0),
        
        # Store for active page
        dcc.Store(id='active-page-store', data='home'),
    ])


# Callbacks for Dashboard
@callback(
    [Output('current-time', 'children'),
     Output('current-date', 'children')],
    Input('clock-interval', 'n_intervals')
)
def update_time_and_date(n):
    """Update the current time and date display with IST timezone"""
    # Get IST timezone (Asia/Kolkata = UTC+5:30)
    ist = pytz.timezone('Asia/Kolkata')
    
    # Get current time in IST
    now_ist = datetime.now(ist)
    
    # Time format: HH:MM:SS with 24-hour format
    time_str = now_ist.strftime('%H:%M:%S')
    
    # Date format: Day, DD Month YYYY (e.g., Monday, 29 October 2025)
    date_str = now_ist.strftime('%A, %d %B %Y')
    
    return time_str, date_str


@callback(
    Output('sidebar-username', 'children'),
    Input('session-store', 'data')
)
def update_sidebar_username(session_data):
    """Update sidebar username display"""
    if session_data and session_data.get('authenticated'):
        username = session_data.get('username', 'User')
        user_type = session_data.get('user_type', 'user')
        return f"{username} ({user_type.title()})"
    return "Guest"


@callback(
    [Output('nav-settings', 'className', allow_duplicate=True),
     Output('nav-profile', 'className', allow_duplicate=True)],
    Input('session-store', 'data'),
    prevent_initial_call='initial_duplicate'
)
def update_nav_visibility_from_session(session_data):
    """Update navigation visibility when session data changes"""
    if not session_data:
        # Return className to hide
        return 'nav-item-custom nav-hidden', 'nav-item-custom nav-hidden'
    
    username = session_data.get('username', '')
    user_type = session_data.get('user_type', 'user')
    
    # Settings only visible if User_Id == 'admin'
    is_admin = (username == 'admin')
    # Use className to control visibility
    settings_class = 'nav-item-custom' if is_admin else 'nav-item-custom nav-hidden'
    
    # Profile visible for ALL users (both admin and regular users)
    profile_class = 'nav-item-custom'
    
    logger.info(f"🔐 Nav visibility update from session - User_Id: {username}, Is Admin: {is_admin}, Settings visible: {is_admin}, Profile visible: True")
    
    return settings_class, profile_class



@callback(
    [Output('dashboard-content', 'children'),
     Output('active-page-store', 'data'),
     Output('page-title', 'children'),
     Output('page-subtitle', 'children'),
     Output('nav-home', 'className'),
     Output('nav-analytics', 'className'),
     Output('nav-oee', 'className'),
     Output('nav-devices', 'className'),
     Output('nav-profile', 'className', allow_duplicate=True),
     Output('nav-settings', 'className', allow_duplicate=True),
     Output('nav-help', 'className'),
     Output('nav-profile', 'style'),
     Output('nav-settings', 'style')],
    [Input('nav-home', 'n_clicks'),
     Input('nav-analytics', 'n_clicks'),
     Input('nav-oee', 'n_clicks'),
     Input('nav-devices', 'n_clicks'),
     Input('nav-profile', 'n_clicks'),
     Input('nav-settings', 'n_clicks'),
     Input('nav-help', 'n_clicks')],
    [State('active-page-store', 'data'),
     State('session-store', 'data')],
    prevent_initial_call='initial_duplicate'
)
def update_page_content(home_clicks, analytics_clicks, oee_clicks, devices_clicks, profile_clicks, settings_clicks, help_clicks, current_page, session_data):
    """Update page content based on navigation"""
    from dash import ctx
    from app.pages.device_config import create_device_config_layout
    from app.pages.analytics import create_analytics_layout
    from app.pages.settings import create_settings_layout
    
    # Get username (User_Id) from session
    username = session_data.get('username', '') if session_data else ''
    user_type = session_data.get('user_type', 'user') if session_data else 'user'
    # Check if User_Id is admin (only check username/User_Id, not user_type)
    is_admin = (username == 'admin')
    print(f"User_Id (username): {username}, User Type: {user_type}, Is Admin: {is_admin}, Triggered ID: {ctx.triggered_id if ctx.triggered_id else 'None'}")  # Debug
    
    # Determine which button was clicked
    # If no button was clicked (initial load), use current_page from store
    if not ctx.triggered_id:
        page = current_page if current_page else 'home'
    elif ctx.triggered_id == 'nav-analytics':
        page = 'analytics'
    elif ctx.triggered_id == 'nav-oee':
        page = 'oee'
    elif ctx.triggered_id == 'nav-devices':
        page = 'devices'
        logger.info("✅ Devices tab clicked, loading device config layout...")
    elif ctx.triggered_id == 'nav-profile':
        page = 'profile'
    elif ctx.triggered_id == 'nav-settings':
        page = 'settings'
    elif ctx.triggered_id == 'nav-help':
        page = 'help'
    else:
        page = 'home'
    
    # Base classes for nav items
    base_class = 'nav-item-custom'
    active_class = 'nav-item-custom active'
    
    # Set active states
    nav_classes = {
        'home': base_class,
        'analytics': base_class,
        'oee': base_class,
        'devices': base_class,
        'profile': base_class,
        'settings': base_class,
        'help': base_class
    }
    nav_classes[page] = active_class
    
    # Set visibility based on User_Id using className
    # Settings only visible if User_Id == 'admin'
    # Profile visible for ALL users (both admin and regular users)
    profile_class = 'nav-item-custom'  # Always visible for all users
    settings_class = 'nav-item-custom' if is_admin else 'nav-item-custom nav-hidden'
    
    # Update nav_classes with visibility
    nav_classes['profile'] = profile_class
    nav_classes['settings'] = settings_class
    
    # Keep style for color
    profile_style = {'color': 'white'}
    settings_style = {'color': 'white'}
    
    logger.info(f"🔐 Visibility check - User_Id: {username}, Is Admin: {is_admin}, Settings visible: {is_admin}, Settings class: {settings_class}")
    
    # Page content
    if page == 'home':
        content = create_home_content()
        title = "Home"
        subtitle = "Welcome to IOTNarad Dashboard"
    elif page == 'analytics':
        content = create_analytics_layout()
        title = "Analytics"
        subtitle = "Real-time data visualization and insights"
    elif page == 'oee':
        from app.pages.oee_dashboard import create_oee_dashboard_layout
        content = create_oee_dashboard_layout()
        title = "OEE Dashboard"
        subtitle = "Overall Equipment Effectiveness monitoring"
    elif page == 'devices':
        try:
            content = create_device_config_layout()
            title = "Devices"
            subtitle = "Configure and manage your IoT devices"
            logger.info("✅ Devices page content created successfully")
        except Exception as e:
            logger.error(f"❌ Error creating devices page content: {e}")
            logger.exception("Full traceback:")
            content = html.Div([
                dbc.Alert([
                    html.H4("Error loading Devices page", className='alert-heading'),
                    html.P(f"An error occurred: {str(e)}"),
                    html.P("Please check the logs for more details.", className='mb-0'),
                ], color='danger')
            ])
            title = "Devices"
            subtitle = "Error loading page"
    elif page == 'profile':
        content = create_profile_content(session_data)
        title = "Profile"
        subtitle = "User profile management"
    elif page == 'settings':
        # Only allow admin user to access settings
        if is_admin:
            content = create_settings_content()
            title = "Settings"
            subtitle = "Admin management panel"
        else:
            content = html.Div([
                dbc.Alert([
                    html.H4("Access Denied", className='alert-heading'),
                    html.P("Only admin users can access the Settings page."),
                ], color='danger')
            ])
            title = "Settings"
            subtitle = "Access Denied"
    else:  # help
        content = create_help_content()
        title = "Help"
        subtitle = "Documentation and support"
    
    return (content, page, title, subtitle, 
            nav_classes['home'], nav_classes['analytics'], 
            nav_classes['oee'], nav_classes['devices'], 
            nav_classes['profile'], nav_classes['settings'], nav_classes['help'],
            profile_style, settings_style)


def create_home_content():
    """Create home page content matching OEE Dashboard layout"""
    return html.Div([
        # Top Section - KPI Cards (4 cards)
        dbc.Row([
            # Overall OEE
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-industry fa-2x",
                               style={'color': 'rgba(255,255,255,0.9)'}),
                        html.Div([
                            html.H3("84%", className='mb-0 fw-bold',
                                   style={'color': 'white'}),
                            html.P("Overall OEE", className='mb-0',
                                   style={'fontSize': '0.9rem', 'color': 'rgba(255,255,255,0.9)'}),
                        ], className='ms-3'),
                    ], className='d-flex align-items-center'),
                ], className='stat-card', style={
                    'background': 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                    'borderRadius': '12px',
                    'padding': '1.5rem',
                    'boxShadow': '0 4px 12px rgba(59, 130, 246, 0.3)',
                    'border': 'none',
                    'color': 'white'
                }),
            ], md=3),
            
            # Total Production
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-cogs fa-2x",
                               style={'color': 'rgba(255,255,255,0.9)'}),
                        html.Div([
                            html.H3("375", className='mb-0 fw-bold',
                                   style={'color': 'white'}),
                            html.P("Total Production", className='mb-0',
                                   style={'fontSize': '0.9rem', 'color': 'rgba(255,255,255,0.9)'}),
                        ], className='ms-3'),
                    ], className='d-flex align-items-center'),
                ], className='stat-card', style={
                    'background': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    'borderRadius': '12px',
                    'padding': '1.5rem',
                    'boxShadow': '0 4px 12px rgba(16, 185, 129, 0.3)',
                    'border': 'none',
                    'color': 'white'
                }),
            ], md=3),
            
            # Energy Usage
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-bolt fa-2x",
                               style={'color': 'rgba(255,255,255,0.9)'}),
                        html.Div([
                            html.H3("5.8", className='mb-0 fw-bold',
                                   style={'color': 'white'}),
                            html.P("Energy Usage (kWh)", className='mb-0',
                                   style={'fontSize': '0.9rem', 'color': 'rgba(255,255,255,0.9)'}),
                        ], className='ms-3'),
                    ], className='d-flex align-items-center'),
                ], className='stat-card', style={
                    'background': 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
                    'borderRadius': '12px',
                    'padding': '1.5rem',
                    'boxShadow': '0 4px 12px rgba(249, 115, 22, 0.3)',
                    'border': 'none',
                    'color': 'white'
                }),
            ], md=3),
            
            # Active Alarms
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-exclamation-triangle fa-2x",
                               style={'color': 'rgba(255,255,255,0.9)'}),
                        html.Div([
                            html.H3("1", className='mb-0 fw-bold',
                                   style={'color': 'white'}),
                            html.P("Active Alarms", className='mb-0',
                                   style={'fontSize': '0.9rem', 'color': 'rgba(255,255,255,0.9)'}),
                        ], className='ms-3'),
                    ], className='d-flex align-items-center'),
                ], className='stat-card', style={
                    'background': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                    'borderRadius': '12px',
                    'padding': '1.5rem',
                    'boxShadow': '0 4px 12px rgba(239, 68, 68, 0.3)',
                    'border': 'none',
                    'color': 'white'
                }),
            ], md=3),
        ], className='mb-4'),
        
        # Middle Section - Machine Status (3 Machines)
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6([
                        html.I(className="fas fa-industry me-2", style={'color': '#667eea'}),
                        "Machine Status (3 Machines)"
                    ], className='fw-bold mb-3'),
                    
                    dbc.Row([
                        dbc.Col([
                            create_machine_card("M01", "Running", 89, 92, 2.4, "#10b981")
                        ], md=4),
                        dbc.Col([
                            create_machine_card("M02", "Idle", 68, 55, 1.2, "#f97316")
                        ], md=4),
                        dbc.Col([
                            create_machine_card("M03", "Maintenance", None, None, None, "#ef4444")
                        ], md=4),
                    ]),
                ], className='stat-card p-4', style={
                    'background': 'white',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                    'border': '1px solid #e9ecef'
                }),
            ], md=12),
        ], className='mb-4'),
        
        # Bottom Section - Device Overview Table
        dbc.Row([
            dbc.Col([
                create_device_overview_table()
            ], md=12),
        ]),
    ])


def create_machine_card(machine_id, status, oee, utilization, energy, status_color):
    """Create machine status card with chart"""
    
    # Generate sample chart data based on status
    if status == "Running":
        # Green line chart - increasing trend
        chart_data = go.Scatter(
            x=['8 AM', '9 AM', '10 AM', '11 AM', '12 PM'],
            y=[120, 130, 140, 150, 160],
            mode='lines+markers',
            line=dict(color='#10b981', width=2),
            marker=dict(size=6),
            name='Production'
        )
    elif status == "Idle":
        # Orange line chart - fluctuating
        chart_data = go.Scatter(
            x=['8 AM', '9 AM', '10 AM', '11 AM', '12 PM'],
            y=[75, 80, 78, 82, 80],
            mode='lines+markers',
            line=dict(color='#f97316', width=2),
            marker=dict(size=6),
            name='Production'
        )
    else:  # Maintenance
        # Red flat line
        chart_data = go.Scatter(
            x=['8 AM', '9 AM', '10 AM', '11 AM', '12 PM'],
            y=[0, 0, 0, 0, 0],
            mode='lines+markers',
            line=dict(color='#ef4444', width=2),
            marker=dict(size=6),
            name='Production'
        )
    
    fig = go.Figure(data=[chart_data])
    fig.update_layout(
        height=120,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        font=dict(size=10)
    )
    
    return html.Div([
        html.Div([
            html.H6(f"Machine {machine_id}", className='mb-2 fw-bold'),
            html.Div([
                html.Span([
                    html.I(className="fas fa-circle me-2",
                           style={'color': status_color, 'fontSize': '0.6rem'}),
                    html.Span(status, style={'color': status_color, 'fontWeight': '600'})
                ], className='badge bg-light',
                   style={'fontSize': '0.85rem'}),
            ], className='mb-2'),
            
            html.Div([
                html.Div([
                    html.Small("OEE", className='text-muted d-block', style={'fontSize': '0.75rem'}),
                    html.Span(f"{oee}%" if oee else "-", className='fw-bold',
                             style={'color': status_color, 'fontSize': '1rem'})
                ], className='text-center'),
                html.Div([
                    html.Small("Utilization", className='text-muted d-block', style={'fontSize': '0.75rem'}),
                    html.Span(f"{utilization}%" if utilization else "-", className='fw-bold',
                             style={'fontSize': '1rem'})
                ], className='text-center'),
                html.Div([
                    html.Small("Energy", className='text-muted d-block', style={'fontSize': '0.75rem'}),
                    html.Span(f"{energy} kWh" if energy else "-", className='fw-bold',
                             style={'fontSize': '1rem'})
                ], className='text-center'),
            ], className='d-flex justify-content-between mb-2'),
            
            dcc.Graph(figure=fig, config={'displayModeBar': False}, style={'height': '120px'}),
        ], style={'padding': '0.75rem'})
    ], className='machine-card', style={
        'background': 'white',
        'borderRadius': '8px',
        'border': f'2px solid {status_color}40',
        'boxShadow': '0 2px 6px rgba(0,0,0,0.08)'
    })


def create_device_overview_table():
    """Create Device Overview table with new columns"""
    
    # Sample device data
    device_data = [
        {
            'gateway_id': 'GW-001',
            'device_name': 'Production Line A',
            'location': 'Factory Floor 1',
            'oee': 89.2,
            'status': 'Running',
            'last_update': '2 min ago'
        },
        {
            'gateway_id': 'GW-002',
            'device_name': 'Production Line B',
            'location': 'Factory Floor 1',
            'oee': 85.7,
            'status': 'Running',
            'last_update': '1 min ago'
        },
        {
            'gateway_id': 'GW-003',
            'device_name': 'Production Line C',
            'location': 'Factory Floor 2',
            'oee': 91.3,
            'status': 'Running',
            'last_update': '3 min ago'
        },
        {
            'gateway_id': 'GW-004',
            'device_name': 'Quality Control Station',
            'location': 'Factory Floor 2',
            'oee': 0.0,
            'status': 'Maintenance',
            'last_update': '25 min ago'
        },
        {
            'gateway_id': 'GW-005',
            'device_name': 'Packaging Unit',
            'location': 'Warehouse',
            'oee': 78.5,
            'status': 'Idle',
            'last_update': '5 min ago'
        },
        {
            'gateway_id': 'GW-006',
            'device_name': 'Inspection Station',
            'location': 'Factory Floor 1',
            'oee': 93.6,
            'status': 'Running',
            'last_update': '1 min ago'
        },
    ]
    
    return html.Div([
        html.H6([
            html.I(className="fas fa-table me-2", style={'color': '#667eea'}),
            "DEVICE OVERVIEW"
        ], className='fw-bold mb-3'),
        
        dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Gateway ID"),
                    html.Th("Device Name"),
                    html.Th("Location"),
                    html.Th("OEE"),
                    html.Th("Status"),
                    html.Th("Last Update"),
                    html.Th("Actions"),
                ], style={'background': '#f8f9fa'})
            ]),
            html.Tbody([
                create_device_row(data) for data in device_data
            ])
        ], striped=True, bordered=True, hover=True, responsive=True,
           className='table-sm', style={'fontSize': '0.9rem'}),
    ], className='stat-card p-4', style={
        'background': 'white',
        'borderRadius': '12px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
        'border': '1px solid #e9ecef'
    })


def create_device_row(data):
    """Create a row for device overview table"""
    
    # Determine status color
    if data['status'] == 'Running':
        status_color = '#10b981'
        status_icon = 'fa-play-circle'
    elif data['status'] == 'Maintenance':
        status_color = '#ef4444'
        status_icon = 'fa-wrench'
    else:  # Idle
        status_color = '#f97316'
        status_icon = 'fa-pause-circle'
    
    # Determine OEE color
    if data['oee'] >= 85:
        oee_color = '#10b981'
    elif data['oee'] >= 75:
        oee_color = '#fbbf24'
    elif data['oee'] > 0:
        oee_color = '#f97316'
    else:
        oee_color = '#6c757d'
    
    return html.Tr([
        html.Td([
            html.I(className="fas fa-network-wired me-2", style={'color': '#667eea'}),
            html.Span(data['gateway_id'], className='fw-bold')
        ]),
        html.Td(data['device_name']),
        html.Td([
            html.I(className="fas fa-map-marker-alt me-2", style={'color': '#6c757d', 'fontSize': '0.8rem'}),
            data['location']
        ]),
        html.Td([
            html.Span(f"{data['oee']:.1f}%" if data['oee'] > 0 else "-",
                     style={'color': oee_color, 'fontWeight': 'bold'})
        ]),
        html.Td([
            html.Span([
                html.I(className=f"fas {status_icon} me-2",
                       style={'color': status_color, 'fontSize': '0.7rem'}),
                data['status']
            ], className='badge',
               style={'backgroundColor': f"{status_color}20",
                      'color': status_color,
                      'fontSize': '0.85rem'})
        ]),
        html.Td([
            html.I(className="fas fa-clock me-2", style={'color': '#6c757d', 'fontSize': '0.8rem'}),
            data['last_update']
        ]),
        html.Td([
            dbc.Button("View Details", size='sm', color='primary', outline=True, className='me-1'),
            dbc.Button("Configure", size='sm', color='info', outline=True)
        ]),
    ])


def create_profile_content(session_data=None):
    """Create profile page content with user information"""
    # Get user data from session
    user_data = session_data.get('user_data', {}) if session_data else {}
    username = session_data.get('username', 'N/A') if session_data else 'N/A'
    
    # Try to fetch fresh data from database if username is available
    if username and username != 'N/A':
        try:
            from app.services.user_service import UserService
            user_service = UserService()
            db_user = user_service.get_user_by_id(username)
            if db_user:
                # Use database data, fallback to session data
                user_data = db_user
                logger.info(f"✅ Fetched user data from database for: {username}")
        except Exception as e:
            logger.warning(f"Could not fetch user data from database: {e}")
            # Continue with session data
    
    # Extract user information
    user_id = user_data.get('User_Id', username)
    company_name = user_data.get('Company_Name', 'N/A')
    email = user_data.get('Email_Id', 'N/A')
    phone = user_data.get('Phone_No', 'N/A')
    user_type = user_data.get('User_Type', session_data.get('user_type', 'user') if session_data else 'user')
    status = user_data.get('status', 'active')
    
    # Status badge
    status_badge = dbc.Badge(
        "Active" if status.lower() == 'active' else "Inactive",
        color="success" if status.lower() == 'active' else "secondary",
        className='ms-2'
    )
    
    # User type badge
    user_type_badge = dbc.Badge(
        user_type.title(),
        color="danger" if user_type.lower() == 'admin' else "primary",
        className='ms-2'
    )
    
    return html.Div([
        # Header
        html.Div([
            html.H3([
                html.I(className="fas fa-user-circle me-3"),
                "My Profile"
            ], className='fw-bold mb-2', style={'color': '#1a1a2e'}),
            html.P("View and manage your account information", className='text-muted mb-4'),
        ], className='mb-4'),
        
        # Profile Information Card
        dbc.Card([
            dbc.CardBody([
                html.H5([
                    html.I(className="fas fa-info-circle me-2"),
                    "Account Information"
                ], className='fw-bold mb-4'),
                
                # User Information Display
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Label("User ID", className='fw-bold text-muted mb-2', style={'fontSize': '0.9rem'}),
                            html.Div([
                                html.I(className="fas fa-user me-2", style={'color': '#667eea'}),
                                html.Span(user_id, style={'fontSize': '1.1rem', 'fontWeight': '500'})
                            ], className='d-flex align-items-center')
                        ], className='mb-4'),
                        
                        html.Div([
                            html.Label("Company Name", className='fw-bold text-muted mb-2', style={'fontSize': '0.9rem'}),
                            html.Div([
                                html.I(className="fas fa-building me-2", style={'color': '#667eea'}),
                                html.Span(company_name, style={'fontSize': '1.1rem', 'fontWeight': '500'})
                            ], className='d-flex align-items-center')
                        ], className='mb-4'),
                        
                        html.Div([
                            html.Label("Email Address", className='fw-bold text-muted mb-2', style={'fontSize': '0.9rem'}),
                            html.Div([
                                html.I(className="fas fa-envelope me-2", style={'color': '#667eea'}),
                                html.Span(email, style={'fontSize': '1.1rem', 'fontWeight': '500'})
                            ], className='d-flex align-items-center')
                        ], className='mb-4'),
                    ], md=6),
                    
                    dbc.Col([
                        html.Div([
                            html.Label("Phone Number", className='fw-bold text-muted mb-2', style={'fontSize': '0.9rem'}),
                            html.Div([
                                html.I(className="fas fa-phone me-2", style={'color': '#667eea'}),
                                html.Span(phone, style={'fontSize': '1.1rem', 'fontWeight': '500'})
                            ], className='d-flex align-items-center')
                        ], className='mb-4'),
                        
                        html.Div([
                            html.Label("User Type", className='fw-bold text-muted mb-2', style={'fontSize': '0.9rem'}),
                            html.Div([
                                html.I(className="fas fa-user-tag me-2", style={'color': '#667eea'}),
                                html.Span(user_type.title(), style={'fontSize': '1.1rem', 'fontWeight': '500'}),
                                user_type_badge
                            ], className='d-flex align-items-center')
                        ], className='mb-4'),
                        
                        html.Div([
                            html.Label("Account Status", className='fw-bold text-muted mb-2', style={'fontSize': '0.9rem'}),
                            html.Div([
                                html.I(className="fas fa-check-circle me-2", style={'color': '#667eea'}),
                                html.Span(status.title(), style={'fontSize': '1.1rem', 'fontWeight': '500'}),
                                status_badge
                            ], className='d-flex align-items-center')
                        ], className='mb-4'),
                    ], md=6),
                ]),
                
                html.Hr(className='my-4'),
                
                # Change Password Button
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-key me-2"),
                        "Change Password"
                    ], 
                    id='change-password-btn',
                    color='primary',
                    size='lg',
                    className='px-4',
                    n_clicks=0
                    )
                ], className='text-center mt-4'),
                
            ], className='p-4')
        ], className='border-0 shadow-sm mb-4', style={
            'borderRadius': '12px',
            'background': 'white'
        }),
        
        # Message Display Area
        html.Div(id='profile-message', className='mt-3'),
        
    ], className='p-4')


def create_settings_content():
    """Create settings page content"""
    return html.Div([
        # User Management Section
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("User Management", className='fw-bold mb-4'),
                    
                    # User Management Buttons
                    html.Div([
                        dbc.Button([
                            html.I(className="fas fa-user-plus me-2"),
                            "Create New User"
                        ], id='create-user-btn', color='success', size='lg', className='me-3 mb-3', n_clicks=0),
                        
                        dbc.Button([
                            html.I(className="fas fa-link me-2"),
                            "Assign Devices"
                        ], id='assign-devices-btn', color='info', size='lg', className='me-3 mb-3'),
                        
                        dbc.Button([
                            html.I(className="fas fa-user-minus me-2"),
                            "Delete User"
                        ], id='delete-user-btn', color='danger', size='lg', className='mb-3'),
                    ], className='mb-4'),
                    
                ], className='stat-card', style={
                    'background': 'white',
                    'borderRadius': '12px',
                    'padding': '1.5rem',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                    'border': '1px solid #e9ecef',
                    'transition': 'all 0.3s ease'
                }),
            ]),
        ], className='mb-4'),
        
        # Device List Section
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Device List", className='fw-bold mb-4'),
                    
                    # Toggle Switch for Filter
                    html.Div([
                        dbc.Label("Filter Devices:", className='fw-bold me-3'),
                        dbc.RadioItems(
                            id='device-filter-toggle',
                            options=[
                                {'label': ' UnAssigned', 'value': 'unassigned'},
                                {'label': ' Assigned', 'value': 'assigned'},
                            ],
                            value='unassigned',
                            inline=True,
                            className='mb-3'
                        ),
                    ], className='mb-3'),
                    
                    # Device Assignment Table (Dynamic)
                    html.Div(id='device-list-table-container', children=[
                        dbc.Table([
                            html.Thead([
                                html.Tr([
                                    html.Th("Device ID"),
                                    html.Th("User ID"),
                                    html.Th("Device Name"),
                                    html.Th("Status"),
                                    html.Th("Actions"),
                                ])
                            ]),
                            html.Tbody(id='device-list-tbody', children=[])
                        ], striped=True, bordered=True, hover=True, responsive=True, id='device-list-table')
                    ]),
                    
                ], className='stat-card', style={
                    'background': 'white',
                    'borderRadius': '12px',
                    'padding': '1.5rem',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                    'border': '1px solid #e9ecef',
                    'transition': 'all 0.3s ease'
                }),
            ]),
        ]),
        
        # Assign Devices Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Assign Device to User")),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Select Unassigned Device ID", className='fw-bold'),
                            dcc.Dropdown(
                                id='assign-device-selector',
                                placeholder='Select device...',
                                options=[],
                                value=None,
                                clearable=True
                            ),
                            html.Small("Only devices with Owner = 'admin' are shown", className='text-muted mt-1 d-block'),
                        ], md=12),
                    ], className='mb-3'),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Select User ID", className='fw-bold'),
                            dcc.Dropdown(
                                id='assign-user-selector',
                                placeholder='Select user...',
                                options=[],
                                value=None,
                                clearable=True
                            ),
                            html.Small("Admin user is excluded from this list", className='text-muted mt-1 d-block'),
                        ], md=12),
                    ], className='mb-3'),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Enter Device Name", className='fw-bold'),
                            dbc.Input(
                                id='assign-device-name',
                                type='text',
                                placeholder='Enter device name...',
                                value=''
                            ),
                        ], md=12),
                    ], className='mb-3'),
                    
                    # Alert for success/error messages
                    html.Div(id='assign-device-alert', children=[]),
                ]),
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="close-assign-device-modal", className="ms-auto", n_clicks=0, color="secondary"),
                dbc.Button("Assign Device", id="save-assign-device-btn", color="primary", n_clicks=0),
            ]),
        ], id="assign-device-modal", is_open=False, size="lg"),
        
        # Delete User Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Delete User")),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Select User ID to Delete", className='fw-bold'),
                            dcc.Dropdown(
                                id='delete-user-selector',
                                placeholder='Select user...',
                                options=[],
                                value=None,
                                clearable=True
                            ),
                            html.Small("Admin user is excluded from this list", className='text-muted mt-1 d-block'),
                        ], md=12),
                    ], className='mb-3'),
                    
                    # User Details Display (shown when user is selected)
                    html.Div(id='delete-user-details', children=[]),
                    
                    # Alert for messages
                    html.Div(id='delete-user-alert', children=[]),
                ]),
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="close-delete-user-modal", className="ms-auto", n_clicks=0, color="secondary"),
                dbc.Button("Delete User", id="confirm-delete-user-btn", color="danger", n_clicks=0, disabled=True),
            ]),
        ], id="delete-user-modal", is_open=False, size="lg"),
        
        # Edit Device Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Edit Device Assignment")),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Device ID", className='fw-bold'),
                            dbc.Input(
                                id='edit-device-id',
                                type='text',
                                value='',
                                disabled=True,
                                style={'backgroundColor': '#f8f9fa'}
                            ),
                            html.Small("Device ID is fixed and cannot be changed", className='text-muted mt-1 d-block'),
                        ], md=12),
                    ], className='mb-3'),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Select New User ID", className='fw-bold'),
                            dcc.Dropdown(
                                id='edit-user-selector',
                                placeholder='Select user...',
                                options=[],
                                value=None,
                                clearable=True
                            ),
                            html.Small("Admin and current owner are excluded from this list", className='text-muted mt-1 d-block'),
                        ], md=12),
                    ], className='mb-3'),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Enter Device Name", className='fw-bold'),
                            dbc.Input(
                                id='edit-device-name',
                                type='text',
                                placeholder='Enter device name...',
                                value=''
                            ),
                        ], md=12),
                    ], className='mb-3'),
                    
                    # Alert for messages
                    html.Div(id='edit-device-alert', children=[]),
                ]),
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="close-edit-device-modal", className="ms-auto", n_clicks=0, color="secondary"),
                dbc.Button("Save Changes", id="save-edit-device-btn", color="primary", n_clicks=0),
            ]),
        ], id="edit-device-modal", is_open=False, size="lg"),
    ])


# Settings Page Callbacks - Navigate to create-user page
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('create-user-btn', 'n_clicks'),
    prevent_initial_call=True
)
def navigate_to_create_user_from_settings(n_clicks):
    """Navigate to create user page from settings"""
    if n_clicks and n_clicks > 0:
        return '/create-user'
    return no_update


# Settings Page Callbacks - Assign Devices Modal
@callback(
    Output("assign-device-modal", "is_open"),
    [Input("assign-devices-btn", "n_clicks"),
     Input("close-assign-device-modal", "n_clicks"),
     Input("save-assign-device-btn", "n_clicks")],
    [State("assign-device-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_assign_device_modal(open_clicks, close_clicks, save_clicks, is_open):
    """Toggle assign device modal"""
    from dash import ctx
    
    if not ctx.triggered:
        return is_open
    
    ctx_triggered = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if ctx_triggered == "assign-devices-btn" and open_clicks:
        return True
    elif ctx_triggered in ["close-assign-device-modal", "save-assign-device-btn"]:
        return False
    return is_open


# Load unassigned devices (Owner = "admin") in dropdown
@callback(
    Output('assign-device-selector', 'options'),
    Input('assign-device-modal', 'is_open'),
    prevent_initial_call=True
)
def load_unassigned_devices(modal_is_open):
    """Load devices where Owner = 'admin' for assignment"""
    if not modal_is_open:
        return no_update
    
    try:
        from app.services.device_info_service import DeviceInfoService
        device_info_service = DeviceInfoService()
        
        if not device_info_service.is_connected():
            logger.error("❌ Device Info Service not connected")
            return [{'label': '⚠️ Database not connected', 'value': None, 'disabled': True}]
        
        # Get all devices with Owner = "admin"
        all_devices = device_info_service.get_all_devices_info(
            owner_filter="admin",
            is_admin=False
        )
        
        # Filter to only show devices with Owner = "admin"
        unassigned_devices = [
            {'label': f"{device.get('Sr_No')} - {device.get('Device_Name', 'Unnamed')}", 
             'value': device.get('Sr_No')}
            for device in all_devices
            if device.get('Owner') == 'admin'
        ]
        
        if not unassigned_devices:
            return [{'label': 'No unassigned devices found', 'value': None, 'disabled': True}]
        
        logger.info(f"✅ Loaded {len(unassigned_devices)} unassigned devices")
        return unassigned_devices
        
    except Exception as e:
        logger.error(f"Error loading unassigned devices: {e}")
        logger.exception("Full error traceback:")
        return [{'label': f'⚠️ Error loading devices: {str(e)}', 'value': None, 'disabled': True}]


# Load users (excluding admin) in dropdown
@callback(
    Output('assign-user-selector', 'options'),
    Input('assign-device-modal', 'is_open'),
    prevent_initial_call=True
)
def load_users_for_assignment(modal_is_open):
    """Load all users except 'admin' for device assignment"""
    if not modal_is_open:
        return no_update
    
    try:
        from app.services.user_service import UserService
        user_service = UserService()
        
        if not user_service.connected:
            logger.error("❌ User Service not connected")
            return [{'label': '⚠️ Database not connected', 'value': None, 'disabled': True}]
        
        # Get all users
        all_users = user_service.get_all_users()
        
        # Filter out 'admin' user and get unique user IDs
        seen_user_ids = set()
        user_options = []
        
        for user in all_users:
            user_id = user.get('User_Id')
            if user_id and user_id != 'admin' and user_id not in seen_user_ids:
                seen_user_ids.add(user_id)
                # Get user details for label
                email = user.get('Email_Id', '')
                company = user.get('Company_Name', '')
                label_parts = [user_id]
                if email:
                    label_parts.append(f"({email})")
                if company:
                    label_parts.append(f"- {company}")
                
                user_options.append({
                    'label': ' - '.join(label_parts),
                    'value': user_id
                })
        
        # Sort by user ID
        user_options.sort(key=lambda x: x['value'])
        
        if not user_options:
            return [{'label': 'No users found (excluding admin)', 'value': None, 'disabled': True}]
        
        logger.info(f"✅ Loaded {len(user_options)} users for assignment (admin excluded)")
        return user_options
        
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        logger.exception("Full error traceback:")
        return [{'label': f'⚠️ Error loading users: {str(e)}', 'value': None, 'disabled': True}]


# Assign device to user callback
@callback(
    [Output('assign-device-alert', 'children'),
     Output('assign-device-modal', 'is_open', allow_duplicate=True),
     Output('assign-device-selector', 'value'),
     Output('assign-user-selector', 'value'),
     Output('assign-device-name', 'value')],
    Input('save-assign-device-btn', 'n_clicks'),
    [State('assign-device-selector', 'value'),
     State('assign-user-selector', 'value'),
     State('assign-device-name', 'value')],
    prevent_initial_call=True
)
def assign_device_to_user(n_clicks, serial_number, user_id, device_name):
    """Assign device to user by deleting old records and creating new one"""
    if not n_clicks:
        return no_update, no_update, no_update, no_update, no_update
    
    # Validation
    if not serial_number:
        alert = dbc.Alert(
            "⚠️ Please select a device to assign",
            color="warning",
            dismissable=True,
            duration=3000
        )
        return alert, True, no_update, no_update, no_update
    
    if not user_id:
        alert = dbc.Alert(
            "⚠️ Please select a user to assign the device to",
            color="warning",
            dismissable=True,
            duration=3000
        )
        return alert, True, no_update, no_update, no_update
    
    if not device_name or not device_name.strip():
        alert = dbc.Alert(
            "⚠️ Please enter a device name",
            color="warning",
            dismissable=True,
            duration=3000
        )
        return alert, True, no_update, no_update, no_update
    
    try:
        from app.services.device_info_service import DeviceInfoService
        device_info_service = DeviceInfoService()
        
        if not device_info_service.is_connected():
            alert = dbc.Alert(
                "❌ Database connection error. Please try again.",
                color="danger",
                dismissable=True,
                duration=5000
            )
            return alert, True, no_update, no_update, no_update
        
        # Assign device using the new method that deletes old records first
        success = device_info_service.assign_device_to_user(
            serial_number=serial_number,
            new_owner=user_id,
            device_name=device_name.strip()
        )
        
        if success:
            alert = dbc.Alert(
                f"✅ Device '{serial_number}' successfully assigned to user '{user_id}' with name '{device_name.strip()}'",
                color="success",
                dismissable=True,
                duration=5000
            )
            logger.info(f"✅ Device assignment successful: {serial_number} -> {user_id}")
            # Clear form and close modal
            return alert, False, None, None, ""
        else:
            alert = dbc.Alert(
                f"❌ Failed to assign device. Please check logs for details.",
                color="danger",
                dismissable=True,
                duration=5000
            )
            logger.error(f"❌ Device assignment failed: {serial_number} -> {user_id}")
            return alert, True, no_update, no_update, no_update
        
    except Exception as e:
        logger.error(f"Error assigning device: {e}")
        logger.exception("Full error traceback:")
        alert = dbc.Alert(
            f"❌ Error: {str(e)}",
            color="danger",
            dismissable=True,
            duration=5000
        )
        return alert, True, no_update, no_update, no_update


# Settings Page Callbacks - Delete User Modal
@callback(
    Output("delete-user-modal", "is_open"),
    [Input("delete-user-btn", "n_clicks"),
     Input("close-delete-user-modal", "n_clicks"),
     Input("confirm-delete-user-btn", "n_clicks")],
    [State("delete-user-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_delete_user_modal(open_clicks, close_clicks, delete_clicks, is_open):
    """Toggle delete user modal"""
    from dash import ctx
    
    if not ctx.triggered:
        return is_open
    
    ctx_triggered = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if ctx_triggered == "delete-user-btn" and open_clicks:
        return True
    elif ctx_triggered in ["close-delete-user-modal", "confirm-delete-user-btn"]:
        return False
    return is_open


# Load users (excluding admin) for delete dropdown
@callback(
    Output('delete-user-selector', 'options'),
    Input('delete-user-modal', 'is_open'),
    prevent_initial_call=True
)
def load_users_for_deletion(modal_is_open):
    """Load all users except 'admin' for deletion"""
    if not modal_is_open:
        return no_update
    
    try:
        from app.services.user_service import UserService
        user_service = UserService()
        
        if not user_service.connected:
            logger.error("❌ User Service not connected")
            return [{'label': '⚠️ Database not connected', 'value': None, 'disabled': True}]
        
        # Get all users
        all_users = user_service.get_all_users()
        
        # Filter out 'admin' user and get unique user IDs
        seen_user_ids = set()
        user_options = []
        
        for user in all_users:
            user_id = user.get('User_Id')
            if user_id and user_id != 'admin' and user_id not in seen_user_ids:
                seen_user_ids.add(user_id)
                # Get user details for label
                email = user.get('Email_Id', '')
                company = user.get('Company_Name', '')
                label_parts = [user_id]
                if email:
                    label_parts.append(f"({email})")
                if company:
                    label_parts.append(f"- {company}")
                
                user_options.append({
                    'label': ' - '.join(label_parts),
                    'value': user_id
                })
        
        # Sort by user ID
        user_options.sort(key=lambda x: x['value'])
        
        if not user_options:
            return [{'label': 'No users found (excluding admin)', 'value': None, 'disabled': True}]
        
        logger.info(f"✅ Loaded {len(user_options)} users for deletion (admin excluded)")
        return user_options
        
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        logger.exception("Full error traceback:")
        return [{'label': f'⚠️ Error loading users: {str(e)}', 'value': None, 'disabled': True}]


# Show user details and check for assigned devices when user is selected
@callback(
    [Output('delete-user-details', 'children'),
     Output('confirm-delete-user-btn', 'disabled'),
     Output('delete-user-alert', 'children')],
    Input('delete-user-selector', 'value'),
    prevent_initial_call=True
)
def show_user_details_and_check_devices(selected_user_id):
    """Show user details and check if user has assigned devices"""
    if not selected_user_id:
        return [], True, []
    
    # Safety check: Never allow admin deletion
    if selected_user_id == 'admin':
        alert = dbc.Alert(
            "❌ Admin user cannot be deleted",
            color="danger",
            dismissable=True,
            duration=3000
        )
        return [], True, alert
    
    try:
        from app.services.user_service import UserService
        from app.services.device_info_service import DeviceInfoService
        
        user_service = UserService()
        device_info_service = DeviceInfoService()
        
        if not user_service.connected:
            alert = dbc.Alert(
                "❌ Database connection error",
                color="danger",
                dismissable=True,
                duration=3000
            )
            return [], True, alert
        
        # Get user details
        user = user_service.get_user_by_id(selected_user_id)
        if not user:
            alert = dbc.Alert(
                f"❌ User '{selected_user_id}' not found",
                color="danger",
                dismissable=True,
                duration=3000
            )
            return [], True, alert
        
        # Check if user has assigned devices
        has_devices = device_info_service.user_has_assigned_devices(selected_user_id)
        
        # Build user details display
        user_details = [
            html.Hr(className='my-3'),
            html.H6("User Details", className='fw-bold mb-3'),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-building me-2", style={'color': '#e91e63'}),
                        html.Strong("Company Name: "),
                        html.Span(user.get('Company_Name', 'N/A'))
                    ], className='mb-2')
                ], md=6),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-envelope me-2", style={'color': '#dc3545'}),
                        html.Strong("Email ID: "),
                        html.Span(user.get('Email_Id', 'N/A'))
                    ], className='mb-2')
                ], md=6),
            ], className='mb-2'),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-phone me-2", style={'color': '#9c27b0'}),
                        html.Strong("Phone Number: "),
                        html.Span(user.get('Phone_No', 'N/A'))
                    ], className='mb-2')
                ], md=6),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-user-tag me-2", style={'color': '#9c27b0'}),
                        html.Strong("User Type: "),
                        html.Span(user.get('User_Type', 'N/A'))
                    ], className='mb-2')
                ], md=6),
            ], className='mb-3'),
        ]
        
        # Check for assigned devices
        if has_devices:
            # Get device list for display
            devices = device_info_service.get_all_devices_info(owner_filter=selected_user_id, is_admin=False)
            device_list = [device.get('Sr_No') for device in devices]
            
            alert = dbc.Alert([
                html.H6("⚠️ Cannot Delete User", className='alert-heading'),
                html.P(f"This user cannot be deleted because {len(devices)} device(s) are still assigned:"),
                html.Ul([html.Li(device_id) for device_id in device_list[:10]], className='mb-0'),
                html.P("Please unassign all devices first before deleting this user.", className='mb-0 mt-2')
            ], color="warning", dismissable=True)
            
            # Disable delete button
            return user_details, True, alert
        else:
            alert = dbc.Alert(
                "✅ This user has no assigned devices. Safe to delete.",
                color="success",
                dismissable=True,
                duration=5000
            )
            # Enable delete button
            return user_details, False, alert
        
    except Exception as e:
        logger.error(f"Error showing user details: {e}")
        logger.exception("Full error traceback:")
        alert = dbc.Alert(
            f"❌ Error: {str(e)}",
            color="danger",
            dismissable=True,
            duration=5000
        )
        return [], True, alert


# Delete user callback
@callback(
    [Output('delete-user-alert', 'children', allow_duplicate=True),
     Output('delete-user-modal', 'is_open', allow_duplicate=True),
     Output('delete-user-selector', 'value')],
    Input('confirm-delete-user-btn', 'n_clicks'),
    [State('delete-user-selector', 'value')],
    prevent_initial_call=True
)
def delete_user(n_clicks, user_id):
    """Delete user after safety checks"""
    if not n_clicks:
        return no_update, no_update, no_update
    
    # Safety check: Never allow admin deletion
    if user_id == 'admin':
        alert = dbc.Alert(
            "❌ Admin user cannot be deleted",
            color="danger",
            dismissable=True,
            duration=5000
        )
        return alert, True, no_update
    
    if not user_id:
        alert = dbc.Alert(
            "⚠️ Please select a user to delete",
            color="warning",
            dismissable=True,
            duration=3000
        )
        return alert, True, no_update
    
    try:
        from app.services.user_service import UserService
        from app.services.device_info_service import DeviceInfoService
        
        user_service = UserService()
        device_info_service = DeviceInfoService()
        
        if not user_service.connected:
            alert = dbc.Alert(
                "❌ Database connection error. Please try again.",
                color="danger",
                dismissable=True,
                duration=5000
            )
            return alert, True, no_update
        
        # Final safety check: Verify user has no assigned devices
        has_devices = device_info_service.user_has_assigned_devices(user_id)
        if has_devices:
            devices = device_info_service.get_all_devices_info(owner_filter=user_id, is_admin=False)
            device_list = [device.get('Sr_No') for device in devices]
            
            alert = dbc.Alert([
                html.H6("❌ Cannot Delete User", className='alert-heading'),
                html.P(f"This user cannot be deleted because {len(devices)} device(s) are still assigned:"),
                html.Ul([html.Li(device_id) for device_id in device_list[:10]], className='mb-0'),
                html.P("Please unassign all devices first before deleting this user.", className='mb-0 mt-2')
            ], color="danger", dismissable=True)
            return alert, True, no_update
        
        # Delete user - this will delete all User_info records for this user
        success = user_service.delete_all_user_entries(user_id)
        
        if success:
            alert = dbc.Alert(
                f"✅ User '{user_id}' has been successfully deleted from the system.",
                color="success",
                dismissable=True,
                duration=5000
            )
            logger.info(f"✅ User deletion successful: {user_id}")
            # Clear form and close modal
            return alert, False, None
        else:
            alert = dbc.Alert(
                f"❌ Failed to delete user. Please check logs for details.",
                color="danger",
                dismissable=True,
                duration=5000
            )
            logger.error(f"❌ User deletion failed: {user_id}")
            return alert, True, no_update
        
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        logger.exception("Full error traceback:")
        alert = dbc.Alert(
            f"❌ Error: {str(e)}",
            color="danger",
            dismissable=True,
            duration=5000
        )
        return alert, True, no_update


# Settings Page Callbacks - Device List Table (Real-time)
@callback(
    Output('device-list-tbody', 'children'),
    [Input('device-filter-toggle', 'value'),
     Input('assign-device-modal', 'is_open'),  # Refresh when assign modal closes
     Input('delete-user-modal', 'is_open')],  # Refresh when delete modal closes
    prevent_initial_call=False
)
def load_device_list_table(filter_value, assign_modal_open, delete_modal_open, edit_modal_open):
    """Load device list table based on filter toggle"""
    from dash import ctx
    
    try:
        from app.services.device_info_service import DeviceInfoService
        device_info_service = DeviceInfoService()
        
        if not device_info_service.is_connected():
            logger.error("❌ Device Info Service not connected")
            return [html.Tr([
                html.Td("Database not connected", colSpan=5, className='text-center text-muted')
            ])]
        
        # Get all devices (admin sees all)
        all_devices = device_info_service.get_all_devices_info(owner_filter=None, is_admin=True)
        
        if not all_devices:
            return [html.Tr([
                html.Td("No devices found", colSpan=5, className='text-center text-muted')
            ])]
        
        # Filter devices based on toggle
        if filter_value == 'unassigned':
            # Show only devices with Owner = "admin"
            filtered_devices = [d for d in all_devices if d.get('Owner') == 'admin']
        else:  # assigned
            # Show only devices with Owner != "admin"
            filtered_devices = [d for d in all_devices if d.get('Owner') != 'admin']
        
        if not filtered_devices:
            status_text = "UnAssigned" if filter_value == 'unassigned' else "Assigned"
            return [html.Tr([
                html.Td(f"No {status_text.lower()} devices found", colSpan=5, className='text-center text-muted')
            ])]
        
        # Build table rows
        rows = []
        for device in filtered_devices:
            device_id = device.get('Sr_No', 'N/A')
            user_id = device.get('Owner', 'admin')
            device_name = device.get('Device_Name', 'Unnamed')
            
            # Debug logging to check device data
            logger.debug(f"Device in table: Sr_No={device_id}, Owner={user_id}, Device_Name={device_name}")
            
            # Status badge
            if filter_value == 'unassigned':
                status_badge = html.Span("Not Alloted", className='badge bg-secondary')
            else:
                status_badge = html.Span("Allotted", className='badge bg-success')
            
            # Actions buttons
            if filter_value == 'unassigned':
                # UnAssigned devices: Only Delete button
                actions = dbc.Button(
                    "Delete",
                    size='sm',
                    color='danger',
                    id={'type': 'delete-device-btn', 'index': device_id},
                    n_clicks=0
                )
            else:
                # Assigned devices: Edit + Free buttons
                actions = html.Div([
                    dbc.Button(
                        "Edit",
                        size='sm',
                        color='primary',
                        className='me-1',
                        id={'type': 'edit-device-btn', 'index': device_id},
                        n_clicks=0
                    ),
                    dbc.Button(
                        "Free",
                        size='sm',
                        color='warning',
                        id={'type': 'free-device-btn', 'index': device_id},
                        n_clicks=0
                    )
                ])
            
            rows.append(html.Tr([
                html.Td(device_id),
                html.Td(user_id if filter_value == 'assigned' else 'Unassigned'),
                html.Td(device_name),
                html.Td(status_badge),
                html.Td(actions)
            ]))
        
        logger.info(f"✅ Loaded {len(rows)} {filter_value} devices in table")
        return rows
        
    except Exception as e:
        logger.error(f"Error loading device list: {e}")
        logger.exception("Full error traceback:")
        return [html.Tr([
            html.Td(f"Error loading devices: {str(e)}", colSpan=5, className='text-center text-danger')
        ])]


# Settings Page Callbacks - Edit Device Modal
@callback(
    [Output("edit-device-modal", "is_open"),
     Output("edit-device-id", "value"),
     Output("edit-device-name", "value"),
     Output("edit-user-selector", "value")],
    [Input({'type': 'edit-device-btn', 'index': ALL}, 'n_clicks'),
     Input("close-edit-device-modal", "n_clicks"),
     Input("save-edit-device-btn", "n_clicks")],
    [State("edit-device-modal", "is_open"),
     State({'type': 'edit-device-btn', 'index': ALL}, 'id')],
    prevent_initial_call=True
)
def toggle_edit_device_modal(edit_clicks_list, close_clicks, save_clicks, is_open, edit_button_ids):
    """Toggle edit device modal and load device info"""
    from dash import ctx
    
    if not ctx.triggered:
        return is_open, '', '', None
    
    ctx_triggered = ctx.triggered[0]['prop_id']
    
    # Handle Edit button clicks
    if 'edit-device-btn' in ctx_triggered:
        # Extract device_id from triggered prop_id
        device_id = None
        try:
            # The prop_id format is like: '{"type":"edit-device-btn","index":"SN1234567891"}.n_clicks'
            import json
            prop_id_str = ctx_triggered.split('.')[0]
            prop_id_dict = json.loads(prop_id_str)
            device_id = prop_id_dict.get('index')
        except Exception as e:
            logger.warning(f"Could not parse device_id from prop_id: {e}")
            # Fallback: try to find from button IDs and clicks
            if edit_button_ids and edit_clicks_list:
                for i, btn_id in enumerate(edit_button_ids):
                    if btn_id and isinstance(btn_id, dict) and btn_id.get('type') == 'edit-device-btn':
                        if i < len(edit_clicks_list) and edit_clicks_list[i] and edit_clicks_list[i] > 0:
                            device_id = btn_id.get('index')
                            break
        
        if device_id:
            # Load device info
            try:
                from app.services.device_info_service import DeviceInfoService
                device_info_service = DeviceInfoService()
                device_info = device_info_service.get_device_info(device_id)
                
                if device_info:
                    device_name = device_info.get('Device_Name', 'Unnamed')
                    logger.info(f"✅ Loaded device info for edit: {device_id}, Device_Name: {device_name}")
                    return True, device_id, device_name, None
                else:
                    logger.warning(f"Device {device_id} not found")
                    return True, device_id, '', None
            except Exception as e:
                logger.error(f"Error loading device info: {e}")
                return True, device_id, '', None
        else:
            logger.warning("Could not extract device_id from edit button click")
            return is_open, '', '', None
    
    # Handle close/save button clicks
    elif ctx_triggered in ["close-edit-device-modal", "save-edit-device-btn"]:
        return False, '', '', None
    
    return is_open, '', '', None


# Load users for Edit Device (excluding admin and current owner)
@callback(
    [Output('edit-user-selector', 'options'),
     Output('edit-user-selector', 'value')],
    [Input('edit-device-modal', 'is_open'),
     Input('edit-device-id', 'value')],
    prevent_initial_call=True
)
def load_users_for_edit_device(modal_is_open, device_id):
    """Load users excluding admin and current device owner"""
    if not modal_is_open or not device_id:
        return no_update, no_update
    
    try:
        from app.services.user_service import UserService
        from app.services.device_info_service import DeviceInfoService
        
        user_service = UserService()
        device_info_service = DeviceInfoService()
        
        if not user_service.connected:
            logger.error("❌ User Service not connected")
            return [{'label': '⚠️ Database not connected', 'value': None, 'disabled': True}], None
        
        # Get current device owner
        device_info = device_info_service.get_device_info(device_id)
        current_owner = None
        if device_info:
            current_owner = device_info.get('Owner', 'admin')
            logger.info(f"Current owner of device {device_id}: {current_owner}")
        
        # Get all users
        all_users = user_service.get_all_users()
        
        # Filter out 'admin' and current owner
        seen_user_ids = set()
        user_options = []
        
        for user in all_users:
            user_id = user.get('User_Id')
            if user_id and user_id != 'admin' and user_id != current_owner and user_id not in seen_user_ids:
                seen_user_ids.add(user_id)
                # Get user details for label
                email = user.get('Email_Id', '')
                company = user.get('Company_Name', '')
                label_parts = [user_id]
                if email:
                    label_parts.append(f"({email})")
                if company:
                    label_parts.append(f"- {company}")
                
                user_options.append({
                    'label': ' - '.join(label_parts),
                    'value': user_id
                })
        
        # Sort by user ID
        user_options.sort(key=lambda x: x['value'])
        
        if not user_options:
            return [{'label': f'No other users available (admin and {current_owner} excluded)', 'value': None, 'disabled': True}], None
        
        logger.info(f"✅ Loaded {len(user_options)} users for edit device (admin and {current_owner} excluded)")
        return user_options, None
        
    except Exception as e:
        logger.error(f"Error loading users for edit: {e}")
        logger.exception("Full error traceback:")
        return [{'label': f'⚠️ Error loading users: {str(e)}', 'value': None, 'disabled': True}], None


# Save Edit Device (Re-assign device)
@callback(
    [Output('edit-device-alert', 'children'),
     Output('edit-device-modal', 'is_open', allow_duplicate=True),
     Output('edit-device-id', 'value', allow_duplicate=True),
     Output('edit-device-name', 'value', allow_duplicate=True),
     Output('edit-user-selector', 'value', allow_duplicate=True)],
    Input('save-edit-device-btn', 'n_clicks'),
    [State('edit-device-id', 'value'),
     State('edit-user-selector', 'value'),
     State('edit-device-name', 'value')],
    prevent_initial_call=True
)
def save_edit_device(n_clicks, device_id, new_user_id, device_name):
    """Re-assign device to new user with updated device name"""
    if not n_clicks:
        return no_update, no_update, no_update, no_update, no_update
    
    # Validation
    if not device_id:
        alert = dbc.Alert(
            "⚠️ Device ID is missing",
            color="warning",
            dismissable=True,
            duration=3000
        )
        return alert, True, no_update, no_update, no_update
    
    if not new_user_id:
        alert = dbc.Alert(
            "⚠️ Please select a new user to assign the device to",
            color="warning",
            dismissable=True,
            duration=3000
        )
        return alert, True, no_update, no_update, no_update
    
    if not device_name or not device_name.strip():
        alert = dbc.Alert(
            "⚠️ Please enter a device name",
            color="warning",
            dismissable=True,
            duration=3000
        )
        return alert, True, no_update, no_update, no_update
    
    try:
        from app.services.device_info_service import DeviceInfoService
        device_info_service = DeviceInfoService()
        
        if not device_info_service.is_connected():
            alert = dbc.Alert(
                "❌ Database connection error. Please try again.",
                color="danger",
                dismissable=True,
                duration=5000
            )
            return alert, True, no_update, no_update, no_update
        
        # Re-assign device using the same method that deletes old records first
        success = device_info_service.assign_device_to_user(
            serial_number=device_id,
            new_owner=new_user_id,
            device_name=device_name.strip()
        )
        
        if success:
            alert = dbc.Alert(
                f"✅ Device '{device_id}' successfully re-assigned to user '{new_user_id}' with name '{device_name.strip()}'",
                color="success",
                dismissable=True,
                duration=5000
            )
            logger.info(f"✅ Device edit successful: {device_id} -> {new_user_id}")
            # Clear form and close modal
            return alert, False, '', '', None
        else:
            alert = dbc.Alert(
                f"❌ Failed to update device. Please check logs for details.",
                color="danger",
                dismissable=True,
                duration=5000
            )
            logger.error(f"❌ Device edit failed: {device_id} -> {new_user_id}")
            return alert, True, no_update, no_update, no_update
        
    except Exception as e:
        logger.error(f"Error editing device: {e}")
        logger.exception("Full error traceback:")
        alert = dbc.Alert(
            f"❌ Error: {str(e)}",
            color="danger",
            dismissable=True,
            duration=5000
        )
        return alert, True, no_update, no_update, no_update
             

# Profile Page Callbacks - Navigate to change password page
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('change-password-btn', 'n_clicks'),
    prevent_initial_call=True
)
def navigate_to_change_password(n_clicks):
    """Navigate to change password page from profile"""
    if n_clicks and n_clicks > 0:
        return '/change-password'
    return no_update


def create_help_content():
    """Create help page content"""
    return html.Div([
        html.Div([
            html.H4("📚 Documentation", className='fw-bold mb-4'),
            
            dbc.Accordion([
                dbc.AccordionItem([
                    html.P("IOTNarad is a comprehensive IoT device management platform that allows you to:"),
                    html.Ul([
                        html.Li("Configure ESP32 devices remotely via MQTT"),
                        html.Li("Monitor real-time sensor data"),
                        html.Li("Store and analyze historical data"),
                        html.Li("Manage multiple devices from a single dashboard"),
                    ])
                ], title="What is IOTNarad?"),
                
                dbc.AccordionItem([
                    html.P("The system uses the following architecture:"),
                    html.Pre("""
IoT Devices → Mosquitto MQTT → Docker App → InfluxDB 2.x → Dashboard
     ↓              ↓                ↓              ↓              ↓
  Sensors    Local Broker      GCP VM App   Cloud Database  Plotly Dash
                (GCP VM)         (GCP VM)                    + WebSocket
                    """, style={'background': '#f8f9fa', 'padding': '1rem', 'borderRadius': '8px'})
                ], title="System Architecture"),
                
                dbc.AccordionItem([
                    html.Ol([
                        html.Li("Login with your admin credentials"),
                        html.Li("Navigate to the Devices page"),
                        html.Li("Select the device type (Analog, Digital, or Communication)"),
                        html.Li("Configure the channels and settings"),
                        html.Li("Click Save to push configuration to devices via MQTT"),
                    ])
                ], title="How to Configure Devices"),
                
                dbc.AccordionItem([
                    html.P("For support, contact:"),
                    html.Ul([
                        html.Li([html.B("Email: "), "support@iotnarad.com"]),
                        html.Li([html.B("GitHub: "), html.A("github.com/iotnarad", href="#")]),
                        html.Li([html.B("Documentation: "), html.A("docs.iotnarad.com", href="#")]),
                    ])
                ], title="Support & Contact"),
            ], start_collapsed=True),
        ], className='stat-card', style={
            'background': 'white',
            'borderRadius': '12px',
            'padding': '1.5rem',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
            'border': '1px solid #e9ecef',
            'transition': 'all 0.3s ease'
        }),
    ])
            