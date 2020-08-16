import Levenshtein

from undercover import GameState, Role, Status
from undercover.models import Player, PlayingRole

from .helpers import clear_game, evaluate_game


def guess_word(user_id, word):
    player = Player.get(user_id)
    if player is None or not player.guessing:
        return [GameState(Status.NOT_IN_GUESSING_TURN)]

    civilian_word = PlayingRole.get_word(player.room_id, Role.CIVILIAN)
    if word.lower() == civilian_word.word.lower() or Levenshtein.distance(
        word.lower(), civilian_word.word.lower()
    ) < int((len(civilian_word.word)) / 10):
        clear_game(player.room_id)
        return [GameState(Status.MR_WHITE_WIN, room_id=player.room_id)]

    Player.update(user_id, guessing=False)
    return [evaluate_game(player.room_id)]
