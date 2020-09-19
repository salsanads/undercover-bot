from sqlalchemy import BigInteger, Column, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base, add_session


class Poll(Base):
    __tablename__ = "poll"

    poll_id = Column(BigInteger, nullable=False, primary_key=True)
    room_id = Column(BigInteger, nullable=False, unique=True)
    votes = relationship("Vote", backref="poll")

    def __init__(self, poll_id, room_id):
        self.poll_id = poll_id
        self.room_id = room_id

    @classmethod
    @add_session(expire_on_commit=False)
    def get(cls, room_id, session):
        poll_id = session.query(cls.poll_id).filter_by(room_id=room_id).first()
        return poll_id

    @classmethod
    @add_session
    def add(cls, poll, session):
        session.add(poll)

    @classmethod
    @add_session
    def delete(cls, poll_id, session):
        session.query(cls).filter_by(poll_id=poll_id).delete()
