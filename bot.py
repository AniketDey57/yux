import os
import re
import shutil
import subprocess
from urllib.parse import urlparse
from telethon import TelegramClient, events
from mutagen import File

# Set up your MTProto API credentials (API ID and hash from Telegram's Developer Portal)
api_id = '10074048'
api_hash = 'a08b1ed3365fa3b04bcf2bcbf71aff4d'
session_name = 'beatport_downloader'

# Regular expression to match track and album URLs
track_pattern = '^https:\/\/www\.beatport\.com\/track\/[\w -]+\/\d+$'
album_pattern = '^https:\/\/www\.beatport\.com\/release\/[\w -]+\/\d+$'

# Initialize the client
client = TelegramClient(session_name, api_id, api_hash)

# Start the client and listen for new messages
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply("Hi! I'm Beatport Downloader using MTProto API.\n\n"
                      "Commands:\n"
                      "/download <track_url> - Download a track from Beatport.\n"
                      "/download <album_url> - Download an album from Beatport.\n\n"
                      "Example:\n"
                      "/download https://www.beatport.com/track/take-me/17038421\n"
                      "/download https://www.beatport.com/release/album-name/17038421")

@client.on(events.NewMessage(pattern='/download'))
async def download_handler(event):
    input_text = event.message.text.split(maxsplit=1)[1]
    
    # Check if the input is a track or an album URL
    is_track = re.match(rf'{track_pattern}', input_text)
    is_album = re.match(rf'{album_pattern}', input_text)

    if is_track or is_album:
        await event.reply("Downloading and processing the audio... Please be patient.")
        url = urlparse(input_text)
        components = url.path.split('/')

        # Run the orpheus script to download the track or album
        os.system(f'python orpheus.py {input_text}')

        # Directory where the downloads are saved
        download_dir = f'downloads/{components[-1]}'
        
        # Check if the download directory exists
        if not os.path.exists(download_dir):
            await event.reply("Download directory does not exist. Please check the download process.")
            return
        
        # List all the downloaded files (either single track or multiple tracks from an album)
        downloaded_files = os.listdir(download_dir)

        # Check for files in the album directory
        audio_files = [file for file in downloaded_files if os.path.isfile(os.path.join(download_dir, file))]

        if not audio_files:
            await event.reply("No audio files found in the album directory.")
            return

        for filename in audio_files:
            filepath = os.path.join(download_dir, filename)

            try:
                # Extract metadata using mutagen
                audio = File(filepath, easy=True)
                artist = audio.get('artist', ['Unknown Artist'])[0]
                title = audio.get('title', ['Unknown Title'])[0]

                # Create the new filename based on artist and title
                new_filename = f"{artist} - {title}.flac"
                new_filepath = os.path.join(download_dir, new_filename)

                # Convert the downloaded file to FLAC format using ffmpeg
                subprocess.run(['ffmpeg', '-i', filepath, new_filepath], check=True)

                # Send the FLAC file to the user
                await client.send_file(event.chat_id, new_filepath)
            except Exception as e:
                await event.reply(f"An error occurred while processing {filename}: {str(e)}")

        # Clean up the downloaded files after sending
        shutil.rmtree(download_dir)
        
        await event.reply("Album or track download completed.")
    else:
        await event.reply('Invalid track or album link.\nPlease enter a valid track or album link.')

async def main():
    # Start the Telegram client
    async with client:
        print("Client is running...")
        await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
