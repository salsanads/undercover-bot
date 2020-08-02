from functools import wraps

from undercover import GameState, Status
from undercover.models import Player

from .helpers import get_elimination_result, ongoing_game_found


def elimination_valid(func):
    @wraps(func)
    def wrapper(room_id, user_id, *args, **kwargs):
        player_found = Player.exists(user_id)
        data = {"player": user_id}
        if not player_found:
            return [GameState(Status.ELIMINATED_PLAYER_NOT_FOUND, data)]

        player = Player.get(user_id)
        if player.room_id != room_id:
            return [GameState(Status.ELIMINATED_PLAYER_NOT_FOUND, data)]

        if not player.alive:
            return [GameState(Status.ELIMINATED_PLAYER_ALREADY_SLAIN, data)]

        return func(room_id, user_id, *args, **kwargs)

    return wrapper


@ongoing_game_found(True)
@elimination_valid
def eliminate(room_id, user_id):
    Player.kill(user_id)
    player = Player.get(user_id)
    game_states = get_elimination_result(player, return_eliminated_role=True)
    return game_states
