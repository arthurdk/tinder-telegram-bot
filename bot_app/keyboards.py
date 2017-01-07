from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from bot_app.messages import *
import bot_app.data_retrieval as data_retrieval
import json


# Homemade enum -> will change
class InlineKeyboard:
    # SUPERLIKE = BaseInlineAction("SUPER_LIKE")
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"
    MORE_PICS = "MORE_PICS"
    BIO = "BIO"
    # BACK = BaseInlineAction("BACK")
    # NEXT = BaseInlineAction("NEXT")
    # PREVIOUS = BaseInlineAction("PREVIOUS")
    INSTAGRAM = "INSTAGRAM"

main_keyboard = ["Matches"]


def get_vote_keyboard(conversation, bot_name):
    """
    Return the vote keyboard
    :param conversation:
    :param bot_name:
    :param user_id: pynder uid
    :return:
    """
    global data
    likes, dislikes = conversation.get_stats()
    like_label = "❤️"
    dislike_label = "❌"

    if not conversation.settings.get_setting("blind_mode"):
        like_label += " (%d)" % likes
        dislike_label += " (%d)" % dislikes

    keyboard = \
        [
            [
                InlineKeyboardButton(like_label, callback_data=InlineKeyboard.LIKE),
                InlineKeyboardButton("More pictures", callback_data=InlineKeyboard.MORE_PICS),
                InlineKeyboardButton(dislike_label, callback_data=InlineKeyboard.DISLIKE)
            ],
        ]
    second_row = [
        InlineKeyboardButton("Inline pictures",
                             switch_inline_query_current_chat="pictures " + str(conversation.group_id))
    ]
    user = conversation.current_user
    # Instagram button
    instagram_user = user.instagram_username
    if instagram_user is not None:
        label = "Instagram"
        if conversation.cur_user_insta_private is None:
            conversation.cur_user_insta_private = data_retrieval.is_instagram_private(instagram_user)
        if not conversation.cur_user_insta_private:
            button = InlineKeyboardButton(label, url="http://instagram.com/%s" % instagram_user)
        else:
            button = InlineKeyboardButton(label, callback_data=InlineKeyboard.INSTAGRAM)
        second_row.append(button)

    second_row.append(InlineKeyboardButton("Matches",
                                           switch_inline_query_current_chat="matches " + str(conversation.group_id)))
    keyboard.append(second_row)
    if conversation.group_id < 0:
        keyboard.append(
            [InlineKeyboardButton(messages['switch_private'], url="https://telegram.me/%s?start=" % bot_name)])

    return InlineKeyboardMarkup(keyboard)


def switch_private_chat_keyboard(bot_name):
    keyboard = [[InlineKeyboardButton(messages['switch_private'], url="https://telegram.me/%s?start=" % bot_name)]]

    return InlineKeyboardMarkup(keyboard)


def switch_group_keyboard():
    keyboard = [[InlineKeyboardButton(messages["back_group"], switch_inline_query="")]]
    return InlineKeyboardMarkup(keyboard)


"""
One day this code will emerge from the dead.

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
"""


def get_vote_finished_keyboard():
    keyboard = \
        [
            [
                InlineKeyboardButton("More pictures", callback_data=InlineKeyboard.MORE_PICS)
            ],
        ]
    return InlineKeyboardMarkup(keyboard)
