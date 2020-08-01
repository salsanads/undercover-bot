from sqlalchemy import Boolean, Column, ForeignKeyConstraint, String

from .database import Base, add_session
from .playing_role import PlayingRole


# TODO : Tambah CASCADE --> ga tau ini apa cari ya (@salsanads)
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

    def __init__(self, user_id, room_id, role, alive=True, guessing=False):
        self.user_id = user_id
        self.alive = alive
        self.guessing = guessing
        self.room_id = room_id
        self.role = role

    @classmethod
    @add_session
    def insert(cls, player, session):
        session.add(player)
