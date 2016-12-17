import bot_app.settings as settings
from telegram import ParseMode

# Help messages for all the bot commands. Use the internal function names as key!
help_messages = {}
help_messages["send_message"] = "Usage of /msg:\n/msg <match-id> <message>\nYou can get the match-id by executing /matches. Supports id ranges."
help_messages["poll_messages"] = "Usage of /poll_msgs:\n/poll_msgs <match-id> <n>\nPolls the last n messages from the match. You can get the match-id by executing /matches. Supports id ranges. Second argument can be omitted and defaults to 5."
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
                        " * Use /msg to send a message to a match, and /poll_msgs to get the chat history with a match.\n" \
                        "\n" \
                        "_Configuration:_\n" \
                        " * Use /list_settings to list all settings and their values.\n" \
                        " * Use /set_setting to change a setting.This command can only be executed by the account owner.\n" \
                        "\n" \
                        "_Ranges:_\n" \
                        "Ranges are a comma-separated lists of numbers or number pairs. Number pairs are separated by a hyphen. Use no spaces in your range definition."

# All normal messages sent to the user
messages = {}
messages["welcome"] = 'Hey ! \nFirst things first, you will need to set your authentication ' \
                      'token using the /set_account command if you want to link your Tinder account.\n' \
                      'If you need help, type /help!'
messages["location_updated"] = "Location updated."
messages["setting_updated"] = "Setting updated."

# Error messages
error_messages = {}
error_messages["account_not_setup"] = "Chat not registered yet, please add token."
error_messages["unknown_match_id"] = "Unknown match-id."
error_messages["command_not_allowed"] = "This command must not be executed by this user."
error_messages["range_too_large"] = "The given range is too large."

### Functions for sending messages to the user ###


def debug(bot, chat_id, message):
    if settings.DEBUG_MODE:
        bot.sendMessage(chat_id, text=message)


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
        raise Exception('Unknown message: ' + name)

    bot.sendMessage(chat_id, text=messages[name])


def send_error(bot, chat_id, name):
    if name not in error_messages:
        raise Exception('Unknown error messages: ' + name)

    bot.sendMessage(chat_id, text=error_messages[name])


def send_custom_message(bot, chat_id, message):
    bot.sendMessage(chat_id, text=message)

### Handling bot commands ###


def send_help_message(bot, update):
    send_help(bot, update.message.chat_id, "help")