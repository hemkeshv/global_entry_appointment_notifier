import requests
import json
from datetime import datetime
import time

# Set chat_id (User ID) and api_key of your telegram bot from this tutorial: https://hackernoon.com/from-python-to-telegram-build-your-own-notification-system
chat_id = "XYZ"
api_key = "ABC"

# Set your current interview date in the format "Month DD, YYYY"
current_interview_date_str = "September 20, 2024"

# Set your enrollment location id from the README file
enrollment_location_id = "5446"

GOES_URL_FORMAT = 'https://ttp.cbp.dhs.gov/schedulerapi/slots?orderBy=soonest&limit=3&locationId={0}&minimum=1'

def send_telegram_message(message: str,
                          chat_id: str,
                          api_key: str,
                          proxy_username: str = None,
                          proxy_password: str = None,
                          proxy_url: str = None):
    headers = {'Content-Type': 'application/json',
               'Proxy-Authorization': 'Basic base64'}
    data_dict = {'chat_id': chat_id,
                 'text': message,
                 'parse_mode': 'HTML',
                 'disable_notification': True}
    data = json.dumps(data_dict)
    url = f'https://api.telegram.org/bot{api_key}/sendMessage'
    response = requests.post(url,
                             data=data,
                             headers=headers,
                             proxies=None,
                             verify=False)
    return response
        
def get_dates():
    try:
        # obtain the json from the web url
        response = requests.get(GOES_URL_FORMAT.format(enrollment_location_id))
        data = response.json()
    except requests.exceptions.RequestException as e:
        send_telegram_message(f"RequestException encountered: {e}", chat_id, api_key)
        return
    except requests.exceptions.JSONDecodeError:
        send_telegram_message("JSONDecodeError encountered. Exiting the function.", chat_id, api_key)
        return
    
    if response.status_code != 200:
        send_telegram_message(f"Error: Status code is {response.status_code}", chat_id, api_key)
        raise Exception("Error Status Code is not 200")
        return
    
    # parse the json
    current_apt = datetime.strptime(current_interview_date_str, '%B %d, %Y')
    dates = []
    for o in data:
        if o['active']:
            dt = o['startTimestamp'] #2024-06-20T15:30
            dtp = datetime.strptime(dt, '%Y-%m-%dT%H:%M')
            if current_apt > dtp:
                dates.append(dtp.strftime('%A, %B %d @ %I:%M%p'))
    
    return dates

def main():
    while True:
        dates = get_dates()
        if dates:
            message = "Available dates:\n" + "\n".join(dates)
            send_telegram_message(message, chat_id, api_key)
        
        # Sleep for 60 seconds (1 minute)
        time.sleep(60)
   
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        print("Something went wrong in the program. Please check")
        raise