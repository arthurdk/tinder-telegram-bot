from bot_app.messages import *
from bot_app.value_types import *
import bot_app.data as data
import bot_app.settings as settings


class Setting:
    def __init__(self, name, valid_values, help_message):
        self.name = name
        self.value = str(settings.settings_defaults[name])
        self.valid_values = valid_values
        self.help_message = help_message

    def get_default_value(self):
        return self.value

    def value_str(self, value):
        return "`" + self.name + "`: `" + str(value) + "` [" + str(self.valid_values) + "]"

    def help_str(self):
        return " - /" + self.name + " " + str(self.valid_values) + ": " + self.help_message

    def __contains__(self, item):
        return item in self.valid_values


class Settings:
    settings = {
        "chat_mode": Setting("chat_mode", String(["off", "owner", "all"]),
                             "Different modes for chatting. Off means /msg and /poll_msgs are disabled. Owner means, "
                             "only the owner of the current account can use /msg, everybody can use /poll_msgs. All "
                             "means everybody can /msg and /poll_msgs."),
        "max_poll_range_size": Setting("max_poll_range_size", Range(1, 100),
                                       "Maximum size of a range for the /poll_msgs command."),
        "max_send_range_size": Setting("max_send_range_size", Range(1, 10),
                                       "Maximum size of a range for the /msg command."),
        "min_votes_before_timeout": Setting("min_votes_before_timeout", Range(1, 5),
                                            "Number of votes required to end the session."),
        "min_timeout": Setting("min_timeout", Range(10, 3600), "The minimum value for the timeout the users can set."),
        "max_timeout": Setting("max_timeout", Range(10, 3600), "The maximum value for the timeout the users can set."),
        "send_block_time": Setting("send_block_time", Range(0, 600),
                                   "The block time after a /msg command. In this time, nobody can send a message. The "
                                   "time is given in seconds and scales linearly with the range size of the /msg "
                                   "command. Example: send_block_time is 5 and we send '/msg 2,4-6 Hey', then the "
                                   "block time will be 20 seconds."),
        "poll_block_time": Setting("poll_block_time", Range(0, 60),
                                    "The block time after a /poll_msgs command. In this time, nobody can poll "
                                    "messages. The time is given in seconds and scales linearly with the range size of "
                                    "the /poll_msgs command. Example: poll_block_time is 5 and we send "
                                    "'/poll_msgs 2,4-6', then the block time will be 20 seconds."),
        "blind_mode": Setting("blind_mode", Boolean(), "If turned one, it will hide the vote count."),
        "matches_cache_time": Setting("matches_cache_time", Range(0, 60),
                                      "The time in seconds the matches for the /matches command are cached."),
        "timeout_mode": Setting("timeout_mode", String(["first_vote", "required_votes", "dynamic"]),
                                "Different modes for the timeout. 'first_vote' starts the timeout as soon as the first "
                                "vote was cast. The vote doesn't end before the required amount of nodes is reached."
                                "'required_votes' starts the timeout after the required amount of votes has been "
                                "reached. 'dynamic' allows voting to finish before the required amount of votes has "
                                "been reached, but with a higher timeout.")
    }

    def __init__(self):
        self.values = {}

        for setting in Settings.settings.keys():
            self.values[setting] = Settings.settings[setting].get_default_value()

    def set_setting(self, setting, value):
        if setting not in Settings.settings.keys():
            raise Exception("Unknown setting: " + str(setting))

        if value not in Settings.settings[setting]:
            return False

        self.values[setting] = Settings.settings[setting].valid_values.convert(value)
        return True

    def get_setting(self, setting):
        if setting not in Settings.settings.keys():
            raise Exception("Unknown setting: " + str(setting))

        value = self.values[setting]
        return Settings.settings[setting].valid_values.convert(value)


def list_settings(bot, update):
    global data

    chat_id = update.message.chat_id

    if chat_id not in data.conversations:
        send_error(bot, chat_id, "account_not_setup")
        return

    settings = data.conversations[chat_id].settings
    message = "*Settings*:\n"

    for s in sorted(Settings.settings.keys()):
        message += Settings.settings[s].value_str(settings.values[s]) + "\n"

    send_custom_message(bot, chat_id, message)


def help_settings(bot, update):
    global data

    chat_id = update.message.chat_id

    message = "*Settings*:\n"
    for s in sorted(Settings.settings.keys()):
        message += Settings.settings[s].help_str() + "\n"

    send_custom_message(bot, chat_id, message)


def set_setting(bot, update, args):
    global data

    chat_id = update.message.chat_id
    sender = update.message.from_user.id

    if chat_id not in data.conversations:
        send_error(bot, chat_id, "account_not_setup")
        return

    conversation = data.conversations[chat_id]

    if sender != conversation.owner and conversation.owner is not None:
        send_error(bot, chat_id, "command_not_allowed")
        return

    if len(args) != 2:
        send_help(bot, chat_id, "set_setting", "Wrong number of arguments")
        return

    key = args[0]
    value = args[1]

    if key not in conversation.settings.settings:
        send_help(bot, chat_id, "set_setting", "Unknown setting")
        return

    if conversation.settings.set_setting(args[0], value):
        send_message(bot, chat_id, "setting_updated")
    else:
        send_message(bot, chat_id, "Unknown value for setting: " + str(key) + " = " + str(value))