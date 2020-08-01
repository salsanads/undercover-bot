import json
from enum import Enum, auto

from discord.ext import commands
<<<<<<< HEAD
from discord.
=======
>>>>>>> 122000ece56221e32ce6cd69cd70649b95b9701a

messages_file = open("messages.json", "r")
messages = json.load(messages_file)


class CommandStatus(Enum):
    GUILD_ONLY_COMMAND = auto()


def generate_message(key, params=None):
    message = messages[key]
    if params is not None:
        message = message.format(**params)
    return message
<<<<<<< HEAD


def generate_playing_order(user_ids):
	mentioned_users = []

	for user_id in user_ids:
        mentioned_users.append('@<{u_id}>'.format(u_id=user_id))
	playing_order = " ".join(mentioned_users)

	return playing_order 
=======
>>>>>>> 122000ece56221e32ce6cd69cd70649b95b9701a
