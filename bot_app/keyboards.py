from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from bot_app.messages import *

# Homemade enum
class InlineKeyboard:
    SUPERLIKE = "SUPERLIKE"
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"
    MORE = "MORE"
    BACK = "BACK"
    NEXT = "NEXT"
    PREVIOUS = "PREVIOUS"


# BIO = "BIO"

main_keyboard = ["Matches"]


def get_vote_keyboard(conversation):
    global data
    likes, dislikes = conversation.get_stats()
    like_label = "❤️"
    dislike_label = "❌"

    if not bool(conversation.settings.get_setting("blind_mode")):
        like_label += " (%d)" % likes
        dislike_label += " (%d)" % dislikes

    keyboard = [[InlineKeyboardButton(like_label, callback_data=InlineKeyboard.LIKE),
                 InlineKeyboardButton("More pictures", callback_data=InlineKeyboard.MORE),
                 InlineKeyboardButton(dislike_label, callback_data=InlineKeyboard.DISLIKE)],
                ]
    second_row = []
    second_row.append(InlineKeyboardButton("Inline pictures",
                                           switch_inline_query_current_chat="pictures " + str(conversation.group_id)))
    instagram_user = conversation.current_user.instagram_username
    if instagram_user is not None:
        second_row.append(InlineKeyboardButton("Instagram",
                                               url="http://instagram.com/%s" % instagram_user))

    second_row.append(InlineKeyboardButton("Matches",
                                           switch_inline_query_current_chat="matches " + str(conversation.group_id)))
    keyboard.append(second_row)
    return InlineKeyboardMarkup(keyboard)


def switch_private_chat_keyboard(bot_name):
    keyboard = [[InlineKeyboardButton(messages['switch_private'], url="https://telegram.me/%s?start=" % bot_name)]]

    return InlineKeyboardMarkup(keyboard)


def switch_group_keyboard():
    keyboard = [[ InlineKeyboardButton(messages["back_group"], switch_inline_query="")]]
    return InlineKeyboardMarkup(keyboard)


def get_main_keyboard():
    keyboard = [[KeyboardButton("/set_account"),
                 KeyboardButton("/auto")],
                [KeyboardButton("/new_vote"),
                 KeyboardButton("Matches"),
                 KeyboardButton("/poll_unanswered")],
                [
                    KeyboardButton("/help_settings"),
                    KeyboardButton("/help"),
                    KeyboardButton("/list_settings")
                ]]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, selective=True)


def get_matches_menu(conversation):
    keyboard = [[InlineKeyboardButton("Quick view",
                                      switch_inline_query_current_chat="matches " + str(conversation.group_id)),
                 InlineKeyboardButton("Private pictures", callback_data=InlineKeyboard.MORE),
                 InlineKeyboardButton("Conversation", callback_data=("test", "test2"))]
                ]

    return InlineKeyboardMarkup(keyboard)


def get_conversation_menu(conversation):
    keyboard = [[InlineKeyboardButton("Previous",
                                      switch_inline_query_current_chat="matches " + str(conversation.group_id)),
                 InlineKeyboardButton("<< Back", callback_data=InlineKeyboard.MORE),
                 InlineKeyboardButton("Next", callback_data=InlineKeyboard.DISLIKE)]
                ]
    # Add matches
    nb_cur_row = 0
    cur_row = []
    for match in conversation.get_matches():
        if nb_cur_row >= 3:
            nb_cur_row = 0
            keyboard.append(cur_row)
            cur_row = []
        cur_row.append(InlineKeyboardButton(match.user.name, callback_data=InlineKeyboard.DISLIKE))
    keyboard.append(cur_row)
    return InlineKeyboardMarkup(keyboard)
