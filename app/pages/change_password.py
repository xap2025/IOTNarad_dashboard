"""
Change Password Page Layout
Allows users to change their password
"""
from dash import html, dcc, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import secrets
import string
import logging

logger = logging.getLogger(__name__)

# Import server session storage (defined in main.py)
try:
    from app.main import _server_sessions
except ImportError:
    # Fallback if import fails (shouldn't happen in normal operation)
    _server_sessions = {}

def create_change_password_layout():
    """Create change password page layout"""
    
    return dbc.Container([
        # Header
        html.Div([
            html.H3([
                html.I(className="fas fa-key me-3"),
                "Change Password"
            ], className='fw-bold mb-3', style={'color': '#1a1a2e'}),
            html.P("Enter your current password and choose a new password.", className='text-muted mb-4'),
        ], className='mb-4', style={'padding': '2rem 0', 'background': '#f8f9fa'}),
        
        # Change Password Form
        dbc.Card([
            dbc.CardBody([
                dbc.Form(id='change-password-form', children=[
                    # Current Password
                    html.Div([
                        dbc.Label("Current Password", html_for="current-password", className='fw-bold mb-2'),
                        dbc.InputGroup([
                            dbc.InputGroupText(
                                html.I(className="fas fa-lock"),
                                className='bg-light border-end-0'
                            ),
                            dbc.Input(
                                id='current-password',
                                type='password',
                                placeholder='Enter your current password',
                                className='border-start-0',
                                required=True
                            )
                        ]),
                        dbc.FormFeedback(id='current-password-feedback', type='invalid'),
                    ], className='mb-3'),
                    
                    # New Password
                    html.Div([
                        dbc.Label("New Password", html_for="new-password", className='fw-bold mb-2'),
                        dbc.InputGroup([
                            dbc.InputGroupText(
                                html.I(className="fas fa-key"),
                                className='bg-light border-end-0'
                            ),
                            dbc.Input(
                                id='new-password',
                                type='password',
                                placeholder='Enter new password (min 8 characters)',
                                className='border-start-0',
                                required=True,
                                minLength=8
                            )
                        ]),
                        dbc.FormText("Password must be at least 8 characters long.", color="muted", className='mt-1'),
                        dbc.FormFeedback(id='new-password-feedback', type='invalid'),
                    ], className='mb-3'),
                    
                    # Confirm New Password
                    html.Div([
                        dbc.Label("Confirm New Password", html_for="confirm-password", className='fw-bold mb-2'),
                        dbc.InputGroup([
                            dbc.InputGroupText(
                                html.I(className="fas fa-check-circle"),
                                className='bg-light border-end-0'
                            ),
                            dbc.Input(
                                id='confirm-password',
                                type='password',
                                placeholder='Confirm new password',
                                className='border-start-0',
                                required=True
                            )
                        ]),
                        dbc.FormFeedback(id='confirm-password-feedback', type='invalid'),
                    ], className='mb-4'),
                    
                    # Submit Button
                    html.Div([
                        dbc.Button([
                            html.I(className="fas fa-save me-2"),
                            "Change Password"
                        ], id='submit-change-password-btn', color='primary', size='lg', className='w-100', n_clicks=0),
                    ], className='mb-3'),
                    
                    # Back to Profile Button
                    html.Div([
                        dbc.Button([
                            html.I(className="fas fa-arrow-left me-2"),
                            "Back to Profile"
                        ], id='back-to-profile-btn', color='secondary', size='md', className='w-100', n_clicks=0),
                    ]),
                ]),
            ], className='p-4')
        ], className='border-0 shadow-sm', style={
            'borderRadius': '12px',
            'background': 'white',
            'maxWidth': '600px',
            'margin': '0 auto'
        }),
        
        # Success/Error Messages
        dbc.Row([
            dbc.Col([
                html.Div(id='change-password-message'),
            ], width=12),
        ], className='mt-4'),
        
    ], fluid=True, style={'minHeight': '100vh', 'background': '#f8f9fa', 'padding': '2rem'})


@callback(
    Output('new-password-feedback', 'children'),
    Output('new-password-feedback', 'type'),
    Input('new-password', 'value')
)
def validate_new_password(value):
    """Validate new password"""
    if not value:
        return '', 'invalid'
    if len(value) < 8:
        return 'Password must be at least 8 characters long', 'invalid'
    return 'Valid password', 'valid'


@callback(
    Output('confirm-password-feedback', 'children'),
    Output('confirm-password-feedback', 'type'),
    [Input('confirm-password', 'value'),
     Input('new-password', 'value')]
)
def validate_confirm_password(confirm_value, new_value):
    """Validate password confirmation"""
    if not confirm_value:
        return '', 'invalid'
    if confirm_value != new_value:
        return 'Passwords do not match', 'invalid'
    return 'Passwords match', 'valid'


@callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('back-to-profile-btn', 'n_clicks'),
    prevent_initial_call=True
)
def navigate_back_to_profile(n_clicks):
    """Navigate back to dashboard/profile"""
    if n_clicks and n_clicks > 0:
        return '/dashboard'
    return no_update


@callback(
    [Output('change-password-message', 'children'),
     Output('current-password', 'value'),
     Output('new-password', 'value'),
     Output('confirm-password', 'value'),
     Output('submit-change-password-btn', 'disabled')],
    Input('submit-change-password-btn', 'n_clicks'),
    [State('current-password', 'value'),
     State('new-password', 'value'),
     State('confirm-password', 'value'),
     State('session-store', 'data')],
    prevent_initial_call=True
)
def handle_change_password(n_clicks, current_password, new_password, confirm_password, session_data):
    """Handle password change request"""
    from app.services.user_service import UserService
    
    if not n_clicks or n_clicks == 0:
        return '', no_update, no_update, no_update, False
    
    # Validate input
    if not current_password or not new_password or not confirm_password:
        return dbc.Alert([
            html.H4("⚠️ Validation Error", className='fw-bold'),
            html.P("Please fill all fields.")
        ], color='warning'), no_update, no_update, no_update, False
    
    # Validate password length
    if len(new_password) < 8:
        return dbc.Alert([
            html.H4("⚠️ Validation Error", className='fw-bold'),
            html.P("New password must be at least 8 characters long.")
        ], color='warning'), no_update, no_update, no_update, False
    
    # Validate password match
    if new_password != confirm_password:
        return dbc.Alert([
            html.H4("⚠️ Validation Error", className='fw-bold'),
            html.P("New password and confirm password do not match.")
        ], color='warning'), no_update, no_update, no_update, False
    
    # Get user ID from session
    if not session_data:
        return dbc.Alert([
            html.H4("❌ Error", className='fw-bold'),
            html.P("Session expired. Please login again.")
        ], color='danger'), no_update, no_update, no_update, False
    
    user_id = session_data.get('username')
    if not user_id:
        return dbc.Alert([
            html.H4("❌ Error", className='fw-bold'),
            html.P("User ID not found in session.")
        ], color='danger'), no_update, no_update, no_update, False
    
    # Change password
    user_service = UserService()
    try:
        success = user_service.change_password(user_id, current_password, new_password)
        
        if success:
            # CRITICAL: Clear all sessions when password changes successfully
            # This forces user to login again with new password
            # Note: user_service.change_password() already calls invalidate_user_sessions()
            # But we also clear current Flask session here for immediate effect
            from flask import session as flask_session
            
            # Clear Flask session
            flask_session.clear()
            flask_session.permanent = False
            flask_session.modified = True
            
            logger.info(f"🔒 Flask session cleared for user '{user_id}' after password change")
            
            return dbc.Alert([
                html.H4([
                    html.I(className="fas fa-check-circle me-2"),
                    "Password Changed Successfully!"
                ], className='fw-bold'),
                html.P("Your password has been updated. All existing sessions have been invalidated for security."),
                html.P("Please login again with your new password.", className='fw-bold mt-2'),
                html.Hr(),
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-sign-in-alt me-2"),
                        "Go to Login"
                    ], id='success-back-btn', href='/login', color='primary', className='me-2'),
                ], className='mb-0')
            ], color='success'), '', '', '', False
        else:
            return dbc.Alert([
                html.H4([
                    html.I(className="fas fa-times-circle me-2"),
                    "Password Change Failed"
                ], className='fw-bold'),
                html.P("Current password is incorrect or an error occurred. Please try again.")
            ], color='danger'), no_update, no_update, no_update, False
            
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        return dbc.Alert([
            html.H4([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "Error"
            ], className='fw-bold'),
            html.P(f"An error occurred: {str(e)}")
        ], color='danger'), no_update, no_update, no_update, False

