from telegram.ext.dispatcher import run_async

from bot_app.messages import *
from bot_app.admin import *
import bot_app.data as data

@run_async
def send_message(bot, update, args):
    global data
    global settings

    chat_id = update.message.chat_id
    sender = update.message.from_user.id

    if not chat_id in data.conversations:
        send_error(bot=bot, chat_id=chat_id, name="account_not_setup")
        return

    if ensure_setting_is_unset(bot, chat_id, "everybody_can_send_messages", sender == data.conversations[chat_id].owner):
        send_error(bot, chat_id, "command_not_allowed")
        return

    if len(args) < 2:
        send_help(bot, chat_id, "send_message")
        return

    try:
        match_id = int(args[0])
    except ValueError:
        send_help(bot, chat_id, "send_message", "First argument must be an integer")
        return


    destination = get_match(bot, update, match_id)
    if destination is None:
        return

    message = " ".join(args[1:])

    destination.message(message)

    destination = get_match(bot, update, match_id)
    if destination is None:
        return

    send_custom_message(bot, chat_id, poll_last_messages_as_string(destination, 5))

def poll_last_messages(match, n):
    return match.messages[-n:]

def get_match(bot, update, id):
    global data
    chat_id = update.message.chat_id
    matches = data.conversations[chat_id].session.matches()

    if id < 0 or id >= len(matches):
        send_error(bot, chat_id, "unknown_match_id")
        return None

    return matches[id]

def poll_last_messages_as_string(match, n):
    last_messages = "Messages with " + match.user.name + ":\n"
    has_messages = False

    for m in poll_last_messages(match, n):
        has_messages = True
        last_messages += m._data["sent_date"] + " " + m.sender.name + ": " + m.body + "\n"

    if not has_messages:
        last_messages = "No messages found for " + match.user.name

    return last_messages

def poll_messages(bot, update, args):
    global data
    chat_id = update.message.chat_id

    if not chat_id in data.conversations:
        send_error(bot, chat_id, "account_not_setup")
        return

    if ensure_setting_is_unset(bot, chat_id, "enable_message_polling"):
        return

    if len(args) < 2:
        send_help(bot, chat_id, "poll_messages", "Not enough arguments given")
        return

    try:
        match_id = int(args[0])
    except ValueError:
        send_help(bot, chat_id, "poll_messages", "First argument must be an integer")
        return

    try:
        n = int(args[1])
    except ValueError:
        send_help(bot, chat_id, "poll_messages", "Second argument must be an integer")
        return

    if n < 1:
        send_help(bot, chat_id, "poll_messages", "<n> must be greater than zero!")
        return

    if n > 100:
        send_help(bot, chat_id, "poll_messages", "<n> must be smaller than a hundred.")

    match = get_match(bot, update, match_id)
    if match is None:
        return

    send_custom_message(bot, chat_id, poll_last_messages_as_string(match, n))