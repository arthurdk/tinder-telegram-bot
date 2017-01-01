import pynder
from telegram import ChatAction, Bot
from telegram.ext import JobQueue, Job
import bot_app.keyboards as keyboards
import bot_app.data as data
import bot_app.messages as messages
from telegram.ext.dispatcher import run_async
import time
import pynder
import traceback
import threading


class Session:
    """
    Wrapper class for Pynder session
    """
    def __init__(self, token):
        self.token = token
        # Pynder session
        self.__session = None

    def do_connect(self):
        try:
            self.__session = pynder.Session(facebook_token=self.token)
            return True
        except pynder.errors.RequestError:
            return False
        except BaseException:
            return False

    def get_profile_name(self) -> str:
        return self.__session.profile.name

    def get_profile_id(self):
        return self.__session.profile.id

    def get_matches(self):
        """
        Retrieve matches
        :return:
        """
        return self.__session.matches()

    def nearby_users(self):
        return self.__session.nearby_users()

    def update_location(self, latitude, longitude):
        self.__session.update_location(latitude=latitude, longitude=longitude)


def is_timeout_error(e):
    try:
        result = e.args[0] == 401
        return result
    except BaseException:
        return False


def do_login(bot: Bot, chat_id: str, sender: str, token: str, job_queue: JobQueue):
    from bot_app.model import Conversation
    global data
    try:
        # Notify this is going to take some time
        # In groups
        if data.change_account_queries[sender] != sender:
            bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        # In private chat
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)

        # Create Tinder session
        session = Session(token)
        if session.do_connect():

            message = "Switching to %s's account." % session.get_profile_name()
            messages.send_custom_message(bot=bot, message=message, chat_id=data.change_account_queries[sender])
            if sender != data.change_account_queries[sender]:
                # group_name = bot.getChat(chat_id=data.change_account_queries[sender]).title
                bot.sendMessage(chat_id=sender,
                                text=message,
                                reply_markup=keyboards.switch_group_keyboard())
            # Create conversation
            conversation = Conversation(data.change_account_queries[sender], session, sender)
            data.conversations[data.change_account_queries[sender]] = conversation
            del data.change_account_queries[sender]

            # Launch get matches background job
            cache_time = int(conversation.settings.get_setting("matches_cache_time"))
            job = Job(job_refresh_matches, cache_time + 1, repeat=True, context=conversation)
            job_queue.put(job,  next_t=0.0)

        else:
            messages.send_error(bot=bot, chat_id=chat_id, name="auth_failed")

    except BaseException:
        messages.send_error(bot=bot, chat_id=chat_id, name="auth_failed")


@run_async
def job_refresh_matches(bot: Bot, job):
    global data

    conversation = job.context
    if conversation in data.conversations.values():
        session = conversation.session
        try:
            matches = conversation.get_matches()
            if conversation.prev_nb_match is not None and len(matches) > conversation.prev_nb_match:
                messages.send_message(bot=bot, chat_id=conversation.group_id, name="new_match")
        except pynder.errors.RequestError:
            do_reconnect(bot=bot, chat_id=conversation.group_id, conversation=conversation)
    else:
        job.schedule_removal()


def do_reconnect(bot: Bot, chat_id: str, conversation):
    # TODO insert lock ;)
    messages.send_error(bot=bot, chat_id=chat_id, name="tinder_timeout")
    global data
    session = conversation.session
    if session.do_connect():
        message = "Switching to %s's account." % session.get_profile_name()
        messages.send_custom_message(bot=bot, message=message, chat_id=chat_id)
        # Refresh list of users so they have the new session
        conversation.refresh_users()
    else:
        messages.send_error(bot=bot, chat_id=chat_id, name="auth_failed")
