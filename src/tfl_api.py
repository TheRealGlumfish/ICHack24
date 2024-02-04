import requests

from utils.settings import APP_ID
from utils.settings import APP_KEY

API_SERVER = 'https://api.tfl.gov.uk'
TIMEOUT = 20

# Returns the modes the journey planner allows as an object
def journey_modes():
    params = {'app_id': APP_ID, 'app_key': APP_KEY}
    response = requests.get(f'{API_SERVER}/Journey/Meta/Modes', params, timeout=TIMEOUT)
    return response.json()

# TODO: Add parameters for options to the journey planner
# Fetches the journey from the journey planner as an object
def journey(source, destination):
    params = {'app_id': APP_ID, 'app_key': APP_KEY}
    response = requests.get(f'{API_SERVER}/Journey/JourneyResults/{source}/to/{destination}', params, timeout=TIMEOUT)
    return response.json()

def get_nearest_station(lat, long):
    radius = 1000
    params = {
        'app_id': APP_ID, 'app_key': APP_KEY,
        'lat': lat, 'lon': long,
        'radius': radius,
        'stoptypes': 'NaptanMetroStation,NaptanRailStation,NaptanPublicBusCoachTram'
    }

    for i in range(5):
        params['radius'] = radius * (2 ** i)
        response = requests.get(f'{API_SERVER}/Stoppoint', params, timeout=TIMEOUT)

        if len(response.json()['stopPoints']) != 0:
            break

    station = response.json()['stopPoints'][0]
    return station['naptanId'], station['commonName']

# Returns the duration of each journey
def journey_time(src, dest):
    response = journey(src, dest)
    return min([journey['duration'] for journey in response['journeys']])

