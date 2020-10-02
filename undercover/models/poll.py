from sqlalchemy import BigInteger, Column, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base, add_session


class Poll(Base):
    __tablename__ = "poll"

    room_id = Column(BigInteger, nullable=False, primary_key=True)
    msg_id = Column(BigInteger, nullable=False, unique=True)
    votes = relationship("Vote", backref="poll", cascade="all,delete-orphan")

    def __init__(self, room_id, msg_id):
        self.room_id = room_id
        self.msg_id = msg_id

    @classmethod
    @add_session(expire_on_commit=False)
    def get(cls, room_id, session):
        poll = session.query(cls).get(room_id)
        return poll

    @classmethod
    @add_session
    def add(cls, poll, session):
        session.add(poll)

    @classmethod
    @add_session
    def delete(cls, room_id, session):
        session.query(cls).filter_by(room_id=room_id).delete()
