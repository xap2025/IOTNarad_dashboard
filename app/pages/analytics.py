"""
Analytics Page Layout
Real-time data visualization and insights
"""
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from datetime import datetime, timedelta
import random


def create_analytics_layout():
    """Create analytics page with real-time charts"""
    
    return html.Div([
        # Time Range Selector
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Label("Time Range", className='fw-bold me-3'),
                    dcc.Dropdown(
                        id='time-range-selector',
                        options=[
                            {'label': '⏱️ Last 1 Hour', 'value': '1h'},
                            {'label': '⏱️ Last 6 Hours', 'value': '6h'},
                            {'label': '⏱️ Last 24 Hours', 'value': '24h'},
                            {'label': '⏱️ Last 7 Days', 'value': '7d'},
                            {'label': '⏱️ Last 30 Days', 'value': '30d'},
                        ],
                        value='1h',
                        className='d-inline-block',
                        style={'width': '200px'}
                    ),
                ], className='d-flex align-items-center'),
            ], md=6),
            
            dbc.Col([
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-sync-alt me-2"),
                        "Refresh"
                    ], id='refresh-analytics-btn', color='primary', outline=True, size='sm'),
                ], className='text-end'),
            ], md=6),
        ], className='mb-4'),
        
        # Real-time Charts
        dbc.Row([
            # Temperature Chart
            dbc.Col([
                html.Div([
                    html.H6([
                        html.I(className="fas fa-thermometer-half me-2", style={'color': '#ef4444'}),
                        "Temperature"
                    ], className='fw-bold mb-3'),
                    dcc.Graph(
                        id='temperature-chart',
                        config={'displayModeBar': False},
                        style={'height': '250px'}
                    ),
                ], className='stat-card p-3'),
            ], md=6),
            
            # Humidity Chart
            dbc.Col([
                html.Div([
                    html.H6([
                        html.I(className="fas fa-tint me-2", style={'color': '#3b82f6'}),
                        "Humidity"
                    ], className='fw-bold mb-3'),
                    dcc.Graph(
                        id='humidity-chart',
                        config={'displayModeBar': False},
                        style={'height': '250px'}
                    ),
                ], className='stat-card p-3'),
            ], md=6),
        ], className='mb-4'),
        
        dbc.Row([
            # Voltage Chart
            dbc.Col([
                html.Div([
                    html.H6([
                        html.I(className="fas fa-bolt me-2", style={'color': '#fbbf24'}),
                        "Voltage (0-10V)"
                    ], className='fw-bold mb-3'),
                    dcc.Graph(
                        id='voltage-chart',
                        config={'displayModeBar': False},
                        style={'height': '250px'}
                    ),
                ], className='stat-card p-3'),
            ], md=6),
            
            # Current Chart
            dbc.Col([
                html.Div([
                    html.H6([
                        html.I(className="fas fa-plug me-2", style={'color': '#8b5cf6'}),
                        "Current (4-20mA)"
                    ], className='fw-bold mb-3'),
                    dcc.Graph(
                        id='current-chart',
                        config={'displayModeBar': False},
                        style={'height': '250px'}
                    ),
                ], className='stat-card p-3'),
            ], md=6),
        ], className='mb-4'),
        
        # Digital I/O Status
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6([
                        html.I(className="fas fa-toggle-on me-2", style={'color': '#10b981'}),
                        "Digital I/O Status"
                    ], className='fw-bold mb-3'),
                    
                    dbc.Row([
                        # Digital Inputs
                        dbc.Col([
                            html.Div([
                                html.P("Digital Inputs", className='text-muted mb-2 small'),
                                html.Div([
                                    create_digital_status_badge("DI1", True),
                                    create_digital_status_badge("DI2", False),
                                    create_digital_status_badge("DI3", True),
                                    create_digital_status_badge("DI4", False),
                                ], className='d-flex flex-wrap gap-2'),
                            ]),
                        ], md=6),
                        
                        # Digital Outputs
                        dbc.Col([
                            html.Div([
                                html.P("Digital Outputs", className='text-muted mb-2 small'),
                                html.Div([
                                    create_digital_status_badge("DO1", False),
                                    create_digital_status_badge("DO2", True),
                                    create_digital_status_badge("DO3", False),
                                    create_digital_status_badge("DO4", True),
                                ], className='d-flex flex-wrap gap-2'),
                            ]),
                        ], md=6),
                    ]),
                ], className='stat-card p-3'),
            ], md=12),
        ], className='mb-4'),
        
        # Device Activity Log
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6([
                        html.I(className="fas fa-history me-2", style={'color': '#667eea'}),
                        "Recent Activity"
                    ], className='fw-bold mb-3'),
                    
                    html.Div([
                        create_activity_log_item("ESP32-Gateway-01", "Configuration updated", "2 minutes ago", "success"),
                        create_activity_log_item("ESP32-Gateway-02", "Data received", "5 minutes ago", "info"),
                        create_activity_log_item("ESP32-Gateway-01", "Alert: High temperature", "12 minutes ago", "warning"),
                        create_activity_log_item("ESP32-Gateway-03", "Device connected", "25 minutes ago", "success"),
                        create_activity_log_item("ESP32-Gateway-02", "Configuration updated", "1 hour ago", "info"),
                    ], id='activity-log', style={'maxHeight': '300px', 'overflowY': 'auto'}),
                ], className='stat-card p-3'),
            ], md=12),
        ]),
        
        # Auto-refresh interval
        dcc.Interval(id='analytics-refresh-interval', interval=5000, n_intervals=0),
    ])


def create_digital_status_badge(name, status):
    """Create a digital I/O status badge"""
    color = '#10b981' if status else '#6c757d'
    bg_color = '#d1fae5' if status else '#e9ecef'
    
    return html.Div([
        html.Span([
            html.I(className="fas fa-circle me-2", style={'color': color, 'fontSize': '0.6rem'}),
            name
        ], className='badge px-3 py-2',
           style={'backgroundColor': bg_color, 'color': '#1a1a2e', 'fontWeight': '500'})
    ])


def create_activity_log_item(device, message, time, log_type):
    """Create an activity log item"""
    icon_map = {
        'success': ('fas fa-check-circle', '#10b981'),
        'info': ('fas fa-info-circle', '#3b82f6'),
        'warning': ('fas fa-exclamation-triangle', '#fbbf24'),
        'error': ('fas fa-times-circle', '#ef4444'),
    }
    
    icon_class, icon_color = icon_map.get(log_type, icon_map['info'])
    
    return html.Div([
        html.Div([
            html.I(className=icon_class, style={'color': icon_color, 'fontSize': '1.2rem'}),
        ], style={'width': '30px'}),
        
        html.Div([
            html.Div([
                html.Span(device, className='fw-bold me-2'),
                html.Span(message, className='text-muted'),
            ]),
            html.Small(time, className='text-muted', style={'fontSize': '0.8rem'}),
        ], className='flex-grow-1'),
    ], className='d-flex align-items-start mb-3 pb-3 border-bottom')


# Callbacks for charts
@callback(
    Output('temperature-chart', 'figure'),
    Input('analytics-refresh-interval', 'n_intervals'),
    Input('time-range-selector', 'value')
)
def update_temperature_chart(n, time_range):
    """Update temperature chart"""
    # Generate sample data
    now = datetime.now()
    x = [now - timedelta(minutes=i*5) for i in range(20, 0, -1)]
    y = [20 + random.uniform(-2, 5) for _ in range(20)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#ef4444', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(239, 68, 68, 0.1)'
    ))
    
    fig.update_layout(
        margin=dict(l=40, r=20, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#e9ecef'),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef', title='°C'),
        hovermode='x unified',
        showlegend=False
    )
    
    return fig


@callback(
    Output('humidity-chart', 'figure'),
    Input('analytics-refresh-interval', 'n_intervals'),
    Input('time-range-selector', 'value')
)
def update_humidity_chart(n, time_range):
    """Update humidity chart"""
    now = datetime.now()
    x = [now - timedelta(minutes=i*5) for i in range(20, 0, -1)]
    y = [50 + random.uniform(-10, 10) for _ in range(20)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='lines+markers',
        name='Humidity',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)'
    ))
    
    fig.update_layout(
        margin=dict(l=40, r=20, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#e9ecef'),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef', title='%'),
        hovermode='x unified',
        showlegend=False
    )
    
    return fig


@callback(
    Output('voltage-chart', 'figure'),
    Input('analytics-refresh-interval', 'n_intervals'),
    Input('time-range-selector', 'value')
)
def update_voltage_chart(n, time_range):
    """Update voltage chart"""
    now = datetime.now()
    x = [now - timedelta(minutes=i*5) for i in range(20, 0, -1)]
    y = [5 + random.uniform(-1, 3) for _ in range(20)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='lines+markers',
        name='Voltage',
        line=dict(color='#fbbf24', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(251, 191, 36, 0.1)'
    ))
    
    fig.update_layout(
        margin=dict(l=40, r=20, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#e9ecef'),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef', title='V'),
        hovermode='x unified',
        showlegend=False
    )
    
    return fig


@callback(
    Output('current-chart', 'figure'),
    Input('analytics-refresh-interval', 'n_intervals'),
    Input('time-range-selector', 'value')
)
def update_current_chart(n, time_range):
    """Update current chart"""
    now = datetime.now()
    x = [now - timedelta(minutes=i*5) for i in range(20, 0, -1)]
    y = [12 + random.uniform(-2, 4) for _ in range(20)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='lines+markers',
        name='Current',
        line=dict(color='#8b5cf6', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(139, 92, 246, 0.1)'
    ))
    
    fig.update_layout(
        margin=dict(l=40, r=20, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#e9ecef'),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef', title='mA'),
        hovermode='x unified',
        showlegend=False
    )
    
    return fig

