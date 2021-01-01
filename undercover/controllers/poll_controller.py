from undercover import GameState, Status
from undercover.models import Player, Poll, Vote

from .helpers import (
    count_vote,
    ongoing_game_found,
    ongoing_poll_found,
    player_valid,
)


@ongoing_game_found(True)
@ongoing_poll_found(False)
@player_valid
def start_poll(room_id, user_id, msg_id):  # user_id used inside decorator
    alive_player_ids = Player.alive_player_ids(room_id)
    new_poll = Poll(room_id, msg_id)
    Poll.add(new_poll)
    data = {"players": alive_player_ids}
    return [GameState(Status.POLL_STARTED, data)]


def complete_poll(room_id):
    tally, total_votes = count_vote(room_id)
    data = {"tally": tally}
    if total_votes == 0:
        terminate_poll(room_id)
        return [GameState(Status.NO_VOTES_SUBMITTED, data)]

    alive_player_ids = Player.alive_player_ids(room_id)
    data["players"] = alive_player_ids
    if total_votes < len(alive_player_ids) // 2 + 1:
        terminate_poll(room_id)
        return [GameState(Status.NOT_ENOUGH_VOTES, data)]

    max_votes = max(tally.values())
    voted_players = [
        voted_player
        for voted_player, votes in tally.items()
        if votes == max_votes
    ]
    if len(voted_players) > 1:
        terminate_poll(room_id)
        return [GameState(Status.MULTIPLE_PLAYERS_VOTED, data)]

    data["player"] = voted_players[0]
    terminate_poll(room_id)
    return [GameState(Status.POLL_DECIDED, data)]


def terminate_poll(room_id):
    Vote.delete_all(room_id)
    Poll.delete(room_id)
