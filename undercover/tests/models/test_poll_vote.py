import pytest

from undercover.models import Poll, Vote

EXISTING_POLLS = [(1, 1), (2, 2)]
EXISTING_VOTES = [(1, 1, 2), (2, 1, 2), (3, 2, 1)]


class TestPollVote:
    @staticmethod
    @pytest.fixture(autouse=True)
    def populate_db(session):
        for poll_id, room_id in EXISTING_POLLS:
            session.add(Poll(poll_id, room_id))
        for vote_id, poll_id, voted_user_id in EXISTING_VOTES:
            session.add(Vote(vote_id, poll_id, voted_user_id))
        session.commit()
        yield
        session.query(Poll).delete()
        session.query(Vote).delete()

    @staticmethod
    def test_add_poll(session):
        poll_id = 3
        room_id = 3
        Poll.add(Poll(poll_id, room_id))
        poll = session.query(Poll).filter_by(poll_id=poll_id).first()

        assert poll.poll_id == poll_id
        assert poll.room_id == room_id

    @staticmethod
    def test_add_vote(session):
        poll_id = 3
        vote_id = 4
        voted_user_id = 4
        Vote.add(Vote(vote_id, poll_id, voted_user_id))
        vote = session.query(Vote).filter_by(vote_id=vote_id).first()

        assert vote.poll_id == poll_id
        assert vote.vote_id == vote_id
        assert vote.voted_user_id == voted_user_id

    @staticmethod
    def test_add_duplicate_poll():
        poll_id = 2
        room_id = 3
        with pytest.raises(Exception):
            Poll.add(Poll(poll_id, room_id))

    @staticmethod
    def test_add_duplicate_vote():
        vote_id = 1
        poll_id = 2
        voted_user_id = 3
        with pytest.raises(Exception):
            Vote.add(Vote(vote_id, poll_id, voted_user_id))

    @staticmethod
    def test_delete(session):
        vote_id, _, _ = EXISTING_VOTES[0]
        poll_id, _ = EXISTING_POLLS[0]
        Vote.delete(vote_id)
        Poll.delete(poll_id)
        vote = session.query(Vote).get(vote_id)
        poll = session.query(Poll).get(poll_id)

        assert vote is None
        assert poll is None

    @staticmethod
    def test_delete_all_votes(session):
        poll_id = 1
        Vote.delete_all(poll_id)
        votes = session.query(Vote).all()
        assert len(votes) == 1

    @staticmethod
    def test_find_all_votes():
        votes = Vote.find_all(poll_id=1)
        assert len(votes) == 2
        for vote in votes:
            print(vote.vote_id, vote.poll_id, vote.voted_user_id)

    @staticmethod
    def test_update_vote():
        value = 3
        for vote_id, _, _ in EXISTING_VOTES:
            Vote.update(vote_id, voted_user_id=value)

        votes = Vote.find_all()
        for vote in votes:
            assert vote.voted_user_id == value
