import dash
from dash import html, dcc, callback, Input, Output, State
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
            ], className='fw-bold mb-3', style={'color': 'white'}),
            html.P("Fill in the details below to create a new user account.", className='text-muted mb-4', style={'color': 'rgba(255,255,255,0.8)'}),
        ], className='mb-4'),
        
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
        
        # JavaScript for WebSocket communication
        html.Script("""
            const socket = io();
            
            // Handle form submission
            document.getElementById('submit-user-btn').addEventListener('click', function() {
                const formData = {
                    Company_Name: document.getElementById('user-company-name').value,
                    User_Id: document.getElementById('user-id').value,
                    Email_Id: document.getElementById('user-email').value,
                    Phone_No: document.getElementById('user-phone').value,
                    User_Type: document.getElementById('user-type').value,
                    status: document.getElementById('account-status').value
                };
                
                // Generate password
                const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
                let password = '';
                for (let i = 0; i < 12; i++) {
                    password += alphabet.charAt(Math.floor(Math.random() * alphabet.length));
                }
                formData.Password = password;
                
                // Send via WebSocket
                socket.emit('create_user', formData);
            });
            
            socket.on('user_created', function(data) {
                if (data.status === 'success') {
                    const successHtml = `
                        <div class="alert alert-success" role="alert">
                            <h4 class="alert-heading">
                                <i class="fas fa-check-circle me-2"></i>
                                User Created Successfully!
                            </h4>
                            <p><strong>User ID:</strong> ${data.user_id}</p>
                            <p><strong>Email:</strong> ${data.email}</p>
                            <p><strong>Status:</strong> ${data.email_sent ? 'Credentials sent via email' : 'Email sending failed'}</p>
                            <hr>
                            <div class="mb-0">
                                <a href="/dashboard" class="btn btn-primary me-2">
                                    <i class="fas fa-eye me-2"></i>View Dashboard
                                </a>
                                <a href="/create-user" class="btn btn-success">
                                    <i class="fas fa-plus me-2"></i>Create Another User
                                </a>
                            </div>
                        </div>
                    `;
                    document.getElementById('user-creation-message').innerHTML = successHtml;
                    
                    // Reset form
                    document.getElementById('user-creation-form').reset();
                    document.getElementById('submit-user-btn').disabled = false;
                }
            });
            
            socket.on('user_creation_error', function(data) {
                const errorHtml = `
                    <div class="alert alert-danger" role="alert">
                        <h4 class="alert-heading">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Error Creating User
                        </h4>
                        <p>${data.message}</p>
                        <hr>
                        <div class="mb-0">
                            <button class="btn btn-danger" onclick="location.reload()">
                                <i class="fas fa-redo me-2"></i>Try Again
                            </button>
                        </div>
                    </div>
                `;
                document.getElementById('user-creation-message').innerHTML = errorHtml;
                document.getElementById('submit-user-btn').disabled = false;
            });
        """),
    ])


@callback(
    Output('submit-user-btn', 'disabled'),
    Input('submit-user-btn', 'n_clicks'),
    prevent_initial_call=True
)
def disable_button_during_processing(n_clicks):
    """Disable button during processing"""
    if n_clicks and n_clicks > 0:
        return True
    return False


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