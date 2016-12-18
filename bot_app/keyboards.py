from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from bot_app.model import *


def get_vote_keyboard(conversation):
    global data
    likes, dislikes = conversation.get_stats()
    like_label = "❤️"
    dislike_label = "❌"

    if not conversation.settings.get_setting("blind_mode").get_value():
        like_label += " (%d)" % likes
        dislike_label += " (%d)" % dislikes

    keyboard = [[InlineKeyboardButton(like_label, callback_data=Vote.LIKE),
                 InlineKeyboardButton("More pictures", callback_data=Vote.MORE),
                 InlineKeyboardButton(dislike_label, callback_data=Vote.DISLIKE)],
                [InlineKeyboardButton("Inline pictures",
                                      switch_inline_query_current_chat="pictures "+str(conversation.group_id)),
                 InlineKeyboardButton("Matches",
                                      switch_inline_query_current_chat="matches " + str(conversation.group_id))]]

    return InlineKeyboardMarkup(keyboard)


def get_main_keyboard():

    keyboard = [[KeyboardButton("/set_account", callback_data=Vote.LIKE),
                 KeyboardButton("/matches", callback_data=Vote.MORE),
                 KeyboardButton("/list_settings", callback_data=Vote.DISLIKE)],
                [KeyboardButton("Inline pictures"),
                 KeyboardButton("/help"),
                 KeyboardButton("/poll_unanswered")]]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, selective=True)