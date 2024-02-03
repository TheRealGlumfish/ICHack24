from utils.settings import APP_ID
from utils.settings import APP_KEY

import requests

# Returns the modes the journey planner allows as an object
def journey_modes():
    params = {'app_id': APP_ID, 'app_key': APP_KEY}
    response = requests.get('https://api.tfl.gov.uk/Journey/Meta/Modes', params)
    return response.json()
    
# TODO: Add parameters for options to the journey planner
# Fetches the journey from the journey planner as an object
def journey(source, destination):
    params = {'app_id': APP_ID, 'app_key': APP_KEY, }
    response = requests.get(f'https://api.tfl.gov.uk/Journey/JourneyResults/{source}/to/{destination}', params)
    return response.json()

# Returns the duration of each journey
def journey_time(response):
    times = [journey['duration'] for journey in response['journeys']]
    return times
        
