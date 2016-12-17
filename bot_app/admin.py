from bot_app.messages import *
from bot_app.ranges import *
import bot_app.data as data
from bot_app.FlexibleBoolean import FlexibleBoolean

class Settings:
    values = {}
    values["chat_mode"] = ["off", "owner", "all"]
    values["max_poll_range_size"] = Range(1, 100)
    values["max_send_range_size"] = Range(1, 10)
    values["min_votes_before_timeout"] = Range(1, 100) # Arthur it's a static limit now ;)
    values["min_timeout"] = Range(0, 3600)
    values["max_timeout"] = Range(0, 3600)
    values["send_block_time"] = Range(0, 3600)
    values["poll_block_time"] = Range(0, 3600)
    values["blind_mode"] = FlexibleBoolean(is_value=False)
    values["matches_cache_time"] = Range(0, 60)

    helps = {}
    helps["chat_mode"] = "Different modes for chatting. Off means /msg and /poll_msgs are disabled. " \
                         "Owner means, only the owner of the currenct account can use /msg, " \
                         "everybody can use /poll_msgs. All means everybody can /msg and /poll_msgs."
    helps["max_poll_range_size"] = "Maximum size of a range for the /poll_msgs command."
    helps["max_send_range_size"] = "Maximum size of a range for the /msg command."
    helps["min_votes_before_timeout"] = "Not implemented."
    helps["min_timeout"] = "The minimum value for the timeout the users can set."
    helps["max_timeout"] = "The maximum value for the timeout the users can set."
    helps["send_block_time"] = "The block time after a /msg command. In this time, nobody can send a message. " \
                               "The time is given in seconds and scales linearly with the range size of the /msg " \
                               "command. Example: send_block_time is 5 and we send '/msg 2,4-6 Hey', then the block " \
                               "time will be 20 seconds."
    helps["poll_block_time"] = "The block time after a /poll_msgs command. In this time, nobody can poll messages. " \
                               "The time is given in seconds and scales linearly with the range size of the" \
                               " /poll_msgs command. Example: poll_block_time is 5 and we send '/poll_msgs 2,4-6', " \
                               "then the block time will be 20 seconds."
    helps["blind_mode"] = "If turned one, it will hide the vote count."
    helps["matches_cache_time"] = "The time in seconds the matches for the /matches command are cached."

    def __init__(self):
        self.settings = {}
        self.settings["chat_mode"] = "off"  # Modes are off, owner and all
        self.settings["max_poll_range_size"] = "100"
        self.settings["max_send_range_size"] = "1"
        self.settings["min_votes_before_timeout"] = "1"
        self.settings["min_timeout"] = "10"
        self.settings["max_timeout"] = "86400"
        self.settings["send_block_time"] = "10"
        self.settings["poll_block_time"] = "10"
        self.settings["blind_mode"] = FlexibleBoolean("False", is_value=True)
        self.settings["matches_cache_time"] = "60"

    def set_setting(self, setting, value):
        if setting not in self.settings.keys():
            # TODO handle this one
            raise Exception("Unknown setting: " + str(setting))

        if value not in self.values[setting] and self.values[setting] is not None:
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

    for s in sorted(conversation.settings.settings.keys()):
        if conversation.settings.values[s] is None:
            message += s + ": " + str(conversation.settings.settings[s]) + "\n"
        else:
            message += s + ": " + str(conversation.settings.settings[s]) + " " + str(conversation.settings.values[s]) + "\n"

    send_custom_message(bot, chat_id, message)


def help_settings(bot, update):
    global data

    chat_id = update.message.chat_id

    message = "Settings:\n"
    for s in sorted(Settings.helps.keys()):
        message += " * " + s

        if Settings.values[s] is None:
            message += ": " + Settings.helps[s] + "\n"
        else:
            message += " " + str(Settings.values[s]) + ": " + Settings.helps[s] + "\n"

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

    value = args[1]
    if args[0] == "blind_mode":
        value = FlexibleBoolean(value, is_value=True)

    if data.conversations[chat_id].settings.set_setting(args[0], value):
        send_message(bot, chat_id, "setting_updated")
    else:
        send_message(bot, chat_id, "Unknown value for setting: " + str(args[0]) + " = " + str(args[1]))
