import requests
import json
import os
import datetime
import time
import pytz
import platform
import logging
import threading
from dotenv import load_dotenv
from tkinter import Tk, Label, Entry, Button, Toplevel

# Initialize logging
logging.basicConfig(filename='loadshedding_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

shutdown_flag = threading.Event()

def fetch_schedule(area_id, token):
    url = f"https://developer.sepush.co.za/business/2.0/area?id={area_id}"
    headers = {'Token': token}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return None

def shutdown_computer():
    countdown_window = Tk()
    countdown_window.title("Shutdown Countdown")

    countdown_label = Label(countdown_window, text="Computer will shutdown in 60 seconds. Press cancel to stop.")
    countdown_label.pack()

    def cancel_shutdown():
        shutdown_flag.set()
        countdown_window.destroy()
        print("shutdown cancelled")

    Button(countdown_window, text="Cancel Shutdown", command=cancel_shutdown).pack()

    def update_countdown(time_left):
        if time_left > 0 and not shutdown_flag.is_set():
            countdown_label.config(text=f"Computer will shutdown in {time_left} seconds. Press cancel to stop.")
            countdown_window.after(1000, update_countdown, time_left - 1)
        else:
            check_shutdown_flag()

    countdown_window.after(1000, update_countdown, 60) 
    countdown_window.mainloop()

def check_shutdown_flag():
    if not shutdown_flag.is_set():
        perform_shutdown()

def perform_shutdown():
    os_type = platform.system()
    if os_type == 'Windows':
        os.system('shutdown /s /t 10')
    elif os_type in ['Linux', 'Darwin']:
        os.system('shutdown now')
    logging.info("Shutting down PC")

def check_for_upcoming_load_shedding(schedule, sa_timezone):
    current_time = datetime.datetime.now(sa_timezone)
    for event in schedule.get('events', []):
        start_time_utc = datetime.datetime.fromisoformat(event['start'])
        end_time_utc = datetime.datetime.fromisoformat(event['end'])
        start_time = start_time_utc.astimezone(sa_timezone)
        end_time = end_time_utc.astimezone(sa_timezone)

        if start_time <= current_time < end_time:
            logging.info("Load shedding is currently in progress.")
            return True

        if current_time <= start_time < current_time + datetime.timedelta(minutes=10):
            return True

    return False

def main(api_token, area_id):
    sa_timezone = pytz.timezone('Africa/Johannesburg')
    check_interval_hours = float(os.getenv('CHECK_INTERVAL_HOURS', 2.5))
    while True:
        schedule = fetch_schedule(area_id, api_token)
        if schedule:
            logging.info(json.dumps(schedule))
            if check_for_upcoming_load_shedding(schedule, sa_timezone):
                logging.info("Load shedding within the next 10 minutes. Initiating shutdown.")
                shutdown_computer()
                break
        time.sleep(check_interval_hours * 60 * 60)

def setup_gui():
    def on_submit():
        api_token = api_token_entry.get()
        area_id = area_id_entry.get()
        with open('.env', 'w') as f:
            f.write(f'ESKOMSE_API_TOKEN={api_token}\nAREA_ID={area_id}\n')
        root.destroy()
        main(api_token, area_id)

    root = Tk()
    root.title("Load Shedding App Setup")

    Label(root, text="API Token:").pack()
    api_token_entry = Entry(root)
    api_token_entry.pack()

    Label(root, text="Area ID:").pack()
    area_id_entry = Entry(root)
    area_id_entry.pack()

    Button(root, text="Submit", command=on_submit).pack()

    root.mainloop()

if __name__ == "__main__":
    if not os.path.exists('.env'):
        setup_gui()
    else:
        load_dotenv()
        api_token = os.getenv('ESKOMSE_API_TOKEN')
        area_id = os.getenv('AREA_ID')
        main(api_token, area_id)
