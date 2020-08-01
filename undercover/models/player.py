from sqlalchemy import Boolean, Column, ForeignKeyConstraint, String

from .database import Base, add_session
from .playing_role import PlayingRole


class Player(Base):
    __tablename__ = "player"

    user_id = Column(String, primary_key=True)
    alive = Column(Boolean, nullable=False)
    guessing = Column(Boolean, nullable=False)
    room_id = Column(String, nullable=False)
    role = Column(String, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(
            [room_id, role], [PlayingRole.room_id, PlayingRole.role]
        ),
        {},
    )

    @classmethod
    @add_session
    def insert(cls, session, player):
        session.add(player)
        session.commit()
