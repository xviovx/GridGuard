import requests
import json
from dotenv import load_dotenv
import os
import datetime
import time
import pytz

def fetch_schedule(area_id, token):
    url = f"https://developer.sepush.co.za/business/2.0/area?id={area_id}"
    headers = {'Token': token}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

def shutdown_computer():
    # Windows
    os.system('shutdown /s /t 10')
    print("Shutting down PC")

    # For Unix/Linux/MacOS, uncomment the following line:
    # os.system('shutdown now')

def check_for_upcoming_load_shedding(schedule):
    sa_timezone = pytz.timezone('Africa/Johannesburg')
    current_time = datetime.datetime.now(sa_timezone)
    for event in schedule.get('events', []):
        start_time_utc = datetime.datetime.fromisoformat(event['start'])
        end_time_utc = datetime.datetime.fromisoformat(event['end'])
        start_time = start_time_utc.astimezone(sa_timezone)
        end_time = end_time_utc.astimezone(sa_timezone)
        
        # Check if load shedding is currently in progress
        if start_time <= current_time < end_time:
            print("Load shedding is currently in progress.")
            return True  # Change here to return True

        # Check if load shedding will start within the next 10 minutes
        if current_time <= start_time < current_time + datetime.timedelta(minutes=10):
            return True

    return False


load_dotenv()

# Add your token here
token = os.getenv('ESKOMSE_API_TOKEN')

# Determine your area id, and add it here
area_id = 'eskdo-16-seavistakougaeasterncape'

# Checks schedule every two hours to save API requests (fetching schedule uses 5)
check_interval_hours = 2.5

while True:
    schedule = fetch_schedule(area_id, token)
    if schedule:
        print(json.dumps(schedule, indent=4))
        if check_for_upcoming_load_shedding(schedule):
            print("Load shedding within the next 10 minutes. Initiating shutdown.")
            shutdown_computer()
            break
    time.sleep(check_interval_hours * 60 * 60)  # 2.5 hours
