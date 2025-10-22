"""
Settings Page Layout
Admin management panel with user management and device assignment
"""
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from datetime import datetime


def create_settings_layout():
    """Create settings page with admin management functionality"""
    
    return html.Div([
        # Page Title
        html.Div([
            html.H3([
                html.I(className="fas fa-cog me-3"),
                "Settings"
            ], className='fw-bold mb-3'),
            html.P("Admin management panel for user and device management.", className='text-muted mb-4'),
        ], className='mb-4'),
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
                        ], striped=True, bordered=True, hover=True, responsive=True, 
                           style={'backgroundColor': 'rgba(255,255,255,0.1)'}),
                    ], className='mt-3'),
                    
                ], className='stat-card p-4', style={
                    'background': 'white',
                    'borderRadius': '12px',
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
                    ], striped=True, bordered=True, hover=True, responsive=True,
                       style={'backgroundColor': 'rgba(255,255,255,0.1)'}),
                    
                ], className='stat-card p-4', style={
                    'background': 'white',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                    'border': '1px solid #e9ecef',
                    'transition': 'all 0.3s ease'
                }),
            ]),
        ]),
        
        # Create User Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Create New User")),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Company Name"),
                            dbc.Input(id='user-company-name', placeholder='Enter company name'),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("User ID"),
                            dbc.Input(id='user-id', placeholder='Enter user ID'),
                        ], md=6),
                    ], className='mb-3'),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Email ID"),
                            dbc.Input(id='user-email', type='email', placeholder='Enter email'),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Phone Number"),
                            dbc.Input(id='user-phone', placeholder='Enter phone number'),
                        ], md=6),
                    ], className='mb-3'),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Password"),
                            dbc.Input(id='user-password', type='password', placeholder='Enter password'),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("User Type"),
                            dbc.Select(
                                id='user-type',
                                options=[
                                    {'label': 'User', 'value': 'user'},
                                    {'label': 'Admin', 'value': 'admin'},
                                ],
                                value='user'
                            ),
                        ], md=6),
                    ], className='mb-3'),
                ]),
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="close-user-modal", className="ms-auto", n_clicks=0),
                dbc.Button("Create User", id="save-user-btn", color="primary", n_clicks=0),
            ]),
        ], id="create-user-modal", is_open=False),
        
        # Store for user data
        dcc.Store(id='user-data-store'),
        
        # URL location for navigation
        dcc.Location(id='url', refresh=False),
    ])


# Callbacks for Settings Page
@callback(
    Output("create-user-modal", "is_open"),
    [Input("close-user-modal", "n_clicks"),
     Input("save-user-btn", "n_clicks")],
    [State("create-user-modal", "is_open")],
)
def toggle_user_modal(n1, n2, is_open):
    """Toggle create user modal"""
    if n1 or n2:
        return not is_open
    return is_open


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


@callback(
    [Output('user-data-store', 'data'),
     Output('create-user-modal', 'is_open', allow_duplicate=True)],
    Input('save-user-btn', 'n_clicks'),
    [State('user-company-name', 'value'),
     State('user-id', 'value'),
     State('user-email', 'value'),
     State('user-phone', 'value'),
     State('user-password', 'value'),
     State('user-type', 'value')],
    prevent_initial_call=True
)
def save_user_data(n_clicks, company_name, user_id, email, phone, password, user_type):
    """Save new user data to InfluxDB via WebSocket"""
    if not n_clicks:
        return None, False
    
    if not all([company_name, user_id, email, phone, password, user_type]):
        return {'error': 'All fields are required'}, True
    
    # Create user data structure matching your InfluxDB schema
    user_data = {
        'Company_Name': company_name,
        'User_Id': user_id,
        'Email_Id': email,
        'Phone_No': phone,
        'Password': password,
        'User_Type': user_type
    }
    
    # Emit to WebSocket for backend processing
    # This will be handled by the SocketIO event in main.py
    return {'success': True, 'data': user_data}, False
