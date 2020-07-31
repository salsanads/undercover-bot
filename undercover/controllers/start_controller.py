import random

from undercover import GameState, Role, Status
from undercover.models import PlayingRole, SecretWord

from .helpers import decide_playing_order, ongoing_game_found

MR_WHITE_WORD = "^^"
# player_num: (civilian_num, undercover_num, mr_white_num)
ROLE_PROPORTIONS = {
    3: (2, 1, 0),
    4: (3, 1, 0),
    5: (3, 1, 1),
    6: (4, 1, 1),
    7: (4, 2, 1),
    8: (5, 2, 1),
    9: (5, 3, 1),
    10: (6, 3, 1),
    11: (6, 3, 2),
    12: (7, 3, 2),
    13: (7, 4, 2),
    14: (8, 4, 2),
    15: (8, 5, 2),
    16: (9, 5, 2),
    17: (9, 5, 3),
    18: (10, 5, 3),
    19: (10, 6, 3),
    20: (11, 6, 3),
}


@ongoing_game_found(False)
def start(room_id, user_ids):
    if not player_num_valid(len(user_ids)):
        data = {"min_player": 0, "max_player": 0}  # TODO
        return GameState(Status.INVALID_PLAYER_NUMBER, data)

    playing_users = get_playing_users(user_ids)
    if len(playing_users) > 0:
        data = {"playing_users": playing_users}
        return GameState(Status.PLAYING_USER_FOUND, data)

    role_proportion = ROLE_PROPORTIONS[len(user_ids)]
    civilian_num, undercover_num, mr_white_num = role_proportion
    civilian_word, undercover_word = get_secret_word()

    store_playing_role(room_id, civilian_word, undercover_word, mr_white_num)
    user_words, mr_whites = assign_role(
        user_ids, civilian_word, undercover_word, role_proportion
    )

    playing_order = decide_playing_order(user_ids, mr_whites)
    data = {"user_words": user_words, "playing_order": playing_order}
    return GameState(Status.PLAYING_ORDER, data)


def player_num_valid(player_num):
    return player_num in ROLE_PROPORTIONS


def get_playing_users(user_ids):
    # TODO
    return []


def get_secret_word():
    secret_word = SecretWord.get_random()
    related_words = secret_word.related_words
    random.shuffle(related_words)
    return related_words[0], related_words[1]


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
    for user_id in user_ids:
        if len(user_words) < civilian_num:
            user_words[user_id] = {"word": civilian_word}
            # TODO store
        elif len(user_words) < civilian_num + undercover_num:
            user_words[user_id] = {"word": undercover_word}
            # TODO store
        else:
            user_words[user_id] = {"word": MR_WHITE_WORD}
            # TODO store
            mr_whites.add(user_id)
    return user_words, mr_whites
