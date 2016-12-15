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