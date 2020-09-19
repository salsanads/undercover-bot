from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import relationship

from .database import Base, add_session


class PlayingRole(Base):
    __tablename__ = "playing_role"

    room_id = Column(BigInteger, primary_key=True)
    role = Column(String, primary_key=True)
    word = Column(String)
    players = relationship(
        "Player", backref="playing_role", cascade="all,delete-orphan"
    )

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

    @classmethod
    @add_session
    def get_word(cls, room_id, role, session):
        word = (
            session.query(cls.word)
            .filter_by(room_id=room_id, role=role.name)
            .first()
        )
        return word

    @classmethod
    @add_session
    def delete(cls, room_id, session):
        session.query(cls).filter_by(room_id=room_id).delete()
