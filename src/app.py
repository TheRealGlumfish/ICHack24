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

import resource_loader

if APP_ID is None and APP_KEY is None:
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


@app.callback(Output("map-london", "figure"),
              [Input("weight-slider", "value"),
              Input("map-london", "clickData")])
def update_map(value, clickData):
    # Get GeoJSON data for postcode sectors
    postcode_sectors = resource_loader.get_postcode_geojson()
    # Get average house price data for colouring
    data_frame = resource_loader.get_postcode_coord_price_data()

    if clickData is not None:
        postcode = clickData['points'][0]['location']
        entry = data_frame.loc[data_frame['Postcode'] == postcode]
        price = entry['Price'].iloc[0]
        lat, long = entry['Latitude'].iloc[0], entry['Longitude'].iloc[0]
        # TODO: Use (lat, long) with TfL data

    figure = px.choropleth_mapbox(
        data_frame,
        geojson=postcode_sectors,
        locations="Postcode",
        featureidkey="properties.RMSect",
        color="Price",
        color_continuous_scale="Jet",
        color_continuous_midpoint=data_frame['Price'].median(),
        mapbox_style="carto-positron",
        center={"lat": 51.5074, "lon": -0.1278},
        range_color=(150,1200),
        zoom=10,
        opacity=0.5
    )

    figure.update_layout(clickmode="event+select")
    return figure


server = app.server

if __name__ == '__main__':
    app.run_server(
        # host=APP_HOST,
        # port=APP_PORT,
        debug=True,
        # dev_tools_props_check=DEV_TOOLS_PROPS_CHECK
    )

