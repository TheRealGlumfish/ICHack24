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
        dcc.Graph(id="map-london")],
        style={"width": "100vw", "height": "100vh"}
    ),
    dbc.Row(
    dbc.Col(
        dbc.Card([
            html.H5(children=["Travel Vs Cost"], className="text-center"),
            dcc.Slider(0, 10, 1, value= 5, id="weight-slider"),
            html.Div(id="slider-output-container")
        ])
    )
    )
])

@app.callback(Output("slider-output-container", "children"),
                     [Input("weight-slider", "value")])
def update_slider(value):
    return 'You have selected "{}"'.format(value)

price_data = pandas.read_csv('assets/postcode_to_coord_and_price.csv')

@app.callback(Output("map-london", "figure"),
              [Input("weight-slider", "value")])
def update_map(value):
    # df = pandas.read_csv("assets/postcode_to_coord.csv")

    # with open('london_boroughs.json', 'r') as f:
    #     geoJson = json.load(f)

    # fig = px.choropleth(
    #     df, geojson=geoJson, color = None, color_continuous_scale="Viridis", locations=None, scope="London", labels = {}
    # )

    #fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    
    maptooltip = {'Price': True, 'Longitude': False, 'Latitude': False}

    map = px.scatter_mapbox(price_data, lat = 'Latitude', lon = 'Longitude', hover_name = 'Postcode', hover_data = maptooltip)
    map.update_layout(mapbox = {'style': 'open-street-map'})

    return map


server = app.server

if __name__ == '__main__':
    app.run_server(
        # host=APP_HOST,
        # port=APP_PORT,
        debug=True,
        # dev_tools_props_check=DEV_TOOLS_PROPS_CHECK
    )

