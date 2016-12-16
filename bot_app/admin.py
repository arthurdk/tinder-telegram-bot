from bot_app.messages import *
from bot_app.data import *

class Settings:
    settings = {}
    settings["everybody_can_send_messages"] = False

    def set_setting(self, setting, value):
        if not setting in self.settings.keys():
            raise Exception("Unknown setting: " + str(setting))

        self.settings[setting] = value
        return True

    def get_setting(self, setting):
        if not setting in self.settings.keys():
            raise Exception("Unknown setting: " + str(setting))

        return self.settings[setting]

settings = Settings()

def list_settings(bot, update):
    global conversations
    global settings

    chat_id = update.message.chat_id

    message = "Settings:\n"

    for s in settings.settings.keys():
        message += s + ": " + str(settings.settings[s]) + "\n"

    send_custom_message(bot, chat_id, message)

def set_setting(bot, update, args):
    global conversations
    global settings
    global owner

    chat_id = update.message.chat_id

    if update.message.from_user.id != owner and owner is not None:
        send_error(bot, chat_id, "command_not_allowed")
        return

    if len(args) != 2:
        send_help(bot, chat_id, "set_setting", "Wrong number of arguments")
        return

    if args[0] not in settings.settings:
        send_help(bot, chat_id, "set_setting", "Unknown setting")
        return

    settings.set_setting(args[0], args[1])
    send_message(bot, chat_id, "setting_updated")