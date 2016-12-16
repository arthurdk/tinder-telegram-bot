from bot_app.messages import *
import bot_app.data as data


class Settings:
    settings = {}
    settings["chat_mode"] = "off" # Modes are off, owner and all

    values = {}
    values["chat_mode"] = ["off", "owner", "all"]

    def set_setting(self, setting, value):
        if setting not in self.settings.keys():
            raise Exception("Unknown setting: " + str(setting))

        if value not in self.values[setting]:
            return False

        self.settings[setting] = value
        return True

    def get_setting(self, setting):
        if setting not in self.settings.keys():
            raise Exception("Unknown setting: " + str(setting))

        return self.settings[setting]

def list_settings(bot, update):
    global data

    chat_id = update.message.chat_id

    if chat_id not in data.conversations:
        send_error(bot, chat_id, "account_not_setup")
        return

    conversation = data.conversations[chat_id]
    message = "Settings:\n"

    for s in conversation.settings.settings.keys():
        message += s + ": " + str(conversation.settings.settings[s]) + " " + str(conversation.settings.values[s]) + "\n"

    send_custom_message(bot, chat_id, message)

def set_setting(bot, update, args):
    global data

    chat_id = update.message.chat_id

    if chat_id not in data.conversations:
        send_error(bot, chat_id, "account_not_setup")
        return

    if update.message.from_user.id != data.conversations[chat_id].owner and data.conversations[chat_id].owner is not None:
        send_error(bot, chat_id, "command_not_allowed")
        return

    if len(args) != 2:
        send_help(bot, chat_id, "set_setting", "Wrong number of arguments")
        return

    if args[0] not in data.conversations[chat_id].settings.settings:
        send_help(bot, chat_id, "set_setting", "Unknown setting")
        return

    if data.conversations[chat_id].settings.set_setting(args[0], args[1]):
        send_message(bot, chat_id, "setting_updated")
    else:
        send_message(bot, chat_id, "Unknown value for setting: " + str(args[0]) + " = " + str(args[1]))
