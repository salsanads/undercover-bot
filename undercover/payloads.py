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
    # start
    PLAYED_WORD = auto()
    PLAYING_ORDER = auto()
    INVALID_PLAYER_NUMBER = auto()
    PLAYING_USER_FOUND = auto()

    # eliminate
    CIVILIAN_ELIMINATED = auto()
    UNDERCOVER_ELIMINATED = auto()
    MR_WHITE_ELIMINATED = auto()

    # guess
    ASK_GUESSED_WORD = auto()
    NOT_IN_GUESSING_TURN = auto()

    # win
    CIVILIAN_WIN = auto()
    NON_CIVILIAN_WIN = auto()
    MR_WHITE_WIN = auto()
    SUMMARY = auto()

    # poll
    POLL_STARTED = auto()
    POLL_DECIDED = auto()
    VOTE_SUCCESS = auto()
    TOTAL_VOTES_REACHED = auto()
    ONGOING_POLL_FOUND = auto()
    ONGOING_POLL_NOT_FOUND = auto()
    NO_VOTES_SUBMITTED = auto()
    NOT_ENOUGH_VOTES = auto()
    MULTIPLE_PLAYERS_VOTED = auto()
    VOTE_EXISTS = auto()

    # common error
    ONGOING_GAME_FOUND = auto()
    ONGOING_GAME_NOT_FOUND = auto()
    PLAYER_NOT_FOUND = auto()
    PLAYER_ALREADY_KILLED = auto()
