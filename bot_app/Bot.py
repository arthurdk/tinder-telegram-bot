from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, TelegramError
from telegram.ext import Updater, CommandHandler, Job, CallbackQueryHandler, Filters, MessageHandler
from telegram.ext.dispatcher import run_async
import logging
import pynder
import time
# from bot_app.db_model import Conversation, db
import bot_app.settings as settings
from bot_app.model import Conversation, Vote
# import peewee as pw


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

global change_account_queries
change_account_queries = {}
global conversations
conversations = {}


def start(bot, update):
    chat_id = update.message.chat_id
    message = 'Hey ! \nFirst thing first, you will need to set your Facebook authentication ' \
              'token using the /set_account command'
    bot.sendMessage(chat_id, text=message)

'''
def set_fb_auth(bot, update, args):
    chat_id = update.message.chat_id
    if len(args) != 1:
        message = "You need to send your Facebook authentication token along with the command"
        bot.sendMessage(chat_id, text=message)
    else:
        try:
            # arse_mode=ParseMode.MARKDOWN
            create_pynder_session(args[0])
            message = "Switching to %s account. \nConnect a group" % t_session.profile.name
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Choose a group", url="https://telegram.me/tindergroupbot?startgroup=test")]])
            bot.sendMessage(chat_id=chat_id, text=message,
                            reply_markup=keyboard)
        except pynder.errors.RequestError:
            message = "Authentication failed! Please try again."
            bot.sendMessage(chat_id, text=message)
'''


def create_pynder_session(fb_token):
    return pynder.Session(facebook_token=fb_token)


def send_location(latitude, longitude, bot, chat_id):
    bot.sendLocation(chat_id, latitude=latitude, longitude=longitude)


def set_location(bot, update, args):
    global conversations
    chat_id = update.message.chat_id
    if chat_id in conversations:
        if len(args) != 2:
            message = "You need to send your location the command (latitude and longitude)"
        else:
            try:
                latitude = args[0]
                longitude = args[1]
                conversations[chat_id].session.update_location(latitude, longitude)
                message = "Location updated."
                send_location(latitude=latitude, longitude=longitude, bot=bot, chat_id=chat_id)
            except AttributeError:
                message = "Facebook token needs to be set up first."
        bot.sendMessage(chat_id, text=message)


def set_timeout(bot, update, args):
    global conversations
    chat_id = update.message.chat_id
    if chat_id in conversations:
        if len(args) != 1:
            message = "You need to send the time in second along with the the command"
        else:
            try:
                conversations[chat_id].timeout = int(args[0])
                message = "Timeout updated to %d seconds." % conversations[chat_id].timeout
            except AttributeError:
                message = "An error happened."
        bot.sendMessage(chat_id, text=message)


def start_vote_session(bot, update, job_queue):
    chat_id = update.message.chat_id
    job = Job(start_vote, 0, repeat=False, context=chat_id)
    job_queue.put(job)


def get_question_match(conversation):
    name = " %s (%d y.o)" % (conversation.current_user.name, conversation.current_user.age)
    return "So what do you think of %s?" % name


def start_vote(bot, job):
    global conversations
    chat_id = job.context
    if chat_id in conversations:
        conversation = conversations[chat_id]
        if not conversation.is_voting:
            conversation.set_is_voting(True)
            # Fetch nearby users
            while len(conversation.users) == 0:
                conversation.refresh_users()
            conversation.current_user = conversation.users[0]
            del conversation.users[0]
            # Reinit votes
            conversation.current_votes = {}
            photos = conversation.current_user.get_photos(width='320')
            name = " %s (%d y.o)" % (conversation.current_user.name, conversation.current_user.age)
            bot.sendPhoto(job.context, photo=photos[0], caption=name)

            # Prepare voting inline keyboard
            reply_markup = get_vote_keyboard(chat_id=chat_id)
            message = get_question_match(conversation=conversation)
            msg = bot.sendMessage(job.context, text=message, reply_markup=reply_markup)
            conversation.result_msg = msg
        else:
            bot.sendMessage(job.context, text="Current vote is not finished yet.")
    else:
        bot.sendMessage(job.context, text="Chat not registered yet, please add token.")


def get_vote_keyboard(chat_id):
    global conversations
    if chat_id in conversations:
        likes, dislikes = conversations[chat_id].get_stats()
        like_label = "❤️ (%d)" % likes
        dislike_label = "❌ (%d)" % dislikes
        keyboard = [[InlineKeyboardButton(like_label, callback_data=Vote.LIKE),
                     InlineKeyboardButton(dislike_label, callback_data=Vote.DISLIKE)],
                    [InlineKeyboardButton("More pictures", callback_data=Vote.MORE),
                     InlineKeyboardButton("Bio", callback_data=Vote.BIO)]]

        return InlineKeyboardMarkup(keyboard)
    else:
        return InlineKeyboardMarkup([[]])


def do_vote(bot, update, job_queue):
    chat_id = update.callback_query.message.chat_id
    query = update.callback_query
    sender = query.from_user.id

    if query.data == Vote.MORE:
        send_more_photos(private_chat_id=sender, group_chat_id=chat_id, bot=bot)
    elif query.data == Vote.BIO:
        send_bio(private_chat_id=sender, group_chat_id=chat_id, bot=bot)
    else:
        conversations[chat_id].current_votes[sender] = query.data
        # Schedule end of voting session
        if not conversations[chat_id].is_alarm_set:
            conversations[chat_id].is_alarm_set = True
            alarm_vote(bot, chat_id)
            """
            t_alarm = threading.Thread(target=alarm_vote, args=(bot, chat_id))
            t_alarm.daemon = True
            t_alarm.run()
            """

    # Send back updated inline keyboard
    reply_markup = get_vote_keyboard(chat_id=chat_id)
    bot.editMessageText(reply_markup=reply_markup,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=get_question_match(conversation=conversations[chat_id]))

@run_async
def send_more_photos(private_chat_id, group_chat_id, bot):
    """
    Function used for sending all pictures to private chat directly
    :param private_chat_id:
    :param group_chat_id:
    :param bot:
    :return:
    """
    global conversations
    if group_chat_id in conversations:
        if conversations[group_chat_id].is_voting:
            photos = conversations[group_chat_id].current_user.get_photos(width='320')
            for idx, photo in enumerate(photos):
                caption = " %s (%d/%d) " % (conversations[group_chat_id].current_user.name, idx + 1, len(photos))
                bot.sendPhoto(private_chat_id, photo=photo, caption=caption)
        else:
            message = "There is not vote going on right now."
            bot.sendMessage(private_chat_id, text=message)


def send_bio(private_chat_id, group_chat_id, bot):
    global conversations
    if group_chat_id in conversations:
        if conversations[group_chat_id].is_voting:
            msg = " %s \n %s" % (conversations[group_chat_id].current_user.name,
                                 conversations[group_chat_id].current_user.bio)
            bot.sendMessage(private_chat_id, text=msg)
        else:
            message = "There is not vote going on right now."
            bot.sendMessage(private_chat_id, text=message)


def set_account(bot, update):
    global change_account_queries
    sender = update.message.from_user.id
    change_account_queries[sender] = update.message.chat_id
    msg = "Send me your facebook authentication token"
    bot.sendMessage(sender, text=msg)

@run_async
def alarm_vote(bot, chat_id):
    conversation = conversations[chat_id]
    time.sleep(conversation.timeout)
    msg = conversation.result_msg
    likes, dislikes = conversation.get_stats()
    message = "%d likes, %d dislikes " % (likes, dislikes)
    bot.editMessageText(chat_id=msg.chat_id, message_id=msg.message_id, text=message)
    conversation.set_is_voting(False)
    conversation.is_alarm_set = False
    if likes > dislikes:
        conversation.current_user.like()
    else:
        conversation.current_user.dislike()


def message_handler(bot, update):
    global conversations
    global change_account_queries
    chat_id = update.message.chat_id
    sender = update.message.from_user.id
    if sender in change_account_queries:
        try:
            # Create Tinder session
            session = create_pynder_session(update.message.text)
            message = "Switching to %s account." % session.profile.name
            bot.sendMessage(chat_id=change_account_queries[sender], text=message)
            # Create conversation
            conversation = Conversation(change_account_queries[sender], session)
            conversations[change_account_queries[sender]] = conversation
            del change_account_queries[sender]
        except pynder.errors.RequestError:
            message = "Authentication failed! Please try again."
            bot.sendMessage(chat_id, text=message)
    else:
        update.message.reply_text("I'm sorry Dave I'm afraid I can't do that.")


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
    dispatcher.add_handler(CommandHandler('location', set_location, pass_args=True))
    dispatcher.add_handler(CommandHandler('set_account', set_account))
    dispatcher.add_handler(CallbackQueryHandler(do_vote, pass_job_queue=True))
    dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    dispatcher.add_handler(CommandHandler('new_vote', start_vote_session, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler('timeout', set_timeout, pass_args=True))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
