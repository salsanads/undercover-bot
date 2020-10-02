import re

import Levenshtein

from undercover import GameState, Role, Status
from undercover.models import Player, PlayingRole

from .helpers import clear_game, evaluate_game


def guess_word(user_id, word):
    player = Player.get(user_id)
    if player is None or not player.guessing:
        return [GameState(Status.NOT_IN_GUESSING_TURN)]

    civilian_word = PlayingRole.get_word(player.room_id, Role.CIVILIAN).word

    word = re.sub("[^a-z0-9]", "", word.lower())
    civilian_word = re.sub("[^a-z0-9]", "", civilian_word.lower())

    if Levenshtein.distance(word, civilian_word) <= 1:
        clear_game(player.room_id)
        return [GameState(Status.MR_WHITE_WIN, room_id=player.room_id)]

    Player.update(user_id, guessing=False)
    return evaluate_game(player.room_id)
