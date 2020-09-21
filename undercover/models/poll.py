from sqlalchemy import BigInteger, Column, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base, add_session


class Poll(Base):
    __tablename__ = "poll"

    poll_id = Column(BigInteger, nullable=False, primary_key=True)
    room_id = Column(BigInteger, nullable=False, unique=True)
    total_players = Column(BigInteger, nullable=False)
    votes = relationship("Vote", backref="poll", cascade="all,delete-orphan")

    def __init__(self, poll_id, room_id, total_players=0):
        self.poll_id = poll_id
        self.room_id = room_id
        self.total_players = total_players

    @classmethod
    @add_session(expire_on_commit=False)
    def get(cls, room_id, session):
        poll = session.query(cls).filter_by(room_id=room_id).first()
        return poll

    @classmethod
    @add_session
    def add(cls, poll, session):
        session.add(poll)

    @classmethod
    @add_session
    def delete(cls, poll_id, session):
        session.query(cls).filter_by(poll_id=poll_id).delete()
