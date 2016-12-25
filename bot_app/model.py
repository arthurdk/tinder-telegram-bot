from bot_app.keyboards import *
import threading
import bot_app.admin as admin
import time


class Conversation:

    def __init__(self, group_id, session, owner):
        # The chat id (private ou group id)
        self.group_id = group_id
        self.session = session
        self.is_voting = False
        self.current_votes = {}
        self.users = []
        self.is_alarm_set = False
        # Message that will be edited after the voting session is finished
        self.result_msg = None
        self.timeout = 60
        self.auto = False
        self.vote_msg = None
        self.settings = admin.Settings()
        self.matches_cache_lock = threading.Lock()
        self.matches_cache_time = 0
        self.matches_cache = None
        self.owner = owner
        self.block_polling_until = 0
        self.block_sending_until = 0
        self.cur_user_insta_private = None
        self.current_mod_candidate = None

    def refresh_users(self):
        self.users = self.session.nearby_users()

    def set_is_voting(self, is_voting):
        self.is_voting = is_voting

    def get_votes(self):
        return self.current_votes

    def get_stats(self):
        likes = 0
        dislikes = 0
        for _, value in self.get_votes().items():
            if value == InlineKeyboard.LIKE:
                likes += 1
            elif value == InlineKeyboard.DISLIKE:
                dislikes += 1
        return likes, dislikes

    def get_matches(self):
        """
        Retrieve matches and store them in cache
        :return:
        """
        self.matches_cache_lock.acquire()
        if time.time() - self.matches_cache_time > int(self.settings.get_setting("matches_cache_time")) \
                or self.matches_cache is None:
            self.matches_cache_time = time.time()
            self.matches_cache = self.session.matches()

        matches = self.matches_cache
        self.matches_cache_lock.release()
        return matches

