from functools import wraps

from undercover import GameState, Status
from undercover.models import Player

from .helpers import get_elimination_state, ongoing_game_found


def check_invalid_kill(func):
    @wraps(func)
    def wrapper(room_id, user_id, *args, **kwargs):
        player_found = Player.exists(room_id, user_id)
        player = Player.get(room_id, user_id)
        data = {"player": user_id}

        if not player_found:
            return [GameState(Status.ELIMINATED_PLAYER_NOT_FOUND, data)]

        if not player.alive:
            return [GameState(Status.ELIMINATED_PLAYER_DEAD, data)]

        return func(room_id, user_id, *args, **kwargs)

    return wrapper


@ongoing_game_found(True)
@check_invalid_kill
def killme(room_id, user_id):
    Player.kill(room_id, user_id)
    player = Player.get(room_id, user_id)
    game_state = get_elimination_state(player, inform_role=True)
    return game_state
