import peewee as pw
import bot_app.settings as settings

db = pw.SqliteDatabase(settings.DB_NAME)


# TODO merge those in models and conversation with conversation..
class Conversation(pw.Model):
    # id = pw.IntegerField() PEEWEE automatically adds this
    fb_auth = pw.CharField(null=True)

    class Meta:
        database = db


# TODO inclure more attribute from model.Conversation
class Vote(pw.Model):
    # id = pw.IntegerField() PEEWEE automatically adds this
    pynder_user_id = pw.CharField(null=False)
    conversation = pw.CharField(null=False)
    message_id = pw.CharField(null=False)
    class Meta:
        database = db


class User(pw.Model):
    # id = pw.IntegerField() PEEWEE automatically adds this

    class Meta:
        database = db


class IsMod(pw.Model):
    user = pw.ForeignKeyField(User)
    group = pw.ForeignKeyField(Conversation)

    class Meta:
        database = db