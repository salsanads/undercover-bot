import random
from functools import wraps

from undercover import GameState, Role, Status
from undercover.models import Player, PlayingRole


def ongoing_game_found(should_be_found):
    def inner(func):
        @wraps(func)
        def wrapper(room_id, *args, **kwargs):
            actual_found = PlayingRole.exists(room_id)
            if not should_be_found and actual_found:
                return GameState(Status.ONGOING_GAME_FOUND)
            elif should_be_found and not actual_found:
                return GameState(Status.ONGOING_GAME_NOT_FOUND)
            return func(room_id, *args, **kwargs)

        return wrapper

    return inner


def evaluate_game(room_id):
    n_alive_civilians = Player.num_alive_players(
        room_id, role=Role.CIVILIAN.name
    )

    if n_alive_civilians == 1:
        clear_game(room_id)
        return [GameState(Status.NON_CIVILIAN_WIN)]

    n_alive_players = Player.num_alive_players(room_id)

    if n_alive_civilians == n_alive_players:
        clear_game(room_id)
        return [GameState(Status.CIVILIAN_WIN)]

    playing_order = new_playing_order(room_id)
    data = {"playing_order": playing_order}
    return [GameState(Status.PLAYING_ORDER, data)]


def new_playing_order(room_id):
    alive_player_ids = Player.alive_player_ids(room_id)
    random.shuffle(alive_player_ids)
    return alive_player_ids


def clear_game(room_id):
    Player.delete(room_id)
    PlayingRole.delete(room_id)
