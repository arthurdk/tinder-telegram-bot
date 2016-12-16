from bot_app.messages import *
import bot_app.data as data

class Settings:
    settings = {}
    settings["everybody_can_send_messages"] = False
    settings["enable_message_polling"] = False

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
    global settings

    chat_id = update.message.chat_id

    message = "Settings:\n"

    for s in settings.settings.keys():
        message += s + ": " + str(settings.settings[s]) + "\n"

    send_custom_message(bot, chat_id, message)

def set_setting(bot, update, args):
    global data
    global settings

    chat_id = update.message.chat_id

    if update.message.from_user.id != data.owner and data.owner is not None:
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

def ensure_setting_is_unset(bot, chat_id, name, bypass = True):
    global settings

    if bypass:
        return False

    if not settings.get_setting(name):
        send_custom_message(bot, chat_id, "Error: " + name + " not set.")
        return True

    return False