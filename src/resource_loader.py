import json
import pandas as pd

def get_postcode_coord_price_data():
    return pd.read_csv("assets/postcode_to_coord_and_price.csv", dtype={
        'Postcode': 'string',
        'Latitude': 'float64',
        'Longitude': 'float64',
        'Price': 'int64',
        r'% of London avg': 'int64'
    })

def get_postcode_geojson():
    with open('assets/wgs84_format_london_postal_sectors.json', 'r') as f:
        return json.load(f)