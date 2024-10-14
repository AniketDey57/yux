import os
import re
import shutil
import subprocess
from urllib.parse import urlparse
from telethon import TelegramClient, events
from mutagen import File, MutagenError
from mutagen.mp4 import MP4, MP4StreamInfoError
import mimetypes

# Set up your MTProto API credentials (API ID and hash from Telegram's Developer Portal)
api_id = '8349121'
api_hash = '9709d9b8c6c1aa3dd50107f97bb9aba6'
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
    try:
        input_text = event.message.text.split(maxsplit=1)[1]
    
        # Check if the input is a track or an album URL
        is_track = re.match(rf'{track_pattern}', input_text)
        is_album = re.match(rf'{album_pattern}', input_text)

        if is_track or is_album:
            await event.reply("Downloading and processing the audio... Please be patient.")
            url = urlparse(input_text)
            components = url.path.split('/')

            # Run the orpheus script to download the track or album
            download_status = os.system(f'python orpheus.py {input_text}')

            # Check if the download was successful
            if download_status != 0:
                await event.reply("Error: Download failed. Please check the URL or try again later.")
                return

            # Directory where the downloads are saved
            download_dir = f'downloads/{components[-1]}'

            # Check if the directory exists before proceeding
            if not os.path.exists(download_dir):
                await event.reply(f"Error: Download directory not found: {download_dir}")
                return

            # Use os.walk to recursively check all directories and subdirectories for files
            for root, dirs, files in os.walk(download_dir):
                for filename in files:
                    filepath = os.path.join(root, filename)

                    # Only process files with supported audio extensions
                    if not filename.lower().endswith(('.mp3', '.flac', '.wav', '.m4a')):
                        await event.reply(f"Skipping unsupported file format: {filename}")
                        continue

                    try:
                        # Tagging the file by checking its type and embedding metadata
                        tag_file(filepath)

                        # Send the processed audio file back to the user
                        await client.send_file(event.chat_id, filepath)
                    except MutagenError as e:
                        await event.reply(f"Error processing file {filename}: {str(e)}")
                        continue

            # Clean up the downloaded files after sending
            shutil.rmtree(download_dir)
            
            await event.reply("Album or track download completed.")
        else:
            await event.reply('Invalid track or album link.\nPlease enter a valid track or album link.')
    except Exception as e:
        await event.reply(f"An error occurred: {str(e)}")

# Function to handle file tagging and embedding metadata
def tag_file(file_path, cover_art=None):
    try:
        # Check if the file is an MP4 file by its MIME type
        mime_type, _ = mimetypes.guess_type(file_path)

        # Only proceed if the MIME type is 'video/mp4' or 'audio/mp4'
        if mime_type in ['video/mp4', 'audio/mp4']:
            # Attempt to tag the file using EasyMP4
            tagger = MP4(file_path)

            # Optionally embed cover art (if provided)
            if cover_art:
                with open(cover_art, 'rb') as cover:
                    tagger['covr'] = [MP4Cover(cover.read())]
            
            tagger.save()

            print(f"Successfully tagged {file_path}")

        else:
            print(f"Skipping file: {file_path} (not an MP4 file)")

    except MP4StreamInfoError:
        print(f"Error: {file_path} is not a valid MP4 file.")
    except MutagenError as e:
        print(f"Error processing {file_path}: {str(e)}")

async def main():
    # Start the Telegram client
    async with client:
        print("Client is running...")
        await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
