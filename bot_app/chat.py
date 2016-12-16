from bot_app.messages import *


def send_message(bot, update, args):
    global conversations
    chat_id = update.message.chat_id

    if chat_id in conversations:
        debug(bot, chat_id, "Reached send_message")

        if len(args) < 2:
            send_help(bot, chat_id, "send_message")
            return

        destination = conversations[chat_id].session.matches()[int(args[0])] # What if int fails?
    else:
        send_account_not_setup(bot=bot, chat_id=chat_id)