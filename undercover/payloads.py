from enum import Enum, auto


class Role(Enum):
    CIVILIAN = auto()
    UNDERCOVER = auto()
    MR_WHITE = auto()


class GameState:
    def __init__(self, status, data=None, room_id=None):
        self.status = status
        self.data = data
        self.room_id = room_id


class Status(Enum):
    # HAPPY PATH
    PLAYED_WORD = auto()
    PLAYING_ORDER = auto()
    CIVILIAN_ELIMINATED = auto()
    UNDERCOVER_ELIMINATED = auto()
    MR_WHITE_ELIMINATED = auto()
    ASK_GUESSED_WORD = auto()
    CIVILIAN_WIN = auto()
    NON_CIVILIAN_WIN = auto()
    MR_WHITE_WIN = auto()
    SUMMARY = auto()

    # UNHAPPY PATH
    INVALID_PLAYER_NUMBER = auto()
    ONGOING_GAME_FOUND = auto()
    ONGOING_POLL_FOUND = auto()
    PLAYING_USER_FOUND = auto()
    ONGOING_GAME_NOT_FOUND = auto()
    ONGOING_POLL_NOT_FOUND = auto()
    PLAYER_NOT_FOUND = auto()
    PLAYER_ALREADY_KILLED = auto()
    NOT_IN_GUESSING_TURN = auto()
