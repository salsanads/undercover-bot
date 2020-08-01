from sqlalchemy import Boolean, Column, ForeignKeyConstraint, String

from undercover import Role

from .database import Base, add_session
from .playing_role import PlayingRole


class Player(Base):
    __tablename__ = "player"

    user_id = Column(String, primary_key=True)
    alive = Column(Boolean, nullable=False)
    guessing = Column(Boolean, nullable=False)
    room_id = Column(String, primary_key=True)
    role = Column(String, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(
            [room_id, role], [PlayingRole.room_id, PlayingRole.role]
        ),
        {},
    )

    @classmethod
    @add_session
    def get(cls, room_id, user_id, session):
        return session.query(cls).filter_by(user_id=user_id, room_id=room_id)

    @classmethod
    @add_session
    def exists(cls, room_id, user_id, session):
        exists = (
            session.query(cls.user_id)
            .filter_by(user_id=user_id, room_id=room_id)
            .first()
        )
        return exists is not None

    @classmethod
    @add_session
    def kill(cls, room_id, user_id, session):
        player = session.query(cls).filter_by(user_id=user_id, room_id=room_id)
        player.alive = False
        session.commit()

    @classmethod
    @add_session
    def num_alive_players(cls, room_id, session):
        num_players = (
            session.query(cls).filter_by(room_id=room_id, alive=True).count()
        )
        num_civilians = (
            session.query(cls)
            .filter_by(room_id=room_id, alive=True, role=Role.CIVILIAN.name)
            .count()
        )
        return num_players, num_civilians

    @classmethod
    @add_session
    def alive_player_ids(cls, room_id, session):
        return session.query(cls.user_id).filter_by(
            room_id=room_id, alive=True
        )

    @classmethod
    @add_session
    def insert(cls, player, session):
        session.add(player)
        session.commit()
