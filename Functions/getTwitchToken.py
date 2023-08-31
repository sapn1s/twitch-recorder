from datetime import datetime, timedelta
import json
import requests
TOKEN_FILE = 'token_data.json'

def get_twitch_token(CLIENT_ID, CLIENT_SECRET):
    # Load token from file if it exists
    try:
        with open(TOKEN_FILE, 'r') as file:
            data = json.load(file)
            token = data['access_token']
            expiry = datetime.strptime(data['expiry'], "%Y-%m-%d %H:%M:%S")
            
            # Check if token is still valid
            if expiry > datetime.now():
                return token
    except (FileNotFoundError, KeyError, ValueError):
        pass
    
    # If we're here, we need a new token
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    
    response = requests.post(url, params=params)
    data = response.json()
    
    if 'access_token' in data:
        token = data['access_token']
        expires_in = data['expires_in']
        expiry_date = (datetime.now() + timedelta(seconds=expires_in)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Save token and expiry_date to file
        with open(TOKEN_FILE, 'w') as file:
            json.dump({"access_token": token, "expiry": expiry_date}, file)
        
        return token
    else:
        # Handle the error based on your requirements, raising an exception for now
        raise Exception("Failed to obtain Twitch OAuth token!")