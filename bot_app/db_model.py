import peewee as pw
import bot_app.settings as settings

db = pw.SqliteDatabase(settings.DB_NAME)


class Conversation(pw.Model):
    id = pw.CharField()

    class Meta:
        database = db
