from functools import wraps

from undercover import GameState, Role, Status
from undercover.models import Player

from .helpers import evaluate_game, ongoing_game_found


def elimination_valid(func):
    @wraps(func)
    def wrapper(room_id, user_id, *args, **kwargs):
        player = Player.get(user_id)
        data = {"player": user_id}

        if player is None or player.room_id != room_id:
            return [GameState(Status.ELIMINATED_PLAYER_NOT_FOUND, data)]

        if not player.alive:
            return [GameState(Status.ELIMINATED_PLAYER_ALREADY_KILLED, data)]

        return func(room_id, user_id, *args, **kwargs)

    return wrapper


def kill_player(user_id):
    player = Player.get(user_id)
    updated_attrs = {"alive": False}
    if player.role == Role.MR_WHITE.name:
        updated_attrs["guessing"] = True
    Player.update(user_id, **updated_attrs)


@ongoing_game_found(True)
@elimination_valid
def eliminate(room_id, user_id):
    kill_player(user_id)
    killed_player = Player.get(user_id)
    data = {"player": killed_player.user_id, "role": killed_player.role}

    if killed_player.role == Role.MR_WHITE.name:
        eliminated_role = GameState(Status.ELIMINATED_MR_WHITE, data)
        game_state = GameState(Status.ASK_GUESSED_WORD)
        return [eliminated_role, game_state]
    else:
        eliminated_role = GameState(Status.ELIMINATED_ROLE, data)
        game_state = evaluate_game(room_id)
        return [eliminated_role, game_state]
