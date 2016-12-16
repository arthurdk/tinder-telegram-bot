# Help messages for all the bot commands. Use the internal function names as key!
help_messages = {}
help_messages["send_message"] = "Usage of /msg:\n/msg <match-id> <message>\nZou can get the match-id by executing /matches"


def send_account_not_setup(bot, chat_id):
    bot.sendMessage(chat_id, text="Chat not registered yet, please add token.")

def debug(bot, chat_id, message):
    bot.sendMessage(chat_id, text=message)

def send_help(bot, chat_id, command):
    bot.sendMessage(chat_id, text=help_messages[command])