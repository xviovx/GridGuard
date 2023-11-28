import requests

def fetch_schedule(area_id, token):
    url = f"https://developer.sepush.co.za/business/2.0/area?id={area_id}&test=current"
    headers = {'Token': token}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

# Replace 'YOUR_API_TOKEN' with your actual EskomSePush API token
token = 'F15F0D58-67074B31-B844CDA5-CF4E25CC'

# Using the area ID for Gallo Manor Ext 2 (16)
area_id = 'eskde-16-gallomanorext2cityofjohannesburggauteng'

schedule = fetch_schedule(area_id, token)
if schedule:
    print(schedule)
else:
    print("No schedule data returned or an error occurred")
