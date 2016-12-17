import bot_app.settings as settings
from telegram import ParseMode
from telegram import TelegramError

# Help messages for all the bot commands. Use the internal function names as key!
help_messages = {}
help_messages["send_message"] = "Usage of /msg:\n/msg <match-id> <message>\nYou can get the match-id by executing /matches. Supports id ranges."
help_messages["poll_messages"] = "Usage of /poll_msgs:\n/poll_msgs <match-id> <n>\nPolls the last n messages from the match. You can get the match-id by executing /matches. Supports id ranges. Second argument can be omitted and defaults to 5."
help_messages["poll_unanswered"] = "Usage of /poll_unanswered:\n/poll_unanswered <match-id> <n>\nPolls the last n messages from the match. Shows them only if the last message is not from you. You should use it with an id range."
help_messages["set_location"] = "Usage of /set_location:\n/set_location <latitude> <longitude>\nYou can also just use telegram to send a location to the group."
help_messages["set_setting"] = "Usage of /set_setting:\n/set_setting <setting> <value>\nCommand may only be used by account owner."

help_messages["help"] = "*Usage of the bot:*\n" \
                        "\n" \
                        "_Logging in with your Tinder account:_\n" \
                        "1. Use /set_account\n" \
                        "2. The bot will ask you for your facebook token. Just send it plain.\n" \
                        "\n" \
                        "_Searching for matches:_\n" \
                        " * Use /location to set your location.\n" \
                        " * Use /new_vote to start voting for a new stranger. Voting time can be set with /timeout.\n" \
                        " * Use /auto to toggle between automatic and manual mode. In automatic mode, a new vote will be started after the current one is finished.\n" \
                        " * Use /matches to list your matches in your private chat.\n" \
                        " * A draw is always a no.\n" \
                        "\n" \
                        "_Chatting with matches:_\n" \
                        " * Use /matches to list your matches in your private chat. Every match has an id. It can change if old matches unmatch.\n" \
                        " * Use /msg to send a message to a match. It supports match ranges.\n" \
                        " * Use /poll_msgs to get the chat history with a match. It supports match ranges.\n" \
                        " * Use /poll_unanswered to check for unanswered messages. Use it with a range. It returns only unanswered chats.\n" \
                        " * The owner may use /unblock to remove the sending/polling blocade once. See /help_settings for more information.\n" \
                        "\n" \
                        "_Configuration:_\n" \
                        " * Use /list_settings to list all settings and their values.\n" \
                        " * Use /set_setting to change a setting.This command can only be executed by the account owner.\n" \
                        " * Use /help_settings to get an explanation of the settings.\n" \
                        "\n" \
                        "_Ranges:_\n" \
                        "Ranges are a comma-separated lists of numbers or number pairs. Number pairs are separated by a hyphen. Use no spaces in your range definition.\n" \
                        "\n" \
                        "_Other:_\n" \
                        " * Use /about to learn more about me."

# All normal messages sent to the user
messages = {}
messages["welcome"] = 'Hey ! \nFirst things first, you will need to set your authentication ' \
                      'token using the /set_account command if you want to link your Tinder account.\n' \
                      'If you need help, type /help!'
messages["location_updated"] = "Location updated."
messages["setting_updated"] = "Setting updated."
messages["about"] = "https://github.com/arthurdk/tinder-telegram-bot"
messages["start_chat"] = "Please start a private conversation with me first. Follow the link: %s"
messages["send_token"] = "Please send me your authentication token in our private conversation %s "
messages["vote_question"] = "So what do you think of %s? (%d votes)"
# Error messages
error_messages = {}
error_messages["account_not_setup"] = "Chat not registered yet, please add token."
error_messages["unknown_match_id"] = "Unknown match-id."
error_messages["command_not_allowed"] = "This command must not be executed by this user."
error_messages["range_too_large"] = "The given range is too large."
error_messages["unknown_command"] = "I'm sorry Dave I'm afraid I can't do that."
### Functions for sending messages to the user ###


def debug(bot, chat_id, message):
    if settings.DEBUG_MODE:
        bot.sendMessage(chat_id, text=message)


def get_question_match(conversation):
    name = " %s (%d y.o)" % (conversation.current_user.name, conversation.current_user.age)
    question = messages["vote_question"] % (name, len(conversation.get_votes()))
    return question


def send_help(bot, chat_id, command, error=""):
    if command not in help_messages:
        raise Exception('Unknown command: ' + command)

    message = ""
    if error != "":
        message = "Error: " + error + "\n"

    message += help_messages[command]
    bot.sendMessage(chat_id, text=message)


def send_message(bot, chat_id, name):
    if name not in messages:
        msg = name
    else:
        msg = messages[name]
    bot.sendMessage(chat_id, text=msg)


def send_private_message(bot, user_id, text):
    """
    Return True if bot was able to actually send private message
    :param bot:
    :param user_id:
    :param text:
    :return:
    """
    try:
        bot.sendMessage(user_id, text=text)
        return True
    except TelegramError as e:
        if e.message == "Unauthorized":
            return False


def send_private_photo(bot, user_id, url, caption):
    """
    Return True if bot was able to actually send private photo
    :param caption:
    :return:
    :param bot:
    :param user_id:
    :param url:
    :return:
    """
    try:
        bot.sendPhoto(user_id, photo=url, caption=caption)
        return True
    except TelegramError as e:
        if e.message == "Unauthorized":
            return False


def notify_start_private_chat(bot, chat_id, incoming_message_id=None):
    if incoming_message_id is not None:
        bot.sendMessage(chat_id, text=messages["start_chat"] % bot.name, reply_to_message_id=incoming_message_id)
    else:
        bot.sendMessage(chat_id, text=messages["start_chat"] % bot.name)


def notify_send_token(bot, chat_id, reply_to_message_id, is_group, group_name):
    msg = messages["send_token"] % bot.name
    if is_group:
        msg += " for the group %s" % group_name
    bot.sendMessage(chat_id,
                    text=msg,
                    reply_to_message_id=reply_to_message_id)


def send_error(bot, chat_id, name):
    if name not in error_messages:
        raise Exception('Unknown error messages: ' + name)

    bot.sendMessage(chat_id, text=error_messages[name])


def unknown(bot, update):
    send_message(bot=bot, chat_id=update.message.chat_id, name=error_messages["unknown_command"])


def send_custom_message(bot, chat_id, message):
    bot.sendMessage(chat_id, text=message)

### Handling bot commands ###


def send_help_message(bot, update):
    send_help(bot, update.message.chat_id, "help")