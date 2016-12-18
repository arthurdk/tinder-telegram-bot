#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
from telegram.ext import InlineQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, TelegramError, error
from telegram.ext import Updater, CommandHandler, Job, CallbackQueryHandler, Filters, MessageHandler
from telegram.ext.dispatcher import run_async
import logging
import pynder
import time
# from bot_app.db_model import Conversation, db
from bot_app.model import Conversation
import bot_app.chat as chat
import bot_app.admin as admin
from bot_app.messages import *
import bot_app.data as data
import bot_app.prediction as prediction
import bot_app.data_retrieval as data_retrieval
import bot_app.keyboards as keyboards
import threading
import time
import re

# import peewee as pw
from bot_app.settings import location_search_url

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

change_account_queries = {}


def start(bot, update):
    chat_id = update.message.chat_id
    send_message(bot, chat_id, "welcome")


def create_pynder_session(fb_token):
    return pynder.Session(facebook_token=fb_token)


def send_location(latitude, longitude, bot, chat_id):
    bot.sendLocation(chat_id, latitude=latitude, longitude=longitude)


def update_location(bot, update):
    location = update.message.location
    set_location(bot, update, [location.latitude, location.longitude])


def set_location(bot, update, args):
    global data
    chat_id = update.message.chat_id
    if chat_id in data.conversations:
        if len(args) < 1:
            send_help(bot, chat_id, "set_location", "Please indicate coordinates or the name of a place")
            return
        else:
            r = requests.get("{}{}?format=json&limit=1&bounded=0"
                             .format(location_search_url, ' '.join([str(x) for x in args])))
        try:
            latitude = r.json()[0]["lat"]
            longitude = r.json()[0]["lon"]
            data.conversations[chat_id].session.update_location(latitude, longitude)
            send_message(bot, chat_id, "location_updated")
            data.conversations[chat_id].refresh_users()
            send_location(latitude=latitude, longitude=longitude, bot=bot, chat_id=chat_id)
        except AttributeError as e:
            send_help(bot, chat_id, "set_location", "Facebook token needs to be set first")
    else:
        send_error(bot=bot, chat_id=chat_id, name="account_not_setup")


def set_timeout(bot, update, args):
    global data
    chat_id = update.message.chat_id
    if chat_id in data.conversations:
        if len(args) != 1:
            message = "You need to send the time in seconds along with the command"
        else:
            try:
                timeout = int(args[0])
                settings = data.conversations[chat_id].settings

                if int(settings.get_setting("min_timeout")) <= timeout and timeout <= int(
                        settings.get_setting("max_timeout")):
                    data.conversations[chat_id].timeout = timeout
                    message = "Timeout updated to %d seconds." % data.conversations[chat_id].timeout
                else:
                    send_custom_message(bot, chat_id, "Timeout out of range: "
                                        + str(settings.get_setting("min_timeout")) + "-"
                                        + str(settings.get_setting("max_timeout")))
            except AttributeError:
                message = "An error happened."
        bot.sendMessage(chat_id, text=message)
    else:
        send_error(bot=bot, chat_id=chat_id, name="account_not_setup")


def set_auto(bot, update):
    global data
    chat_id = update.message.chat_id
    if chat_id in data.conversations:
        data.conversations[chat_id].auto = not data.conversations[chat_id].auto
        if data.conversations[chat_id].auto:
            message = "Automatic mode enabled."
        else:
            message = "Automatic mode disabled."
        bot.sendMessage(chat_id, text=message)
    else:
        send_error(bot=bot, chat_id=chat_id, name="account_not_setup")


@run_async
def send_matches(bot, update):
    global data
    chat_id = update.message.chat_id
    sender_id = update.message.from_user.id
    if chat_id in data.conversations:
        try:
            conversation = data.conversations[chat_id]

            matches = conversation.get_matches()

            id = 0

            for match in matches:
                photo = match.user.get_photos(width='172')[0]
                try:
                    is_msg_sent = send_private_photo(bot=bot, caption=match.user.name + " ID=" + str(id), url=photo,
                                                     user_id=sender_id)

                    if not is_msg_sent:
                        notify_start_private_chat(bot=bot,
                                                  chat_id=chat_id,
                                                  incoming_message_id=update.message.message_id)
                        break
                    id += 1
                except error.BadRequest:
                    bot.sendMessage(sender_id, text="One match could not be loaded: %s" % photo)
                time.sleep(0.1)
        except AttributeError as e:
            message = "An error happened."
            bot.sendMessage(sender_id, text=message)
            print(e)
    else:
        send_error(bot=bot, chat_id=chat_id, name="account_not_setup")


def start_vote_session(bot, update, job_queue):
    chat_id = update.message.chat_id
    job = Job(start_vote, 0, repeat=False, context=(chat_id, job_queue))
    job_queue.put(job)


def start_vote(bot, job):
    global data
    chat_id, job_queue = job.context
    if chat_id in data.conversations:
        conversation = data.conversations[chat_id]
        if not conversation.is_voting:
            conversation.set_is_voting(True)
            # Fetch nearby users
            retry = 0
            while retry < 3 and len(conversation.users) == 0:
                conversation.refresh_users()
                retry += 1
            # Check if there are still user in the queue
            if len(conversation.users) == 0:
                bot.sendMessage(chat_id, text="There are no other users available.")
            else:
                conversation.current_votes = {}
                # Assign user
                try:
                    conversation.current_user = conversation.users[0]
                    del conversation.users[0]

                    # Retrieve photos
                    photos = conversation.current_user.get_photos(width='320')
                    name = " %s (%d y.o)" % (conversation.current_user.name, conversation.current_user.age)
                    # Append bio to caption if it's not empty
                    if len(conversation.current_user.bio) > 0:
                        name += "\n" + data.conversations[chat_id].current_user.bio
                    msg = bot.sendPhoto(chat_id, photo=photos[0], caption=name)
                    conversation.vote_msg = msg
                    # Prepare voting inline keyboard
                    reply_markup = keyboards.get_vote_keyboard(conversation=conversation)
                    message = get_question_match(conversation=conversation)
                    msg2 = bot.sendMessage(chat_id, text=message, reply_markup=reply_markup)
                    conversation.result_msg = msg2
                    # Launch prediction
                    prediction_job = Job(prediction.do_prediction, 0,
                                         repeat=False,
                                         context=(chat_id, conversation.current_user.id, msg.message_id))
                    job_queue.put(prediction_job)
                except BaseException as e:
                    conversation.set_is_voting(False)
        else:
            bot.sendMessage(chat_id, text="Current vote is not finished yet.",
                            reply_to_message_id=conversation.vote_msg.message_id)
    else:
        send_error(bot=bot, chat_id=chat_id, name="account_not_setup")


def do_press_inline_button(bot, update, job_queue):
    global data
    try:
        chat_id = update.callback_query.message.chat_id
        query = update.callback_query
        sender = query.from_user.id

        if query.data == keyboards.InlineKeyboard.MORE:
            send_more_photos(private_chat_id=sender, group_chat_id=chat_id, bot=bot,
                             incoming_message_id=update.callback_query.message.message_id)
        else:
            data.conversations[chat_id].current_votes[sender] = query.data
            # Schedule end of voting session
            if not data.conversations[chat_id].is_alarm_set:
                data.conversations[chat_id].is_alarm_set = True
                alarm_vote(bot, chat_id, job_queue)

        # Send back updated inline keyboard
        reply_markup = keyboards.get_vote_keyboard(data.conversations[chat_id])
        bot.editMessageText(reply_markup=reply_markup,
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id,
                            text=get_question_match(conversation=data.conversations[chat_id]))
    # will catch when pressing same button twice # TODO fix the rotating icon
    except TelegramError:
        pass


@run_async
def send_more_photos(private_chat_id, group_chat_id, bot, incoming_message_id):
    """
    Function used for sending all pictures to private chat directly
    :param incoming_message_id:
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

                is_msg_sent = send_private_photo(bot=bot, caption=caption, url=photo, user_id=private_chat_id)

                if not is_msg_sent:
                    notify_start_private_chat(bot=bot,
                                              chat_id=group_chat_id,
                                              incoming_message_id=incoming_message_id)
                    break

        else:
            message = "There is not vote going on right now."
            bot.sendMessage(private_chat_id, text=message)
    else:
        send_error(bot=bot, chat_id=group_chat_id, name="account_not_setup")


def set_account(bot, update):
    global change_account_queries
    sender = update.message.from_user.id
    change_account_queries[sender] = update.message.chat_id
    msg = messages["ask_for_token"]

    group_name = update.message.chat.title
    if len(group_name) > 0:
        msg += " for chat %s" % group_name

    is_msg_sent = send_private_message(bot, user_id=sender, text=msg)

    if not is_msg_sent:
        notify_start_private_chat(bot=bot,
                                  chat_id=change_account_queries[sender],
                                  incoming_message_id=update.message.message_id)
    elif update.message.chat.type == "group":
        keyboard = keyboards.change_chat_keyboard(messages["switch_private"])
        notify_send_token(bot=bot, is_group=True,
                          chat_id=change_account_queries[sender],
                          reply_to_message_id=update.message.message_id, group_name=group_name,
                          reply_markup=keyboard)


@run_async
def alarm_vote(bot, chat_id, job_queue):
    global data

    conversation = data.conversations[chat_id]

    min_votes = int(conversation.settings.get_setting(setting="min_votes_before_timeout"))
    # Wait for the number of required votes
    while len(conversation.current_votes) < min_votes and len(conversation.current_votes) < 5:
        time.sleep(conversation.timeout)
        min_votes = int(conversation.settings.get_setting(setting="min_votes_before_timeout"))

    msg = conversation.result_msg
    likes, dislikes = conversation.get_stats()
    message = "%d likes, %d dislikes " % (likes, dislikes)
    bot.editMessageText(chat_id=msg.chat_id, message_id=msg.message_id, text=message)

    if likes > dislikes:
        result = True
        conversation.current_user.like()
    else:
        result = False
        conversation.current_user.dislike()

    data_retrieval.do_store_vote(user_id=conversation.current_user.id,
                                 chat_id=chat_id,
                                 is_like=result)

    conversation.set_is_voting(False)
    conversation.is_alarm_set = False
    if conversation.auto:
        job = Job(start_vote, 0, repeat=False, context=(chat_id, job_queue))
        job_queue.put(job)


def message_handler(bot, update):
    global data
    global admin
    global change_account_queries

    chat_id = update.message.chat_id
    sender = update.message.from_user.id
    text = update.message.text
    # Check action from main menu
    if text in keyboards.main_keyboard:
        send_matches_menu(bot, chat_id)
    # Check login
    elif sender in change_account_queries:
        try:
            # Create Tinder session
            session = create_pynder_session(update.message.text)
            message = "Switching to %s account." % session.profile.name
            bot.sendMessage(chat_id=change_account_queries[sender], text=message)
            if sender != change_account_queries[sender]:
                bot.sendMessage(chat_id=sender, text=message,
                                reply_markup=keyboards.change_chat_keyboard(messages["back_group"]))
            # Create conversation
            conversation = Conversation(change_account_queries[sender], session, sender)
            data.conversations[change_account_queries[sender]] = conversation
            del change_account_queries[sender]
        except pynder.errors.RequestError:
            message = "Authentication failed! Please try again."
            bot.sendMessage(chat_id, text=message)

    # Ignore reply to the bot in groups
    elif update.message.chat.type != "group":
        update.message.reply_text(error_messages["unknown_command"])


def send_about(bot, update):
    chat_id = update.message.chat_id
    # bot.sendMessage(chat_id=chat_id, text="test", reply_markup=keyboards.get_main_keyboard())
    message = messages["about"]
    bot.sendMessage(chat_id, text=message)


def send_matches_menu(bot, chat_id):
    global data
    if chat_id in data.conversations:
        conversation = data.conversations[chat_id]
        bot.sendMessage(chat_id=chat_id, text="Matches menu", reply_markup=keyboards.get_matches_menu(conversation))
    else:
        send_error(bot=bot, chat_id=chat_id, name="account_not_setup")


def custom_command_handler(bot, update):
    # /msg command. Preserves whitespace. Leaves error handling to the chat.send_message method
    if update.message.text.startswith('/msg'):
        text = update.message.text[4:].strip()
        splitter = re.search("\s", text).start()
        print(splitter)

        if splitter is None:
            args = [text]
        else:
            args = [text[:splitter].strip(), text[splitter:].strip()]

        chat.send_message(bot, update, args)
    else:
        unknown(bot, update)


def main():
    """
    db.connect()

    try:
        db.create_tables([Conversation])
    except pw.OperationalError:
        pass
    """
    updater = Updater(settings.KEY)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', send_help_message))

    dispatcher.add_handler(CommandHandler('auto', set_auto))
    dispatcher.add_handler(CommandHandler('location', set_location, pass_args=True))
    dispatcher.add_handler(CommandHandler('set_account', set_account))
    dispatcher.add_handler(CommandHandler('matches', send_matches))
    dispatcher.add_handler(CallbackQueryHandler(do_press_inline_button, pass_job_queue=True))
    dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    dispatcher.add_handler(MessageHandler(Filters.location, update_location))
    dispatcher.add_handler(CommandHandler('new_vote', start_vote_session, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler('timeout', set_timeout, pass_args=True))
    dispatcher.add_handler(CommandHandler('about', send_about))

    # Chat functionality
    dispatcher.add_handler(CommandHandler('poll_msgs', chat.poll_messages, pass_args=True))
    dispatcher.add_handler(CommandHandler('poll_unanswered', chat.poll_unanswered_messages, pass_args=True))
    dispatcher.add_handler(CommandHandler('unblock', chat.unblock))

    # Settings
    dispatcher.add_handler(CommandHandler('set_setting', admin.set_setting, pass_args=True))
    dispatcher.add_handler(CommandHandler('list_settings', admin.list_settings))
    dispatcher.add_handler(CommandHandler('help_settings', admin.help_settings))

    inline_caps_handler = InlineQueryHandler(chat.inline_preview)
    dispatcher.add_handler(inline_caps_handler)

    dispatcher.add_handler(MessageHandler(Filters.command, custom_command_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
