from abc import ABC, abstractmethod
import json
import requests
from telegram.ext.dispatcher import run_async


@run_async
def do_prediction(bot, job):
    import bot_app.settings as settings
    if settings.prediction_backend is not None:
        chat_id, user_id, msg_id = job.context
        hot, nope = settings.prediction_backend.predict(user_id=user_id)
        if hot is not None and nope is not None:
            bot.sendMessage(chat_id=chat_id, text="My two cents: \nHot:" + str(hot) + "\nNope:" + str(nope),
                            reply_to_message_id=msg_id)


class BasePredictor(ABC):
    def __init__(self, url):
        self.url = url

    @abstractmethod
    def predict(self, user_id):
        pass


class LoveByHuguesVerlin(BasePredictor):
    def __init__(self, url):
        super().__init__(url)

    def predict(self, user_id):
        response = requests.get(self.url % str(user_id))
        if response.status_code == 200:
            result = response.json()
            hot = result['predictions']['like']
            nope = result['predictions']['nope']
            return hot, nope
        else:
            return None, None