<!-- ABOUT Beatport Bot -->
## About Bot

Beatport Bot is a music track downloader bot written in Python which allows download track from Telegram Chat.


<!-- GETTING STARTED -->
## Getting Started

Follow these steps to get a local copy of Beatport Telegram Bot up and running:

### Prerequisites

* Python 3.7+ (due to the requirement of dataclasses), though Python 3.9 is highly recommended

### Installation

1. Clone the repo
    ```shell
    git clone https://github.com/smartpal93/beatport-telegram-bot.git && cd beatport-telegram-bot
    ```
2. Install all requirements
   ```shell
   pip install -r requirements.txt
   ```
3. Run the command to add Beatport Module
   ```shell
   git clone https://github.com/Dniel97/orpheusdl-beatport.git modules/beatport
   ```
4. Run the command to generate settings file
   ```shell
   python3 orpheus.py settings refresh
   ```
5. Enter Beatport credentials in `config/settings.json` at bottom of file

6. Enter Telegram Bot Token in `bot.py`

<!-- USAGE EXAMPLES -->
## Usage

Just call `python3 bot.py` to activate bot:
```Bot
/help to get help
```

Download track:
```Bot
/download <track url>
```

<!-- CONFIGURATION -->
## Configuration

Two things need to be configured.

### Beatport (config/settings.json)
```json5
"beatport": {
            "username": "YOUR_USERNAME",
            "password": "YOUR_PASSWORD"
        }
```
### Bot (bot.py)
```
API_TOKEN = 'YOUR_BOT_TOKEN'
```
