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
    PLAYING_ORDER = auto()

    INVALID_PLAYER_NUMBER = auto()
    ONGOING_GAME_FOUND = auto()
    ONGOING_GAME_NOT_FOUND = auto()
    PLAYING_USER_FOUND = auto()
