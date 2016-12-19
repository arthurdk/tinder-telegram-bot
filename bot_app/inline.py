from telegram.ext.dispatcher import run_async
from bot_app import messages, keyboards
from telegram import TelegramError

@run_async
def send_instagram_urls(private_chat_id, group_chat_id, bot, incoming_message):
    global data
    if group_chat_id in data.conversations:
        conversation = data.conversations[group_chat_id]
        if conversation.is_voting:
            user = conversation.current_user
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
            message = "There is not vote going on right now."
            bot.sendMessage(private_chat_id, text=message)
    else:
        messages.send_error(bot=bot, chat_id=group_chat_id, name="account_not_setup")


def do_press_inline_button(bot, update, job_queue):
    from bot_app import Bot
    global data
    try:
        chat_id = update.callback_query.message.chat_id
        query = update.callback_query
        sender = query.from_user.id
        new_vote = False
        conversation = data.conversations[chat_id]
        if query.data == keyboards.InlineKeyboard.MORE:
            send_more_photos(private_chat_id=sender, group_chat_id=chat_id, bot=bot,
                             incoming_message=update.callback_query.message)
        elif query.data == keyboards.InlineKeyboard.INSTAGRAM:
            send_instagram_urls(private_chat_id=sender, group_chat_id=chat_id, bot=bot,
                                incoming_message=update.callback_query.message)
        else:
            if (sender in conversation.current_votes and not conversation.current_votes[sender] == query.data) \
                    or sender not in conversation.current_votes:
                new_vote = True
                conversation.current_votes[sender] = query.data
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

    # will catch when pressing same button twice # TODO fix the rotating icon
    except TelegramError as e:
        raise e


@run_async
def send_more_photos(private_chat_id, group_chat_id, bot, incoming_message):
    """
    Function used for sending all pictures to private chat directly
    :param incoming_message:
    :param private_chat_id:
    :param group_chat_id:
    :param bot:
    :return:
    """
    global data
    if group_chat_id in data.conversations:
        if data.conversations[group_chat_id].is_voting:

            photos = data.conversations[group_chat_id].current_user.get_photos(width='320')
            for idx, photo in enumerate(photos):
                caption = " %s (%d/%d) " % (data.conversations[group_chat_id].current_user.name, idx + 1, len(photos))

                is_msg_sent = messages.send_private_photo(bot=bot, caption=caption, url=photo, user_id=private_chat_id)

                if not is_msg_sent:
                    messages.notify_start_private_chat(bot=bot,
                                                       chat_id=group_chat_id,
                                                       incoming_message=incoming_message)
                    break

        else:
            message = "There is not vote going on right now."
            bot.sendMessage(private_chat_id, text=message)
    else:
        messages.send_error(bot=bot, chat_id=group_chat_id, name="account_not_setup")
