from bot_app.prediction import LoveByHuguesVerlin

KEY = "KEY"
DB_NAME = 'tinderbot.sqlite3'
DEBUG_MODE = False

chat_mode_default = "off"  # Modes are off, owner and all
max_poll_range_size_default = "100"
max_send_range_size_default = "1"
min_votes_before_timeout_default = "1"
min_timeout_default = "10"
max_timeout_default = "86400"
send_block_time_default = "10"
poll_block_time_default = "10"
# blind_mode_default = FlexibleBoolean("False", is_value=True)
matches_cache_time_default = "60"

prediction_backend = LoveByHuguesVerlin("http://api.love.huguesverlin.fr/api/predict?user=%s")
location_search_url = "http://nominatim.openstreetmap.org/search/"
data_retrieval_path = "./"
