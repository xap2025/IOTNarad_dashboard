"""
OEE Dashboard Page Layout
Real-time Overall Equipment Effectiveness visualization for manufacturing
"""
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import math


def create_oee_dashboard_layout():
    """Create comprehensive OEE dashboard with real-time manufacturing metrics"""
    
    return html.Div([
        # Time Range Selector
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Label("Time Range", className='fw-bold me-3'),
                    dcc.Dropdown(
                        id='oee-time-range-selector',
                        options=[
                            {'label': '⏱️ Real-time (Live)', 'value': 'live'},
                            {'label': '⏱️ Last 1 Hour', 'value': '1h'},
                            {'label': '⏱️ Last 8 Hours', 'value': '8h'},
                            {'label': '⏱️ Last 24 Hours', 'value': '24h'},
                            {'label': '⏱️ Last 7 Days', 'value': '7d'},
                            {'label': '⏱️ Last 30 Days', 'value': '30d'},
                        ],
                        value='live',
                        className='d-inline-block',
                        style={'width': '200px'}
                    ),
                ], className='d-flex align-items-center'),
            ], md=6),
            
            dbc.Col([
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-sync-alt me-2"),
                        "Refresh OEE"
                    ], id='refresh-oee-btn', color='primary', outline=True, size='sm'),
                    
                    dbc.Button([
                        html.I(className="fas fa-download me-2"),
                        "Export Report"
                    ], id='export-oee-btn', color='success', outline=True, size='sm', className='ms-2'),
                ], className='text-end'),
            ], md=6),
        ], className='mb-4'),
        
        # OEE Overview Cards
        dbc.Row([
            # Overall OEE Score
            dbc.Col([
                create_oee_score_card("Overall OEE", "oee-overall-score", 87.5, "excellent")
            ], md=3),
            
            # Availability
            dbc.Col([
                create_oee_score_card("Availability", "oee-availability-score", 92.3, "good")
            ], md=3),
            
            # Performance
            dbc.Col([
                create_oee_score_card("Performance", "oee-performance-score", 89.7, "good")
            ], md=3),
            
            # Quality
            dbc.Col([
                create_oee_score_card("Quality", "oee-quality-score", 94.8, "excellent")
            ], md=3),
        ], className='mb-4'),
        
        # Production Lines Overview
        dbc.Row([
            dbc.Col([
                create_production_lines_overview()
            ], md=8),
            
            dbc.Col([
                create_oee_trend_chart()
            ], md=4),
        ], className='mb-4'),
        
        # Detailed OEE Charts
        dbc.Row([
            dbc.Col([
                create_oee_breakdown_chart()
            ], md=6),
            
            dbc.Col([
                create_loss_analysis_chart()
            ], md=6),
        ], className='mb-4'),
        
        # Production Monitoring
        dbc.Row([
            dbc.Col([
                create_production_monitoring()
            ], md=12),
        ], className='mb-4'),
        
        # Auto-refresh interval
        dcc.Interval(id='oee-refresh-interval', interval=5000, n_intervals=0),
        
        # Store for OEE data
        dcc.Store(id='oee-data-store', data={}),
    ])


def create_oee_score_card(title, card_id, score, status):
    """Create an OEE score card with gauge visualization"""
    
    # Determine color based on score and status
    if score >= 90:
        color = '#10b981'  # Green
        status_text = 'Excellent'
    elif score >= 80:
        color = '#fbbf24'  # Yellow
        status_text = 'Good'
    elif score >= 70:
        color = '#f97316'  # Orange
        status_text = 'Fair'
    else:
        color = '#ef4444'  # Red
        status_text = 'Poor'
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 70], 'color': "#ef4444"},
                {'range': [70, 80], 'color': "#f97316"},
                {'range': [80, 90], 'color': "#fbbf24"},
                {'range': [90, 100], 'color': "#10b981"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'size': 12}
    )
    
    return html.Div([
        dcc.Graph(
            id=card_id,
            figure=fig,
            config={'displayModeBar': False}
        ),
        html.Div([
            html.Span([
                html.I(className="fas fa-circle me-2", style={'color': color, 'fontSize': '0.7rem'}),
                f"Status: {status_text}"
            ], className='badge bg-light text-dark px-3 py-2',
               style={'fontSize': '0.85rem'})
        ], className='text-center mt-2')
    ], className='stat-card p-3', style={
        'background': 'white',
        'borderRadius': '12px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
        'border': '1px solid #e9ecef'
    })


def create_production_lines_overview():
    """Create production lines overview with real-time status"""
    
    return html.Div([
        html.H6([
            html.I(className="fas fa-industry me-2", style={'color': '#667eea'}),
            "Production Lines Status"
        ], className='fw-bold mb-3'),
        
        dbc.Row([
            dbc.Col([
                create_production_line_card("Line A", "Plastic Molding", 89.2, "running", 1250, 98.5),
            ], md=4),
            
            dbc.Col([
                create_production_line_card("Line B", "Assembly", 85.7, "running", 890, 96.2),
            ], md=4),
            
            dbc.Col([
                create_production_line_card("Line C", "Packaging", 91.3, "running", 2100, 99.1),
            ], md=4),
        ]),
        
        dbc.Row([
            dbc.Col([
                create_production_line_card("Line D", "Quality Control", 78.9, "maintenance", 0, 0),
            ], md=4),
            
            dbc.Col([
                create_production_line_card("Line E", "Inspection", 93.6, "running", 750, 97.8),
            ], md=4),
            
            dbc.Col([
                create_production_line_card("Line F", "Shipping", 87.4, "running", 1100, 95.3),
            ], md=4),
        ]),
    ], className='stat-card p-3', style={
        'background': 'white',
        'borderRadius': '12px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
        'border': '1px solid #e9ecef'
    })


def create_production_line_card(line_name, process, oee_score, status, units_produced, quality_rate):
    """Create individual production line card"""
    
    # Status colors
    status_colors = {
        'running': '#10b981',
        'stopped': '#ef4444',
        'maintenance': '#fbbf24',
        'idle': '#6c757d'
    }
    
    status_icons = {
        'running': 'fas fa-play-circle',
        'stopped': 'fas fa-stop-circle',
        'maintenance': 'fas fa-wrench',
        'idle': 'fas fa-pause-circle'
    }
    
    return html.Div([
        html.Div([
            html.Div([
                html.H6(line_name, className='mb-1 fw-bold'),
                html.Small(process, className='text-muted'),
            ], className='flex-grow-1'),
            
            html.Div([
                html.I(className=status_icons.get(status, 'fas fa-question-circle'), 
                       style={'color': status_colors.get(status, '#6c757d'), 'fontSize': '1.5rem'})
            ])
        ], className='d-flex justify-content-between align-items-center mb-3'),
        
        html.Div([
            html.Div([
                html.Span("OEE", className='text-muted small'),
                html.Br(),
                html.Span(f"{oee_score:.1f}%", className='fw-bold', 
                         style={'color': '#10b981' if oee_score >= 85 else '#fbbf24' if oee_score >= 75 else '#ef4444'})
            ], className='text-center'),
            
            html.Div([
                html.Span("Units", className='text-muted small'),
                html.Br(),
                html.Span(f"{units_produced:,}", className='fw-bold')
            ], className='text-center'),
            
            html.Div([
                html.Span("Quality", className='text-muted small'),
                html.Br(),
                html.Span(f"{quality_rate:.1f}%", className='fw-bold',
                         style={'color': '#10b981' if quality_rate >= 95 else '#fbbf24' if quality_rate >= 90 else '#ef4444'})
            ], className='text-center'),
        ], className='d-flex justify-content-between'),
        
        html.Hr(className='my-2'),
        
        html.Div([
            html.Span([
                html.I(className="fas fa-circle me-2", 
                       style={'color': status_colors.get(status, '#6c757d'), 'fontSize': '0.6rem'}),
                status.title()
            ], className='badge', 
               style={'backgroundColor': f"{status_colors.get(status, '#6c757d')}20", 
                      'color': status_colors.get(status, '#6c757d')})
        ], className='text-center'),
        
    ], className='production-line-card p-3 mb-3', style={
        'border': f'2px solid {status_colors.get(status, "#6c757d")}30',
        'borderRadius': '8px',
        'backgroundColor': f"{status_colors.get(status, '#6c757d')}05"
    })


def create_oee_trend_chart():
    """Create OEE trend chart over time"""
    
    # Generate sample trend data
    now = datetime.now()
    hours = [now - timedelta(hours=i) for i in range(24, 0, -1)]
    oee_values = [85 + random.uniform(-10, 15) for _ in range(24)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours,
        y=oee_values,
        mode='lines+markers',
        name='OEE Trend',
        line=dict(color='#667eea', width=3),
        marker=dict(size=6),
        fill='tonexty'
    ))
    
    # Add target line
    fig.add_hline(y=85, line_dash="dash", line_color="red", 
                  annotation_text="Target: 85%")
    
    fig.update_layout(
        title="OEE Trend (24h)",
        height=400,
        margin=dict(l=40, r=20, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#e9ecef'),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef', title='OEE %'),
        hovermode='x unified',
        showlegend=False
    )
    
    return html.Div([
        dcc.Graph(
            id='oee-trend-chart',
            figure=fig,
            config={'displayModeBar': False}
        )
    ], className='stat-card p-3', style={
        'background': 'white',
        'borderRadius': '12px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
        'border': '1px solid #e9ecef'
    })


def create_oee_breakdown_chart():
    """Create OEE breakdown pie chart"""
    
    # Sample data for OEE breakdown
    labels = ['Availability', 'Performance', 'Quality']
    values = [92.3, 89.7, 94.8]
    colors = ['#10b981', '#fbbf24', '#667eea']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker_colors=colors,
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{value:.1f}%<br>(%{percent})',
        hovertemplate='<b>%{label}</b><br>Value: %{value:.1f}%<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="OEE Breakdown",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        annotations=[dict(text='OEE<br>87.5%', x=0.5, y=0.5, font_size=16, showarrow=False)]
    )
    
    return html.Div([
        dcc.Graph(
            id='oee-breakdown-chart',
            figure=fig,
            config={'displayModeBar': False}
        )
    ], className='stat-card p-3', style={
        'background': 'white',
        'borderRadius': '12px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
        'border': '1px solid #e9ecef'
    })


def create_loss_analysis_chart():
    """Create loss analysis chart showing the Six Big Losses"""
    
    # Six Big Losses data
    categories = [
        'Equipment Failure',
        'Setup & Adjustments', 
        'Idling & Minor Stops',
        'Reduced Speed',
        'Startup Rejects',
        'Production Rejects'
    ]
    
    losses = [2.1, 3.2, 1.8, 2.9, 0.8, 1.7]
    colors = ['#ef4444', '#f97316', '#fbbf24', '#84cc16', '#22c55e', '#10b981']
    
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=losses,
        marker_color=colors,
        text=[f'{loss:.1f}%' for loss in losses],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Loss: %{y:.1f}%<extra></extra>'
    )])
    
    fig.update_layout(
        title="Six Big Losses Analysis",
        height=350,
        margin=dict(l=40, r=20, t=40, b=60),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, tickangle=45),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef', title='Loss %'),
        showlegend=False
    )
    
    return html.Div([
        dcc.Graph(
            id='loss-analysis-chart',
            figure=fig,
            config={'displayModeBar': False}
        )
    ], className='stat-card p-3', style={
        'background': 'white',
        'borderRadius': '12px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
        'border': '1px solid #e9ecef'
    })


def create_production_monitoring():
    """Create detailed production monitoring table"""
    
    # Sample production data
    production_data = [
        {
            'line': 'Line A - Plastic Molding',
            'target': 1500,
            'actual': 1250,
            'efficiency': 83.3,
            'quality': 98.5,
            'downtime': 45,
            'status': 'Running'
        },
        {
            'line': 'Line B - Assembly',
            'target': 1000,
            'actual': 890,
            'efficiency': 89.0,
            'quality': 96.2,
            'downtime': 30,
            'status': 'Running'
        },
        {
            'line': 'Line C - Packaging',
            'target': 2500,
            'actual': 2100,
            'efficiency': 84.0,
            'quality': 99.1,
            'downtime': 60,
            'status': 'Running'
        },
        {
            'line': 'Line D - Quality Control',
            'target': 800,
            'actual': 0,
            'efficiency': 0.0,
            'quality': 0.0,
            'downtime': 480,
            'status': 'Maintenance'
        },
        {
            'line': 'Line E - Inspection',
            'target': 900,
            'actual': 750,
            'efficiency': 83.3,
            'quality': 97.8,
            'downtime': 25,
            'status': 'Running'
        },
        {
            'line': 'Line F - Shipping',
            'target': 1200,
            'actual': 1100,
            'efficiency': 91.7,
            'quality': 95.3,
            'downtime': 15,
            'status': 'Running'
        }
    ]
    
    return html.Div([
        html.H6([
            html.I(className="fas fa-table me-2", style={'color': '#667eea'}),
            "Production Monitoring Detail"
        ], className='fw-bold mb-3'),
        
        dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Production Line"),
                    html.Th("Target"),
                    html.Th("Actual"),
                    html.Th("Efficiency"),
                    html.Th("Quality %"),
                    html.Th("Downtime (min)"),
                    html.Th("Status"),
                    html.Th("Actions"),
                ])
            ]),
            html.Tbody([
                create_production_row(data) for data in production_data
            ])
        ], striped=True, bordered=True, hover=True, responsive=True,
           style={'backgroundColor': 'rgba(255,255,255,0.1)'})
    ], className='stat-card p-4', style={
        'background': 'white',
        'borderRadius': '12px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
        'border': '1px solid #e9ecef'
    })


def create_production_row(data):
    """Create a row for production monitoring table"""
    
    # Determine efficiency color
    efficiency_color = '#10b981' if data['efficiency'] >= 85 else '#fbbf24' if data['efficiency'] >= 75 else '#ef4444'
    
    # Determine status color
    status_color = '#10b981' if data['status'] == 'Running' else '#fbbf24' if data['status'] == 'Maintenance' else '#ef4444'
    
    return html.Tr([
        html.Td([
            html.Div([
                html.I(className="fas fa-industry me-2", style={'color': '#667eea'}),
                html.Span(data['line'], className='fw-bold')
            ])
        ]),
        html.Td(f"{data['target']:,}"),
        html.Td(f"{data['actual']:,}"),
        html.Td([
            html.Span(f"{data['efficiency']:.1f}%", 
                     style={'color': efficiency_color, 'fontWeight': 'bold'})
        ]),
        html.Td(f"{data['quality']:.1f}%"),
        html.Td(f"{data['downtime']} min"),
        html.Td([
            html.Span([
                html.I(className="fas fa-circle me-2", 
                       style={'color': status_color, 'fontSize': '0.6rem'}),
                data['status']
            ], className='badge', 
               style={'backgroundColor': f"{status_color}20", 'color': status_color})
        ]),
        html.Td([
            dbc.Button("View Details", size='sm', color='primary', className='me-1'),
            dbc.Button("Stop", size='sm', color='danger') if data['status'] == 'Running' 
            else dbc.Button("Start", size='sm', color='success')
        ]),
    ])


# OEE Dashboard Callbacks
@callback(
    [Output('oee-overall-score', 'figure'),
     Output('oee-availability-score', 'figure'),
     Output('oee-performance-score', 'figure'),
     Output('oee-quality-score', 'figure'),
     Output('oee-trend-chart', 'figure')],
    [Input('oee-refresh-interval', 'n_intervals'),
     Input('oee-time-range-selector', 'value')]
)
def update_oee_metrics(n, time_range):
    """Update OEE metrics with real-time data"""
    
    # Generate realistic OEE data
    overall_oee = 85 + random.uniform(-5, 10)
    availability = 90 + random.uniform(-5, 8)
    performance = 88 + random.uniform(-8, 10)
    quality = 92 + random.uniform(-3, 6)
    
    # Ensure values are within realistic bounds
    overall_oee = max(60, min(100, overall_oee))
    availability = max(70, min(100, availability))
    performance = max(65, min(100, performance))
    quality = max(75, min(100, quality))
    
    # Update gauge charts
    overall_fig = update_gauge_chart("Overall OEE", overall_oee)
    availability_fig = update_gauge_chart("Availability", availability)
    performance_fig = update_gauge_chart("Performance", performance)
    quality_fig = update_gauge_chart("Quality", quality)
    
    # Update trend chart
    trend_fig = update_trend_chart(time_range)
    
    return overall_fig, availability_fig, performance_fig, quality_fig, trend_fig


def update_gauge_chart(title, value):
    """Update individual gauge chart"""
    
    # Determine color based on value
    if value >= 90:
        color = '#10b981'
    elif value >= 80:
        color = '#fbbf24'
    elif value >= 70:
        color = '#f97316'
    else:
        color = '#ef4444'
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 70], 'color': "#ef4444"},
                {'range': [70, 80], 'color': "#f97316"},
                {'range': [80, 90], 'color': "#fbbf24"},
                {'range': [90, 100], 'color': "#10b981"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 85
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'size': 12}
    )
    
    return fig


def update_trend_chart(time_range):
    """Update OEE trend chart based on time range"""
    
    now = datetime.now()
    
    if time_range == 'live' or time_range == '1h':
        # Show last hour with 5-minute intervals
        time_points = [now - timedelta(minutes=i*5) for i in range(12, 0, -1)]
        oee_values = [85 + random.uniform(-8, 12) for _ in range(12)]
    elif time_range == '8h':
        # Show last 8 hours with 30-minute intervals
        time_points = [now - timedelta(minutes=i*30) for i in range(16, 0, -1)]
        oee_values = [85 + random.uniform(-10, 15) for _ in range(16)]
    elif time_range == '24h':
        # Show last 24 hours with hourly intervals
        time_points = [now - timedelta(hours=i) for i in range(24, 0, -1)]
        oee_values = [85 + random.uniform(-12, 18) for _ in range(24)]
    else:
        # Show last 7 days with daily intervals
        time_points = [now - timedelta(days=i) for i in range(7, 0, -1)]
        oee_values = [85 + random.uniform(-15, 20) for _ in range(7)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time_points,
        y=oee_values,
        mode='lines+markers',
        name='OEE Trend',
        line=dict(color='#667eea', width=3),
        marker=dict(size=6),
        fill='tonexty'
    ))
    
    # Add target line
    fig.add_hline(y=85, line_dash="dash", line_color="red", 
                  annotation_text="Target: 85%")
    
    fig.update_layout(
        title=f"OEE Trend ({time_range})",
        height=400,
        margin=dict(l=40, r=20, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#e9ecef'),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef', title='OEE %'),
        hovermode='x unified',
        showlegend=False
    )
    
    return fig
