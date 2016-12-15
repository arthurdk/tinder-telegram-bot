from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, Job, CallbackQueryHandler, Filters
import logging
import pynder
import sched, time
from bot_app.db_model import Conversation, db
import bot_app.settings as settings


# Homemade enum
class Vote:
    SUPERLIKE = "SUPERLIKE"
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"
    MORE = "MORE"
    BIO = "BIO"


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

global t_session
t_session = None
global users
users = None
global is_voting
is_voting = False
global current_vote


def start(bot, update):
    chat_id = update.message.chat_id
    message = 'Hey !'
    bot.sendMessage(chat_id, text=message)


def set_fb_auth(bot, update, args):
    chat_id = update.message.chat_id
    if len(args) != 1:
        message = "You need to send your Facebook auth with the command"
        bot.sendMessage(chat_id, text=message)
    else:
        create_pynder_session(args[0])
        message = "Switching to %s account." % t_session.profile.name
        bot.sendMessage(chat_id, text=message)


def create_pynder_session(fb_token):
    global t_session
    t_session = pynder.Session(facebook_token=fb_token)
    get_users()


def get_users():
    global users
    global t_session
    users = t_session.nearby_users()


def set_location(bot, update, args):
    chat_id = update.message.chat_id
    if len(args) != 2:
        message = "You need to send your location the command (latitude and longitude)"
    else:
        try:
            latitude = args[0]
            longitude = args[1]
            t_session.update_location(latitude, longitude)
            message = "Location updated."
        except AttributeError:
            message = "Facebook token needs to be set up first."
    bot.sendMessage(chat_id, text=message)


def start_vote_session(bot, update, job_queue):
    chat_id = update.message.chat_id
    job = Job(start_vote, 0, repeat=False, context=chat_id)
    job_queue.put(job)


def get_question_match():
    name = " %s (%d y.o)" % (current_vote['user'].name, current_vote['user'].age)
    return "So what do you think of %s?" % name


def start_vote(bot, job):
    global is_voting
    global current_vote
    current_vote = {}
    if not is_voting:
        is_voting = True
        current_vote['votes'] = {}
        while len(users) == 0:
            get_users()
        current_vote['user'] = users[0]
        del users[0]

        photos = current_vote['user'].get_photos(width='320')
        name = " %s (%d y.o)" % (current_vote['user'].name, current_vote['user'].age)
        bot.sendPhoto(job.context, photo=photos[0], caption=name)

        reply_markup = get_vote_keyboard()
        message = get_question_match()
        msg = bot.sendMessage(job.context, text=message, reply_markup=reply_markup)

        s = sched.scheduler(time.time, time.sleep)
        s.enter(10, 1, alarm_vote, argument=(bot, job, msg))
        s.run()

    else:
        pass


def get_stats(votes):
    likes = 0
    dislikes = 0
    for _, value in votes.items():
        if value == Vote.LIKE:
            likes += 1
        elif value == Vote.DISLIKE:
            dislikes += 1
    return likes, dislikes


def get_vote_keyboard():
    likes, dislikes = get_stats(current_vote['votes'])
    like_label = "❤️ (%d)" % likes
    dislike_label = "❌ (%d)" % dislikes
    keyboard = [[InlineKeyboardButton(like_label, callback_data=Vote.LIKE),
                 InlineKeyboardButton(dislike_label, callback_data=Vote.DISLIKE)],
                [InlineKeyboardButton("More pictures", callback_data=Vote.MORE),
                 InlineKeyboardButton("Bio", callback_data=Vote.BIO)]]

    return InlineKeyboardMarkup(keyboard)


def do_vote(bot, update):
    query = update.callback_query
    sender = query.from_user.id
    if query.data == Vote.MORE:
        send_more_photos(sender, bot)
    elif query.data == Vote.BIO:
        send_bio(sender, bot)
    else:
        current_vote['votes'][sender] = query.data

    reply_markup = get_vote_keyboard()
    bot.editMessageText(reply_markup=reply_markup,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=get_question_match())


def send_more_photos(chat_id, bot):
    global is_voting
    if is_voting:
        photos = current_vote['user'].get_photos(width='320')
        for idx, photo in enumerate(photos):
            caption = " %s (%d/%d) " % (current_vote['user'].name, idx + 1, len(photos))
            bot.sendPhoto(chat_id, photo=photo, caption=caption)
    else:
        message = "There is not vote going on right now."
        bot.sendMessage(chat_id, text=message)


def send_bio(chat_id, bot):
    global is_voting
    if is_voting:
        msg = " %s \n %s" % (current_vote['user'].name, current_vote['user'].bio)
        bot.sendMessage(chat_id, text=msg)
    else:
        message = "There is not vote going on right now."
        bot.sendMessage(chat_id, text=message)


def alarm_vote(bot, job, msg):
    global is_voting
    is_voting = False
    likes, dislikes = get_stats(current_vote['votes'])
    message = "%d likes, %d dislikes " % (likes, dislikes)
    bot.editMessageText(chat_id=msg.chat_id, message_id=msg.message_id, text=message)



db.connect()
db.create_tables([Conversation])

updater = Updater(settings.KEY)

dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('fb_token', set_fb_auth, pass_args=True))
dispatcher.add_handler(CommandHandler('location', set_location, pass_args=True))
dispatcher.add_handler(CallbackQueryHandler(do_vote))
dispatcher.add_handler(CommandHandler('start_vote', start_vote_session, pass_job_queue=True))
updater.start_polling()
updater.idle()
