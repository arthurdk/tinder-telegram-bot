import pynder
from telegram import ChatAction
import bot_app.keyboards as keyboards
from bot_app.model import Conversation
import bot_app.data as data
import bot_app.messages as messages


def create_pynder_session(fb_token):
    return pynder.Session(facebook_token=fb_token)


def do_login(bot, chat_id: str, sender: str, token: str):
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
    except pynder.errors.RequestError:
        messages.send_error(bot=bot, chat_id=chat_id, name="auth_failed")


def do_reconnect(bot, chat_id: str, conversation: Conversation):
    messages.send_error(bot=bot, chat_id=chat_id, name="tinder_timeout")
    global data
    try:
        session = create_pynder_session(conversation.token)
        conversation.session = session
        message = "Switching to %s's account." % session.profile.name
        messages.send_custom_message(bot=bot, message=message, chat_id=chat_id)
    except pynder.errors.RequestError:
        messages.send_error(bot=bot, chat_id=chat_id, name="auth_failed")
