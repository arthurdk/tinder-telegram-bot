#!/bin/sh



cat > $ROOT_FOLDER/bot_app/settings.py << EOL
KEY = "$BOT_KEY"
DB_NAME = 'tinderbot.sqlite3'
EOL

python $ROOT_FOLDER/bot_app/Bot.py