#!/usr/bin/python3
# -*- coding: utf-8 -*-/s
from abc import ABC, abstractmethod
import requests
from telegram.ext.dispatcher import run_async
from telegram import ChatAction
from collections import OrderedDict
from random import randint
from enum import Enum


class Categories(Enum):
    VERY_HOT = 1
    HOT = 2
    LIKABLE = 3
    UNSURE = 4
    DISLIKABLE = 5
    NOPE = 6
    SUPER_NOPE = 7


class BasePrediction:
    def __init__(self):
        pass

    def send_prediction(self, bot, chat_id, hot, nope, cat, reply_to_message_id):
        bot.sendMessage(chat_id=chat_id,
                        text="My two cents: \nHot: " + str(hot) + "\nNope: " + str(nope),
                        reply_to_message_id=reply_to_message_id)


class EmojiPrediction(BasePrediction):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_sentence(cat):
        # Would be nice to load from file
        emoji = {Categories.VERY_HOT: ["❤️", "😍", "😻", "💓", "🔞", "💍", "💘"],
                 Categories.HOT: ["😚", "🌡", "👌", "😽", "🔥"],
                 Categories.LIKABLE: ["👍", "😙"],
                 Categories.UNSURE: ["🤔"],
                 Categories.DISLIKABLE: ["👎"],
                 Categories.NOPE: ["🙈", "😐", "😦", "🐐"],
                 Categories.SUPER_NOPE: ["😰", "💩", "😷", "🙀"]}

        idx = randint(0, len(emoji[cat]) - 1)
        return emoji[cat][idx]

    def send_prediction(self, bot, chat_id, hot, nope, cat, reply_to_message_id):
        bot.sendMessage(chat_id=chat_id,
                        text=self.get_sentence(cat=cat),
                        reply_to_message_id=reply_to_message_id)


class TwoLinersPrediction(BasePrediction):
    def __init__(self):
        super().__init__()

        # Example sending a one line of cat 1 even though really cat is 7
        # and then sending something like "Not just kidding"


class OneLinerPrediction(BasePrediction):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_sentence(cat):
        # Would be nice to load from file
        line = {Categories.VERY_HOT: ["Dat ass",
                                      "These eyes make me undress",
                                      "Hot ten!",
                                      "Ten out of ten!",
                                      "Will you marry me?",
                                      "Welcome to heaven",
                                      "Cute",
                                      "Mmmmhhhmmm please undress!",
                                      "Show me more of that perfect ..... sexy ..... bodiuuuunngh *continues to moan*"],

                Categories.HOT: ["I like your style",
                                 "Do you want to come to my bed?",
                                 "Come and see daddy!",
                                 "Hot chick!",
                                 "*Whistles*",
                                 "Pretty",
                                 "Attractive",
                                 "My little robot likes it",
                                 "Goodlooking"],

                Categories.LIKABLE: ["Nice.",
                                     "I hope she has a good personality.",
                                     "What about we meet and get to know each other better?",
                                     "I think you would fit me good.",
                                     "YOLO",
                                     "You are similar to my ex-girlfriend."
                                     "Let's check her personality."],

                Categories.UNSURE: ["Well I don't really know.",
                                    "Unsure."
                                    ],

                Categories.DISLIKABLE: ["Well, maybe not.",
                                        "I’m willing to lower my standards if you’re going on a date with me.",
                                        "What else do you have to offer?",
                                        "Not very attractive",
                                        "Not very cute",
                                        "Let's be friends!",
                                        "Meh."],

                Categories.NOPE: ["I would not implement you as a feature into my life",
                                  "If you were in my life you would be a bug",
                                  "Is your dad retarded? Because you’re special.",
                                  "Yuk!",
                                  "I rather go and play world of warcraft.",
                                  "Even with those filters, you are still ugly",
                                  "Did you fall from heaven? Because your face is completely ruined."
                                  ],

                Categories.SUPER_NOPE: ["Run you fools",
                                        "Even with those filters, you're still ugly",
                                        "Kill it! Kill it with fire!",
                                        "If you were on fire and I had a glass of water, I would drink it.",
                                        "Welcome to hell",
                                        "Thar she blows! (This is an old sailors expression for sighting a whale. So "
                                        "it is very degrading. I'm sorry.)"]
                }
        idx = randint(0, len(line[cat]) - 1)
        return line[cat][idx]

    def send_prediction(self, bot, chat_id, hot, nope, cat, reply_to_message_id):
        bot.sendMessage(chat_id=chat_id,
                        text=self.get_sentence(cat=cat),
                        reply_to_message_id=reply_to_message_id)


class GuggyPrediction(BasePrediction):
    def __init__(self, sentence_providers):
        super().__init__()
        self.guggy_api = "http://text2gif.guggy.com/v2/guggify"
        self.sentence_providers = sentence_providers

    def get_sentence(self, cat):
        idx = randint(0, len(self.sentence_providers) - 1)
        return self.sentence_providers[idx].get_sentence(cat)

    def send_prediction(self, bot, chat_id, hot, nope, cat, reply_to_message_id):
        import bot_app.settings as settings
        if settings.guggy_api_key is not None:
            # First launch api request
            headers = {
                "Content-Type": "application/json",
                "apiKey": settings.guggy_api_key,
            }
            payload = "{\"sentence\": \"" + self.get_sentence(cat) + "\"}"
            response = requests.post(self.guggy_api, headers=headers, data=payload.encode('utf-8'))

            if response.status_code == 200:
                result = response.json()
                is_gif = randint(0, 1)
                if is_gif == 0:
                    content = result["animated"]
                    length = len(content)
                    idx = randint(0, length - 1)
                    url = content[idx]["gif"]["original"]["url"]
                    bot.sendChatAction(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
                    bot.sendDocument(chat_id=chat_id, document=url,
                                     reply_to_message_id=reply_to_message_id)

                else:
                    content = result["sticker"]
                    length = len(content)
                    idx = randint(0, length - 1)
                    url = content[idx]["webp"]["original"]["url"]

                    bot.sendChatAction(chat_id=chat_id, action=ChatAction.UPLOAD_VIDEO)
                    bot.sendVideo(chat_id=chat_id,
                                  video=url,
                                  reply_to_message_id=reply_to_message_id)


emoji_pred = EmojiPrediction()
one_liner_pred = OneLinerPrediction()


def create_sender():
    import bot_app.settings as settings
    # Not the best implementation ever, feel free to change
    senders = OrderedDict()
    senders[20] = emoji_pred
    senders[40] = one_liner_pred
    if settings.guggy_api_key is not None:
        senders[100] = GuggyPrediction(sentence_providers=[emoji_pred, one_liner_pred])
    max = 0
    for key, value in senders.items():
        max = max if max > key else key
    result = randint(0, max)
    for key, sender in senders.items():
        if result <= key:
            return sender
    # Should never happen
    return BasePrediction()


def choose_category(hot: float):
    if hot > 0.9:
        return Categories.VERY_HOT
    elif hot > 0.75:
        return Categories.HOT
    elif hot > 0.55:
        return Categories.LIKABLE
    elif hot > 0.45:
        return Categories.UNSURE
    elif hot > 0.25:
        return Categories.DISLIKABLE
    elif hot > 0.1:
        return Categories.NOPE
    else:
        return Categories.SUPER_NOPE


def send_prediction(bot, chat_id, hot, nope, reply_to_message_id):
    cat = choose_category(hot=hot)
    choosen_sender = create_sender()
    choosen_sender.send_prediction(bot=bot, chat_id=chat_id, hot=hot,
                                   nope=nope,
                                   reply_to_message_id=reply_to_message_id,
                                   cat=cat)


@run_async
def do_prediction(bot, job):
    import bot_app.settings as settings
    if settings.prediction_backend is not None:
        chat_id, user_id, msg_id = job.context
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        hot, nope = settings.prediction_backend.predict(user_id=user_id)
        if is_prediction_valid(hot, nope):
            send_prediction(bot=bot, chat_id=chat_id, hot=hot, nope=nope, reply_to_message_id=msg_id)


def is_prediction_valid(hot, nope):
    return hot is not None and nope is not None and hot != 0 and nope != 0


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
