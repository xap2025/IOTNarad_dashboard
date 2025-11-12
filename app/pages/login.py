"""
Login Page Layout
Professional authentication interface for IOTNarad Dashboard
"""
from dash import html, dcc
import dash_bootstrap_components as dbc


def create_login_layout():
    """Create a beautiful, modern login page with perfect centering"""
    
    return html.Div([
        # Background with gradient and proper centering
        html.Div(children=[
            # Login Card
            dbc.Card([
                dbc.CardBody([
                    # Logo and Title
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-microchip fa-3x mb-3", 
                                   style={'color': '#00d4ff'}),
                        ], className='text-center'),
                        html.H2("IOTNarad", className='text-center fw-bold mb-2',
                                style={'color': '#1a1a2e', 'letterSpacing': '1px'}),
                        html.P("IoT Device Management Platform", 
                               className='text-center text-muted mb-4',
                               style={'fontSize': '0.9rem'}),
                    ]),
                    
                    # Login Form
                    html.Div([
                        # Username Input
                        dbc.InputGroup([
                            dbc.InputGroupText(
                                html.I(className="fas fa-user"),
                                className='bg-light border-end-0'
                            ),
                            dbc.Input(
                                id='username-input',
                                type='text',
                                placeholder='User ID',
                                className='border-start-0',
                                style={'paddingLeft': '0'},
                                required=True
                            )
                        ], className='mb-3'),
                        
                        # Password Input
                        dbc.InputGroup([
                            dbc.InputGroupText(
                                html.I(className="fas fa-lock"),
                                className='bg-light border-end-0'
                            ),
                            dbc.Input(
                                id='password-input',
                                type='password',
                                placeholder='Password',
                                className='border-start-0',
                                style={'paddingLeft': '0'},
                                required=True
                            )
                        ], className='mb-3'),
                        
                        # Forgot Password Link
                        html.Div([
                            html.A(
                                "Forgot Password?",
                                id='forgot-password-link',
                                href='#',
                                className='text-decoration-none',
                                n_clicks=0,
                                style={
                                    'color': '#667eea',
                                    'fontSize': '0.9rem',
                                    'cursor': 'pointer'
                                }
                            )
                        ], className='text-end mb-3'),
                        
                        # Login Button
                        dbc.Button(
                            [html.I(className="fas fa-sign-in-alt me-2"), "Login"],
                            id='login-button',
                            color='primary',
                            className='w-100 py-2 fw-bold',
                            style={
                                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                'border': 'none',
                                'borderRadius': '8px',
                                'fontSize': '1rem'
                            }
                        ),
                        
                        # Login Message
                        html.Div(id='login-message', className='mt-3'),
                        
                    ], className='px-3'),
                    
                    # Footer
                    html.Div([
                        html.Hr(className='my-4'),
                        html.Div([
                            html.I(className="fas fa-shield-alt me-2", 
                                   style={'color': '#667eea'}),
                            html.Span("Secure Login", 
                                      style={'fontSize': '0.85rem', 'color': '#666'})
                        ], className='text-center'),
                    ]),
                ], className='p-4')
            ], className='border-0', style={
                'maxWidth': '420px',
                'width': '100%',
                'borderRadius': '16px',
                'background': 'rgba(255, 255, 255, 0.95)',
                'backdropFilter': 'blur(10px)',
                'boxShadow': '0 20px 40px rgba(0,0,0,0.1)'
            })
        ], style={
            'minHeight': '100vh',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'position': 'relative',
            'overflow': 'hidden',
            'margin': '0',
            'padding': '0'
        }),
        
        # Forgot Password Modal
        dbc.Modal([
            dbc.ModalHeader([
                html.I(className="fas fa-key me-2"),
                "Reset Password"
            ]),
            dbc.ModalBody([
                html.P("Enter your User ID and registered Phone Number to reset your password.", 
                       className='text-muted mb-4'),
                
                # User ID Input
                dbc.InputGroup([
                    dbc.InputGroupText(
                        html.I(className="fas fa-user"),
                        className='bg-light border-end-0'
                    ),
                    dbc.Input(
                        id='forgot-user-id',
                        type='text',
                        placeholder='User ID',
                        className='border-start-0'
                    )
                ], className='mb-3'),
                
                # Phone Number Input
                dbc.InputGroup([
                    dbc.InputGroupText(
                        html.I(className="fas fa-phone"),
                        className='bg-light border-end-0'
                    ),
                    dbc.Input(
                        id='forgot-phone-no',
                        type='tel',
                        placeholder='Phone Number (e.g., +919876543210)',
                        className='border-start-0'
                    )
                ], className='mb-3'),
                
                # Message Display
                html.Div(id='forgot-password-message', className='mb-3'),
                
            ]),
            dbc.ModalFooter([
                dbc.Button(
                    "Cancel",
                    id='forgot-password-cancel',
                    color='secondary',
                    className='me-2',
                    n_clicks=0
                ),
                dbc.Button(
                    [html.I(className="fas fa-paper-plane me-2"), "Send Reset Link"],
                    id='forgot-password-submit',
                    color='primary',
                    n_clicks=0
                ),
            ]),
        ], 
        id='forgot-password-modal',
        is_open=False,
        centered=True,
        backdrop=True,
        size='md'
        ),
    ], style={'margin': '0', 'padding': '0'})