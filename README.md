# Twitch Stream Recorder

A Python script to automatically detect when a Twitch user goes online and then records their stream.

## Requirements

- Python 3+
- Streamlink
- ffmpeg

## Configuration

Before you begin, make sure to set up the `settings.ini` file with the required Twitch credentials. Here's a sample:

  ```ini
  [TWITCH]
  CLIENT_ID = your_client_id
  CLIENT_SECRET = your_client_secret
  [STREAMERS]
  username = twitch_username
  [OUTPUT]
  quality=28
  ```

## Installation

1. Install the required Python packages:
  ```
  pip install -r requirements.txt
  ```

2. Install and set up FFmpeg:
- **For Windows**: Download FFmpeg from its official website and add the bin directory to your system's PATH variable.
- **For Linux**: You can install FFmpeg using the package manager for your distribution, for example:
  ```
  sudo apt-get install ffmpeg
  ```

3. Run the script:
  ```
  python main.py
  ```

## How It Works

1. The script checks if the specified Twitch user (from `settings.ini`) is online every 2 minutes.
2. Once the user is detected online, it fetches the best stream URL.
3. It then uses FFmpeg to record the stream. The stream is saved as a `.ts` file format because it's more resilient to interruptions than other formats.
4. The recorded stream is saved in the `outputs` directory with the format: `username_DD-MM-YY_HH-MM.ts`.
5. If any errors occur, it retries with an exponential backoff strategy.

## Quality Settings

The quality of the recorded stream can be adjusted in the `settings.ini` file under the `[OUTPUT]` section by setting the `quality` parameter. This corresponds to the CRF (Constant Rate Factor) value used by the x264 encoder. The value can range from 0-51:

- CRF 0: Lossless compression (largest file size).
- CRF 23: Default value in FFmpeg, a balance between file size and quality.
- CRF 51: Worst quality but smallest file size.

The default value in this script is set to 28, offering a good trade-off between file size and video quality.
