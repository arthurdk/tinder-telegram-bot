import peewee as pw
import bot_app.settings as settings

db = pw.SqliteDatabase(settings.DB_NAME)


class Conversation(pw.Model):
    # id = pw.IntegerField() PEEWEE automatically adds this
    fb_auth = pw.CharField(null=True)

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