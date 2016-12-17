from telegram.ext.dispatcher import run_async

from bot_app.messages import *
from bot_app.admin import *
import bot_app.data as data
import datetime
import time


@run_async
def send_message(bot, update, args):
    global data

    chat_id = update.message.chat_id
    sender = update.message.from_user.id

    if chat_id not in data.conversations:
        send_error(bot=bot, chat_id=chat_id, name="account_not_setup")
        return

    conversation = data.conversations[chat_id]
    owner = conversation.owner
    settings = conversation.settings
    session = conversation.session

    chat_mode = settings.get_setting("chat_mode")
    if  chat_mode == "off" or (chat_mode == "owner" and sender != owner):
        send_error(bot, chat_id, "command_not_allowed")
        return

    if conversation.block_sending_until > time.time():
        blocktime = int(conversation.block_sending_until - time.time())
        send_custom_message(bot, chat_id, "Sending is blocked for " + str(blocktime) + " more seconds.")
        return

    if len(args) < 2:
        send_help(bot, chat_id, "send_message")
        return

    try:
        match_ids = parse_range(bot, chat_id, args[0], int(settings.get_setting("max_send_range_size")))
    except ValueError:
        send_help(bot, chat_id, "send_message", "First argument must be an integer range")
        return

    matches = session.matches()
    message = " ".join(args[1:])

    for match_id in match_ids:
        destination = get_match(bot, update, match_id, matches)
        destination.message(message)

    matches = session.matches()

    for match_id in match_ids:
        destination = get_match(bot, update, match_id, matches)

        if destination is not None:
            send_custom_message(bot, chat_id, poll_last_messages_as_string(destination, match_id, 5))

    # Block sending for some time
    ts = time.time()
    conversation.block_sending_until = ts + float(settings.get_setting("send_block_time")) * len(match_ids)


def poll_last_messages(match, n):
    return match.messages[-n:]


def get_match(bot, update, id, matches=None):
    global data
    chat_id = update.message.chat_id

    if matches is None:
        matches = data.conversations[chat_id].session.matches()

    if id < 0 or id >= len(matches):
        send_error(bot, chat_id, "unknown_match_id")
        return None

    return matches[id]


def parse_range(bot, chat_id, range_string, max_size):
    ranges = range_string.split(',')
    result = []

    for r in ranges:
        if len(result) > max_size:
            send_error(bot, chat_id, "range_too_large")
            return []

        if "-" in r:
            r = r.split('-')

            a = int(r[0])
            b = int(r[1])

            if a < 0 or b < 0:
                send_error(bot, chat_id, "unknown_match_id")
                return []

            if b - a > max_size:
                send_error(bot, chat_id, "range_too_large")
                return []

            result += range(int(r[0]), int(r[1]) + 1)
        else:
            result += [int(r)]

    return result


def poll_last_messages_as_string(match, id, n):
    last_messages = "Messages with " + match.user.name + " (ID=" + str(id) + ")" + ":\n"
    has_messages = False

    for m in poll_last_messages(match, n):
        has_messages = True

        date = datetime.datetime.strptime(m._data["sent_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        now = datetime.datetime.now()

        ts = time.time()
        utc_offset = (datetime.datetime.fromtimestamp(ts) -
                      datetime.datetime.utcfromtimestamp(ts)).total_seconds()

        date += datetime.timedelta(seconds=utc_offset)
        now += datetime.timedelta(seconds=utc_offset)

        if now.day == date.day and now.month == date.month and now.year == date.year:
            strdate = date.strftime("%H:%M")
        else:
            strdate = date.strftime("%Y-%m-%d %H:%M")

        last_messages += strdate + " " + m.sender.name + ": " + m.body + "\n"

    if not has_messages:
        last_messages = "No messages found for " + match.user.name + " (ID=" + str(id) + ")"

    return last_messages


@run_async
def poll_messages(bot, update, args):
    global data
    chat_id = update.message.chat_id

    if chat_id not in data.conversations:
        send_error(bot, chat_id, "account_not_setup")
        return

    conversation = data.conversations[chat_id]
    settings = conversation.settings

    chat_mode = settings.get_setting("chat_mode")
    if chat_mode == "off":
        send_error(bot, chat_id, "command_not_allowed")
        return

    if conversation.block_polling_until > time.time():
        blocktime = int(conversation.block_polling_until - time.time())
        send_custom_message(bot, chat_id, "Polling is blocked for " + str(blocktime) + " more seconds.")
        return

    if len(args) < 1:
        send_help(bot, chat_id, "poll_messages", "Not enough arguments given")
        return

    try:
        match_ids = parse_range(bot, chat_id, args[0], int(settings.get_setting("max_poll_range_size")))
    except ValueError:
        send_help(bot, chat_id, "poll_messages", "First argument must be an integer range")
        return

    if len(args) < 2:
        n = 5
    else:
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

    matches = conversation.session.matches()
    for match_id in match_ids:
        match = get_match(bot, update, match_id, matches)

        if match is not None:
            send_custom_message(bot, chat_id, poll_last_messages_as_string(match, match_id, n))

    # Block polling for some time
    ts = time.time()
    conversation.block_polling_until = ts + float(settings.get_setting("poll_block_time")) * len(match_ids)


def unblock(bot, update):
    global data
    chat_id = update.message.chat_id
    conversation = data.conversations[chat_id]
    owner = conversation.owner
    sender = update.message.from_user.id

    if sender != owner:
        send_error(bot, chat_id, "command_not_allowed")
        return

    conversation.block_polling_until = 0
    conversation.block_sending_until = 0