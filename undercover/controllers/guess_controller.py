from undercover import GameState, Role, Status
from undercover.models import Player, PlayingRole

from .helpers import evaluate_game


def guess_word(user_id, word):
    player = Player.get(user_id)
    if player is None or not player.guessing:
        return [GameState(Status.NOT_IN_GUESSING_TURN)]

    room_id = player.room_id
    role = Role.CIVILIAN
    civilian_word = PlayingRole.get_word(room_id, role)
    if word.lower() == civilian_word.lower():
        return [GameState(Status.MR_WHITE_WIN)]

    return evaluate_game(room_id)
