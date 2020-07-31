import random
from functools import wraps

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


def player_num_valid(func):
    @wraps(func)
    def wrapper(room_id, user_ids, *args, **kwargs):
        if len(user_ids) not in ROLE_PROPORTIONS:
            data = {
                "min_player": min(ROLE_PROPORTIONS),
                "max_player": max(ROLE_PROPORTIONS),
            }
            return [GameState(Status.INVALID_PLAYER_NUMBER, data)]
        return func(room_id, user_ids, *args, **kwargs)

    return wrapper


def playing_users_not_found(func):
    @wraps(func)
    def wrapper(room_id, user_ids, *args, **kwargs):
        playing_users = []  # TODO query
        if len(playing_users) > 0:
            data = {"playing_users": playing_users}
            return [GameState(Status.PLAYING_USER_FOUND, data)]
        return func(room_id, user_ids, *args, **kwargs)

    return wrapper


@ongoing_game_found(False)
@player_num_valid
@playing_users_not_found
def start(room_id, user_ids):
    role_proportion = ROLE_PROPORTIONS[len(user_ids)]
    civilian_num, undercover_num, mr_white_num = role_proportion
    civilian_word, undercover_word = get_secret_word()

    store_playing_role(room_id, civilian_word, undercover_word, mr_white_num)
    user_words, mr_whites = assign_role(
        user_ids, civilian_word, undercover_word, role_proportion
    )
    played_word_state = GameState(Status.PLAYED_WORD, user_words)

    playing_order = decide_playing_order(user_ids, mr_whites)
    playing_order_state = GameState(Status.PLAYING_ORDER, playing_order)

    return [played_word_state, playing_order_state]


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
