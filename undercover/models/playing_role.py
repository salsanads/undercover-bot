from sqlalchemy import Column, String, literal

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
    def exists(cls, room_id, session):
        room_id = session.query(cls.room_id).filter_by(room_id=room_id).first()
        return room_id is not None

    @classmethod
    @add_session
    def insert(cls, playing_role, session):
        session.add(playing_role)
