from bot_app.messages import *
from bot_app.data import *
from telegram.ext.dispatcher import run_async
import time


@run_async
def send_message(bot, update, args):
    global conversations
    chat_id = update.message.chat_id

    if not chat_id in conversations:
        send_error(bot=bot, chat_id=chat_id, name="account_not_setup")
        return

    if len(args) < 2:
        send_help(bot, chat_id, "send_message")
        return

    try:
        match_id = int(args[0])
    except ValueError:
        send_help(bot, chat_id, "send_message", "First argument must be an integer")

    destination = conversations[chat_id].session.matches()[match_id]
    message = " ".join(args[1:])

    destination.message(message)

    destination = conversations[chat_id].session.matches()[match_id]
    send_custom_message(bot, chat_id, poll_last_messages_as_string(destination, 5))

def poll_last_messages(match, n):
    return match.messages[-n:]

def poll_last_messages_as_string(match, n):
    last_messages = "Messages with " + match.user.name + ":\n"
    has_messages = False

    for m in poll_last_messages(match, 5):
        has_messages = True
        last_messages += m._data["sent_date"] + " " + m.sender.name + ": " + m.body + "\n"

    if not has_messages:
        last_messages = "No messages found for " + match.user.name

    return last_messages

def poll_messages(bot, update, args):
    global conversations
    chat_id = update.message.chat_id

    if not chat_id in conversations:
        send_error(bot, chat_id, "account_not_setup")
        return

    if len(args) < 2:
        send_help(bot, chat_id, "poll_messages", "Not enough arguments given")

    try:
        match_id = int(args[0])
    except ValueError:
        send_help(bot, chat_id, "poll_message", "First argument must be an integer")

    try:
        n = int(args[1])
    except ValueError:
        send_help(bot, chat_id, "poll_message", "Second argument must be an integer")

    match = conversations[chat_id].session.matches()[match_id]
    send_custom_message(bot, chat_id, poll_last_messages_as_string(match, n))