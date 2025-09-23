from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from flask_socketio import SocketIO
from app import socketio
from app.services.mqtt_client import publish_message


def layout():
    return dbc.Container([
        html.H2("Universal Dashboard"),
        dbc.Row([
            dbc.Col([
                dbc.Input(id="publish-topic", value="devices/test/uplink", placeholder="MQTT topic", className="mb-2"),
                dbc.Input(id="publish-payload", value='{"temp":25}', placeholder="JSON payload", className="mb-2"),
                dbc.Button("Publish test", id="publish-btn", color="secondary", className="mb-3"),
                html.Div(id="publish-status", className="text-muted mb-3")
            ], md=4)
        ]),
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


@callback(Output("publish-status", "children"), Input("publish-btn", "n_clicks"), State("publish-topic", "value"), State("publish-payload", "value"))
def do_publish(n, topic, payload):
    if not n:
        return ""
    if not topic or not payload:
        return "Enter topic and payload"
    ok = publish_message(topic, payload)
    return "Published" if ok else "Publish failed (MQTT not ready)"

