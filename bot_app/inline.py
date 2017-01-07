from telegram.ext.dispatcher import run_async
from bot_app import messages, keyboards, session
from telegram import TelegramError, Bot
import bot_app.data as data
from telegram import InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent


@run_async
def send_instagram_urls(private_chat_id: str, group_chat_id: str, bot, incoming_message, user):
    global data
    if group_chat_id in data.conversations:
        photos = user.instagram_photos
        max_idx = len(photos) if len(photos) < 5 else 5
        for idx, photo in enumerate(photos):
            if idx >= max_idx:
                break
            caption = " %s (%d/%d) " % (user.name, idx + 1, max_idx)

            is_msg_sent = messages.send_private_photo(caption=caption, bot=bot, url=photo['image'],
                                                      user_id=private_chat_id)

            if not is_msg_sent:
                messages.notify_start_private_chat(bot=bot,
                                                   chat_id=group_chat_id,
                                                   incoming_message=incoming_message)
                break
    else:
        messages.send_error(bot=bot, chat_id=group_chat_id, name="account_not_setup")


def do_press_inline_button(bot, update, job_queue):
    """
    Handle any inline button pressing (considering it's not an inline query nor a link)
    :param bot:
    :param update:
    :param job_queue:
    :return:
    """
    from bot_app import Bot
    global data
    try:
        chat_id = update.callback_query.message.chat_id
        query = update.callback_query
        sender = query.from_user.id
        new_vote = False
        msg_id = query.message.message_id
        if chat_id in data.conversations:
            conversation = data.conversations[chat_id]
            if query.data in keyboards.InlineKeyboard.user_based_actions:
                if conversation.is_vote_message_stored(msg_id):
                    msg_vote = conversation.get_vote_message(message_id=msg_id)
                    user = conversation.get_single_user(msg_vote.pynder_user_id)

                    if query.data == keyboards.InlineKeyboard.MORE_PICS:

                        send_more_photos(private_chat_id=sender, group_chat_id=chat_id, bot=bot,
                                         incoming_message=update.callback_query.message, user=user)

                    elif query.data == keyboards.InlineKeyboard.INSTAGRAM:
                        send_instagram_urls(private_chat_id=sender, group_chat_id=chat_id, bot=bot,
                                            incoming_message=update.callback_query.message, user=user)

                    elif query.data == keyboards.InlineKeyboard.BIO:
                        send_bio(private_chat_id=sender, group_chat_id=chat_id, bot=bot,
                                            incoming_message=update.callback_query.message, user=user)

                else:
                    # messages.send_custom_message(bot=bot, chat_id=chat_id, message="Unknown user.")
                    bot.editMessageCaption(chat_id=chat_id,
                                           message_id=query.message.message_id,
                                           caption=query.message.caption)
            else:
                if (sender in conversation.current_votes and not conversation.current_votes[sender] == query.data) \
                        or sender not in conversation.current_votes:
                    if conversation.is_vote_message_stored(msg_id) \
                            and conversation.current_user is not None \
                            and conversation.get_vote_message(msg_id).pynder_user_id == conversation.current_user.id:
                        new_vote = True
                        # Registering vote
                        conversation.current_votes[sender] = query.data
                    elif not conversation.is_vote_message_stored(msg_id):
                        # Unknown user - Remove keyboard
                        bot.editMessageCaption(chat_id=chat_id,
                                               message_id=query.message.message_id,
                                               caption=query.message.caption)
                    elif conversation.current_user is None \
                            or conversation.get_vote_message(msg_id).pynder_user_id != conversation.current_user.id:
                        # Old user - voting not allowed - Switch keyboard
                        msg_vote = conversation.get_vote_message(message_id=msg_id)
                        user = conversation.get_single_user(msg_vote.pynder_user_id)
                        keyboard = keyboards.get_vote_finished_keyboard(conversation=conversation, user=user)
                        bot.editMessageCaption(chat_id=chat_id,
                                               message_id=query.message.message_id,
                                               reply_markup=keyboard,
                                               caption=query.message.caption)

                # Schedule end of voting session
                if not data.conversations[chat_id].is_alarm_set:
                    data.conversations[chat_id].is_alarm_set = True
                    Bot.alarm_vote(bot, chat_id, job_queue)

            # Send back updated inline keyboard
            if new_vote:
                reply_markup = keyboards.get_vote_keyboard(data.conversations[chat_id],
                                                           bot_name=bot.username)
                current_vote = len(conversation.get_votes())
                max_vote = conversation.settings.get_setting("min_votes_before_timeout")
                caption = messages.get_caption_match(conversation.current_user, current_vote, max_vote, bio=True)
                bot.editMessageCaption(chat_id=chat_id,
                                       message_id=query.message.message_id,
                                       reply_markup=reply_markup,
                                       caption=caption)
        else:
            messages.send_error(bot=bot, chat_id=chat_id, name="account_not_setup")
    # will catch when pressing same button twice # TODO fix the rotating icon
    except TelegramError as e:
        raise e


def inline_preview(bot: Bot, update):
    """

    :param bot:
    :param update:
    :return:
    """
    global data
    query = update.inline_query.query
    # Return on empty query
    if not query:
        return
    if update.inline_query.offset:
        offset = int(update.inline_query.offset)
    else:
        offset = 0

    args = query.split(" ")
    if len(args) != 2:
        return
    mode = args[0]
    if mode not in ["pictures", "matches"]:
        return

    chat_id = int(args[1])
    if chat_id not in data.conversations:
        return

    conversation = data.conversations[chat_id]
    user_id = update.inline_query.from_user.id
    chat_member = bot.getChatMember(user_id=user_id, chat_id=chat_id)
    if chat_member.status == chat_member.KICKED or chat_member.status == chat_member.LEFT:
        return
    results = list()
    last_idx = 0
    cache = 60
    cpt = 0
    if mode == "matches":
        matches = conversation.get_matches()

        for idx, match in enumerate(matches):
            if idx >= offset:
                thumb = match.user.get_photos(width='84')[0]
                full = match.user.get_photos(width='640')[0]

                results.append(InlineQueryResultPhoto(id=idx, caption=match.user.name, description=match.user.name,
                                                      photo_width=640,
                                                      thumb_url=thumb,
                                                      photo_url=full))
                last_idx = idx + 1
                cpt += 1
                if cpt > 20:
                    break
    elif mode == "pictures":
        cur_user = conversation.current_user
        thumbs = cur_user.get_photos(width='84')
        fulls = cur_user.get_photos(width='640')
        for idx, pic in enumerate(thumbs):
            if idx >= offset:
                thumb = pic
                full = fulls[idx]

                results.append(InlineQueryResultPhoto(id=idx, caption="%s %d/%d" % (cur_user.name, idx, len(thumbs)),
                                                      description=cur_user.name,
                                                      photo_width=640,
                                                      thumb_url=thumb,
                                                      photo_url=full))
                last_idx = idx + 1

        cache = conversation.timeout
        if cache > 0:
            cache -= 1

    bot.answerInlineQuery(update.inline_query.id, results, cache_time=cache, next_offset=last_idx)


@run_async
def send_bio(private_chat_id: str, group_chat_id: str, bot: Bot, incoming_message, user):
    """
    :param user:  Pynder user object
    :param incoming_message:
    :param private_chat_id:
    :param group_chat_id:
    :param bot:
    :return:
    """
    global data
    if group_chat_id in data.conversations:
        bio = messages.get_bio(user)
        is_msg_sent = messages.send_private_message(bot=bot, user_id=private_chat_id, text=bio)

        if not is_msg_sent:
            messages.notify_start_private_chat(bot=bot,
                                               chat_id=group_chat_id,
                                               incoming_message=incoming_message)
    else:
        messages.send_error(bot=bot, chat_id=group_chat_id, name="account_not_setup")


@run_async
def send_more_photos(private_chat_id: str, group_chat_id: str, bot: Bot, incoming_message, user):
    """
    Function used for sending all user pictures to private chat directly
    :param user: Pynder user object
    :param incoming_message:
    :param private_chat_id:
    :param group_chat_id:
    :param bot:
    :return:
    """
    global data
    if group_chat_id in data.conversations:

        photos = user.get_photos(width='320')
        for idx, photo in enumerate(photos):
            caption = " %s (%d/%d) " % (user.name, idx + 1, len(photos))

            is_msg_sent = messages.send_private_photo(bot=bot, caption=caption, url=photo, user_id=private_chat_id)

            if not is_msg_sent:
                messages.notify_start_private_chat(bot=bot,
                                                   chat_id=group_chat_id,
                                                   incoming_message=incoming_message)
                break

    else:
        messages.send_error(bot=bot, chat_id=group_chat_id, name="account_not_setup")


def is_user_allowed(self, chat_id, user_id):
    pass
