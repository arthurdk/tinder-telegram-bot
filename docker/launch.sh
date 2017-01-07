#!/bin/sh


if [ -z "$PREDICTION_BACKEND" ]; then
    PREDICTION_BACKEND=None
fi

if [ -z "$GUGGY_API_KEY" ]; then
    GUGGY_API_KEY=None
fi

if [ -z "$LOCATION_BACKEND" ]; then
    LOCATION_BACKEND=http://nominatim.openstreetmap.org/search/
fi

if [ -z "$DEBUG" ]; then
    DEBUG=False
fi

if [ -z "$CHAT_MODE" ]; then
    CHAT_MODE=owner
fi

if [ -z "$PREDICTION" ]; then
    PREDICTION=true
fi

if [ -z "$STORE_VOTES" ]; then
    STORE_VOTES=false
fi



cat > $ROOT_FOLDER/bot_app/settings.py << EOL
from bot_app.prediction import *
KEY = "$BOT_KEY"
DB_NAME = '/db/tinderbot.sqlite3'
DEBUG_MODE = $DEBUG

settings_defaults = {
    "chat_mode": "$CHAT_MODE",  #  off, owner and all
    "max_poll_range_size": "100",
    "max_send_range_size": "1",
    "min_votes_before_timeout": "1",
    "min_timeout": "10",
    "max_timeout": "86400",
    "send_block_time": "10",
    "poll_block_time": "10",
    "blind_mode": "False",
    "matches_cache_time": "60",
    "timeout_mode": "required_votes",
    "prediction": "$PREDICTION",
    "store_votes": "$STORE_VOTES"
}

guggy_api_key = "$GUGGY_API_KEY"
prediction_backend = $PREDICTION_BACKEND
location_search_url = "$LOCATION_BACKEND"
data_retrieval_path = "/votes/"
EOL

cd $ROOT_FOLDER
python bot_app/Bot.py