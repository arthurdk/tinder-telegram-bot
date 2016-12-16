# tinder-telegram-bot
Unofficial Telegram bot for choosing the perfect Tinder match with your mates (or alone).

The bot is working both in a group conversation and in private conversation, the main feature is that person in the chat decide if the user will be liked/disliked.

## Rules

* A tie equals to a dislike

## Online demo

An instance of the bot is available on Telegram, but it's hosted on a small machine so it may be highly unavailable if lot of people are using it.

[Add the bot to a group](https://telegram.me/tindergroupbot?startgroup=groupwithtinder)

[Start a private conversation with the bot](https://telegram.me/tindergroupbot?start=yes )

## Screenshots

## Usage

If you join a group where a bot is active, remember to start a conversation with the bot in order to let it send you private message.

|            Command            |                                                       Explanation                                                       |
|:-----------------------------:|:-----------------------------------------------------------------------------------------------------------------------:|
| /set_account                  | Send this command to the bot and he will send you a private message asking to send him the private authentication token |
| /new_vote                     |                                     Begin a new vote session if one is not happening                                    |
| /matches                      |          Receives the current matches of the connected Tinder account to your private conversation with the bot         |
| /auto                         |                        Toggle automatic mode (the bot will begin new vote session automatically)                        |
| /location                     |                                        Change your location using GPS coordinates. Usage: /location 60.169101 24.932847 |
| /timeout                      | Change the duration on how many seconds the bot will wait after the first vote. Usage: /timeout <time>                  |
| /msg                          | Send a message to a match. Usage: /msg <match-id> <message> You can get the match-id by executing /matches.             |
| /poll_msgs                    | Read messages from a conversation. Usage: /poll_msgs <match-id> <nb_messages>                                           |

Note: Only one person needs to set the Tinder account in order for the bot to work. The others can just enjoy.

## Retrieving the authentication token
This part is a bit tricky, so you will need to be tech friendly.

### Automated solutions
Note:

I did not test those personally so use it at your own risks.

#### Chrome plugin
* https://chrome.google.com/webstore/detail/tinder-auth-token-grabber/pgjknpecbogfcnlfjehdidbeablebepc?hl=en-GB

#### Webapp

* https://github.com/tinderjs/tinderauth

### Manual solution

#### Android

Note: This was tested by not having the Facebook application on the phone but it could also work.
* Download a package sniffer on your phone like [Package Capture](https://play.google.com/store/apps/details?id=app.greyshirts.sslcapture&hl=en)
* Logout of your Tinder account
* Close other apps (you'll have less package in the app)
* Begin sniffing packages
* Login in Tinder
* Go to the sniffer again, stop the sniffing
* Look for the Tinder /auth request and more precisely for the facebook_token parameter, that's it you are done.


## Installation

First get your Bot Api Key from the [BotFather](https://core.telegram.org/bots#3-how-do-i-create-a-bot).

### Docker (from DockerHub)

Simply write your bot api key in the dedicated environment variable and launch the container:
```
docker run -d -e BOT_KEY="YOUR_BOT_API_KEY" --restart=always --name tinder-bot arthurdk/tinder-telegram-bot:dev
```

More info available on [this bot Docker Hub repository](https://hub.docker.com/r/arthurdk/tinder-telegram-bot/)

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
DEBUG_MODE = False
EOL
```

Launch the bot:
```
python3.5 bot_app/Bot.py
```

### In chat autocompletion

Again you will need to talk to the BotFather, edit the commands of your bot and write the following:

```
set_account - Specify your Tinder authentication token for Facebook
new_vote - Launch new vote session
matches - View already matched user
auto - Toggle automatic mode for launching vote session
location - Update the location (Example /location 60.166807 24.931737)
timeout - Set the timeout for voting session (Example /timeout 60)
msg - Send a message to a match
poll_msgs - Read messages for a specific conversation
```

And do not forget to delete your bot from the conversation and add it again.

If you are in a private conversation with the bot delete the conversation and start afresh.

#### Troubleshooting:
In case the module is not recognized:
```
export PYTHONPATH=.
```

## License
----

MIT