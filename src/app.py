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
            dcc.Graph(id="map-london", style={"height": "100vh"}),
            width={"size":8},
            #style={"height": "100vh"},
        ),
        dbc.Col([
            dbc.Form([
            dbc.Input(id="input-latitude", placeholder="Latitude Here", type="number", style={"margin-bottom":"10px", "margin-top":"20px"}),
            dbc.Input(id="input-longitude", placeholder="Longitude Here", type="number", style={"margin-bottom":"20px"}),
            dbc.Button("Submit", id="Submit", color="primary")
            ]),
            html.Div(id="longitude-out"),
            html.Div(id="latitude-out")
        ], width={"size": 2, "offset": 1}
            
        )
        ],
        #style={"width": "100vw", "height": "100vh"}
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
              [Input("weight-slider", "value"),
               Input("Submit", "n_clicks"),
               Input("map-london", "clickData")])
def update_map(slider, submit, click):
    # df = pandas.read_csv("assets/postcode_to_coord.csv")

    # with open('london_boroughs.json', 'r') as f:
    #     geoJson = json.load(f)

    # fig = px.choropleth(
    #     df, geojson=geoJson, color = None, color_continuous_scale="Viridis", locations=None, scope="London", labels = {}
    # )

    #fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    
    maptooltip = {'Price': True, 'Longitude': False, 'Latitude': False}

    map = px.scatter_mapbox(price_data, lat = 'Latitude', lon = 'Longitude', hover_name = 'Postcode', hover_data = maptooltip)
    map.update_layout(mapbox = {'style': 'open-street-map'}, margin={'r': 10, 't': 10, 'l':10, 'b':10}, clickmode='event+select')

    return map

@app.callback(Output("latitude-out", "children"),
              Output("longitude-out", "children"),
              Output("map-london", "clickData"),
              [Input("map-london", "clickData"),
               Input("Submit", "n_clicks")],
              [State("input-longitude", "value"), State("input-latitude", "value")])
def update_on_point_click(clickData, nc, long, lat):
    if long is None and lat is None and clickData is None:
        return None, None, None

    if clickData is not None:
        ls = clickData['points']
        lat = ls[0]['lat']#
        lon = ls[0]['lon']
        return lon, lat, None

    if long is not None and lat is not None:
        return long, lat, None

    return 0, 0

server = app.server

if __name__ == '__main__':
    app.run_server(
        # host=APP_HOST,
        # port=APP_PORT,
        debug=True,
        # dev_tools_props_check=DEV_TOOLS_PROPS_CHECK
    )

