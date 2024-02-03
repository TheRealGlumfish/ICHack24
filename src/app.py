# package imports
import dash
from dash import html
import dash_bootstrap_components as dbc
from flask import Flask
# from utils.settings import APP_HOST, APP_PORT, APP_DEBUG, DEV_TOOLS_PROPS_CHECK
import os
import sys
from utils.settings import APP_ID
from utils.settings import APP_KEY

if APP_ID == None and APP_KEY == None:
    print('APP_KEY and/or APP_ID has not been set.\nExiting...', file=sys.stderr)
    quit(128)

server = Flask(__name__)

app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.SOLAR])

app.config.suppress_callback_exceptions = True

app.layout = html.Div([
html.Div(children='My First App with Data')
])

server = app.server

if __name__ == '__main__':
    app.run_server(
        # host=APP_HOST,
        # port=APP_PORT,
        debug=True,
        # dev_tools_props_check=DEV_TOOLS_PROPS_CHECK
    )

