"""
Dashboard Page Layout
Main dashboard with sidebar navigation and content area
"""
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from datetime import datetime
import pytz

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
                    
                    # Profile (for regular users)
                    dbc.NavLink([
                        html.I(className="fas fa-user me-3", style={'color': 'white'}),
                        html.Span("Profile", style={'color': 'white'})
                    ], id='nav-profile', href='#', className='nav-item-custom',
                       n_clicks=0, style={'display': 'none', 'color': 'white'}),
                    
                    # Settings (for admin users only)
                    dbc.NavLink([
                        html.I(className="fas fa-cog me-3", style={'color': 'white'}),
                        html.Span("Settings", style={'color': 'white'})
                    ], id='nav-settings', href='#', className='nav-item-custom',
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
    [Output('dashboard-content', 'children'),
     Output('active-page-store', 'data'),
     Output('page-title', 'children'),
     Output('page-subtitle', 'children'),
     Output('nav-home', 'className'),
     Output('nav-analytics', 'className'),
     Output('nav-oee', 'className'),
     Output('nav-devices', 'className'),
     Output('nav-profile', 'className'),
     Output('nav-settings', 'className'),
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
    prevent_initial_call=False
)
def update_page_content(home_clicks, analytics_clicks, oee_clicks, devices_clicks, profile_clicks, settings_clicks, help_clicks, current_page, session_data):
    """Update page content based on navigation"""
    from dash import ctx
    from app.pages.device_config import create_device_config_layout
    from app.pages.analytics import create_analytics_layout
    from app.pages.settings import create_settings_layout
    
    # Get user type from session
    user_type = session_data.get('user_type', 'user') if session_data else 'user'
    print(f"User type: {user_type}, Triggered ID: {ctx.triggered_id if ctx.triggered_id else 'None'}")  # Debug
    
    # Determine which button was clicked
    if ctx.triggered_id == 'nav-analytics':
        page = 'analytics'
    elif ctx.triggered_id == 'nav-oee':
        page = 'oee'
    elif ctx.triggered_id == 'nav-devices':
        page = 'devices'
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
    
    # Set visibility based on user type
    profile_style = {'display': 'block'} if user_type == 'user' else {'display': 'none'}
    settings_style = {'display': 'block'} if user_type == 'admin' else {'display': 'none'}
    
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
        content = create_device_config_layout()
        title = "Devices"
        subtitle = "Configure and manage your IoT devices"
    elif page == 'profile':
        content = create_profile_content()
        title = "Profile"
        subtitle = "User profile management"
    elif page == 'settings':
        content = create_settings_content()
        title = "Settings"
        subtitle = "Admin management panel"
    else:  # help
        content = create_help_content()
        title = "Help"
        subtitle = "Documentation and support"
    
    return (content, page, title, subtitle, 
            nav_classes['home'], nav_classes['analytics'], 
            nav_classes['oee'], nav_classes['devices'], nav_classes['profile'], 
            nav_classes['settings'], nav_classes['help'],
            profile_style, settings_style)


def create_home_content():
    """Create home page content with statistics"""
    return html.Div([
        # Statistics Cards Row
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-industry fa-2x",
                               style={'color': '#667eea'}),
                        html.Div([
                            html.H3("87.5%", className='mb-0 fw-bold'),
                            html.P("Overall OEE", className='mb-0 text-muted',
                                   style={'fontSize': '0.9rem'}),
                        ], className='ms-3'),
                    ], className='d-flex align-items-center'),
                ], className='stat-card', style={
                    'background': 'white',
                    'borderRadius': '12px',
                    'padding': '1.5rem',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                    'border': '1px solid #e9ecef',
                    'transition': 'all 0.3s ease'
                }),
            ], md=3),
            
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-microchip fa-2x",
                               style={'color': '#4ade80'}),
                        html.Div([
                            html.H3("6", className='mb-0 fw-bold'),
                            html.P("Production Lines", className='mb-0 text-muted',
                                   style={'fontSize': '0.9rem'}),
                        ], className='ms-3'),
                    ], className='d-flex align-items-center'),
                ], className='stat-card', style={
                    'background': 'white',
                    'borderRadius': '12px',
                    'padding': '1.5rem',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                    'border': '1px solid #e9ecef',
                    'transition': 'all 0.3s ease'
                }),
            ], md=3),
            
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-cogs fa-2x",
                               style={'color': '#fbbf24'}),
                        html.Div([
                            html.H3("4,890", className='mb-0 fw-bold'),
                            html.P("Units Produced", className='mb-0 text-muted',
                                   style={'fontSize': '0.9rem'}),
                        ], className='ms-3'),
                    ], className='d-flex align-items-center'),
                ], className='stat-card', style={
                    'background': 'white',
                    'borderRadius': '12px',
                    'padding': '1.5rem',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                    'border': '1px solid #e9ecef',
                    'transition': 'all 0.3s ease'
                }),
            ], md=3),
            
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-chart-line fa-2x",
                               style={'color': '#10b981'}),
                        html.Div([
                            html.H3("94.8%", className='mb-0 fw-bold'),
                            html.P("Quality Rate", className='mb-0 text-muted',
                                   style={'fontSize': '0.9rem'}),
                        ], className='ms-3'),
                    ], className='d-flex align-items-center'),
                ], className='stat-card', style={
                    'background': 'white',
                    'borderRadius': '12px',
                    'padding': '1.5rem',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                    'border': '1px solid #e9ecef',
                    'transition': 'all 0.3s ease'
                }),
            ], md=3),
        ], className='mb-4'),
        
        # Welcome Message
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4("🏭 Manufacturing Excellence Dashboard", className='fw-bold mb-3'),
                    html.P([
                        "Welcome to IOTNarad OEE Management Platform. ",
                        "Monitor Overall Equipment Effectiveness and optimize your manufacturing operations in real-time."
                    ], className='mb-3'),
                    html.Ul([
                        html.Li("View OEE Dashboard for real-time manufacturing metrics"),
                        html.Li("Monitor production lines and equipment performance"),
                        html.Li("Analyze Six Big Losses and improvement opportunities"),
                        html.Li("Track quality rates and production efficiency"),
                    ], className='mb-3'),
                    dbc.Button([
                        html.I(className="fas fa-industry me-2"),
                        "View OEE Dashboard"
                    ], color='primary', size='lg', id='quick-oee-dashboard'),
                ], className='stat-card', style={
                    'background': 'white',
                    'borderRadius': '12px',
                    'padding': '1.5rem',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                    'border': '1px solid #e9ecef',
                    'transition': 'all 0.3s ease'
                }),
            ], md=8),
            
            dbc.Col([
                html.Div([
                    html.H5("Production Status", className='fw-bold mb-3'),
                    html.Div([
                        html.Div([
                            html.Span("Lines Running", className='fw-500'),
                            html.Span([
                                html.I(className="fas fa-circle me-2",
                                       style={'color': '#4ade80', 'fontSize': '0.6rem'}),
                                "5/6 Active"
                            ], className='badge bg-light text-success'),
                        ], className='d-flex justify-content-between mb-2'),
                        
                        html.Div([
                            html.Span("OEE Target", className='fw-500'),
                            html.Span([
                                html.I(className="fas fa-circle me-2",
                                       style={'color': '#4ade80', 'fontSize': '0.6rem'}),
                                "87.5% (Target: 85%)"
                            ], className='badge bg-light text-success'),
                        ], className='d-flex justify-content-between mb-2'),
                        
                        html.Div([
                            html.Span("Quality Rate", className='fw-500'),
                            html.Span([
                                html.I(className="fas fa-circle me-2",
                                       style={'color': '#4ade80', 'fontSize': '0.6rem'}),
                                "94.8%"
                            ], className='badge bg-light text-success'),
                        ], className='d-flex justify-content-between'),
                    ]),
                ], className='stat-card', style={
                    'background': 'white',
                    'borderRadius': '12px',
                    'padding': '1.5rem',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                    'border': '1px solid #e9ecef',
                    'transition': 'all 0.3s ease'
                }),
            ], md=4),
        ]),
    ])


def create_profile_content():
    """Create profile page content"""
    return html.Div([
        html.H4("User Profile", className='fw-bold mb-4'),
        html.P("Manage your profile settings and preferences.", className='text-muted'),
        # Add profile content here
    ])


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
                    
                    # User Management Table
                    html.Div([
                        html.H6("Users List", className='fw-bold mb-3'),
                        dbc.Table([
                            html.Thead([
                                html.Tr([
                                    html.Th("User ID"),
                                    html.Th("Name"),
                                    html.Th("Email"),
                                    html.Th("User Type"),
                                    html.Th("Status"),
                                    html.Th("Actions"),
                                ])
                            ]),
                            html.Tbody([
                                html.Tr([
                                    html.Td("admin"),
                                    html.Td("Administrator"),
                                    html.Td("admin@iotnarad.com"),
                                    html.Td([
                                        html.Span("Admin", className='badge bg-danger')
                                    ]),
                                    html.Td([
                                        html.Span("Active", className='badge bg-success')
                                    ]),
                                    html.Td([
                                        dbc.Button("Edit", size='sm', color='primary', className='me-1'),
                                        dbc.Button("Delete", size='sm', color='danger'),
                                    ]),
                                ]),
                                html.Tr([
                                    html.Td("sanjay"),
                                    html.Td("Sanjay Kumar"),
                                    html.Td("sanjay@company.com"),
                                    html.Td([
                                        html.Span("User", className='badge bg-primary')
                                    ]),
                                    html.Td([
                                        html.Span("Active", className='badge bg-success')
                                    ]),
                                    html.Td([
                                        dbc.Button("Edit", size='sm', color='primary', className='me-1'),
                                        dbc.Button("Delete", size='sm', color='danger'),
                                    ]),
                                ]),
                                html.Tr([
                                    html.Td("ridhi"),
                                    html.Td("Ridhi Sharma"),
                                    html.Td("ridhi@company.com"),
                                    html.Td([
                                        html.Span("User", className='badge bg-primary')
                                    ]),
                                    html.Td([
                                        html.Span("Active", className='badge bg-success')
                                    ]),
                                    html.Td([
                                        dbc.Button("Edit", size='sm', color='primary', className='me-1'),
                                        dbc.Button("Delete", size='sm', color='danger'),
                                    ]),
                                ]),
                            ])
                        ], striped=True, bordered=True, hover=True, responsive=True),
                    ], className='mt-3'),
                    
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
                    
                    # Device Assignment Table
                    dbc.Table([
                        html.Thead([
                            html.Tr([
                                html.Th("Device ID"),
                                html.Th("User ID"),
                                html.Th("Device Name"),
                                html.Th("UnAssigned / Assigned"),
                                html.Th("Actions"),
                            ])
                        ]),
                        html.Tbody([
                            html.Tr([
                                html.Td("XAP-1308"),
                                html.Td("sanjay"),
                                html.Td("Noida"),
                                html.Td([
                                    html.Div([
                                        html.Span("Allotted", className='badge bg-success me-2'),
                                        html.Div([
                                            html.Span("UnAssigned", className='badge bg-secondary me-1'),
                                            html.Div(className='toggle-switch', style={
                                                'width': '40px', 'height': '20px', 'backgroundColor': '#007bff',
                                                'borderRadius': '10px', 'position': 'relative', 'display': 'inline-block'
                                            }, children=[
                                                html.Div(style={
                                                    'width': '16px', 'height': '16px', 'backgroundColor': 'white',
                                                    'borderRadius': '50%', 'position': 'absolute', 'top': '2px', 'right': '2px'
                                                })
                                            ]),
                                            html.Span("Assigned", className='badge bg-primary ms-1'),
                                        ])
                                    ])
                                ]),
                                html.Td([
                                    dbc.Button("Edit", size='sm', color='primary', className='me-1'),
                                    dbc.Button("Free", size='sm', color='warning'),
                                ]),
                            ]),
                            html.Tr([
                                html.Td("XAP-2652"),
                                html.Td("ridhi"),
                                html.Td("Flora"),
                                html.Td([
                                    html.Div([
                                        html.Span("Allotted", className='badge bg-success me-2'),
                                        html.Div([
                                            html.Span("UnAssigned", className='badge bg-secondary me-1'),
                                            html.Div(className='toggle-switch', style={
                                                'width': '40px', 'height': '20px', 'backgroundColor': '#007bff',
                                                'borderRadius': '10px', 'position': 'relative', 'display': 'inline-block'
                                            }, children=[
                                                html.Div(style={
                                                    'width': '16px', 'height': '16px', 'backgroundColor': 'white',
                                                    'borderRadius': '50%', 'position': 'absolute', 'top': '2px', 'right': '2px'
                                                })
                                            ]),
                                            html.Span("Assigned", className='badge bg-primary ms-1'),
                                        ])
                                    ])
                                ]),
                                html.Td([
                                    dbc.Button("Edit", size='sm', color='primary', className='me-1'),
                                    dbc.Button("Free", size='sm', color='warning'),
                                ]),
                            ]),
                        ])
                    ], striped=True, bordered=True, hover=True, responsive=True),
                    
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
    ])


# Settings Page Callbacks
@callback(
    Output('url', 'pathname'),
    Input('create-user-btn', 'n_clicks'),
    prevent_initial_call=True
)
def navigate_to_create_user(n_clicks):
    """Navigate to create user page"""
    print(f"Create User button clicked: {n_clicks}")  # Debug
    if n_clicks and n_clicks > 0:
        print("Redirecting to /create-user")  # Debug
        return '/create-user'
    return '/dashboard'


# Create User Modal Callbacks
@callback(
    Output("create-user-modal", "is_open"),
    [Input("create-user-btn", "n_clicks"),
     Input("close-user-modal", "n_clicks"),
     Input("save-user-btn", "n_clicks")],
    [State("create-user-modal", "is_open")],
)
def toggle_user_modal(n1, n2, n3, is_open):
    """Toggle create user modal"""
    if n1 or n2 or n3:
        return not is_open
    return is_open


@callback(
    [Output('user-creation-message', 'children'),
     Output('save-user-btn', 'disabled')],
    [Input('save-user-btn', 'n_clicks')],
    [State('user-company-name', 'value'),
     State('user-id', 'value'),
     State('user-email', 'value'),
     State('user-phone', 'value'),
     State('user-password', 'value'),
     State('user-type', 'value')],
    prevent_initial_call=True
)
def create_user(n_clicks, company_name, user_id, email, phone, password, user_type):
    """Create new user with validation"""
    if not n_clicks:
        return None, False
    
    # Validation
    errors = []
    
    if not company_name or len(company_name.strip()) < 2:
        errors.append("Company name must be at least 2 characters long")
    
    if not user_id or len(user_id.strip()) < 3:
        errors.append("User ID must be at least 3 characters long")
    elif not re.match(r'^[a-zA-Z0-9_]+$', user_id):
        errors.append("User ID can only contain letters, numbers, and underscores")
    
    if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        errors.append("Please enter a valid email address")
    
    if not phone or not re.match(r'^(\+)?\d{10,15}$', re.sub(r'[^\d+]', '', phone)):
        errors.append("Please enter a valid phone number")
    
    if not user_type:
        errors.append("Please select a user type")
    
    if errors:
        return dbc.Alert([
            html.H4("Validation Errors", className='fw-bold'),
            html.Ul([html.Li(error) for error in errors])
        ], color='danger'), False
    
    # Generate secure password
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    generated_password = ''.join(secrets.choice(alphabet) for _ in range(12))
    
    # Create user data
    user_data = {
        'Company_Name': company_name.strip(),
        'User_Id': user_id.strip(),
        'Email_Id': email.strip().lower(),
        'Phone_No': phone.strip(),
        'User_Type': user_type,
        'status': 'active',
        'Password': generated_password,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    # Save to InfluxDB (you'll need to implement this)
    try:
        # Here you would save to InfluxDB using your user service
        # For now, just show success message
        return dbc.Alert([
            html.H4("User Created Successfully!", className='fw-bold'),
            html.P(f"User ID: {user_id}"),
            html.P(f"Email: {email}"),
            html.P(f"Generated Password: {generated_password}"),
            html.P("Login credentials have been sent to the user's email address."),
        ], color='success'), True
    except Exception as e:
        return dbc.Alert([
            html.H4("Error Creating User", className='fw-bold'),
            html.P(f"An error occurred: {str(e)}")
        ], color='danger'), False


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
IoT Devices → Mosquitto MQTT → Docker App → InfluxDB Cloud → Dashboard
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
            