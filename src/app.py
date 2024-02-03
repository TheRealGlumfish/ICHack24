# package imports
import dash
import pandas
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask import Flask
import plotly.express as px
# from utils.settings import APP_HOST, APP_PORT, APP_DEBUG, DEV_TOOLS_PROPS_CHECK
import os
import sys
from utils.settings import APP_ID
from utils.settings import APP_KEY
import json

if APP_ID == None and APP_KEY == None:
    print('APP_KEY and/or APP_ID has not been set.\nExiting...', file=sys.stderr)
    quit(128)
from dash.dependencies import Input, Output, State

server = Flask(__name__)

app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.LITERA])

app.config.suppress_callback_exceptions = True

app.layout = html.Div([
dbc.Row([
    dbc.Col(
        dcc.Graph(id="map_London")
        #style={"width: 100vw, height: 100vh"}
    ),
    dbc.Col(
        dbc.Card([
            html.H5(children=["Travel Vs Cost"], className="text-center"),
            dcc.Slider(0, 10, 1, value= 5, id="weight-slider"),
            html.Div(id="slider-output-container")
        ])
    )
], style={"width": "100vw", "height": "100vh"})
])

@app.callback(Output("slider-output-container", "children"),
                     [Input("weight-slider", "value")])
def update_slider(value):
    return 'You have selected "{}"'.format(value)

@app.callback(Output("map-london", "figure"),
              [Input("weight-slider", "value")])
def update_map():
    df = pandas.read_csv("assets/postcode_to_coord.csv")

    with open('london_boroughs.json', 'r') as f:
        geoJson = json.load(f)

    # fig = px.choropleth(
    #     df, geojson=geoJson, color = None, color_continuous_scale="Viridis", locations=None, scope="London", labels = {}
    # )

    #fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    fig = px.scatter(df, x="longitude", y="latitude")

    return fig


server = app.server

if __name__ == '__main__':
    app.run_server(
        # host=APP_HOST,
        # port=APP_PORT,
        debug=True,
        # dev_tools_props_check=DEV_TOOLS_PROPS_CHECK
    )

