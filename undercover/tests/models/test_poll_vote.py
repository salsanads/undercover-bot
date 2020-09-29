import pytest

from undercover.models import Poll, Vote

EXISTING_POLLS = [(1, 1), (2, 2)]
EXISTING_VOTES = [(1, 1, 2), (2, 1, 2), (3, 2, 1)]


class TestPollVote:
    @staticmethod
    @pytest.fixture(autouse=True)
    def populate_db(session):
        for room_id, msg_id in EXISTING_POLLS:
            session.add(Poll(room_id, msg_id))
        for voter_id, room_id, voted_id in EXISTING_VOTES:
            session.add(Vote(voter_id, room_id, voted_id))
        session.commit()
        yield
        session.query(Poll).delete()
        session.query(Vote).delete()

    @staticmethod
    def test_add_poll(session):
        room_id = 3
        msg_id = 3
        Poll.add(Poll(room_id, msg_id))
        poll = session.query(Poll).filter_by(room_id=room_id).first()
        assert poll.room_id == room_id
        assert poll.msg_id == msg_id

    @staticmethod
    def test_add_vote(session):
        room_id = 3
        voter_id = 4
        voted_id = 4
        Vote.add(Vote(voter_id, room_id, voted_id))
        vote = session.query(Vote).filter_by(voter_id=voter_id).first()
        assert vote.room_id == room_id
        assert vote.voter_id == voter_id
        assert vote.voted_id == voted_id

    @staticmethod
    def test_add_duplicate_poll():
        room_id, msg_id = EXISTING_POLLS[-1]
        with pytest.raises(Exception):
            Poll.add(Poll(room_id, msg_id))

    @staticmethod
    def test_add_duplicate_vote():
        voter_id, room_id, voted_id = EXISTING_VOTES[-1]
        with pytest.raises(Exception):
            Vote.add(Vote(voter_id, room_id, voted_id))

    @staticmethod
    def test_delete(session):
        voter_id, _, _ = EXISTING_VOTES[0]
        room_id, _ = EXISTING_POLLS[0]
        Vote.delete(voter_id)
        Poll.delete(room_id)
        vote = session.query(Vote).get(voter_id)
        poll = session.query(Poll).get(room_id)

        assert vote is None
        assert poll is None

    @staticmethod
    def test_delete_all_votes(session):
        room_id = 1
        Vote.delete_all(room_id)
        votes = session.query(Vote).all()
        assert len(votes) == 1

    @staticmethod
    def test_find_all_votes():
        votes = Vote.find_all(room_id=1)
        assert len(votes) == 2
        for vote in votes:
            print(vote.voter_id, vote.room_id, vote.voted_id)

    @staticmethod
    def test_update_vote():
        value = 3
        for voter_id, _, _ in EXISTING_VOTES:
            Vote.update(voter_id, voted_id=value)

        votes = Vote.find_all()
        for vote in votes:
            assert vote.voted_id == value
