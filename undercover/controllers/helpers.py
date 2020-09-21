import random
from collections import Counter
from functools import wraps

from undercover import GameState, Role, Status
from undercover.models import Player, PlayingRole, Poll, Vote


def ongoing_game_found(should_be_found):
    def inner(func):
        @wraps(func)
        def wrapper(room_id, *args, **kwargs):
            actual_found = PlayingRole.exists(room_id)
            if not should_be_found and actual_found:
                return [GameState(Status.ONGOING_GAME_FOUND)]
            elif should_be_found and not actual_found:
                return [GameState(Status.ONGOING_GAME_NOT_FOUND)]
            return func(room_id, *args, **kwargs)

        return wrapper

    return inner


def ongoing_poll_found(should_be_found):
    def inner(func):
        @wraps(func)
        def wrapper(room_id, *args, **kwargs):
            poll = Poll.get(room_id)
            actual_found = poll is not None
            if not should_be_found and actual_found:
                return [GameState(Status.ONGOING_POLL_FOUND)]
            elif should_be_found and not actual_found:
                return [GameState(Status.ONGOING_POLL_NOT_FOUND)]
            return func(room_id, *args, **kwargs)

        return wrapper

    return inner


def count_vote(poll_id):
    votes = Vote.find_all(poll_id=poll_id)
    tally = Counter()
    for vote in votes:
        tally[vote.voted_id] += 1
    return tally, len(votes)


# generalize @elimination_valid and its payload to this
def player_valid(func):
    @wraps(func)
    def wrapper(room_id, user_id, *args, **kwargs):
        player = Player.get(user_id)
        data = {"player": user_id}
        if player is None or player.room_id != room_id:
            return [GameState(Status.PLAYER_NOT_FOUND, data)]
        if not player.alive:
            return [GameState(Status.PLAYER_ALREADY_KILLED, data)]
        return func(room_id, user_id, *args, **kwargs)

    return wrapper


def evaluate_game(room_id):
    n_alive_civilians = Player.num_alive_players(
        room_id, role=Role.CIVILIAN.name
    )

    if n_alive_civilians == 1:
        summary = generate_summary(room_id)
        clear_game(room_id)
        return [
            GameState(Status.NON_CIVILIAN_WIN, room_id=room_id),
            GameState(Status.SUMMARY, data=summary),
        ]

    n_alive_players = Player.num_alive_players(room_id)

    if n_alive_civilians == n_alive_players:
        summary = generate_summary(room_id)
        clear_game(room_id)
        return [
            GameState(Status.CIVILIAN_WIN, room_id=room_id),
            GameState(Status.SUMMARY, data=summary),
        ]

    alive_player_ids = Player.alive_player_ids(room_id)
    playing_order = decide_playing_order(alive_player_ids)
    return [GameState(Status.PLAYING_ORDER, playing_order, room_id=room_id)]


def decide_playing_order(user_ids, mr_whites=None):
    random.shuffle(user_ids)
    while mr_whites is not None and user_ids[0] in mr_whites:
        random.shuffle(user_ids)
    return {"playing_order": user_ids}


def clear_game(room_id):
    PlayingRole.delete(room_id)
    Player.delete(room_id)
    poll = Poll.get(room_id)
    if poll is not None:
        Poll.delete(poll.poll_id)
        Vote.delete_all(poll.poll_id)


def generate_summary(room_id):
    players = Player.get_all(room_id)
    civilians = []
    undercovers = []
    mr_whites = []

    for player in players:
        if player.role == Role.CIVILIAN.name:
            civilians.append(
                {"user_id": player.user_id, "alive": player.alive}
            )
        elif player.role == Role.UNDERCOVER.name:
            undercovers.append(
                {"user_id": player.user_id, "alive": player.alive}
            )
        elif player.role == Role.MR_WHITE.name:
            mr_whites.append(
                {"user_id": player.user_id, "alive": player.alive}
            )

    return {
        "civilian_word": PlayingRole.get_word(room_id, Role.CIVILIAN).word,
        "undercover_word": PlayingRole.get_word(room_id, Role.UNDERCOVER).word,
        "civilians": civilians,
        "undercovers": undercovers,
        "mr_whites": mr_whites,
    }
