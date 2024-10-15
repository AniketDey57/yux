import os
import shutil
import logging
import re
import zipfile
from urllib.parse import urlparse
from aiogram import Bot, Dispatcher, executor, types

# Patterns for track and album
track_pattern = '^https:\/\/www\.beatport\.com\/track\/[\w -]+\/\d+$'
album_pattern = '^https:\/\/www\.beatport\.com\/release\/[\w -]+\/\d+$'

API_TOKEN = '6325844279:AAFpFPp-M9rzG5nh5ZDxNTA0GuMUBCkk7oI'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer("🤖 Hey There\!!\, I\'m Beatport Downloader Bot ⚡ Developed by \@piklujazz\n\n🗣️ Supported Command\:\n\/download \<track\_url\> or \<album\_url\>\nTo download track or album 💫☢️", parse_mode=types.ParseMode.MARKDOWN_V2)


@dp.message_handler(commands=['download'])
async def download(message: types.Message):
    input_text = message.get_args()

    # Check if it's a valid track or album link
    is_track = re.match(rf'{track_pattern}', input_text)
    is_album = re.match(rf'{album_pattern}', input_text)

    if is_track:
        await message.answer("⚙️ Fetching audio & uploading track...⚡")
        await download_track(input_text, message)

    elif is_album:
        await message.answer("⚙️ Fetching album & uploading...⚡")
        await download_album(input_text, message)

    else:
        await message.answer('Invalid link.\nPlease `enter` a valid track or album link')


async def download_track(input_text, message):
    # Fetching and downloading a single track
    url = urlparse(input_text)
    components = url.path.split('/')
    
    # Assuming `orpheus.py` handles downloading and saving files into a `downloads/` folder
    os.system(f'python orpheus.py {input_text}')
    
    # Fetch the downloaded file
    filename = os.listdir(f'downloads/{components[-1]}')
    file = open(f'downloads/{components[-1]}/{filename[0]}', 'rb')
    
    # Send the file to the user
    await message.answer_audio(file)
    
    # Cleanup the download folder
    shutil.rmtree(f'downloads/{components[-1]}')


async def download_album(input_text, message):
    # Fetching and downloading a complete album
    url = urlparse(input_text)
    components = url.path.split('/')
    
    # Download all tracks in the album (orpheus.py should support album downloading)
    os.system(f'python orpheus.py {input_text}')
    
    # Create a ZIP file from the downloaded album folder
    album_id = components[-1]
    album_folder = f'downloads/{album_id}'
    zip_filename = f'{album_id}.zip'
    zip_path = f'downloads/{zip_filename}'
    
    # Compress the album folder
    with zipfile.ZipFile(zip_path, 'w') as album_zip:
        for folder_name, subfolders, filenames in os.walk(album_folder):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                album_zip.write(file_path, os.path.relpath(file_path, album_folder))
    
    # Send the ZIP file to the user
    zip_file = open(zip_path, 'rb')
    await message.answer_document(zip_file)
    
    # Cleanup the downloaded album folder and ZIP file
    shutil.rmtree(album_folder)
    os.remove(zip_path)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
