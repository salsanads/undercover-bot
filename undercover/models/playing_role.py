from sqlalchemy import Column, String

from .database import Base, add_session


class PlayingRole(Base):
    __tablename__ = "playing_role"

    room_id = Column(String, primary_key=True)
    role = Column(String, primary_key=True)
    word = Column(String)

    def __init__(self, room_id, role, word=None):
        self.room_id = room_id
        self.role = role
        self.word = word

    @classmethod
    @add_session
    def insert(cls, session, playing_role):
        session.add(playing_role)
        session.commit()
