import bot_app.settings as settings
from telegram import ParseMode
from telegram.error import TelegramError, Unauthorized

# Help messages for all the bot commands. Use the internal function names as key!
help_messages = {}
help_messages["send_message"] = "Usage of /msg:\n" \
                                "/msg <match-id> <message>\n" \
                                "You can get the match-id by executing /matches. Supports id ranges. With first argument = 'last', the max last matches are messaged."
help_messages["poll_messages"] = "Usage of `/poll_msgs`:\n" \
                                 "`/poll_msgs` <match-id> <n>\n" \
                                 "Polls the last n messages from the match. You can get the match-id by executing /matches. Supports id ranges. Second argument can be omitted and defaults to 5. Without arguments or with first argument = 'last', the max last matches are polled."
help_messages["poll_unanswered"] = "Usage of `/poll_unanswered`:\n" \
                                   "`/poll_unanswered` <match-id> <n>\nPolls the last n messages from the match. Shows them only if the last message is not from you. You should use it with an id range. Without arguments or with first argument = 'last', the max last matches are polled."
help_messages[
    "set_location"] = "Usage of /location:\n/set_location <place name> or <latitude> <longitude\nYou can also just use telegram to send a location to the group."
help_messages[
    "set_setting"] = "Usage of `/set_setting`:\n`/set_setting` <setting> <value>\nCommand may only be used by account owner."
help_messages[
    "make_me_a_mod"] = "Usage of `/set_mod`:\n`/set_mod` <user> <True|False>\nChange moderator status of a user."

# If you modify this sure the markdown is compatible with telegram !
help_messages["help"] = "*Usage of the bot:*\n" \
                        "\n" \
                        "_Logging in with your Tinder account:_\n" \
                        "1. Use `/set_account` \n" \
                        "2. The bot will ask you for your facebook token. Just send it plain.\n" \
                        "3. Use `/unlink` when your Tinder account unlinked from the bot\n" \
                        "\n" \
                        "_Searching for matches:_\n" \
                        " - Use /location to set your location.\n" \
                        " - Use `/new_vote` to start voting for a new stranger. Voting time can be set with /timeout. See `/help_settings` for more details.\n" \
                        " - Use /auto to toggle between automatic and manual mode. In automatic mode, a new vote will be started after the current one is finished.\n" \
                        " - Use /matches to list your matches in your private chat.\n" \
                        " - A draw is always a no.\n" \
                        "\n" \
                        "_Chatting with matches:_\n" \
                        " - Use /matches to list your matches in your private chat. Every match has an id. It can change if old matches unmatch.\n" \
                        " - Use /msg to send a message to a match. It supports match ranges.\n" \
                        " - Use `/poll_msgs` to get the chat history with a match. It supports match ranges.\n" \
                        " - Use `/poll_unanswered` to check for unanswered messages. Use it with a range. It returns only unanswered chats.\n" \
                        " - The owner may use /unblock to remove the sending/polling blocade once. See `/help_settings` for more information.\n" \
                        "\n" \
                        "_Configuration:_\n" \
                        " - Use `/list_settings` to list all settings and their values.\n" \
                        " - Use `/set_setting` to change a setting.This command can only be executed by the account owner.\n" \
                        " - Use `/help_settings` to get an explanation of the settings.\n" \
                        "\n" \
                        "_Ranges:_\n" \
                        "Ranges are a comma-separated lists of numbers or number pairs. Number pairs are separated by a hyphen. Use no spaces in your range definition. A range can be replaced with the word 'last'. Then the maximum last matches are used.\n" \
                        "\n" \
                        "_Other:_\n" \
                        " - Use /about to learn more about me."

# All normal messages sent to the user
messages = {}
messages["welcome"] = 'Hey ! \nFirst things first, you will need to set your authentication ' \
                      'token using the /set_account command in the chat you want the bot to be enabled, if you want to link your Tinder account.\n' \
                      'If you need help, type /help!'
messages["location_updated"] = "Location updated. (this may not work, due to Tinder API)"
messages["setting_updated"] = "Setting updated."
messages[
    "about"] = "I'm open source, you can learn more about me on Github: https://github.com/arthurdk/tinder-telegram-bot"
messages[
    "start_chat"] = "Please start a private conversation with me first. Follow the link: %s and then press 'Start' and then come back to this chat."
messages["send_token"] = "Please send me your authentication token in *our private conversation* %s "
messages["vote_question"] = "So what do you think of %s? (%d/%d votes)"
messages["unblocking_successful"] = "Sending and polling were unblocked."
messages["switch_private"] = "🔒 Switch to private chat"
messages["back_group"] = "Switch to group"
messages["new_match"] = "You have a new match."
messages["account_unlinked"] = "Account successfully unlinked."
messages["ask_for_token"] = "Please, send me your Tinder *authentication token*.\n*Note*: This token " \
                            "is only for accessing your Tinder account, your Facebook account is *safe*.\n" \
                            "Don't know how to retrieve this token?\n" \
                            "➡️ [Retrieving the authentication token]" \
                            "(https://github.com/arthurdk/tinder-telegram-bot#retrieving-the-authentication-token)\n" \
                            "*WARNING: * By sharing * YOUR * token, you will give access this bot with your Tinder account (and potentially to the bot owner too if he wants to)."

# Error messages
error_messages = {}
error_messages["account_not_setup"] = "Chat not registered yet, please add token using /set_account"
error_messages["unknown_match_id"] = "Unknown match-id."
error_messages["command_not_allowed"] = "This command must not be executed by the account owner."
error_messages["range_too_large"] = "The given range is too large."
error_messages[
    "unknown_command"] = "I'm sorry Dave I'm afraid I can't do that. Type /help if you does not want what to do."
error_messages["tinder_timeout"] = "Tinder account timed out, I'll try reconnecting the chat to Tinder right away."
error_messages["auth_failed"] = "Authentication failed! Please try again."
error_messages["new_vote_failed"] = "Failed to start new vote, please try again."
error_messages["no_more_users"] = "There are no other users available."
error_messages["failed_to_vote"] = "I failed to like/dislike this user on Tinder."
error_messages["no_location"] = "Location expired. Please use /location and start voting again."
error_messages["error"] = "Something went wrong."


# Functions for sending messages to the user

def debug(bot, chat_id, message):
    if settings.DEBUG_MODE:
        __actual_send_message(bot=bot, chat_id=chat_id, text=message)


def get_question_match(conversation):
    name = " %s (%d y.o)" % (conversation.current_user.name, conversation.current_user.age)
    question = messages["vote_question"] % (name,
                                            len(conversation.get_votes()),
                                            int(conversation.settings.get_setting("min_votes_before_timeout")))
    return question


def get_caption_match(user, current_vote, max_vote, bio=False):
    name = " %s - %d y.o - %d km away - %d/%s votes" % (user.name, user.age, user.distance_km, current_vote, max_vote)
    # Append bio to caption if it's not empty
    if bio and len(user.bio) > 0:
        name += "\n" + user.bio
    if len(user.jobs) > 0:
        pass
    if len(user.schools) > 0:
        name += "\nSchools: %s" % ",".join(user.schools)
    return name


def send_help(bot, chat_id, command, error=""):
    if command not in help_messages:
        raise Exception('Unknown command: ' + command)

    message = ""
    if error != "":
        message = "Error: " + error + "\n"

    message += help_messages[command]
    try:
        __actual_send_message(chat_id=chat_id, bot=bot, text=message, parse_mode=ParseMode.MARKDOWN)
    except TelegramError as e:
        raise e


def send_message(bot, chat_id, name):
    if name not in messages:
        msg = name
    else:
        msg = messages[name]
    __actual_send_message(bot=bot, chat_id=chat_id, text=msg)


def __actual_send_message(bot, chat_id, text,
                          parse_mode=None,
                          disable_web_page_preview=None,
                          disable_notification=False,
                          reply_to_message_id=None,
                          reply_markup=None,
                          timeout=None):
    """
    Try sending markdown and revert to normal text if broken
    :param bot:
    :param chat_id:
    :param text:
    :return:
    """
    try:
        bot.sendMessage(chat_id, text=text, parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=disable_web_page_preview,
                        disable_notification=disable_notification,
                        reply_to_message_id=reply_to_message_id,
                        reply_markup=reply_markup,
                        timeout=timeout)
    except TelegramError:
        bot.sendMessage(chat_id, text=text,
                        disable_web_page_preview=disable_web_page_preview,
                        disable_notification=disable_notification,
                        reply_to_message_id=reply_to_message_id,
                        reply_markup=reply_markup,
                        timeout=timeout)


def send_private_message(bot, user_id, text):
    """
    Return True if bot was able to actually send private message
    :param bot:
    :param user_id:
    :param text:
    :return:
    """
    try:
        __actual_send_message(bot=bot, chat_id=user_id, text=text)
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
    except Unauthorized:
        return False
    except TelegramError as e:
        # Todo try to send failed to send photo...
        pass


def send_private_link(bot, user_id, url):
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
        __actual_send_message(bot=bot, chat_id=user_id, text=url + " ")
        return True
    except Unauthorized:
        return False
    except TelegramError as e:
        # Todo try to send failed to message photo...
        pass


def notify_start_private_chat(bot, chat_id, incoming_message=None):
    if incoming_message is not None and incoming_message.from_user.username != bot.username:
        import bot_app.keyboards as keyboards
        reply_markup = keyboards.switch_private_chat_keyboard(bot.username)
        __actual_send_message(bot=bot, chat_id=chat_id, text=messages["start_chat"] % bot.name,
                              reply_to_message_id=incoming_message.message_id,
                              reply_markup=reply_markup)
    else:
        __actual_send_message(bot=bot, chat_id=chat_id, text=messages["start_chat"] % bot.name)


def notify_send_token(bot, chat_id, reply_to_message_id, is_group, group_name, reply_markup=[[]]):
    """

    :param bot:
    :param chat_id:
    :param reply_to_message_id:
    :param is_group:
    :param group_name:
    :param reply_markup:
    :return:
    """
    msg = messages["send_token"] % bot.name
    if is_group:
        msg += " for the group %s" % group_name

        __actual_send_message(bot=bot, chat_id=chat_id, text=msg,
                              reply_to_message_id=reply_to_message_id,
                              reply_markup=reply_markup,
                              parse_mode=ParseMode.MARKDOWN)


def send_error(bot, chat_id, name):
    if name not in error_messages:
        raise Exception('Unknown error messages: ' + name)

    __actual_send_message(bot, chat_id=chat_id, text=error_messages[name])


def unknown(bot, update):
    send_message(bot=bot, chat_id=update.message.chat_id, name=error_messages["unknown_command"])


def send_custom_message(bot, chat_id, message, parse_mode=None,
                        disable_web_page_preview=None,
                        disable_notification=False,
                        reply_to_message_id=None,
                        reply_markup=None,
                        timeout=None):
    """
    Send a custom message (not predefined)
    :param timeout:
    :param reply_markup:
    :param reply_to_message_id:
    :param parse_mode:
    :param disable_notification:
    :param disable_web_page_preview:
    :param bot:
    :param chat_id:
    :param message:
    :return:
    """
    __actual_send_message(bot, chat_id=chat_id, text=message, parse_mode=parse_mode,
                          disable_web_page_preview=disable_web_page_preview,
                          disable_notification=disable_notification,
                          reply_to_message_id=reply_to_message_id,
                          reply_markup=reply_markup,
                          timeout=timeout)


# Handling bot commands
def send_help_message(bot, update):
    send_help(bot, update.message.chat_id, "help")


def send_location(latitude, longitude, bot, chat_id):
    bot.sendLocation(chat_id, latitude=latitude, longitude=longitude)


def send_chat_action(bot, chat_id, action):
    bot.sendChatAction(chat_id=chat_id, action=action)
