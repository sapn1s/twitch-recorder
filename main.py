import configparser
import requests
import sys
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


async def wait_for_user_input(stop_event):
    """Wait for user input and then set the stop_event."""
    input("Press Enter to stop the recording...")
    await stop_event.set()


async def record_stream(stream_url, filename, stop_event):
    """Record the stream and listen for the stop event."""
    ffmpeg_cmd = [
        'ffmpeg', '-i', stream_url,
        '-loglevel', 'error',
        '-c:v', 'libx264', '-preset', 'faster', '-crf', config['OUTPUT']['quality'],
        '-c:a', 'aac', '-b:a', '128k',
        '-bsf:a', 'aac_adtstoasc',
        f'{filename}'
    ]
    #can be converted to MP4 using the following command (reduces the file size as well)
    #ffmpeg -i input.ts -c:v copy -c:a copy output.mp4

    process = await asyncio.create_subprocess_exec(*ffmpeg_cmd)
    print("Streaming into", filename)

    process_task = asyncio.create_task(process.communicate())
    stop_event_task = asyncio.create_task(stop_event.wait())

    # Wait for the process to complete or for stop_event to be set
    done, pending = await asyncio.wait(
        [process_task, stop_event_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    # If the stop_event was set, we'll terminate the process
    if stop_event.is_set():
        print("Terminating...")
        process.terminate()
        print("Waiting...")
        await process.wait()
        print("Done...")


async def main():
    username = config["STREAMERS"]["username"]
    wait_time = 1

    

    while True:
        try:
            streaming = False
            while not streaming:
                print(f"Checking if {username} is online...")
                token = get_twitch_token(
                    config['TWITCH']['CLIENT_ID'], config['TWITCH']['CLIENT_SECRET'])
                streaming = check_streaming(token, username)
                if (streaming):
                    break
                await asyncio.sleep(120)
            # Online
            print(f"{username} is online!")
            stop_event = asyncio.Event()
            input_task = asyncio.create_task(wait_for_user_input(stop_event))
            stream_url = get_stream_url(username)
            print("Stream URL:", stream_url)
            if (stream_url):
                # record stream
                filename = f"{output_folder}/{username}_{datetime.now().strftime('%d-%m-%y_%H-%M')}.ts"
                await record_stream(stream_url, filename, stop_event)
                if stop_event.is_set():
                    break

        except Exception as e:
            print("Error occured:", e)
            traceback.print_exc()
            print(f"Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            wait_time = min(wait_time * 2, MAX_WAIT_TIME)
        finally:
            # Cancel the input task if it's still running
            input_task.cancel()


def check_streaming(token, username):
    headers = {
        'Client-ID': config['TWITCH']['CLIENT_ID'],
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(
        f'https://api.twitch.tv/helix/users?login={username}', headers=headers)
    response_data = response.json()
    user_id = response_data['data'][0]['id']

    # Then, check if the user is currently streaming
    response = requests.get(
        f'https://api.twitch.tv/helix/streams?user_id={user_id}', headers=headers)
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
