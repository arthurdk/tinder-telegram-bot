# tinder-telegram-bot
Unofficial Telegram bot for choosing the perfect Tinder match with your mates (or alone).

The bot is working both in a group conversation and in private conversation, the main feature is that person in the chat decide if the user will be liked/disliked.

## Rules

* A tie equals to a dislike
## Online demo

An instance of the bot is available on Telegram, but it's hosted on a small machine so it may be highly unavailable if lot of people are using it.

[Add the bot to a group](https://telegram.me/tindergroupbot?startgroup=groupwithtinder)

[Start a private conversation with the bot](https://telegram.me/tindergroupbot?start=yes )

## Usage

If you join a group where a bot is active, remember to start a conversation with the bot in order to let it send you private message.

|            Command            |                                                       Explanation                                                       |
|:-----------------------------:|:-----------------------------------------------------------------------------------------------------------------------:|
| /set_account                  | Send this command to the bot and he will send you a private message asking to send him the private authentication token |
| /new_vote                     |                                     Begin a new vote session if one is not happening                                    |
| /matches                      |          Receives the current matches of the connected Tinder account to your private conversation with the bot         |
| /auto                         |                        Toggle automatic mode (the bot will begin new vote session automatically)                        |
| /location,60.169101 24.932847 |                                        Change your location using GPS coordinates                                       |
| /timeout 50                   | Change the duration on how many seconds the bot will wait after the first vote                                          |

Note: Only one person needs to set the Tinder account in order for the bot to work. The others can just enjoy.

## Installation

### Docker (from DockerHub)

Simply write your bot api key in the dedicated environment variable and launch the container:
```
docker run -d -e BOT_KEY="YOUR_BOT_API_KEY" --restart=always --name tinder-bot arthurdk/tinder-telegram-bot:dev
```


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

### Python (Dev)

Note: This was tested on Ubuntu 16.04 based distribution only.

Install Pynder (Tinder client)
```
git clone https://github.com/charliewolf/pynder.git \
&& cd pynder && python setup.py install
```

Install dependencies:
```
pip3 install -r requirements.txt
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