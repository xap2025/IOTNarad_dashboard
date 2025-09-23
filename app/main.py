import os
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from flask import redirect

from app import create_flask_app, socketio
from app.pages import login as login_page
from app.pages import dashboard as dashboard_page
from app.services.mqtt_client import mqtt_service


flask_app = create_flask_app()

external_stylesheets = [dbc.themes.BOOTSTRAP]
dash_app = Dash(
    __name__, server=flask_app, use_pages=False, external_stylesheets=external_stylesheets
)


@flask_app.route("/")
def root():
    return redirect("/login")


dash_app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="page-content")
])


@dash_app.callback(
    dash.dependencies.Output("page-content", "children"),
    dash.dependencies.Input("url", "pathname"),
)
def display_page(pathname):
    if pathname == "/login":
        return login_page.layout()
    return dashboard_page.layout()


def main():
    # Start MQTT background client
    mqtt_service.start()
    port = int(os.getenv("PORT", 8050))
    socketio.init_app(flask_app)
    socketio.run(flask_app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

