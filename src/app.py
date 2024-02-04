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
                dbc.Label("Coordinates"),
                dcc.Store(id="residence-data"),
                dcc.Store(id="residence-data-data"),
                dbc.Input(id="input-latitude", placeholder="Latitude Here", type="number", style={"margin-bottom":"10px", "margin-top":"10px"}),
                dbc.Input(id="input-longitude", placeholder="Longitude Here", type="number", style={"margin-bottom":"20px"}),
            ]),
            html.Div(id="longitude-out"),
            html.Div(id="latitude-out"),
            dbc.ButtonGroup([dbc.Button("Submit Residence", id="submit-residence", color="primary"), 
                             dbc.Button("Submit Destination", id="submit-destination", color="secondary"),
                             dbc.Button("Clear", id="clear", color="danger")]),
            dbc.Label("Residence"),
            dcc.Graph(id="residence-data-table"),
            dcc.Store(id="destinations-data"),
            dbc.Label("Destinations"),
            dcc.Graph(id="destinations-data-table"),
        ], width={"size": 2, "offset": 1}),
    ]),
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
              [State("residence-data", "data"), State("destinations-data", "data")], prevent_initial_call=True)
def update_destinations(submit, residence_data, destinations_data):
    if destinations_data is None:
        merged_data = {'Latitude': [residence_data['Latitude']], 'Longitude': [residence_data['Longitude']]}
    else:
        merged_data = destinations_data
        merged_data['Latitude'].append(residence_data['Latitude'])
        merged_data['Longitude'].append(residence_data['Longitude'])
    destinations_table = go.Figure(data=[go.Table(header=dict(values=['Latitude', 'Longitude']),
                 cells=dict(values=[merged_data['Latitude'], merged_data['Longitude']]))
                     ])
    destinations_table.update_layout(margin=dict(r=0, l=0, t=0, b=0))
    if residence_data=={'Latitude': 'N/A', 'Longitude': 'N/A'} and destinations_data is None:
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
    destinations_data = {'Latitude': ['N/A'], 'Longitude': ['N/A']}
    return residence_data, update_residence(submit, residence_data)[0], None, update_destinations(submit, residence_data, None)[0], 'N/A', 'N/A'

@app.callback(Output("slider-output-container", "children"),
                     [Input("weight-slider", "value")])
def update_slider(value):
    return 'You have selected "{}"'.format(value)

price_data = pandas.read_csv('assets/postcode_to_coord_and_price.csv')

@app.callback(Output("map-london", "figure"),
              [Input("weight-slider", "value"),
               Input("map-london", "clickData")])
def update_map(slider, click):
    # df = pandas.read_csv("assets/postcode_to_coord.csv")

    # with open('london_boroughs.json', 'r') as f:
    #     geoJson = json.load(f)

    # fig = px.choropleth(
    #     df, geojson=geoJson, color = None, color_continuous_scale="Viridis", locations=None, scope="London", labels = {}
    # )

    #fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    
    maptooltip = {'Price': True, '% of London Avg': True, 'Longitude': False, 'Latitude': False}

    map = px.scatter_mapbox(price_data, lat = 'Latitude', lon = 'Longitude', hover_name = 'Postcode', hover_data = maptooltip)
    map.update_layout(mapbox = {'style': 'open-street-map'}, margin={'r': 0, 't': 0, 'l':0, 'b':0}, clickmode='event+select')

    return map

@app.callback(Output("latitude-out", "children"),
              Output("longitude-out", "children"),
              Output("residence-data", "data"),
              [Input("map-london", "clickData")], prevent_initial_call=True)
def update_on_map_click(clickData):
    lat = clickData['points'][0]['lat']
    lon = clickData['points'][0]['lon']
    return lon, lat, {"Latitude": lat, "Longitude": lon}


@app.callback(Output("latitude-out", "children", allow_duplicate=True),
              Output("longitude-out", "children", allow_duplicate=True),
              [Input("input-longitude", "value"), Input("input-latitude", "value")], prevent_initial_call=True)
def update_on_user_write(lon, lat):
    return lon, lat



server = app.server

if __name__ == '__main__':
    app.run_server(
        # host=APP_HOST,
        # port=APP_PORT,
        debug=True,
        # dev_tools_props_check=DEV_TOOLS_PROPS_CHECK
    )

