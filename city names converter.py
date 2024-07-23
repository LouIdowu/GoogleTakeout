#this is a bonus script. and not necesary for the other ones to run.
#the output of running this is already inside of the project directory, this is for those curious.
#in the nlp analysis script, a csv was used to map us city names to states.
#this script utilizes a txt file of several hundred of the most popular us cities and maps them to a state
#tableau prefers for locations to be in one type. it can handle cities, and states individually but doesnt like when you mix them up
#for the purposes of this project, this script uses automatically geopy to map each city name to its corresponding state that will be used in the nlp phase
#the reason this script was sequestered was because of the fact that it utilizes network requests.
#trying to merge this with the nlp wouuldve greately and unnecesarily increased runtime and also forced one of the keystone scripts to rely on network availibility
#user may also add their own cities theyd like to be mapped for specific use cases.

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import os
import time

#initialize the geolocator with a user agent
geolocator = Nominatim(user_agent="city_to_state_converter")

def get_state(city):
    try:
        location = geolocator.geocode(city + ', USA', exactly_one=True)
        if location:
            #reverse geocode to get the state
            location = geolocator.reverse((location.latitude, location.longitude), exactly_one=True, addressdetails=True)
            address = location.raw['address']
            if 'state' in address:
                return address['state']
    except GeocoderTimedOut:
        time.sleep(1)
        return get_state(city)
    except Exception as e:
        print(f"Error fetching state for {city}: {e}")
    return None

#define the project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_DIR = os.path.join(PROJECT_DIR, 'history')

#read the city names from the provided text file
input_file = os.path.join(HISTORY_DIR, 'city_names.txt')
with open(input_file, 'r') as file:
    cities = [line.strip() for line in file.readlines()]

#create a DataFrame to store the city-state mappings
city_state_mapping = []

for city in cities:
    state = get_state(city)
    if state:
        city_state_mapping.append({'City': city, 'State': state})
    else:
        print(f"State not found for city: {city}")

#convert to DataFrame
df_city_state_mapping = pd.DataFrame(city_state_mapping)

#save to CSV
output_file = os.path.join(HISTORY_DIR, 'city_state_mapping.csv')
df_city_state_mapping.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"City to state mapping saved to {output_file}")
