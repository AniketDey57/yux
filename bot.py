import os
import shutil
import logging
import re
from urllib.parse import urlparse
from aiogram import Bot, Dispatcher, executor, types
import subprocess

pattern = '^https:\/\/www\.beatport\.com\/track\/[\w -]+\/\d+$'

API_TOKEN = 'YOUR_BOT_TOKEN'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer("Hi\!\, I\'m Beatport Track Downloader Bot\!\nCreated by \@shahnawazkadari\n\nSupported command\:\n\/download \<track\_url\>\nTo download track\.\n\nEx\:\n\n`\/download https\:\/\/www\.beatport\.com\/track\/take\-me\/17038421`\n\nNote\: I currently support single track downloading\.", parse_mode=types.ParseMode.MARKDOWN_V2)


@dp.message_handler(commands=['download'])
async def download(message: types.Message):
    input_text = message.get_args()
    is_valid = re.match(rf'{pattern}', input_text)
    if is_valid:
        await message.answer("Sending audio file..... Be patient.")
        url = urlparse(input_text)
        components = url.path.split('/')
        
        # Run the orpheus script to download the track
        os.system(f'python orpheus.py {input_text}')
        
        # Get the downloaded filename
        filename = os.listdir(f'downloads/{components[-1]}')[0]
        filepath = f'downloads/{components[-1]}/{filename}'
        
        # Convert the downloaded file to FLAC format using ffmpeg
        flac_file = f'downloads/{components[-1]}/{os.path.splitext(filename)[0]}.flac'
        subprocess.run(['ffmpeg', '-i', filepath, flac_file])
        
        # Send the FLAC file
        with open(flac_file, 'rb') as file:
            await message.answer_audio(file)
        
        # Clean up the downloaded files
        shutil.rmtree(f'downloads/{components[-1]}')
    else:
        await message.answer('Invalid track link.\nPlease `enter` valid track link')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
