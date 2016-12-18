from bot_app.prediction import LoveByHuguesVerlin

KEY = "KEY"
DB_NAME = 'tinderbot.sqlite3'
DEBUG_MODE = False

settings_defaults = {
    "chat_mode": "off", # Modes are off, owner and all
    "max_poll_range_size": "100",
    "max_send_range_size": "1",
    "min_votes_before_timeout": "1",
    "min_timeout": "10",
    "max_timeout": "86400",
    "send_block_time": "10",
    "poll_block_time": "10",
    "blind_mode": "False",
    "matches_cache_time": "60",
    "timeout_mode": "dynamic"
}

prediction_backend = LoveByHuguesVerlin("http://api.love.huguesverlin.fr/api/predict?user=%s")
location_search_url = "http://nominatim.openstreetmap.org/search/"
data_retrieval_path = "./data/"
