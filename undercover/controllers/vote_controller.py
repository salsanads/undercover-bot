from collections import Counter

from undercover import GameState, Status
from undercover.models import Player, Poll, Vote

from .helpers import (
    count_vote,
    ongoing_game_found,
    ongoing_poll_found,
    player_valid,
)


@player_valid
def check_vote_valid(room_id, voted_id, voter_id):
    vote = Vote.get(voter_id)
    if vote is not None:
        data = {"player": voter_id}
        return [GameState(Status.VOTE_EXISTS, data)]


def decide_game_states(room_id):
    tally, total_votes = count_vote(room_id)
    num_alive_players = Player.num_alive_players(room_id)
    poll = Poll.get(room_id)
    data = {"msg_id": poll.msg_id, "tally": tally}
    if total_votes == num_alive_players:
        return [GameState(Status.TOTAL_VOTES_REACHED, data)]
    return [GameState(Status.VOTE_SUCCESS, data)]


@ongoing_poll_found(True)
@player_valid
def vote(room_id, voter_id, voted_id):
    game_states = check_vote_valid(room_id, voted_id, voter_id)
    if game_states is not None:
        return game_states

    new_vote = Vote(voter_id, room_id, voted_id)
    Vote.add(new_vote)

    return decide_game_states(room_id)
