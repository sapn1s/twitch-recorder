# Twitch Stream Recorder

A Python script to automatically detect when a Twitch user goes online and then records their stream using Streamlink.

## Requirements

- Python 3+
- Streamlink

## Configuration

Before you begin, make sure to set up the `settings.ini` file with the required Twitch credentials. Here's a sample:

```ini
[TWITCH]
CLIENT_ID = your_client_id
CLIENT_SECRET = your_client_secret
[STREAMERS]
username = twitch_username
```

## Installation

1. Install the required Python packages:
```
pip install -r requirements.txt
```

2. Install and set up Streamlink:
- **For Windows**: If you've installed `streamlink` using `pip`, you might need to add its installation path to the system's PATH variable. Commonly, this would be in a directory like `C:\Users\<Username>\AppData\Roaming\Python\Python<version>\Scripts`. Add this to your PATH.
  
- **For Linux**: If you've installed `streamlink` with `pip`, it should typically be available globally. If not, you might need to add it to your PATH. This can often be done with:
  ```
  echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
  source ~/.bashrc
  ```

3. Run the script:
```
python main.py
```

## How It Works

1. The script checks if the specified Twitch user (from `settings.ini`) is online every 2 minutes.
2. Once the user is detected online, it fetches the best stream URL.
3. It then uses Streamlink to record the stream.
4. The recorded stream is saved in the `outputs` directory with the format: `username_DD-MM-YY_HH-MM.mp4`.
5. If any errors occur, it retries with an exponential backoff strategy.