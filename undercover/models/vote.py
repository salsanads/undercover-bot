from sqlalchemy import BigInteger, Column, ForeignKey

from .database import Base, add_session


class Vote(Base):
    __tablename__ = "vote"

    voter_id = Column(BigInteger, primary_key=True, nullable=False)
    room_id = Column(
        BigInteger,
        ForeignKey("poll.room_id", onupdate="CASCADE", ondelete="CASCADE"),
        index=True,
    )
    voted_id = Column(BigInteger, nullable=False)

    def __init__(self, voter_id, room_id, voted_id):
        self.voter_id = voter_id
        self.room_id = room_id
        self.voted_id = voted_id

    @classmethod
    @add_session
    def add(cls, vote, session):
        session.add(vote)

    @classmethod
    @add_session(expire_on_commit=False)
    def get(cls, voter_id, session):
        vote = session.query(cls).filter_by(voter_id=voter_id).first()
        return vote

    @classmethod
    @add_session(expire_on_commit=False)
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
    def delete_all(cls, room_id, session):
        session.query(cls).filter_by(room_id=room_id).delete()

    @classmethod
    @add_session
    def delete(cls, voter_id, session):
        session.query(cls).filter_by(voter_id=voter_id).delete()
