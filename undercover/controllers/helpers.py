from functools import wraps

from undercover import GameState, Status
from undercover.models import PlayingRole


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
