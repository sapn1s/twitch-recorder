import configparser
import requests
import time
import os
import streamlink
from datetime import datetime
import asyncio
import traceback
from Functions.getTwitchToken import get_twitch_token
config = configparser.ConfigParser()
config.read('settings.ini')

output_folder = './outputs'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

MAX_WAIT_TIME = 300 

async def main():
    username = config["STREAMERS"]["username"]
    wait_time = 1
    while True:
        try:
            streaming = False
            while not streaming:
                print(f"Checking if {username} is online...")
                token = get_twitch_token(config['TWITCH']['CLIENT_ID'], config['TWITCH']['CLIENT_SECRET'])
                streaming = check_streaming(token, username)
                if(streaming):
                    break
                await asyncio.sleep(120)
            #Online
            print(f"{username} is online!")
            stream_url = get_stream_url(username)
            print("Stream URL:", stream_url)
            if(stream_url):
                #record stream
                filename = f"{output_folder}/{username}_{datetime.now().strftime('%d-%m-%y_%H-%M')}.mp4"
                streamlink_cmd = ['streamlink', stream_url, 'best', '-o', filename]
                process = await asyncio.create_subprocess_exec(*streamlink_cmd)
                print("Streaming into", filename)
                await process.communicate()
                #Stream ended or any other issue
        except Exception as e:
            print("Error occured:", e)
            traceback.print_exc()
            print(f"Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            wait_time = min(wait_time * 2, MAX_WAIT_TIME)



def check_streaming(token, username):
    headers = {
    'Client-ID': config['TWITCH']['CLIENT_ID'],
    'Authorization': f'Bearer {token}'
    }
    response = requests.get(f'https://api.twitch.tv/helix/users?login={username}', headers=headers)
    response_data = response.json()
    user_id = response_data['data'][0]['id']

    # Then, check if the user is currently streaming
    response = requests.get(f'https://api.twitch.tv/helix/streams?user_id={user_id}', headers=headers)
    response_data = response.json()

    if response_data['data']:
        return True
    else:
        return False

def get_stream_url(username):
    url = f"https://www.twitch.tv/{username}"
    streams = streamlink.streams(url)
    if 'best' in streams:
        best_stream = streams['best']
        m3u8_url = best_stream.url
        return m3u8_url
    else:
        print("No available streams found.")
        return False


if __name__ == '__main__':
    asyncio.run(main())