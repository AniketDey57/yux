import os
import shutil
import logging
import re
from urllib.parse import urlparse
from telethon import TelegramClient, events

# Patterns for track and album
track_pattern = '^https:\/\/www\.beatport\.com\/track\/[\w -]+\/\d+$'
album_pattern = '^https:\/\/www\.beatport\.com\/release\/[\w -]+\/\d+$'

# Your MTProto API credentials
api_id = '10074048'
api_hash = 'a08b1ed3365fa3b04bcf2bcbf71aff4d'
phone_number = '+916003585088'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize the Telegram Client
client = TelegramClient('session_name', api_id, api_hash)


@client.on(events.NewMessage(pattern='/start'))
async def send_welcome(event):
    await event.respond("🤖 Hey There\!!\, I\'m Beatport Downloader Bot ⚡ Developed by \@piklujazz\n\n🗣️ Supported Command\:\n\/download \<track\_url\> or \<album\_url\>\nTo download track or album 💫☢️", parse_mode='md')


@client.on(events.NewMessage(pattern='/download'))
async def download(event):
    input_text = event.message.message.split(' ', 1)[1]  # Extract the argument after the command

    # Check if it's a valid track or album link
    is_track = re.match(rf'{track_pattern}', input_text)
    is_album = re.match(rf'{album_pattern}', input_text)

    if is_track:
        await event.respond("⚙️ Fetching audio & uploading track...⚡")
        await download_track(input_text, event)

    elif is_album:
        await event.respond("⚙️ Fetching album & uploading...⚡")
        await download_album(input_text, event)

    else:
        await event.respond('Invalid link.\nPlease `enter` a valid track or album link')


async def download_track(input_text, event):
    # Fetching and downloading a single track
    url = urlparse(input_text)
    components = url.path.split('/')
    
    # Assuming `orpheus.py` handles downloading and saving files into a `downloads/` folder
    os.system(f'python orpheus.py {input_text}')
    
    # Fetch the downloaded file
    filename = os.listdir(f'downloads/{components[-1]}')
    file_path = f'downloads/{components[-1]}/{filename[0]}'
    
    # Send the file to the user
    if os.path.exists(file_path):
        await client.send_file(event.chat_id, file_path)
    else:
        await event.respond(f"Error: File {file_path} does not exist.")
    
    # Cleanup the download folder
    shutil.rmtree(f'downloads/{components[-1]}')


async def download_album(input_text, event):
    # Fetching and downloading a complete album
    url = urlparse(input_text)
    components = url.path.split('/')
    
    # Download all tracks in the album (orpheus.py should support album downloading)
    os.system(f'python orpheus.py {input_text}')
    
    # Get the album folder
    album_id = components[-1]
    album_folder = f'downloads/{album_id}'
    
    # Check if album folder exists
    if os.path.exists(album_folder):
        track_files = os.listdir(album_folder)
        for track in track_files:
            track_path = os.path.join(album_folder, track)
            
            # Check if the path is a file
            if os.path.isfile(track_path):
                try:
                    await client.send_file(event.chat_id, track_path)
                    await event.respond(f"📤 Sent track: {track}")
                except Exception as e:
                    await event.respond(f"Error sending track {track}: {e}")
            # If it's a directory, check for media files inside that directory
            elif os.path.isdir(track_path):
                media_files = os.listdir(track_path)  # List files inside the directory
                for media_file in media_files:
                    media_file_path = os.path.join(track_path, media_file)
                    if os.path.isfile(media_file_path):
                        try:
                            await client.send_file(event.chat_id, media_file_path)
                            await event.respond(f"📤 Sent track: {media_file} from {track}")
                        except Exception as e:
                            await event.respond(f"Error sending track {media_file}: {e}")
                    else:
                        await event.respond(f"Error: {media_file_path} is not a valid file.")
    
    # Cleanup the downloaded album folder after sending the files
    shutil.rmtree(album_folder)


async def main():
    # Start the client and login if necessary
    await client.start(phone=phone_number)
    print("Bot is up and running...")
    
    # Keep the client running until manually stopped
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
