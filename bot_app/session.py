import pynder
from telegram import ChatAction
from telegram.ext import JobQueue, Job
import bot_app.keyboards as keyboards
from bot_app.model import Conversation
import bot_app.data as data
import bot_app.messages as messages
from telegram.ext.dispatcher import run_async


def create_pynder_session(fb_token):
    return pynder.Session(facebook_token=fb_token)


def do_login(bot, chat_id: str, sender: str, token: str, job_queue: JobQueue):
    global data
    try:
        # Notify this is going to take some time
        if data.change_account_queries[sender] != sender:
            bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)

        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)

        # Create Tinder session
        session = create_pynder_session(token)
        message = "Switching to %s's account." % session.profile.name
        messages.send_custom_message(bot=bot, message=message, chat_id=data.change_account_queries[sender])
        if sender != data.change_account_queries[sender]:
            group_name = bot.getChat(chat_id=data.change_account_queries[sender]).title
            bot.sendMessage(chat_id=sender,
                            text=message,
                            reply_markup=keyboards.switch_group_keyboard())
        # Create conversation
        conversation = Conversation(data.change_account_queries[sender], session, sender, token=token)
        data.conversations[data.change_account_queries[sender]] = conversation
        del data.change_account_queries[sender]

        # Launch get matches background job
        cache_time = int(conversation.settings.get_setting("matches_cache_time"))
        job = Job(job_refresh_matches, cache_time + 1, repeat=True, context=conversation)
        job_queue.put(job,  next_t=0.0)

    except pynder.errors.RequestError:
        messages.send_error(bot=bot, chat_id=chat_id, name="auth_failed")


@run_async
def job_refresh_matches(bot, job):
    global data

    conversation = job.context
    if conversation in data.conversations.values():
        try:
            matches = conversation.get_matches()
        except pynder.errors.RequestError:
            do_reconnect(bot=bot, chat_id=conversation.group_id, conversation=conversation)
        if conversation.prev_nb_match is not None and len(matches) > conversation.prev_nb_match:
            messages.send_message(bot=bot, chat_id=conversation.group_id, name="new_match")
    else:
        job.schedule_removal()


def do_reconnect(bot, chat_id: str, conversation: Conversation):
    # TODO insert lock ;)
    messages.send_error(bot=bot, chat_id=chat_id, name="tinder_timeout")
    global data
    try:
        session = create_pynder_session(conversation.token)
        conversation.session = session
        message = "Switching to %s's account." % session.profile.name
        messages.send_custom_message(bot=bot, message=message, chat_id=chat_id)
    except pynder.errors.RequestError:
        messages.send_error(bot=bot, chat_id=chat_id, name="auth_failed")
