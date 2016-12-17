#!/bin/sh



cat > $ROOT_FOLDER/bot_app/settings.py << EOL
from bot_app.prediction import *
KEY = "$BOT_KEY"
DB_NAME = 'tinderbot.sqlite3'
DEBUG_MODE = False

chat_mode_default = "all"  # Modes are off, owner and all
max_poll_range_size_default = "100"
max_send_range_size_default = "10"
min_votes_before_timeout_default = "1"
min_timeout_default = "10"
max_timeout_default = "600"
send_block_time_default = "10"
poll_block_time_default = "10"
#blind_mode_default = FlexibleBoolean("False", is_value=True)
matches_cache_time_default = "60"
prediction_backend = LoveByHuguesVerlin("http://api.love.huguesverlin.fr/api/predict?user=%s")
EOL

python $ROOT_FOLDER/bot_app/Bot.py