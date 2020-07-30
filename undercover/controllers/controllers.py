import random
from enum import Enum

from undercover import GameState, Status
from undercover.models import PlayingRole, SecretWord


class Role(Enum):
    CIVILIAN = 1
    UNDERCOVER = 2
    MR_WHITE = 3


def start(room_id, user_ids):
    if ongoing_game_exists(room_id):
        return GameState(Status.ONGOING_GAME_FOUND)

    if not player_num_valid(len(user_ids)):
        data = {"min_player": 0, "max_player": 0}  # TODO
        return GameState(Status.INVALID_PLAYER_NUMBER, data)

    playing_users = get_playing_users(user_ids)
    if len(playing_users) > 0:
        data = {"playing_users": playing_users}
        return GameState(Status.PLAYING_USER_FOUND, data)

    role_proportion = get_role_proportion(len(user_ids))
    civilian_num, undercover_num, mr_white_num = role_proportion

    civilian_word, undercover_word = get_secret_word()
    store_playing_role(room_id, civilian_word, undercover_word, mr_white_num)
    user_words, mr_whites = assign_role(
        user_ids, civilian_word, undercover_word, role_proportion
    )
    playing_order = decide_playing_order(user_ids, mr_whites)
    data = {"user_words": user_words, "playing_order": playing_order}
    return GameState(Status.PLAYING_ORDER, data)


def ongoing_game_exists(room_id):
    # TODO
    pass


def player_num_valid(player_num):
    # TODO
    pass


def get_playing_users(user_ids):
    # TODO
    return []


def get_role_proportion(player_num):
    # TODO
    return 0, 0, 0


def get_secret_word():
    secret_word = SecretWord.get_random()
    flipped = bool(random.getrandbits(1))
    if flipped:
        return secret_word.word_2, secret_word.word_1
    return secret_word.word_1, secret_word.word_2


def store_playing_role(room_id, civilian_word, undercover_word, mr_white_num):
    PlayingRole.insert(PlayingRole(room_id, Role.CIVILIAN.name, civilian_word))
    PlayingRole.insert(
        PlayingRole(room_id, Role.UNDERCOVER.name, undercover_word)
    )
    if mr_white_num > 0:
        PlayingRole.insert(PlayingRole(room_id, Role.MR_WHITE.name))


def assign_role(user_ids, civilian_word, undercover_word, role_proportion):
    civilian_num, undercover_num, mr_white_num = role_proportion
    random.shuffle(user_ids)
    user_words = {}
    mr_whites = set()
    while len(user_words) < civilian_num:
        # TODO
        pass
    while len(user_words) < civilian_num + undercover_num:
        # TODO
        pass
    while len(user_words) < civilian_num + undercover_num + mr_white_num:
        # TODO
        pass
    return user_words, mr_whites


def decide_playing_order(user_ids, mr_whites):
    # TODO
    return []
