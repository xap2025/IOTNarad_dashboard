from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc


def layout():
    return dbc.Container([
        html.H2("Login"),
        dbc.Row([
            dbc.Col([
                dbc.Input(id="username", placeholder="Username", type="text", className="mb-2"),
                dbc.Input(id="password", placeholder="Password", type="password", className="mb-2"),
                dbc.Button("Login", id="login-btn", color="primary"),
                html.Div(id="login-msg", className="mt-2"),
            ], md=4)
        ])
    ], fluid=True)


@callback(Output("login-msg", "children"), Input("login-btn", "n_clicks"), State("username", "value"), State("password", "value"))
def do_login(n, u, p):
    if not n:
        return ""
    # Dummy auth for now
    if u and p:
        return dcc.Location(pathname="/dashboard", id="redir")
    return "Invalid credentials"

