import bot_app.settings as settings
import os as os


def do_store_vote(user_id, is_like, chat_id, chat_name=""):
    folder_path = "%s%s" % (settings.data_retrieval_path, get_unique_folder_name(chat_id=chat_id))
    ensure_folder_exists(folder_path)
    if is_like:
        file = "likes"
    else:
        file = "dislikes"
    file_path = "%s/%s" % (folder_path, file)
    append_to_file(path=file_path, user_id=user_id)


def ensure_folder_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def append_to_file(path, user_id):
    with open(path, 'a+') as f:
        f.write("%s\n" % user_id)


def get_unique_folder_name(chat_id):
    name = "%s" % (str(chat_id))
    return name.replace(" ", "_")