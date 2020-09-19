import json
from enum import Enum, auto

messages_file = open("messages.json", "r")
messages = json.load(messages_file)


class CommandStatus(Enum):
    DM_ONLY_COMMAND = auto()
    GUILD_ONLY_COMMAND = auto()
    HOW_TO = auto()
    HUMAN_PLAYER_ONLY = auto()


def generate_message(key, params=None):
    message = messages[key]
    if params is not None:
        message = message.format(**params)
    return message


def generate_mention(user_id=None, user_ids=None, style="{mention}"):
    if user_id is None and user_ids is None:
        raise ValueError("Cannot have both user_id and user_ids None")
    elif user_id is not None and user_ids is not None:
        raise ValueError("Cannot have both user_id and user_ids not None")

    if user_id is not None:
        mention = "<@{user_id}>".format(user_id=user_id)
        return style.format(mention=mention)

    mentions = []
    for user_id in user_ids:
        mentions.append(generate_mention(user_id=user_id, style=style))
    one_line_mentions = " ".join(mentions)
    return one_line_mentions
