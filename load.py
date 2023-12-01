import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

def fetch_schedule(area_id, token):
    url = f"https://developer.sepush.co.za/business/2.0/area?id={area_id}"
    headers = {'Token': token}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

# Add your token here
token = os.getenv('ESKOMSE_API_TOKEN')

# Determine your area id, and add it here
area_id = 'eskdo-16-seavistakougaeasterncape'

schedule = fetch_schedule(area_id, token)
if schedule:
    print(json.dumps(schedule, indent=4))
else:
    print("No schedule data returned or an error occurred")
