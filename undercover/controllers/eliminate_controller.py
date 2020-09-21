from functools import wraps

from undercover import GameState, Role, Status
from undercover.models import Player

from .helpers import evaluate_game, ongoing_game_found, player_valid


def kill_player(user_id):
    player = Player.get(user_id)
    updated_attrs = {"alive": False}
    if player.role == Role.MR_WHITE.name:
        updated_attrs["guessing"] = True
    Player.update(user_id, **updated_attrs)


@ongoing_game_found(True)
@player_valid
def eliminate(room_id, user_id):
    kill_player(user_id)
    killed_player = Player.get(user_id)
    data = {"player": killed_player.user_id, "role": killed_player.role}

    game_states = []
    if killed_player.role == Role.CIVILIAN.name:
        game_states.append(GameState(Status.CIVILIAN_ELIMINATED, data))
        game_states += evaluate_game(room_id)
    elif killed_player.role == Role.UNDERCOVER.name:
        game_states.append(GameState(Status.UNDERCOVER_ELIMINATED, data))
        game_states += evaluate_game(room_id)
    elif killed_player.role == Role.MR_WHITE.name:
        game_states.append(GameState(Status.MR_WHITE_ELIMINATED, data))
        game_states.append(GameState(Status.ASK_GUESSED_WORD))

    return game_states
