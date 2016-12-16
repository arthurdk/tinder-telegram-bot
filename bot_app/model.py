

# Homemade enum
class Vote:
    SUPERLIKE = "SUPERLIKE"
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"
    MORE = "MORE"
#    BIO = "BIO"


class Conversation:

    def __init__(self, group_id, session):
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
            if value == Vote.LIKE:
                likes += 1
            elif value == Vote.DISLIKE:
                dislikes += 1
        return likes, dislikes
