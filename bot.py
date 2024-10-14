import os
import shutil
import logging
import re
from urllib.parse import urlparse
from aiogram import Bot, Dispatcher, executor, types
pattern = '^https:\/\/www\.beatport\.com\/track\/[\w -]+\/\d+$'

API_TOKEN = '5930894396:AAH2XUH0P3mlVBrl2OIZy-kvqi00H5WPldY'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer("🤖 Hey There\!!\, I\'m Beatport Downloader Bot ⚡ Developed by \@piklujazz\n\n🗣️ Supported Command\:\n\/download \<track\_url\>\nTo download track\, 💫☢️", parse_mode=types.ParseMode.MARKDOWN_V2)



@dp.message_handler(commands=['download'])
async def download(message: types.Message):
    input_text = message.get_args()
    is_valid = re.match(rf'{pattern}', input_text)
    if is_valid:
        await message.answer("⚙️ fetching audio & uploading...⚡")
        url = urlparse(input_text)
        components = url.path.split('/')
        os.system(f'python orpheus.py {input_text}')
        filename = os.listdir(f'downloads/{components[-1]}')
        file = open(f'downloads/{components[-1]}/{filename[0]}', 'rb')
        await message.answer_audio(file)
        shutil.rmtree(f'downloads/{components[-1]}')
    else:
        await message.answer('Invalid track link.\nPlease `enter` valid track link')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
