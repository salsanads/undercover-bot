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
            return [GameState(Status.ELIMINATED_PLAYER_ALREADY_SLAIN, data)]

        return func(room_id, user_id, *args, **kwargs)

    return wrapper


@ongoing_game_found(True)
@elimination_valid
def eliminate(room_id, user_id):
    player = Player.kill(user_id)
    data = {"player": player.user_id, "role": player.role}
    eliminated_role = GameState(Status.ELIMINATED_ROLE, data)

    if player.role == Role.MR_WHITE.name:
        game_state = GameState(Status.ASK_GUESSED_WORD)
        return [eliminated_role, game_state]
    else:
        game_state = evaluate_game(room_id)[0]
        return [eliminated_role, game_state]
