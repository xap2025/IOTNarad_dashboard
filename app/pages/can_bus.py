"""
CAN Bus Configuration Page
Matches the CAN Bus configuration form from image 2
"""
from dash import html, dcc, Input, Output, State, ALL, callback, ctx, no_update
import dash_bootstrap_components as dbc
import json


def create_can_bus_layout():
    """Create CAN Bus configuration page matching image 2"""
    
    return html.Div([
        # Header
        html.Div([
            html.H5([
                html.I(className="fas fa-bus me-2", style={'color': '#667eea'}),
                "CAN Bus Configuration"
            ], className='fw-bold mb-3'),
        ], className='mb-4'),
        
        # CAN Bus Communication Settings Section
        html.Div([
            html.H5([
                html.I(className="fas fa-cog me-2", style={'color': '#667eea'}),
                "CAN Bus Communication Settings"
            ], className='fw-bold mb-3'),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Baud Rate", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='can-baud-rate',
                        options=[
                            {'label': '125 kbps', 'value': '125'},
                            {'label': '250 kbps', 'value': '250'},
                            {'label': '500 kbps', 'value': '500'},
                            {'label': '1000 kbps (1 Mbps)', 'value': '1000'},
                        ],
                        value='125',
                        clearable=False
                    ),
                ], md=4),
                
                dbc.Col([
                    dbc.Label("Identifier Length", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='can-identifier-length',
                        options=[
                            {'label': '11-bit (Standard)', 'value': '11-bit'},
                            {'label': '29-bit (Extended)', 'value': '29-bit'},
                        ],
                        value='11-bit',
                        clearable=False
                    ),
                ], md=4),
                
                dbc.Col([
                    dbc.Label("CAN Mode", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='can-mode',
                        options=[
                            {'label': 'Normal Mode', 'value': 'Normal'},
                            {'label': 'Listen Only Mode', 'value': 'Listen'},
                            {'label': 'Loopback Mode', 'value': 'Loopback'},
                        ],
                        value='Normal',
                        clearable=False
                    ),
                ], md=4),
            ], className='mb-3'),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Filter Mode", className='fw-bold mb-2'),
                    dcc.Dropdown(
                        id='can-filter-mode',
                        options=[
                            {'label': 'No Filtering', 'value': 'None'},
                            {'label': 'Accept Filter', 'value': 'Accept'},
                            {'label': 'Reject Filter', 'value': 'Reject'},
                        ],
                        value='None',
                        clearable=False
                    ),
                ], md=4),
                
                dbc.Col([
                    dbc.Label("Filter ID (Hex)", className='fw-bold mb-2'),
                    dbc.Input(
                        id='can-filter-id',
                        type='text',
                        value='0x123',
                        placeholder='0x123'
                    ),
                ], md=4),
                
                dbc.Col([
                    dbc.Label("Filter Mask (Hex)", className='fw-bold mb-2'),
                    dbc.Input(
                        id='can-filter-mask',
                        type='text',
                        value='0x7FF',
                        placeholder='0x7FF'
                    ),
                ], md=4),
            ]),
        ], className='stat-card p-4 mb-4'),
        
        # CAN Message Mapping Section
        html.Div([
            html.H5([
                html.I(className="fas fa-map me-2", style={'color': '#667eea'}),
                "CAN Message Mapping"
            ], className='fw-bold mb-3'),
            
            html.P("Map variables to 8-byte CAN data payload", className='text-muted mb-4'),
            
            # CAN Messages Subsection
            html.Div([
                html.H6("CAN Messages", className='fw-bold mb-3'),
                
                dbc.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("CAN ID (Hex)", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Direction", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Period (ms)", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Variable Name", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Action", style={'backgroundColor': '#667eea', 'color': 'white'}),
                        ])
                    ]),
                    html.Tbody(id='can-messages-tbody', children=[])
                ], bordered=True, hover=True, responsive=True, className='mb-3'),
                
                dbc.Button([
                    html.I(className="fas fa-plus me-2"),
                    "Add CAN Message"
                ], id='add-can-message-btn', color='primary', className='mb-4', n_clicks=0),
            ], className='mb-4'),
            
            # Data Mapping Subsection
            html.Div([
                html.H6("Data Mapping (8-byte payload)", className='fw-bold mb-3'),
                
                dbc.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("CAN ID", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Byte Position", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Data Length", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Data Type", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Endianness", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Variable Name", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Scale Factor", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Offset", style={'backgroundColor': '#667eea', 'color': 'white'}),
                            html.Th("Action", style={'backgroundColor': '#667eea', 'color': 'white'}),
                        ])
                    ]),
                    html.Tbody(id='can-data-mapping-tbody', children=[])
                ], bordered=True, hover=True, responsive=True, className='mb-3'),
                
                dbc.Button([
                    html.I(className="fas fa-plus me-2"),
                    "Add Data Mapping"
                ], id='add-can-data-mapping-btn', color='primary', className='mb-3', n_clicks=0),
            ]),
        ], className='stat-card p-4 mb-4'),
        
        # Stores for CAN messages and data mappings
        dcc.Store(id='can-messages-store', data=[{"index": 0, "can_id": "0x123", "direction": "TX", "period": "100", "var_name": "Message Name"}]),
        dcc.Store(id='can-data-mapping-store', data=[{"index": 0, "can_id": "0x123", "byte_pos": "Byte 0", "data_len": "1 Byte", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name", "scale": "1", "offset": "0"}]),
        # Trigger stores
        dcc.Store(id='can-messages-trigger-store', data=0),
        dcc.Store(id='can-data-mapping-trigger-store', data=0),
    ])


def create_can_message_row(index, can_id, direction, period, var_name):
    """Create a single CAN message row"""
    # Normalize direction value
    direction_value = direction if direction in ['TX', 'RX'] else ('TX' if 'TX' in str(direction) else 'RX')
    
    return html.Tr([
        html.Td(
            dbc.Input(
                id={'type': 'can-message-id', 'index': index},
                type='text',
                value=can_id,
                size='sm',
                placeholder='0x123'
            )
        ),
        html.Td(
            dcc.Dropdown(
                id={'type': 'can-message-direction', 'index': index},
                options=[
                    {'label': 'Transmit (TX)', 'value': 'TX'},
                    {'label': 'Receive (RX)', 'value': 'RX'},
                ],
                value=direction_value,
                clearable=False,
                style={'fontSize': '0.9rem'}
            )
        ),
        html.Td(
            dbc.Input(
                id={'type': 'can-message-period', 'index': index},
                type='number',
                value=period,
                size='sm',
                min=1
            )
        ),
        html.Td(
            dbc.Input(
                id={'type': 'can-message-var-name', 'index': index},
                type='text',
                value=var_name,
                size='sm'
            )
        ),
        html.Td(
            dbc.Button(
                html.I(className="fas fa-trash"),
                id={'type': 'can-remove-message', 'index': index},
                color='danger',
                size='sm',
                outline=True,
                n_clicks=0
            )
        ),
    ])


def create_can_data_mapping_row(index, can_id, byte_pos, data_len, data_type, endianness, var_name, scale, offset):
    """Create a single CAN data mapping row"""
    return html.Tr([
        html.Td(
            dbc.Input(
                id={'type': 'can-data-can-id', 'index': index},
                type='text',
                value=can_id,
                size='sm',
                placeholder='0x123'
            )
        ),
        html.Td(
            dcc.Dropdown(
                id={'type': 'can-data-byte-pos', 'index': index},
                options=[{'label': f'Byte {i}', 'value': f'Byte {i}'} for i in range(8)],
                value=byte_pos,
                clearable=False,
                style={'fontSize': '0.9rem'}
            )
        ),
        html.Td(
            dcc.Dropdown(
                id={'type': 'can-data-length', 'index': index},
                options=[
                    {'label': '1 Byte', 'value': '1 Byte'},
                    {'label': '2 Bytes', 'value': '2 Bytes'},
                    {'label': '4 Bytes', 'value': '4 Bytes'},
                    {'label': '8 Bytes', 'value': '8 Bytes'},
                ],
                value=data_len,
                clearable=False,
                style={'fontSize': '0.9rem'}
            )
        ),
        html.Td(
            dcc.Dropdown(
                id={'type': 'can-data-type', 'index': index},
                options=[
                    {'label': 'int8', 'value': 'int8'},
                    {'label': 'uint8', 'value': 'uint8'},
                    {'label': 'int16', 'value': 'int16'},
                    {'label': 'uint16', 'value': 'uint16'},
                    {'label': 'int32', 'value': 'int32'},
                    {'label': 'uint32', 'value': 'uint32'},
                    {'label': 'float32', 'value': 'float32'},
                    {'label': 'float64', 'value': 'float64'},
                ],
                value=data_type,
                clearable=False,
                style={'fontSize': '0.9rem'}
            )
        ),
        html.Td(
            dcc.Dropdown(
                id={'type': 'can-data-endianness', 'index': index},
                options=[
                    {'label': 'Big Endian', 'value': 'Big Endian'},
                    {'label': 'Little Endian', 'value': 'Little Endian'},
                ],
                value=endianness,
                clearable=False,
                style={'fontSize': '0.9rem'}
            )
        ),
        html.Td(
            dbc.Input(
                id={'type': 'can-data-var-name', 'index': index},
                type='text',
                value=var_name,
                size='sm'
            )
        ),
        html.Td(
            dbc.Input(
                id={'type': 'can-data-scale', 'index': index},
                type='number',
                value=scale,
                size='sm',
                step=0.1
            )
        ),
        html.Td(
            dbc.Input(
                id={'type': 'can-data-offset', 'index': index},
                type='number',
                value=offset,
                size='sm',
                step=0.1
            )
        ),
        html.Td(
            dbc.Button(
                html.I(className="fas fa-trash"),
                id={'type': 'can-remove-data-mapping', 'index': index},
                color='danger',
                size='sm',
                outline=True,
                n_clicks=0
            )
        ),
    ])


# Callback to update CAN messages table from store
@callback(
    Output('can-messages-tbody', 'children'),
    Input('can-messages-store', 'data'),
    prevent_initial_call=False
)
def update_can_messages_table(messages_data):
    """Update CAN messages table rows from store data"""
    if not messages_data or len(messages_data) == 0:
        messages_data = [{"index": 0, "can_id": "0x123", "direction": "TX", "period": "100", "var_name": "Message Name"}]
    
    rows = []
    for message in messages_data:
        rows.append(create_can_message_row(
            message.get("index", 0),
            message.get("can_id", "0x123"),
            message.get("direction", "TX"),
            message.get("period", "100"),
            message.get("var_name", "Message Name")
        ))
    
    return rows


# Callback to update CAN data mapping table from store
@callback(
    Output('can-data-mapping-tbody', 'children'),
    Input('can-data-mapping-store', 'data'),
    prevent_initial_call=False
)
def update_can_data_mapping_table(mappings_data):
    """Update CAN data mapping table rows from store data"""
    if not mappings_data or len(mappings_data) == 0:
        mappings_data = [{"index": 0, "can_id": "0x123", "byte_pos": "Byte 0", "data_len": "1 Byte", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name", "scale": "1", "offset": "0"}]
    
    rows = []
    for mapping in mappings_data:
        rows.append(create_can_data_mapping_row(
            mapping.get("index", 0),
            mapping.get("can_id", "0x123"),
            mapping.get("byte_pos", "Byte 0"),
            mapping.get("data_len", "1 Byte"),
            mapping.get("data_type", "int8"),
            mapping.get("endianness", "Big Endian"),
            mapping.get("var_name", "Variable Name"),
            mapping.get("scale", "1"),
            mapping.get("offset", "0")
        ))
    
    return rows


# Unified callback for CAN messages (add and remove)
@callback(
    Output('can-messages-store', 'data'),
    Output('can-messages-trigger-store', 'data'),
    Input('add-can-message-btn', 'n_clicks'),
    Input({'type': 'can-remove-message', 'index': ALL}, 'n_clicks'),
    State('can-messages-store', 'data'),
    State('can-messages-trigger-store', 'data'),
    prevent_initial_call=True
)
def manage_can_messages(add_clicks, remove_clicks_list, messages_data, trigger_value):
    """Handle both add and remove CAN message operations"""
    if not ctx.triggered:
        return no_update, no_update
    
    triggered_id = ctx.triggered[0]['prop_id']
    
    # Initialize messages_data if needed
    if messages_data is None:
        messages_data = []
    if len(messages_data) == 0:
        messages_data = [{"index": 0, "can_id": "0x123", "direction": "TX", "period": "100", "var_name": "Message Name"}]
    
    # Handle ADD operation
    if 'add-can-message-btn' in triggered_id:
        updated_messages = []
        for idx, message in enumerate(messages_data):
            updated_messages.append({
                "index": idx,
                "can_id": str(message.get("can_id", "0x123")),
                "direction": str(message.get("direction", "TX")),
                "period": str(message.get("period", "100")),
                "var_name": str(message.get("var_name", "Message Name"))
            })
        
        new_index = len(updated_messages)
        updated_messages.append({
            "index": new_index,
            "can_id": "0x123",
            "direction": "TX",
            "period": "100",
            "var_name": "Message Name"
        })
        
        return updated_messages, (trigger_value if trigger_value is not None else 0) + 1
    
    # Handle REMOVE operation
    if 'can-remove-message' in triggered_id and 'index' in triggered_id:
        try:
            prop_id_json = triggered_id.split('.n_clicks')[0]
            button_id = json.loads(prop_id_json)
            index_to_remove = button_id.get('index')
        except (json.JSONDecodeError, KeyError, ValueError):
            try:
                start_idx = triggered_id.find('"index":') + 8
                end_idx = triggered_id.find(',', start_idx)
                if end_idx == -1:
                    end_idx = triggered_id.find('}', start_idx)
                index_to_remove = int(triggered_id[start_idx:end_idx])
            except (ValueError, AttributeError):
                return no_update, no_update
        
        if len(messages_data) <= 1:
            return no_update, no_update
        
        updated_messages = []
        for message in messages_data:
            if message.get("index") != index_to_remove:
                updated_messages.append({
                    "index": len(updated_messages),
                    "can_id": str(message.get("can_id", "0x123")),
                    "direction": str(message.get("direction", "TX")),
                    "period": str(message.get("period", "100")),
                    "var_name": str(message.get("var_name", "Message Name"))
                })
        
        if len(updated_messages) == 0:
            updated_messages = [{"index": 0, "can_id": "0x123", "direction": "TX", "period": "100", "var_name": "Message Name"}]
        
        return updated_messages, (trigger_value if trigger_value is not None else 0) + 1
    
    return no_update, no_update


# Unified callback for CAN data mappings (add and remove)
@callback(
    Output('can-data-mapping-store', 'data'),
    Output('can-data-mapping-trigger-store', 'data'),
    Input('add-can-data-mapping-btn', 'n_clicks'),
    Input({'type': 'can-remove-data-mapping', 'index': ALL}, 'n_clicks'),
    State('can-data-mapping-store', 'data'),
    State('can-data-mapping-trigger-store', 'data'),
    prevent_initial_call=True
)
def manage_can_data_mappings(add_clicks, remove_clicks_list, mappings_data, trigger_value):
    """Handle both add and remove CAN data mapping operations"""
    if not ctx.triggered:
        return no_update, no_update
    
    triggered_id = ctx.triggered[0]['prop_id']
    
    # Initialize mappings_data if needed
    if mappings_data is None:
        mappings_data = []
    if len(mappings_data) == 0:
        mappings_data = [{"index": 0, "can_id": "0x123", "byte_pos": "Byte 0", "data_len": "1 Byte", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name", "scale": "1", "offset": "0"}]
    
    # Handle ADD operation
    if 'add-can-data-mapping-btn' in triggered_id:
        updated_mappings = []
        for idx, mapping in enumerate(mappings_data):
            updated_mappings.append({
                "index": idx,
                "can_id": str(mapping.get("can_id", "0x123")),
                "byte_pos": str(mapping.get("byte_pos", "Byte 0")),
                "data_len": str(mapping.get("data_len", "1 Byte")),
                "data_type": str(mapping.get("data_type", "int8")),
                "endianness": str(mapping.get("endianness", "Big Endian")),
                "var_name": str(mapping.get("var_name", "Variable Name")),
                "scale": str(mapping.get("scale", "1")),
                "offset": str(mapping.get("offset", "0"))
            })
        
        new_index = len(updated_mappings)
        updated_mappings.append({
            "index": new_index,
            "can_id": "0x123",
            "byte_pos": "Byte 0",
            "data_len": "1 Byte",
            "data_type": "int8",
            "endianness": "Big Endian",
            "var_name": "Variable Name",
            "scale": "1",
            "offset": "0"
        })
        
        return updated_mappings, (trigger_value if trigger_value is not None else 0) + 1
    
    # Handle REMOVE operation
    if 'can-remove-data-mapping' in triggered_id and 'index' in triggered_id:
        try:
            prop_id_json = triggered_id.split('.n_clicks')[0]
            button_id = json.loads(prop_id_json)
            index_to_remove = button_id.get('index')
        except (json.JSONDecodeError, KeyError, ValueError):
            try:
                start_idx = triggered_id.find('"index":') + 8
                end_idx = triggered_id.find(',', start_idx)
                if end_idx == -1:
                    end_idx = triggered_id.find('}', start_idx)
                index_to_remove = int(triggered_id[start_idx:end_idx])
            except (ValueError, AttributeError):
                return no_update, no_update
        
        if len(mappings_data) <= 1:
            return no_update, no_update
        
        updated_mappings = []
        for mapping in mappings_data:
            if mapping.get("index") != index_to_remove:
                updated_mappings.append({
                    "index": len(updated_mappings),
                    "can_id": str(mapping.get("can_id", "0x123")),
                    "byte_pos": str(mapping.get("byte_pos", "Byte 0")),
                    "data_len": str(mapping.get("data_len", "1 Byte")),
                    "data_type": str(mapping.get("data_type", "int8")),
                    "endianness": str(mapping.get("endianness", "Big Endian")),
                    "var_name": str(mapping.get("var_name", "Variable Name")),
                    "scale": str(mapping.get("scale", "1")),
                    "offset": str(mapping.get("offset", "0"))
                })
        
        if len(updated_mappings) == 0:
            updated_mappings = [{"index": 0, "can_id": "0x123", "byte_pos": "Byte 0", "data_len": "1 Byte", "data_type": "int8", "endianness": "Big Endian", "var_name": "Variable Name", "scale": "1", "offset": "0"}]
        
        return updated_mappings, (trigger_value if trigger_value is not None else 0) + 1
    
    return no_update, no_update
