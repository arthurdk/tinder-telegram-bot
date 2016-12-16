import bot_app.settings as settings

# Help messages for all the bot commands. Use the internal function names as key!
help_messages = {}
help_messages["send_message"] = "Usage of /msg:\n/msg <match-id> <message>\nZou can get the match-id by executing /matches"

# All normal messages sent to the user
messages = {}
messages["welcome"] = 'Hey ! \nFirst things first, you will need to set your authentication ' \
                      'token using the /set_account command if you want to link your Tinder account.'
# Error messages
error_messages = {}
error_messages["account_not_setup"] = "Chat not registered yet, please add token."


def debug(bot, chat_id, message):
    if settings.DEBUG_MODE:
        bot.sendMessage(chat_id, text=message)


def send_help(bot, chat_id, command):
    bot.sendMessage(chat_id, text=help_messages[command])

def send_message(bot, chat_id, name):
    bot.sendMessage(chat_id, text=messages[name])

def send_error(bot, chat_id, name):
    bot.sendMessage(chat_id, text=error_messages[name])