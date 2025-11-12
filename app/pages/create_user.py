import dash
from dash import html, dcc, callback, Input, Output, State, no_update, ctx
import dash_bootstrap_components as dbc
import re
import secrets
import string
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

def create_user_form_layout():
    """Create user creation form layout"""
    
    return dbc.Container([
        # Header
        html.Div([
            html.H3([
                html.I(className="fas fa-user-plus me-3"),
                "Create New User"
            ], className='fw-bold mb-3', style={'color': '#1a1a2e'}),
            html.P("Fill in the details below to create a new user account.", className='text-muted mb-4'),
        ], className='mb-4', style={'padding': '2rem 0', 'background': '#f8f9fa'}),
        
        # User Creation Form
        dbc.Card([
            dbc.CardBody([
                dbc.Form(id='user-creation-form', children=[
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Company Name", html_for="user-company-name", className='fw-bold'),
                            dbc.Input(id='user-company-name', placeholder='Enter company name', type='text', className='mb-2'),
                            dbc.FormFeedback(id='company-name-feedback', type='invalid'),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("User ID", html_for="user-id", className='fw-bold'),
                            dbc.Input(id='user-id', placeholder='Enter unique user ID', type='text', className='mb-2'),
                            dbc.FormFeedback(id='user-id-feedback', type='invalid'),
                        ], md=6),
                    ], className='mb-3'),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Email Address", html_for="user-email", className='fw-bold'),
                            dbc.Input(id='user-email', placeholder='Enter email address', type='email', className='mb-2'),
                            dbc.FormFeedback(id='email-feedback', type='invalid'),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Phone Number", html_for="user-phone", className='fw-bold'),
                            dbc.Input(id='user-phone', placeholder='Enter phone number (e.g., +919876543210)', type='tel', className='mb-2'),
                            dbc.FormFeedback(id='phone-feedback', type='invalid'),
                        ], md=6),
                    ], className='mb-3'),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("User Type", html_for="user-type", className='fw-bold'),
                            dbc.Select(
                                id='user-type',
                                options=[
                                    {'label': 'Select User Type', 'value': '', 'disabled': True},
                                    {'label': 'User', 'value': 'user'},
                                    {'label': 'Admin', 'value': 'admin'},
                                ],
                                value='',
                                className='mb-2'
                            ),
                            dbc.FormFeedback(id='user-type-feedback', type='invalid'),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Account Status", html_for="account-status", className='fw-bold'),
                            dbc.Select(
                                id='account-status',
                                options=[
                                    {'label': 'Active', 'value': 'active'},
                                    {'label': 'Inactive', 'value': 'inactive'},
                                ],
                                value='active',
                                className='mb-2'
                            ),
                        ], md=6),
                    ], className='mb-4'),
                    
                    dbc.Button([
                        html.I(className="fas fa-user-plus me-2"),
                        "Create User"
                    ], id='submit-user-btn', color='primary', className='mt-3', n_clicks=0),
                ]),
            ]),
        ], className='mb-4', style={
            'background': 'white',
            'borderRadius': '12px',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.05)',
            'border': '1px solid #e9ecef'
        }),
        
        # Success/Error Messages
        dbc.Row([
            dbc.Col([
                html.Div(id='user-creation-message'),
            ]),
        ], className='mt-4'),
        
        # Store for form data
        dcc.Store(id='user-form-data'),
    ], fluid=True, style={'minHeight': '100vh', 'background': '#f8f9fa', 'padding': '2rem'})


@callback(
    [Output('user-creation-message', 'children'),
     Output('submit-user-btn', 'disabled')],
    Input('submit-user-btn', 'n_clicks'),
    [State('user-company-name', 'value'),
     State('user-id', 'value'),
     State('user-email', 'value'),
     State('user-phone', 'value'),
     State('user-type', 'value'),
     State('account-status', 'value')],
    prevent_initial_call=True
)
def handle_user_submission(n_clicks, company_name, user_id, email, phone, user_type, status):
    """Handle user form submission via Dash callback"""
    import secrets
    import string
    
    if not n_clicks or n_clicks == 0:
        return dash.no_update, False
    
    # Validate form
    if not all([company_name, user_id, email, phone, user_type]):
        return dbc.Alert([
            html.H4("⚠️ Validation Error", className='fw-bold'),
            html.P("Please fill all required fields.")
        ], color='warning'), False
    
    # Generate password
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(12))
    
    # Prepare form data
    form_data = {
        'Company_Name': company_name.strip(),
        'User_Id': user_id.strip(),
        'Email_Id': email.strip(),
        'Phone_No': phone.strip(),
        'User_Type': user_type,
        'Status': status or 'active',
        'Password': password
    }
    
    # Import services here to avoid circular imports
    from app.services.user_service import UserService
    from app.services.email_service import EmailService
    
    user_service = UserService()
    email_service = EmailService()
    
    try:
        # Check if user ID already exists
        existing_user = user_service.get_user_by_id(form_data['User_Id'])
        if existing_user:
            return dbc.Alert([
                html.H4("❌ Error", className='fw-bold'),
                html.P(f"User ID '{form_data['User_Id']}' already exists. Please choose a different User ID.")
            ], color='danger'), False
        
        # Create user in database
        success = user_service.create_user(form_data)
        
        if success:
            # Send email
            email_sent = email_service.send_user_credentials(form_data)
            
            # Success message
            return dbc.Alert([
                html.H4([
                    html.I(className="fas fa-check-circle me-2"),
                    "User Created Successfully!"
                ], className='fw-bold'),
                html.P([
                    html.Strong("User ID: "), form_data['User_Id']
                ]),
                html.P([
                    html.Strong("Email: "), form_data['Email_Id']
                ]),
                html.P([
                    html.Strong("Password: "),
                    html.Code(password, style={'background': '#f8f9fa', 'padding': '4px 8px', 'borderRadius': '4px'})
                ]),
                html.P([
                    html.Strong("Email Status: "),
                    html.Span("✅ Credentials sent via email", className='text-success') if email_sent 
                    else html.Span("⚠️ Email sending failed (but user is created)", className='text-warning')
                ]),
                html.Hr(),
                html.Div([
                    html.A([
                        html.I(className="fas fa-eye me-2"),
                        "View Dashboard"
                    ], href="/dashboard", className='btn btn-primary me-2'),
                    html.A([
                        html.I(className="fas fa-plus me-2"),
                        "Create Another User"
                    ], href="/create-user", className='btn btn-success', id='create-another-user-link')
                ], className='mb-0')
            ], color='success'), False
        else:
            return dbc.Alert([
                html.H4("❌ Error", className='fw-bold'),
                html.P("Failed to create user in database. Please check server logs for details.")
            ], color='danger'), False
            
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return dbc.Alert([
            html.H4("❌ Error", className='fw-bold'),
            html.P(f"An error occurred: {str(e)}")
        ], color='danger'), False


# Validation callbacks for real-time feedback
@callback(
    Output('company-name-feedback', 'children'),
    Output('company-name-feedback', 'type'),
    Input('user-company-name', 'value')
)
def validate_company_name(value):
    if not value:
        return '', 'invalid'
    if len(value.strip()) < 2:
        return 'Company name must be at least 2 characters', 'invalid'
    return 'Valid company name', 'valid'


@callback(
    Output('user-id-feedback', 'children'),
    Output('user-id-feedback', 'type'),
    Input('user-id', 'value')
)
def validate_user_id(value):
    if not value:
        return '', 'invalid'
    if len(value.strip()) < 3:
        return 'User ID must be at least 3 characters', 'invalid'
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        return 'User ID can only contain letters, numbers, and underscores', 'invalid'
    return 'Valid user ID', 'valid'


@callback(
    Output('email-feedback', 'children'),
    Output('email-feedback', 'type'),
    Input('user-email', 'value')
)
def validate_email(value):
    if not value:
        return '', 'invalid'
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
        return 'Please enter a valid email address', 'invalid'
    return 'Valid email address', 'valid'


@callback(
    Output('phone-feedback', 'children'),
    Output('phone-feedback', 'type'),
    Input('user-phone', 'value')
)
def validate_phone(value):
    if not value:
        return '', 'invalid'
    if not re.match(r'^(\+)?\d{10,15}$', re.sub(r'[^\d+]', '', value)):
        return 'Please enter a valid phone number', 'invalid'
    return 'Valid phone number', 'valid'


@callback(
    Output('user-type-feedback', 'children'),
    Output('user-type-feedback', 'type'),
    Input('user-type', 'value')
)
def validate_user_type(value):
    if not value:
        return 'Please select a user type', 'invalid'
    return 'User type selected', 'valid'