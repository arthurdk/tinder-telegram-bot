# tinder-telegram-bot
Unofficial Telegram bot for choosing the perfect Tinder match with your mates (or alone).



## Installation


### Docker (build)

First, retrieve sources:

```
git clone https://github.com/arthurdk/tinder-telegram-bot.git && cd tinder-telegram-bot
```

Then, build the image:
```
docker build -f docker/Dockerfile -t <your-repo-name>/tinder-telegram-bot:dev .
```

Finally, write your bot api key in the dedicated environment variable and launch the container:

```
docker run -d -e BOT_KEY="YOUR_BOT_API_KEY" --restart=always --name tinder-bot <your-repo-name>/tinder-telegram-bot:dev
```

### Python

Install Pynder (Tinder client)
```
git clone https://github.com/charliewolf/pynder.git \
&& cd pynder && python setup.py install
```

Install dependencies:
```
pip install -r $ROOT_FOLDER/requirements.txt
```


Create file containing the bot api key.
```
cat > bot_app/settings.py << EOL
KEY = "YOUR_KEY_HERE"
DB_NAME = 'tinderbot.sqlite3'
EOL
```

Launch the bot:
```
python3.5 bot_app/Bot.py
```

#### Troubleshooting:
In case the module is not recognized:
```
export PYTHONPATH=.
```