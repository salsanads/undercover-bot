import json
from enum import Enum, auto

messages_file = open("messages.json", "r")
messages = json.load(messages_file)


class CommandStatus(Enum):
    GUILD_ONLY_COMMAND = auto()


def generate_message(key, params=None):
    message = messages[key]
    if params is not None:
        message = message.format(**params)
    return message


def generate_mentions(user_ids):
    mentioned_users = []

    for user_id in user_ids:
        mentioned_users.append("<@{user_id}>".format(user_id=user_id))
    mentions = " ".join(mentioned_users)

    return mentions
