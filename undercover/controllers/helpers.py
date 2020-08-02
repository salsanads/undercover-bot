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
                return [GameState(Status.ONGOING_GAME_FOUND)]
            elif should_be_found and not actual_found:
                return [GameState(Status.ONGOING_GAME_NOT_FOUND)]
            return func(room_id, *args, **kwargs)

        return wrapper

    return inner


def get_elimination_result(player, return_eliminated_role=False):
    states = []
    if player.alive:
        return states

    room_id = player.room_id
    n_alive_players = Player.num_alive_players(room_id)
    n_alive_civilians = Player.num_alive_players(
        room_id, role=Role.CIVILIAN.name
    )

    if return_eliminated_role:
        data = {"player": player.user_id, "role": player.role}
        states.append(GameState(Status.ELIMINATED_ROLE, data))

    if (
        return_eliminated_role
        and player.role == Role.MR_WHITE.name
        and player.guessing
    ):
        states.append(GameState(Status.ASK_GUESSED_WORD))
        return states

    if n_alive_civilians == n_alive_players:
        clear_game(room_id)
        states.append(GameState(Status.CIVILIAN_WIN))
        return states

    if n_alive_civilians == 1:
        clear_game(room_id)
        states.append(GameState(Status.NON_CIVILIAN_WIN))
        return states

    playing_order = new_playing_order(room_id)
    data = {"playing_order": playing_order}
    states.append(GameState(Status.PLAYING_ORDER, data))
    return states


def new_playing_order(room_id):
    alive_player_ids = Player.alive_player_ids(room_id)
    random.shuffle(alive_player_ids)
    return alive_player_ids


def clear_game(room_id):
    Player.delete(room_id)
    PlayingRole.delete(room_id)
