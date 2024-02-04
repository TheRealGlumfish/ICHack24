import json
from pyproj import Transformer

src_proj = 'epsg:27700'
tgt_proj = 'epsg:4326'

# Create a transformer
transformer = Transformer.from_crs(src_proj, tgt_proj)

def convert_coordinates(x, y):
    lon, lat = transformer.transform(x, y)
    return lat, lon

# Read the GeoJSON file
with open('assets/bng_highres_london.json', 'r') as f:
    geojson = json.load(f)

# Convert the coordinates
for feature in geojson['features']:
    if feature['geometry']['type'] == 'Polygon':
        for polygon in feature['geometry']['coordinates']:
            for point in polygon:
                point[0], point[1] = convert_coordinates(point[0], point[1])
    elif feature['geometry']['type'] == 'MultiPolygon':
        for multipolygon in feature['geometry']['coordinates']:
            for polygon in multipolygon:
                for point in polygon:
                    point[0], point[1] = convert_coordinates(point[0], point[1])

# Write the corrected GeoJSON to a new file
with open('assets/wgs84_highres_london.json', 'w') as f:
    json.dump(geojson, f)