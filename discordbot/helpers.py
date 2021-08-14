from enum import Enum, auto

import yaml

from .errors import BotPlayerFound

command_desc_file = open("commands.yaml", "r")
command_desc = yaml.load(command_desc_file, Loader=yaml.BaseLoader)

messages_file = open("messages.yaml", "r")
messages = yaml.load(messages_file, Loader=yaml.BaseLoader)

metadata_file = open("metadata.yaml", "r")
metadata = yaml.load(metadata_file, Loader=yaml.BaseLoader)


class MessageKey(Enum):
    # start message
    GAME_STARTED_INSTRUCTION = auto()

    # win message
    SUMMARY_TITLE = auto()

    # how to message
    HOW_TO_TITLE = auto()
    HOW_TO_CONTENT = auto()
    WIN_CONDITION_TITLE = auto()
    WIN_CONDITION_CONTENT = auto()

    # poll message
    POLL_GENERATING_PROCESS = auto()
    POLL_TIMER = auto()
    POLL_STARTED = auto()
    EMPTY_VOTE_FOUND = auto()
    MULTIPLE_VOTES_FOUND = auto()
    # poll instruction
    POLL_INSTRUCTION_TITLE = auto()
    POLL_INSTRUCTION_CONTENT = auto()
    # poll status
    POLL_STATUS_TITLE = auto()
    POLL_STATUS_VOTED_PLAYER_INFO = auto()
    # poll result
    POLL_RESULT_TITLE = auto()
    POLL_RESULT_VOTED_PLAYER_INFO = auto()
    POLL_RESULT_INFO = auto()
    POLL_RESULT_NO_VOTES_SUBMITTED = auto()

    # clear game message
    GAME_CLEARED = auto()

    # common error message
    DM_ONLY_COMMAND = auto()
    GUILD_ONLY_COMMAND = auto()
    BOT_PLAYER_FOUND = auto()


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


def generate_message(key, params=None):
    if isinstance(key, Enum):
        key = key.name
    message = messages[key]
    if params is not None:
        message = message.format(**params)
    return message


def retrieve_player_ids(ctx, include_author=True):
    user_ids = set()
    if include_author:
        user_ids.add(ctx.author.id)
    for user in ctx.message.mentions:
        if user.bot:
            raise BotPlayerFound
        user_ids.add(user.id)
    return list(user_ids)


async def send_message(recipient, game_state, user_id_key=None):
    if user_id_key is not None and type(game_state.data[user_id_key]) == list:
        game_state.data[user_id_key] = generate_mention(
            user_ids=game_state.data[user_id_key]
        )
    elif user_id_key is not None:
        game_state.data[user_id_key] = generate_mention(
            user_id=game_state.data[user_id_key]
        )
    message = generate_message(game_state.status, game_state.data)
    return await recipient.send(message)
