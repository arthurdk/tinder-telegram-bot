from telegram.ext.dispatcher import run_async
from telegram import InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent
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
    if chat_mode == "off" or (chat_mode == "owner" and sender != owner):
        send_error(bot, chat_id, "command_not_allowed")
        return

    if conversation.block_sending_until > time.time():
        blocktime = int(conversation.block_sending_until - time.time())
        send_custom_message(bot, chat_id, "Sending is blocked for " + str(blocktime) + " more seconds.")
        return

    if len(args) < 2:
        send_help(bot, chat_id, "send_message")
        return

    max_range_size = int(settings.get_setting("max_send_range_size"))

    try:
        if args[0].lower() == "last":
            match_ids = None
        else:
            match_ids = parse_range(bot, chat_id, args[0], max_range_size)
    except ValueError:
        send_help(bot, chat_id, "send_message", "First argument must be an integer range or 'last'.")
        return

    matches = session.matches()
    message = " ".join(args[1:])

    if match_ids is None:
        match_ids = range(max(0, len(matches) - max_range_size), len(matches))

    for match_id in match_ids:
        destination = get_match(bot, update, match_id, matches)
        destination.message(message)

    matches = session.matches()
    messages_shown = 0

    for match_id in match_ids:
        destination = get_match(bot, update, match_id, matches)

        if destination is not None:
            send_custom_message(bot, chat_id, poll_last_messages_as_string(destination, match_id, 5))
            messages_shown += 1

    # Block sending for some time
    ts = time.time()
    conversation.block_sending_until = ts + float(settings.get_setting("send_block_time")) * messages_shown


def inline_preview(bot, update):
    global data
    query = update.inline_query.query
    # Return on empty query
    if not query:
        return
    if update.inline_query.offset:
        offset = int(update.inline_query.offset)
    else:
        offset = 0

    args = query.split(" ")
    if len(args) != 2:
        return
    mode = args[0]
    if mode not in ["pictures", "matches"]:
        return

    chat_id = int(args[1])
    if chat_id not in data.conversations:
        return

    conversation = data.conversations[chat_id]
    session = conversation.session

    results = list()
    last_idx = 0
    cache = 60
    if mode == "matches":
        matches = session.matches()

        for idx, match in enumerate(matches):
            if idx >= offset:
                thumb = match.user.get_photos(width='84')[0]
                full = match.user.get_photos(width='640')[0]

                results.append(InlineQueryResultPhoto(id=idx, caption=match.user.name, description=match.user.name,
                                                      photo_height=0,
                                                      thumb_url=thumb,
                                                      photo_url=full))
                last_idx = idx + 1
    elif mode == "pictures":
        cur_user = conversation.current_user
        thumbs = cur_user.get_photos(width='84')
        fulls = cur_user.get_photos(width='640')
        for idx, pic in enumerate(thumbs):
            if idx >= offset:
                thumb = pic
                full = fulls[idx]

                results.append(InlineQueryResultPhoto(id=idx, caption="%s %d/%d" % (cur_user.name, idx, len(thumbs)),
                                                      description=cur_user.name,
                                                      photo_height=0,
                                                      thumb_url=thumb,
                                                      photo_url=full))
                last_idx = idx + 1

        cache = conversation.timeout
        if cache > 0:
            cache -= 1

    bot.answerInlineQuery(update.inline_query.id, results, cache_time=cache, next_offset=last_idx)


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
def poll_messages(bot, update, args, only_unanswered=False):
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

    max_range_size = int(settings.get_setting("max_poll_range_size"))
    match_ids = None

    if len(args) > 0:
        if args[0].lower() != "last":
            try:
                match_ids = parse_range(bot, chat_id, args[0], max_range_size)
            except ValueError:
                send_help(bot, chat_id, "poll_unanswered" if only_unanswered else "poll_messages", "First argument must be an integer range or 'last'")
                return

    if len(args) < 2:
        n = 5
    else:
        try:
            n = int(args[1])
        except ValueError:
            send_help(bot, chat_id, "poll_unanswered" if only_unanswered else "poll_messages", "Second argument must be an integer")
            return

    if n < 1:
        send_help(bot, chat_id, "poll_unanswered" if only_unanswered else "poll_messages", "<n> must be greater than zero!")
        return

    if n > 100:
        send_help(bot, chat_id, "poll_unanswered" if only_unanswered else "poll_messages", "<n> must be smaller than a hundred.")

    matches = conversation.session.matches()
    my_id = conversation.session.profile.id
    messages_shown = 0

    if match_ids is None:
        match_ids = range(max(0, len(matches) - max_range_size), len(matches))

    for match_id in match_ids:
        match = get_match(bot, update, match_id, matches)

        if match is not None:
            if not only_unanswered or has_unanswered_messages(my_id, match):
                send_custom_message(bot, chat_id, poll_last_messages_as_string(match, match_id, n))
                messages_shown += 1

    # Block polling for some time
    ts = time.time()
    conversation.block_polling_until = ts + float(settings.get_setting("poll_block_time")) * messages_shown


def has_unanswered_messages(my_id, match):
    if len(match.messages) == 0:
        return False

    sender_id = match.messages[-1].sender.id
    return my_id != sender_id


def poll_unanswered_messages(bot, update, args):
    poll_messages(bot, update, args, True)


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

    send_message(bot, chat_id, 'unblocking_successful')
