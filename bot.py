import os
import re
import shutil
import subprocess
from urllib.parse import urlparse
from telethon import TelegramClient, events
from mutagen import File

# Set up your MTProto API credentials (API ID and hash from Telegram's Developer Portal)
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
session_name = 'beatport_downloader'

# Regular expressions for Beatport and Crates.co URLs (Track and Album)
beatport_track_pattern = r'^https:\/\/www\.beatport\.com\/track\/[\w-]+\/\d+$'
beatport_album_pattern = r'^https:\/\/www\.beatport\.com\/release\/[\w-]+\/\d+$'
crates_track_pattern = r'^https:\/\/crates\.co\/track\/[\w-]+\/\d+$'
crates_album_pattern = r'^https:\/\/crates\.co\/release\/[\w-]+\/\d+$'

# Initialize the client
client = TelegramClient(session_name, api_id, api_hash)

# Start the client and listen for new messages
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply("Hi! I'm Beatport Track & Album Downloader using MTProto API.\n\n"
                      "Commands:\n"
                      "/download <track_url> - Download a track from Beatport or Crates.co.\n"
                      "/download_album <album_url> - Download an album from Beatport or Crates.co.\n\n"
                      "Examples:\n"
                      "/download https://www.beatport.com/track/take-me/17038421\n"
                      "/download_album https://www.beatport.com/release/the-album/123456")

# Handle single track download
@client.on(events.NewMessage(pattern='/download'))
async def download_handler(event):
    input_text = event.message.text.split(maxsplit=1)[1]
    
    # Validate the track URL against Beatport and Crates.co patterns
    is_beatport_track = re.match(beatport_track_pattern, input_text)
    is_crates_track = re.match(crates_track_pattern, input_text)

    if is_beatport_track or is_crates_track:
        if is_crates_track:
            input_text = input_text.replace('crates.co', 'www.beatport.com')

        await download_single_track(event, input_text)
    else:
        await event.reply('Invalid track link.\nPlease enter a valid track link.')

# Handle album download
@client.on(events.NewMessage(pattern='/download_album'))
async def download_album_handler(event):
    input_text = event.message.text.split(maxsplit=1)[1]
    
    # Validate the album URL against Beatport and Crates.co patterns
    is_beatport_album = re.match(beatport_album_pattern, input_text)
    is_crates_album = re.match(crates_album_pattern, input_text)

    if is_beatport_album or is_crates_album:
        if is_crates_album:
            input_text = input_text.replace('crates.co', 'www.beatport.com')

        await download_album(event, input_text)
    else:
        await event.reply('Invalid album link.\nPlease enter a valid album link.')

async def download_single_track(event, input_text):
    await event.reply("Downloading and processing the track... Please be patient.")
    url = urlparse(input_text)
    components = url.path.split('/')

    # Run the orpheus script to download the track
    os.system(f'python orpheus.py {input_text}')

    # Get the downloaded filename
    filename = os.listdir(f'downloads/{components[-1]}')[0]
    filepath = f'downloads/{components[-1]}/{filename}'

    # Extract metadata using mutagen
    audio = File(filepath, easy=True)
    artist = audio.get('artist', ['Unknown Artist'])[0]
    title = audio.get('title', ['Unknown Title'])[0]

    # Create the new filename based on artist and title
    new_filename = f"{artist} - {title}.flac"
    new_filepath = f'downloads/{components[-1]}/{new_filename}'

    # Convert the downloaded file to FLAC format using ffmpeg
    subprocess.run(['ffmpeg', '-i', filepath, new_filepath])

    # Send the renamed FLAC file to the user
    await client.send_file(event.chat_id, new_filepath)

    # Clean up the downloaded files
    shutil.rmtree(f'downloads/{components[-1]}')

async def download_album(event, input_text):
    await event.reply("Downloading and processing the album... Please be patient.")
    
    # Use the orpheus script to download the album
    os.system(f'python orpheus.py {input_text}')

    url = urlparse(input_text)
    album_id = url.path.split('/')[-1]  # Extract the album ID
    album_path = f'downloads/{album_id}'

    # Check if the album directory exists
    if not os.path.exists(album_path):
        await event.reply("Failed to download the album.")
        return

    # Iterate through all files in the album directory
    for filename in os.listdir(album_path):
        filepath = os.path.join(album_path, filename)

        # Extract metadata for each track
        audio = File(filepath, easy=True)
        artist = audio.get('artist', ['Unknown Artist'])[0]
        title = audio.get('title', ['Unknown Title'])[0]

        # Create a new filename based on artist and title
        new_filename = f"{artist} - {title}.flac"
        new_filepath = os.path.join(album_path, new_filename)

        # Convert the downloaded file to FLAC format using ffmpeg
        subprocess.run(['ffmpeg', '-i', filepath, new_filepath])

        # Send the FLAC file to the user
        await client.send_file(event.chat_id, new_filepath)

    # Clean up the downloaded album files
    shutil.rmtree(album_path)

async def main():
    # Start the Telegram client
    async with client:
        print("Client is running...")
        await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
