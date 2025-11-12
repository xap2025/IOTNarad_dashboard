"""
Dashboard Page Layout
Main dashboard with sidebar navigation and content area
"""
from dash import html, dcc, Input, Output, State, callback, no_update
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
            