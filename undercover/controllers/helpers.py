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


def get_elimination_state(player, inform_role=False):
    state = []
    n_alive_players, n_alive_civilians = Player.num_alive_players(
        player.room_id
    )

    if player.alive:
        return state

    if inform_role:
        data = {"player": player.user_id, "role": player.role}
        state.append(GameState(Status.ELIMINATED_ROLE, data))

    if player.role == Role.MR_WHITE.name:
        state.append(GameState(Status.ASK_GUESSED_WORD))
        return state

    if n_alive_civilians == n_alive_players:
        state.append(GameState(Status.CIVILIAN_WIN))
        return state

    if n_alive_civilians == 1:
        state.append(GameState(Status.NON_CIVILIAN_WIN))
        return state

    playing_order = new_playing_order(player.room_id)
    data = {"playing_order": playing_order}
    state.append(GameState(Status.PLAYING_ORDER, data))
    return state


def new_playing_order(room_id):
    alive_player_ids = Player.alive_player_ids(room_id)
    return random.shuffle(alive_player_ids)
