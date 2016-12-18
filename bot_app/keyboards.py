from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


# Homemade enum
class InlineKeyboard:
    SUPERLIKE = "SUPERLIKE"
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"
    MORE = "MORE"
    BACK = "BACK"
    NEXT = "NEXT"
    PREVIOUS = "PREVIOUS"
#    BIO = "BIO"

main_keyboard = ["Matches"]


def get_vote_keyboard(conversation):
    global data
    likes, dislikes = conversation.get_stats()
    like_label = "❤️"
    dislike_label = "❌"

    if not conversation.settings.get_setting("blind_mode").get_value():
        like_label += " (%d)" % likes
        dislike_label += " (%d)" % dislikes

    keyboard = [[InlineKeyboardButton(like_label, callback_data=InlineKeyboard.LIKE),
                 InlineKeyboardButton("More pictures", callback_data=InlineKeyboard.MORE),
                 InlineKeyboardButton(dislike_label, callback_data=InlineKeyboard.DISLIKE)],
                [InlineKeyboardButton("Inline pictures",
                                      switch_inline_query_current_chat="pictures "+str(conversation.group_id)),
                 InlineKeyboardButton("Matches",
                                      switch_inline_query_current_chat="matches " + str(conversation.group_id))]]

    return InlineKeyboardMarkup(keyboard)


def change_chat_keyboard(txt):

    keyboard = [[InlineKeyboardButton(txt, switch_inline_query="")]]

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