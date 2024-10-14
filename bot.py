import os
import re
import shutil
from urllib.parse import urlparse
from telethon import TelegramClient, events
from mutagen.mp4 import MP4, MP4StreamInfoError
from mutagen import MutagenError

# Set up your MTProto API credentials
api_id = '8349121'
api_hash = '9709d9b8c6c1aa3dd50107f97bb9aba6'
session_name = 'beatport_downloader'

track_pattern = '^https:\/\/www\.beatport\.com\/track\/[\w -]+\/\d+$'
album_pattern = '^https:\/\/www\.beatport\.com\/release\/[\w -]+\/\d+$'

client = TelegramClient(session_name, api_id, api_hash)

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
    
        is_track = re.match(rf'{track_pattern}', input_text)
        is_album = re.match(rf'{album_pattern}', input_text)

        if is_track or is_album:
            await event.reply("Downloading and processing the audio... Please be patient.")
            url = urlparse(input_text)
            components = url.path.split('/')

            download_status = os.system(f'python orpheus.py {input_text}')

            if download_status != 0:
                await event.reply("Error: Download failed. Please check the URL or try again later.")
                return

            download_dir = f'downloads/{components[-1]}'

            if not os.path.exists(download_dir):
                await event.reply(f"Error: Download directory not found: {download_dir}")
                return

            for root, dirs, files in os.walk(download_dir):
                for filename in files:
                    filepath = os.path.join(root, filename)

                    try:
                        # Attempt to tag the file regardless of its format
                        tag_file(filepath)
                        await client.send_file(event.chat_id, filepath)
                    except Exception as e:
                        # Log the error and continue with the next file
                        print(f"Error processing {filename}: {str(e)}")
                        continue

            shutil.rmtree(download_dir)
            await event.reply("Album or track download completed.")
        else:
            await event.reply('Invalid track or album link.\nPlease enter a valid track or album link.')
    except Exception as e:
        await event.reply(f"An error occurred: {str(e)}")

def tag_file(file_path):
    try:
        # Attempt to read and tag the file using Mutagen
        tagger = MP4(file_path)
        tagger.save()
        print(f"Successfully tagged {file_path}")
    except MP4StreamInfoError:
        print(f"Warning: {file_path} is not a valid MP4 file. Skipping tagging.")
    except MutagenError as e:
        print(f"Error processing {file_path}: {str(e)}")

async def main():
    async with client:
        print("Client is running...")
        await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
