from sqlalchemy import Column, ForeignKey, Integer

from .database import Base, add_session


class Vote(Base):
    __tablename__ = "vote"

    voter_id = Column(Integer, primary_key=True, nullable=False)
    poll_id = Column(Integer, ForeignKey("poll.poll_id"), index=True)
    voted_user_id = Column(Integer, nullable=False, index=True)

    def __init__(self, voter_id, poll_id, voted_user_id):
        self.voter_id = voter_id
        self.poll_id = poll_id
        self.voted_user_id = voted_user_id

    @classmethod
    @add_session
    def add(cls, vote, session):
        session.add(vote)

    @classmethod
    @add_session
    def get(cls, voter_id, session):
        vote = session.query(cls).filter_by(voter_id=voter_id).first()
        return vote

    @classmethod
    @add_session
    def find_all(cls, session, **kwargs):
        for attr in kwargs:
            if not hasattr(cls, attr):
                kwargs.pop(attr)
        votes = session.query(cls).filter_by(**kwargs).all()
        return votes

    @classmethod
    @add_session
    def update(cls, voter_id, session, **kwargs):
        vote = session.query(cls).get(voter_id)
        if vote is None:
            raise Exception("No votes found")
        for column, updated_value in kwargs.items():
            if hasattr(vote, column):
                setattr(vote, column, updated_value)

    @classmethod
    @add_session
    def delete_all(cls, poll_id, session):
        session.query(cls).filter_by(poll_id=poll_id).delete()
