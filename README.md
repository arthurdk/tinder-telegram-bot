# tinder-telegram-bot
Unofficial Telegram bot for choosing the perfect Tinder match with your mates (or alone).

The bot is working both in a group conversation and in private conversation.

Features:

* Vote with your friends to decide if the user will be liked/disliked.
* Chat with matches
* Use Tinder without having the app installed ;)
* Move around the world easily


The bot is also able to try to determinate the **likeliness** for the group to like or not an user. This `prediction` feature is based on picture analysis and make use of neural network that learn on **YOUR** votes (if the parameter is turned on).

**Note**: Please remember that predictions are here to make the bot more alive and funny to use, but are not to be taken seriously as this is not exact science at all (you would need to have thousands of picture for the bot to start to be accurate accordingly to **YOUR** previous votes.

**Note 2**: For now prediction are made based on our choices.

**Note 3**: The prediction code is not yet included in the bot :-( 

## Rules

* A tie will result in a dislike

## Table of contents

- [tinder-telegram-bot](#tinder-telegram-bot)
  - [Rules](#rules)
  - [Online demo](#online-demo)
  - [Screenshots](#screenshots)
  - [Usage](#usage)
  - [Retrieving the authentication token](#retrieving-the-authentication-token)
    - [Automated solutions](#automated-solutions)
      - [Chrome plugin](#chrome-plugin)
      - [Web app](#web-app)
    - [Manual solution](#manual-solution)
      - [Android](#android)
  - [Installation](#installation)
    - [Docker (from DockerHub)](#docker-from-dockerhub)
      - [Docker environment variable](#docker-environment-variable)
    - [Docker (build)](#docker-build)
    - [Python (Dev)](#python-dev)
      - [Troubleshooting:](#troubleshooting)
    - [In chat autocompletion](#in-chat-autocompletion)
  - [Contributing](#contributing)
  - [License](#license)


## Online demo

An instance of the bot is available on Telegram, but it's hosted on a small machine so it may be highly unavailable if lot of people are using it or just rebooted due to updates (so you'll have to login again).

**WARNING** Anyway I don't advise you to trust any instance of this bot as your token will be available in plain text to any of those bot owner, so they will basically be able to login on Tinder with your account.

[Add the bot to a group](https://telegram.me/matchpartybot?startgroup=groupwithtinder)

[Start a private conversation with the bot](https://telegram.me/matchpartybot?start=yes )

## Screenshots

If you are reading this text on DockerHub go to the [arthurdk/tinder-telegram-bot](https://github.com/arthurdk/tinder-telegram-bot) GitHub repository to see screenshots.

* Connect your account and start voting

<img src="http://imgur.com/BkHSqdq.png"  data-canonical-src="http://imgur.com/BkHSqdq.png" width="300" height="500" />

* View more pictures

<img src="http://imgur.com/CR0zq42.png"  data-canonical-src="http://imgur.com/CR0zq42.png" width="300" height="500" />

* The bot speaks its mind

<img src="http://imgur.com/AU1wCxt.png"  data-canonical-src="http://imgur.com/AU1wCxt.png" width="300" height="500" />

* And many more features..

## Usage

If you join a group where a bot is active, remember to start a conversation with the bot in order to let it send you private message.


_Logging in with your Tinder account:_

1. Use /set_account
2. The bot will ask you for your facebook token. Just send it plain.
3. Use `/unlink` when your Tinder account unlinked from the bot

_Searching for matches:_

 * Use /location to set your location.
 * Use /new_vote to start voting for a new stranger. Voting time can be set with /timeout.
 * Use /auto to toggle between automatic and manual mode. In automatic mode, a new vote will be started after the current one is finished.
 * Use /matches to list your matches in your private chat.
 * A draw is always a no.

_Chatting with matches:_

 * Use /matches to list your matches in your private chat. Every match has an id. It can change if old matches unmatch.
 * Use /msg to send a message to a match, and /poll_msgs to get the chat history with a match.
 * The owner may use /unblock to remove the sending/polling blocade once. See /help_settings for more information.

_Configuration:_

 * Use /list_settings to list all settings and their values.
 * Use /set_setting to change a setting.This command can only be executed by the account owner.
 * Use /help_settings to get an explanation of the settings.

_Ranges:_

Ranges are a comma-separated lists of numbers or number pairs. Number pairs are separated by a hyphen. Use no spaces in your range definition.

_Other:_

 * Use /about to learn more about me.

Note: Only one person needs to set the Tinder account in order for the bot to work. The others can just enjoy.

## Retrieving the authentication token
This part is a bit tricky, so you will need to be tech friendly.

### Automated solutions
**Note**: I did not test those personally so use them at your own risks.

#### Chrome plugin
* https://chrome.google.com/webstore/detail/tinder-auth-token-grabber/pgjknpecbogfcnlfjehdidbeablebepc?hl=en-GB

#### Web app

* https://github.com/tinderjs/tinderauth

### Manual solution

#### Android

**Note**: This was tested by not having the Facebook application on the phone but it could also work.

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
**Note**: Vote data is stored under /votes.
**Note 2**: The database is stored under /db.

Simply write your bot api key in the dedicated environment variable and launch the container:
```
docker run -d \ 
 -e BOT_KEY="YOUR_BOT_API_KEY" \ 
 --restart=always \ 
 --name tinder-bot \ 
 arthurdk/tinder-telegram-bot:latest
```

More info available on [this bot Docker Hub repository](https://hub.docker.com/r/arthurdk/tinder-telegram-bot/)

#### Docker environment variable

| Variable      | Description                                                          | Values             | Default value |
|---------------|----------------------------------------------------------------------|--------------------|---------------|
| BOT_KEY       | Your Telegram bot API key                                            | "your_key"         | -             |
| GUGGY_API_KEY | API Key for displaying GIF and stickers                              | None, "your_key"   | None          |
| DEBUG         | Toggle debugging mode                                                | True, False        | False         |
| CHAT_MODE     | The default chat mode                                                | off, owner and all | owner         |
| PREDICTION    | Toggle prediction by default  (a prediction backend must be enabled) | true, false        | true          |
| STORE_VOTES   | Toggle storing vote results by default                               | true, false        | false         |

* Example command

```
docker pull arthurdk/tinder-telegram-bot:latest && \
docker run -d \
 -v /votes:/votes  \
 -e GUGGY_API_KEY="your_key"  \
 -e BOT_KEY="your_key" \
 -e DEBUG=False \
 -e CHAT_MODE=all \
 -e STORE_VOTES=true \
 --restart=always \
 --name tinder-bot \
arthurdk/tinder-telegram-bot:latest
```

### Docker (build)

First, retrieve sources:

```
git clone https://github.com/arthurdk/tinder-telegram-bot.git \
 && cd tinder-telegram-bot
```

Then, build the image:

```
docker build -f Dockerfile \
 -t <your-repo-name>/tinder-telegram-bot:latest .
```

Finally, write your bot api key in the dedicated environment variable and launch the container:

```
docker run -d \
 -e BOT_KEY="YOUR_BOT_API_KEY" \ 
 --restart=always \ 
 --name tinder-bot <your-repo-name>/tinder-telegram-bot:latest
```

### Python (Dev)

Note: This was tested on Ubuntu 16.04 based distribution only.

Install Pynder (Tinder client)

```
git clone https://github.com/charliewolf/pynder.git \
 && cd pynder \
 && git checkout d5389088d11ade0b5227b0c594695f19e7936399 \ 
 && python3 setup.py install
```

Install dependencies:

```
pip3 install -r requirements.txt
```


Create file containing the bot api key.

```
cat > settings.py << EOL
from bot_app.prediction import LoveByHuguesVerlin

KEY = "KEY"
DB_NAME = './tinderbot.sqlite3'
DEBUG_MODE = False

settings_defaults = {
    "chat_mode": "off",  # Modes are off, owner and all
    "max_poll_range_size": "100",
    "max_send_range_size": "1",
    "min_votes_before_timeout": "1",
    "min_timeout": "10",
    "max_timeout": "86400",
    "send_block_time": "10",
    "poll_block_time": "10",
    "blind_mode": "False",
    "matches_cache_time": "60",
    "timeout_mode": "dynamic",
    "prediction": "false",
    "store_votes": "false"
}


# Get your key on their website
guggy_api_key = None
prediction_backend = None
location_search_url = "http://nominatim.openstreetmap.org/search/"
data_retrieval_path = "./data/"
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
list_settings - List all settings and their values.
set_setting - Change a setting. If an account is set, this command can only be executed by the account owner.
help_settings - Display help for settings
unblock - Remove the sending/polling blocade once
poll_unanswered - Read only unanswered messages
about - Learn more about the bot
help - Display help
unlink - Unlink your Tinder account from the bot
```

And do not forget to delete your bot from the conversation and add it again.

If you are in a private conversation with the bot delete the conversation and start afresh.

## Contributing

Any contribution is welcomed (feature request, issues, pull request...).

Please remember this is still in a WIP state, so there are still issues and known bugs. Refactoring is also needed.

## License
----

MIT