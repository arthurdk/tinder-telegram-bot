#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from telegram.ext import InlineQueryHandler
from telegram import ChatAction, error, Bot, Update
from telegram.ext import Updater, CommandHandler, Job, CallbackQueryHandler, Filters, MessageHandler
from telegram.ext.dispatcher import run_async
import logging
import pynder
import time
import bot_app.db_model as db
import peewee as pw
from bot_app.model import Conversation
import bot_app.chat as chat
import bot_app.admin as admin
from bot_app.messages import *
import bot_app.data as data
import bot_app.session as session
import bot_app.prediction as prediction
import bot_app.data_retrieval as data_retrieval
import bot_app.keyboards as keyboards
import re
import traceback
import math
import bot_app.inline as inline
import git
from bot_app.settings import location_search_url

if settings.DEBUG_MODE:
    log_level = logging.DEBUG
else:
    log_level = logging.ERROR

logging.basicConfig(level=log_level,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def start(bot: Bot, update: Update):
    """
    Handle /start command
    :param bot:
    :param update:
    :return:
    """
    chat_id = update.message.chat_id
    # TODO if using already logging in -> do not display welcome message
    send_message(bot, chat_id, "welcome")


def send_location(latitude, longitude, bot, chat_id):
    bot.sendLocation(chat_id, latitude=latitude, longitude=longitude)


def update_location(bot: Bot, update: Update):
    """
    Handle location being sent in the conversation
    :param bot:
    :param update:
    :return:
    """
    location = update.message.location
    set_location(bot, update, [location.latitude, location.longitude])


def set_location(bot: Bot, update: Update, args):
    """
    Handles /location command
    :param bot:
    :param update:
    :param args:
    :return:
    """
    global data
    chat_id = update.message.chat_id
    if chat_id in data.conversations:
        if len(args) < 1:
            send_help(bot, chat_id, "set_location", "Please indicate GPS coordinates or the name of a place")
            return
        else:
            bot.sendChatAction(chat_id=chat_id, action=ChatAction.FIND_LOCATION)
            r = requests.get("{}{}?format=json&limit=1&bounded=0"
                             .format(location_search_url, ' '.join([str(x) for x in args])))
        try:
            conversation = data.conversations[chat_id]
            latitude = r.json()[0]["lat"]
            longitude = r.json()[0]["lon"]
            conversation.session.update_location(latitude, longitude)
            send_message(bot, chat_id, "location_updated")
            conversation.refresh_users()
            send_location(latitude=latitude, longitude=longitude, bot=bot, chat_id=chat_id)
        except AttributeError:
            send_help(bot, chat_id, "set_location", "Facebook token needs to be set first")
    else:
        send_error(bot=bot, chat_id=chat_id, name="account_not_setup")


def set_timeout(bot: Bot, update: Update, args):
    """
    Handles /timeout command
    :param bot:
    :param update:
    :param args:
    :return:
    """
    global data
    chat_id = update.message.chat_id
    if chat_id in data.conversations:
        if len(args) != 1:
            timeout = str(data.conversations[chat_id].timeout)
            message = "Current timeout %s seconds." % timeout
            send_custom_message(bot, chat_id, message=message)
        else:
            try:
                timeout = int(args[0])
                settings = data.conversations[chat_id].settings

                if int(settings.get_setting("min_timeout")) <= timeout <= int(
                        settings.get_setting("max_timeout")):
                    data.conversations[chat_id].timeout = timeout
                    message = "Timeout updated to %d seconds." % data.conversations[chat_id].timeout
                    send_custom_message(bot, chat_id, message=message)
                else:
                    send_custom_message(bot, chat_id, "Timeout out of range: "
                                        + str(settings.get_setting("min_timeout")) + "-"
                                        + str(settings.get_setting("max_timeout")))
            except AttributeError:
                message = "An error happened."
                send_custom_message(bot, chat_id, message=message)
    else:
        send_error(bot=bot, chat_id=chat_id, name="account_not_setup")


@run_async
def set_auto(bot: Bot, update: Update):
    """
    Handles /auto command
    :param bot:
    :param update:
    :return:
    """
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
def send_matches(bot: Bot, update: Update):
    """
    Send list of matches (pictures) to private chat
    :param bot:
    :param update:
    :return:
    """
    global data
    chat_id = update.message.chat_id
    sender_id = update.message.from_user.id
    if chat_id in data.conversations:
        try:
            conversation = data.conversations[chat_id]
            matches = conversation.get_matches()
            id = 0
            # TODO cache the photo urls for some time
            for match in matches:
                photo = match.user.get_photos(width='172')[0]
                try:
                    is_msg_sent = send_private_photo(bot=bot, caption=match.user.name + " ID=" + str(id), url=photo,
                                                     user_id=sender_id)

                    if not is_msg_sent:
                        notify_start_private_chat(bot=bot,
                                                  chat_id=chat_id,
                                                  incoming_message=update.message)
                        break
                    id += 1
                except error.BadRequest:
                    bot.sendMessage(sender_id, text="One match could not be loaded: %s" % photo)
                time.sleep(0.1)
        except AttributeError as e:
            message = "An error happened."
            bot.sendMessage(sender_id, text=message)
    else:
        send_error(bot=bot, chat_id=chat_id, name="account_not_setup")


def start_vote_session(bot: Bot, update: Update, job_queue):
    """
    Handles /new_vote command
    :param bot:
    :param update:
    :param job_queue:
    :return:
    """
    chat_id = update.message.chat_id
    job = Job(start_vote, 0, repeat=False, context=(chat_id, job_queue))
    job_queue.put(job)


def start_vote(bot, job):
    """
    Actually handles the /new_vote command
    :param bot:
    :param job:
    :return:
    """
    global data
    chat_id, job_queue = job.context
    # If conversation is already registered
    if chat_id in data.conversations:
        conversation = data.conversations[chat_id]
        # Check if no vote is already happening
        if not conversation.is_voting:
            conversation.set_is_voting(True)
            # Fetch nearby users
            retry = 0
            bot.sendChatAction(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
            try:

                while retry < 3 and len(conversation.users) == 0:
                    conversation.refresh_users()
                    retry += 1
                # Check if there are still users in the queue
                if len(conversation.users) == 0:
                    conversation.set_is_voting(False)
                    send_error(bot=bot, chat_id=chat_id, name="no_more_users")
                else:
                    # Empty the vote list
                    conversation.current_votes = {}
                    # Choose user
                    conversation.current_user = conversation.users[0]
                    del conversation.users[0]
                    conversation.cur_user_insta_private = None
                    # Retrieve photos
                    photos = conversation.current_user.get_photos(width='320')
                    max_vote = conversation.settings.get_setting("min_votes_before_timeout")
                    caption = get_caption_match(conversation.current_user, 0, max_vote, bio=True)
                    # Prepare inline keyboard for voting
                    reply_markup = keyboards.get_vote_keyboard(conversation=conversation, bot_name=bot.username)
                    msg = bot.sendPhoto(chat_id, photo=photos[0], caption=caption,
                                        reply_markup=reply_markup)
                    # Why? Before this commit a question was sent to the group along with the photo.
                    # TODO => refactor properly
                    conversation.vote_msg = msg
                    conversation.result_msg = msg

                    if settings.prediction_backend is not None \
                            and conversation.settings.get_setting(setting="prediction"):
                        prediction_job = Job(prediction.do_prediction, 0,
                                             repeat=False,
                                             context=(chat_id, conversation.current_user.id, msg.message_id))
                        job_queue.put(prediction_job)
            except pynder.errors.RequestError as e:
                conversation.set_is_voting(False)
                if session.is_timeout_error(e):
                    session.do_reconnect(bot=bot, chat_id=chat_id, conversation=conversation)
                else:
                    send_error(bot=bot, chat_id=chat_id, name="new_vote_failed")
                if settings.DEBUG_MODE:
                    traceback.print_exc()
            except BaseException as e:
                conversation.set_is_voting(False)
                send_error(bot=bot, chat_id=chat_id, name="new_vote_failed")
                if settings.DEBUG_MODE:
                    traceback.print_exc()
        else:
            bot.sendMessage(chat_id, text="Current vote is not finished yet.",
                            reply_to_message_id=conversation.vote_msg.message_id)
    else:
        send_error(bot=bot, chat_id=chat_id, name="account_not_setup")


def unlink(bot: Bot, update: Update):
    """
    Handles /unlink command
    :param bot:
    :param update:
    :return:
    """
    global data
    sender = update.message.from_user.id
    chat_id = update.message.chat_id
    if chat_id in data.conversations:
        if sender == data.conversations[chat_id].owner:
            del data.conversations[chat_id]
            send_message(bot, chat_id, name="account_unlinked")
        else:
            send_error(bot, chat_id=chat_id, name="command_not_allowed")
    else:
        send_error(bot, chat_id=chat_id, name="account_not_setup")


def set_account(bot: Bot, update: Update):
    """
    Handles /set_account command
    :param bot:
    :param update:
    :return:
    """
    global data
    sender = update.message.from_user.id
    data.change_account_queries[sender] = update.message.chat_id
    msg = messages["ask_for_token"]

    group_name = update.message.chat.title
    if len(group_name) > 0:
        msg += " for chat %s" % group_name

    is_msg_sent = send_private_message(bot, user_id=sender, text=msg)
    # Check if user already allowed bot to send private messages
    if not is_msg_sent:
        notify_start_private_chat(bot=bot,
                                  chat_id=data.change_account_queries[sender],
                                  incoming_message=update.message)
    # If the bot is not used in a private chat, display a button allowing user to easily switch to the private chat
    elif sender != data.change_account_queries[sender]:
        keyboard = keyboards.switch_private_chat_keyboard(bot.username)
        notify_send_token(bot=bot, is_group=True,
                          chat_id=data.change_account_queries[sender],
                          reply_to_message_id=update.message.message_id, group_name=group_name,
                          reply_markup=keyboard)


def dynamic_timeout_formular(min_votes, votes_fraction):
    """
    Formula used for dynamic timeout
    :param min_votes:
    :param votes_fraction:
    :return:
    """
    if votes_fraction >= 1:
        return 1 / votes_fraction  # Reduce timeout if more people than necessary voted

    result = 1
    result += (1 - votes_fraction) * math.log2(min_votes)  # Linear part makes timeout rise
    result += min_votes * (
    min_votes ** ((1 - votes_fraction) ** 3) - 1)  # Exponential part to punish really low vote counts
    result += (40 - 40 ** (votes_fraction)) / min_votes ** 2  # Punish missing votes harder if min_votes is low
    return result


def wait_for_vote_timeout(conversation: Conversation):
    """
    Wait until the vote is finished (following the settings)
    :param conversation:
    :return:
    """
    min_votes = int(conversation.settings.get_setting(setting="min_votes_before_timeout"))
    timeout_mode = conversation.settings.get_setting(setting="timeout_mode")
    starting_time = -1

    # Wait for the number of required votes
    while (len(conversation.current_votes) < min_votes and len(conversation.current_votes) < 5) \
            or timeout_mode == "dynamic":
        if len(conversation.current_votes) > 0 and starting_time == -1:
            starting_time = time.time()

        time.sleep(1)
        min_votes = int(conversation.settings.get_setting(setting="min_votes_before_timeout"))

        if timeout_mode == "dynamic" and len(conversation.current_votes) > 0:
            votes_fraction = len(conversation.current_votes) / min_votes
            current_time = time.time()

            if current_time > starting_time + conversation.timeout * dynamic_timeout_formular(min_votes,
                                                                                              votes_fraction):
                break

    if timeout_mode == "required_votes":
        time.sleep(conversation.timeout)
    elif timeout_mode == "first_vote":
        time.sleep(max(0, conversation.timeout + starting_time - time.time()))


@run_async
def alarm_vote(bot: Bot, chat_id: str, job_queue):
    """
    Handles the end of a voting session
    :param bot:
    :param chat_id:
    :param job_queue:
    :return:
    """
    global data

    conversation = data.conversations[chat_id]
    wait_for_vote_timeout(conversation)
    # Update the message to show that vote is ended
    msg = conversation.result_msg
    likes, dislikes = conversation.get_stats()
    message = "%d likes, %d dislikes " % (likes, dislikes)
    current_vote = len(conversation.get_votes())
    max_vote = conversation.settings.get_setting("min_votes_before_timeout")
    caption = get_caption_match(conversation.current_user, current_vote, max_vote, bio=False)
    try:
        bot.editMessageCaption(chat_id=msg.chat_id,
                               message_id=msg.message_id,
                               caption=caption + "\n%s" % message)
    except BaseException:
        traceback.print_exc()
    conversation.set_is_voting(False)
    conversation.is_alarm_set = False
    try:
        if likes > dislikes:
            conversation.current_user.like()
        else:
            conversation.current_user.dislike()
    except pynder.errors.RequestError as e:
        if e.args[0] == 401:
            session.do_reconnect(bot=bot, chat_id=chat_id, conversation=conversation)
            send_error(bot=bot, chat_id=chat_id, name="failed_to_vote")
        else:
            send_error(bot=bot, chat_id=chat_id, name="failed_to_vote")
    except BaseException:
        send_error(bot=bot, chat_id=chat_id, name="failed_to_vote")
    # Store vote for future prediction processing
    if conversation.settings.get_setting("store_votes"):
        data_retrieval.do_store_vote(user_id=conversation.current_user.id,
                                     chat_id=chat_id,
                                     is_like=likes > dislikes)

    # If the bot is set to auto -> launch another vote
    if conversation.auto:
        job = Job(start_vote, 0, repeat=False, context=(chat_id, job_queue))
        job_queue.put(job)


def message_handler(bot: Bot, update: Update, job_queue):
    """
    Handles incoming text based messages
    :param job_queue:
    :param bot:
    :param update:
    :return:
    """
    global data

    chat_id = update.message.chat_id
    sender = update.message.from_user.id
    text = update.message.text
    # Check action from main menu
    if text in keyboards.main_keyboard:
        send_matches_menu(bot, chat_id)
    # Check if someone is trying to login
    elif sender in data.change_account_queries and chat_id == sender:
        session.do_login(bot=bot, chat_id=chat_id, sender=sender,
                         token=update.message.text, job_queue=job_queue)

    # Ignore reply to the bot in groups
    elif sender in data.change_account_queries.keys():
        if data.change_account_queries[sender] == sender:
            update.message.reply_text(error_messages["unknown_command"])
    # TODO: THIS SHOULD BE SOMEWHERE ELSE I SUPPOSE
    elif text.strip() == "YES":
        if chat_id not in data.make_me_mod_queries.keys():
            return

        group_id = data.make_me_mod_queries[chat_id]
        del data.make_me_mod_queries[chat_id]

        if group_id not in data.conversations.keys():
            send_error(bot=bot, chat_id=group_id, name="account_not_setup")
            return

        conversation = data.conversations[group_id]
        mod_candidate = conversation.current_mod_candidate
        conversation.current_mod_candidate = None

        mod_candidate_entry = db.User.get_or_create(id=mod_candidate.id)[0]
        conversation_entry = db.Conversation.get_or_create(id=group_id)[0]

        mod_candidate_id = mod_candidate_entry.id
        conversation_entry_id = conversation_entry.id

        query = db.IsMod.select().where((db.IsMod.user == mod_candidate_id) & (db.IsMod.group == conversation_entry_id))

        if not query.exists():
            db.IsMod.create(user=mod_candidate_entry, group=conversation_entry)
            bot.sendMessage(chat_id, text="Mod added.")
            # Inform group to notify that a new user can become a candidate
            bot.sendMessage(group_id, text="Mod " + mod_candidate.name + " added.")
        else:
            bot.sendMessage(chat_id, text="User is already a mod.")
            bot.sendMessage(group_id, text="User " + mod_candidate.name + " was already a mod.")

    # Abort all running transactions between the users and the bot
    else:
        if chat_id in data.make_me_mod_queries.keys():
            group_id = data.make_me_mod_queries[chat_id]
            del data.make_me_mod_queries[chat_id]
            bot.sendMessage(chat_id, text="Mod request denied.")

            if group_id in data.conversations.keys():
                msg = "User " + data.conversations[group_id].current_mod_candidate.name + " was not made a mod."
                send_custom_message(bot, chat_id=group_id, message=msg)
                data.conversations[group_id].current_mod_candidate = None


@run_async
def send_about(bot: Bot, update: Update):
    """
    Send the about message from the /about command
    :param bot:
    :param update:
    :return:
    """
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    msg = messages["about"] + "\nLast commit [%s](https://github.com/arthurdk/tinder-telegram-bot/commit/%s)" % (sha, sha)
    chat_id = update.message.chat_id
    send_custom_message(bot=bot, chat_id=chat_id, message=msg)


def send_matches_menu(bot: Bot, chat_id: str):
    """
    Not implemented yet.
    :param bot:
    :param chat_id:
    :return:
    """
    global data
    if chat_id in data.conversations:
        conversation = data.conversations[chat_id]
        bot.sendMessage(chat_id=chat_id, text="Matches menu", reply_markup=keyboards.get_matches_menu(conversation))
    else:
        send_error(bot=bot, chat_id=chat_id, name="account_not_setup")


def custom_command_handler(bot: Bot, update: Update):
    """
    /msg command. Preserves whitespace. Leaves error handling to the chat.send_message method
    :param bot:
    :param update:
    :return:
    """
    if update.message.text.startswith('/msg'):
        text = update.message.text[4:].strip()

        if text.startswith("@"):
            splitter = re.search("\s", text).start()

            if splitter is not None:
                text = text[splitter:].strip()

        splitter = re.search("\s", text).start()

        if splitter is None:
            args = [text]
        else:
            args = [text[:splitter].strip(), text[splitter:].strip()]

        chat.send_message(bot, update, args)
    else:
        unknown(bot, update)


def main():
    db.db.connect()

    try:
        db.db.create_tables([db.Conversation, db.User, db.IsMod])
    except pw.OperationalError:
        pass

    updater = Updater(settings.KEY)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', send_help_message))

    dispatcher.add_handler(CommandHandler('auto', set_auto))
    dispatcher.add_handler(CommandHandler('location', set_location, pass_args=True))
    dispatcher.add_handler(CommandHandler('set_account', set_account))
    dispatcher.add_handler(CommandHandler('unlink', unlink))
    dispatcher.add_handler(CommandHandler('matches', send_matches))
    dispatcher.add_handler(CallbackQueryHandler(inline.do_press_inline_button, pass_job_queue=True))
    dispatcher.add_handler(MessageHandler(Filters.text, message_handler, pass_job_queue=True))
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

    # Moderators
    dispatcher.add_handler(CommandHandler('make_me_a_mod', admin.make_me_a_mod))

    inline_caps_handler = InlineQueryHandler(inline.inline_preview)
    dispatcher.add_handler(inline_caps_handler)

    dispatcher.add_handler(MessageHandler(Filters.command, custom_command_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
