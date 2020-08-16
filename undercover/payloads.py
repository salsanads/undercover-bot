from enum import Enum, auto


class Role(Enum):
    CIVILIAN = auto()
    UNDERCOVER = auto()
    MR_WHITE = auto()


class GameState:
    def __init__(self, status, data=None):
        self.status = status
        self.data = data


class Status(Enum):
    # HAPPY PATH
    PLAYED_WORD = auto()
    PLAYING_ORDER = auto()
    ELIMINATED_ROLE = auto()
    ASK_GUESSED_WORD = auto()
    CIVILIAN_WIN = auto()
    NON_CIVILIAN_WIN = auto()

    # UNHAPPY PATH
    INVALID_PLAYER_NUMBER = auto()
    ONGOING_GAME_FOUND = auto()
    PLAYING_USER_FOUND = auto()
    ONGOING_GAME_NOT_FOUND = auto()

    # MR WHITE
    NOT_IN_GUESSING_TURN = auto()
    MR_WHITE_WIN = auto()
