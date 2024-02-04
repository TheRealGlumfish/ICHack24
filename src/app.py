# package imports
import dash
import pandas
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask import Flask
import plotly.express as px
import plotly.graph_objects as go
# from utils.settings import APP_HOST, APP_PORT, APP_DEBUG, DEV_TOOLS_PROPS_CHECK
import os
import sys
from utils.settings import APP_ID
from utils.settings import APP_KEY
import json
import time

import resource_loader
import tfl_api

if APP_ID is None and APP_KEY is None:
    print('APP_KEY and/or APP_ID has not been set.\nExiting...', file=sys.stderr)
    quit(128)

# Get GeoJSON data for postcode sectors
postcode_sectors = resource_loader.get_postcode_geojson()
# Get average house price data for colouring
data_frame = resource_loader.get_postcode_coord_price_data()

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
                dbc.Label("Coordinates"),
                dcc.Store(id="residence-data"),
                dcc.Store(id="residence-data-data"),
                dbc.Input(id="input-latitude", placeholder="Latitude", type="number", style={"margin-bottom":"10px", "margin-top":"10px"}),
                dbc.Input(id="input-longitude", placeholder="Longitude", type="number", style={"margin-bottom":"20px"}),
                dbc.Input(id="input-name", placeholder="Name", type="string", style={"margin-bottom":"20px", "margin-top": "10px"}),
            ]),
            html.Div(id="longitude-out"),
            html.Div(id="latitude-out"),
            dbc.ButtonGroup([dbc.Button("Submit Residence", id="submit-residence", color="primary"), 
                             dbc.Button("Submit Destination", id="submit-destination", color="secondary"),
                             dbc.Button("Clear", id="clear", color="danger")]),
            dbc.Spinner(),
            dbc.Label("Residence"),
            dcc.Graph(id="residence-data-table", style={"height":"50px"}),
            dcc.Store(id="destinations-data"),
            dbc.Label("Destinations"),
            dcc.Graph(id="destinations-data-table", style={"height":"100px"}),
            dbc.Button("Find", id="submit-find", color="success"),
            dbc.Spinner(color="success"),
            dcc.Graph(id="journey-data-table"),
        ], width={"size": 3, "offset": 1}),
    ]),
    dbc.Row(
    dbc.Col(
        dbc.Card([
            html.H5(children=["Hourly Salary"], className="text-center"),
            dcc.Slider(15, 350, 15, id="weight-slider"),
            html.Div(id="slider-output-container"),
            dcc.Store(id="journey-data")
        ])
    )
    )
])



@app.callback(Output("journey-data-table", "figure"),
              Output("journey-data", "data"),
              [Input("submit-find", "n_clicks")],
              [State("residence-data-data", "data"),
               State("destinations-data", "data")], prevent_initial_call=True)
def fetch_journeys(sumbit, residence_data, destination_data):
    residence_lat = residence_data['Latitude']
    residence_lon = residence_data['Longitude']
    destination_data['Journey Times'] = []
    destination_data['Avg Time'] = []
    destination_data["Max Time"] = []
    destination_data["Min Time"] = []
    # destination_data['Journey Fares'] = []
    for (destination_lat, destination_lon) in zip(destination_data['Latitude'], destination_data['Longitude']):
        journeys = tfl_api.journey(f'{residence_lat},{residence_lon}', f'{destination_lat},{destination_lon}')
        journey_times = tfl_api.journey_time(journeys);
        # journey_fares = tfl_api.journey_fares(journeys);
        destination_data['Journey Times'].append(journey_times);
        destination_data['Avg Time'].append(round(sum(journey_times) / len(journey_times), 2))
        destination_data["Max Time"].append(max(journey_times))
        destination_data["Min Time"].append(min(journey_times))
        # destination_data['Journey Fares'].append(journey_fares);

    # print(len(destination_data['Journey Times']))
    # destination_data['Avg Time'] = sum(destination_data['Journey Times']) / len(destination_data['Journey Times'])
    # destination_data['Max Time'] = max(destination_data['Journey Times'])
    # destination_data['Min Time'] = min(destination_data['Journey Times'])

    journey_data = destination_data

    journey_table = go.Figure(data=[go.Table(header=dict(values=['Name', 'Latitude', 'Longitude', 'Journey Times', 'Avg Time', 'Max Time', 'Min Time']),
                 cells=dict(values=[journey_data['Name'], journey_data['Latitude'], journey_data['Longitude'], journey_data['Journey Times'], journey_data['Avg Time'], journey_data['Max Time'], journey_data['Min Time']]))
                     ])
    journey_table.update_layout(margin=dict(r=0, l=0, t=0, b=0))
    return journey_table, journey_data

@app.callback(Output("residence-data-table", "figure"),
              Output("residence-data-data", "data"),
              [Input("submit-residence", "n_clicks")],
              [State("residence-data", "data")], prevent_initial_call=True)
def update_residence(submit, residence_data):
    residence_table = go.Figure(data=[go.Table(header=dict(values=['Latitude', 'Longitude']),
                 cells=dict(values=[[residence_data['Latitude']], [residence_data['Longitude']]]))
                     ])
    residence_table.update_layout(margin=dict(r=0, l=0, t=0, b=0))
    return residence_table, residence_data

@app.callback(Output("destinations-data-table", "figure"),
              Output("destinations-data", "data"),
              [Input("submit-destination", "n_clicks")],
              [State("input-name", "value"), State("residence-data", "data"), State("destinations-data", "data")], prevent_initial_call=True)
def update_destinations(submit, name, residence_data, destinations_data):
    if destinations_data is None:
        merged_data = {'Name': [name], 'Latitude': [residence_data['Latitude']], 'Longitude': [residence_data['Longitude']]}
    else:
        merged_data = destinations_data
        merged_data['Latitude'].append(residence_data['Latitude'])
        merged_data['Longitude'].append(residence_data['Longitude'])
        merged_data['Name'].append(name)
    destinations_table = go.Figure(data=[go.Table(header=dict(values=['Name', 'Latitude', 'Longitude']),
                 cells=dict(values=[merged_data['Name'], merged_data['Latitude'], merged_data['Longitude']]))
                     ])
    destinations_table.update_layout(margin=dict(r=0, l=0, t=0, b=0))
    if residence_data=={'Name': 'N/A', 'Latitude': 'N/A', 'Longitude': 'N/A'} and destinations_data is None:
        merged_data = None
    return destinations_table, merged_data

@app.callback(Output("residence-data", "data", allow_duplicate=True),
              Output("residence-data-table", "figure", allow_duplicate=True),
              Output("destinations-data", "data", allow_duplicate=True),
              Output("destinations-data-table", "figure", allow_duplicate=True),
              Output("latitude-out", "children", allow_duplicate=True),
              Output("longitude-out", "children", allow_duplicate=True),
              [Input("clear", "n_clicks")], prevent_initial_call=True)
def clear(submit):
    residence_data = {'Latitude': 'N/A', 'Longitude': 'N/A'}
    destination_data = {'Name': 'N/A', 'Latitude': 'N/A', 'Longitude': 'N/A'}
    return residence_data, update_residence(submit, residence_data)[0], None, update_destinations(submit, 'N/A', destination_data, None)[0], 'N/A', 'N/A'

@app.callback(Output("slider-output-container", "children"),
                     [Input("weight-slider", "value")],
                     [State("journey-data", "data")], prevent_intial_call=True)
def update_slider(value, journey_data):
    minutes_daily = sum(journey_data['Min Time'])
    travel_loss = (float(minutes_daily) / float(60)) * value
    travel_loss_annual = travel_loss * 365
    return f'Minutes spent travelling: {minutes_daily}\nTravel earnings loss (daily/annually): {travel_loss}/{travel_loss_annual} GBP\n'


@app.callback(Output("map-london", "figure"),
              [Input("weight-slider", "value")])
def update_map(value):

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

    figure.update_layout(clickmode="event+select", margin={'r': 0, 't': 0, 'l':0, 'b':0})
    return figure

@app.callback(Output("latitude-out", "children"),
              Output("longitude-out", "children"),
              Output("residence-data", "data", allow_duplicate=True),
              [Input("map-london", "clickData")], prevent_initial_call=True)
def update_on_map_click(clickData):
    if clickData is not None:
        postcode = clickData['points'][0]['location']
        entry = data_frame.loc[data_frame['Postcode'] == postcode]
        lat, lon = entry['Latitude'].iloc[0], entry['Longitude'].iloc[0]
    return lon, lat, {"Latitude": lat, "Longitude": lon}


@app.callback(Output("latitude-out", "children", allow_duplicate=True),
              Output("longitude-out", "children", allow_duplicate=True),
              Output("residence-data", "data", allow_duplicate=True),
              [Input("input-longitude", "value"), Input("input-latitude", "value")], prevent_initial_call=True)
def update_on_user_write(lon, lat):
    return lon, lat, {"Latitude": lat, "Longitude": lon}



server = app.server

if __name__ == '__main__':
    app.run_server(
        # host=APP_HOST,
        # port=APP_PORT,
        debug=True,
        # dev_tools_props_check=DEV_TOOLS_PROPS_CHECK
    )

