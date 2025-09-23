from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from flask_socketio import SocketIO
from app import socketio


def layout():
    return dbc.Container([
        html.H2("Universal Dashboard"),
        html.Div("Live MQTT messages:"),
        html.Pre(id="mqtt-stream", style={"height": "300px", "overflowY": "auto", "border": "1px solid #ccc", "padding": "8px"}),
        dcc.Interval(id="tick", n_intervals=0, interval=1000)
    ], fluid=True)


_messages: list[str] = []


@socketio.on("mqtt_message")
def _on_mqtt_message(data):
    text = f"{data.get('topic')}: {data.get('payload')}"
    _messages.append(text)
    if len(_messages) > 200:
        del _messages[: len(_messages) - 200]


@callback(Output("mqtt-stream", "children"), Input("tick", "n_intervals"))
def refresh_stream(_):
    return "\n".join(_messages)

