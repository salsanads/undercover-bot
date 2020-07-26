import json
from enum import Enum, auto

from discord.ext import commands

messages_file = open("messages.json", "r")
messages = json.load(messages_file)


class CommandStatus(Enum):
    GUILD_ONLY_COMMAND = auto()


def generate_message(key, params=None):
    message = messages[key]
    if params is not None:
        message = message.format(**params)
    return message
