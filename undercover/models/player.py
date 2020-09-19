from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKeyConstraint,
    String,
)

from .database import Base, add_session
from .playing_role import PlayingRole


class Player(Base):
    __tablename__ = "player"

    user_id = Column(BigInteger, primary_key=True)
    alive = Column(Boolean, nullable=False)
    guessing = Column(Boolean, nullable=False)
    room_id = Column(BigInteger, nullable=False, index=True)
    role = Column(String, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(
            [room_id, role],
            [PlayingRole.room_id, PlayingRole.role],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
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

    @classmethod
    @add_session(expire_on_commit=False)
    def get(cls, user_id, session):
        return session.query(cls).filter_by(user_id=user_id).first()

    @classmethod
    @add_session(expire_on_commit=False)
    def get_all(cls, room_id, session):
        return session.query(cls).filter_by(room_id=room_id).all()

    @classmethod
    @add_session
    def filter_exists(cls, user_ids, session):
        existing_user_ids = (
            session.query(cls.user_id).filter(cls.user_id.in_(user_ids)).all()
        )
        return [user_id for user_id, in existing_user_ids]

    @classmethod
    @add_session
    def update(cls, user_id, session, **kwargs):
        player = session.query(cls).get(user_id)
        if player is None:
            raise Exception(f"No player with user_id {user_id} is found")
        for column, updated_value in kwargs.items():
            if hasattr(player, column):
                setattr(player, column, updated_value)

    @classmethod
    @add_session
    def delete(cls, room_id, session):
        session.query(cls).filter_by(room_id=room_id).delete()

    @classmethod
    @add_session
    def num_alive_players(cls, room_id, session, role=None):
        if role is not None:
            return (
                session.query(cls)
                .filter_by(room_id=room_id, alive=True, role=role)
                .count()
            )

        return (
            session.query(cls).filter_by(room_id=room_id, alive=True).count()
        )

    @classmethod
    @add_session
    def alive_player_ids(cls, room_id, session, role=None):
        if role is not None:
            player_with_role_ids = (
                session.query(cls.user_id)
                .filter_by(room_id=room_id, alive=True, role=role)
                .all()
            )
            return [user_id for user_id, in player_with_role_ids]

        player_ids = (
            session.query(cls.user_id)
            .filter_by(room_id=room_id, alive=True)
            .all()
        )
        return [user_id for user_id, in player_ids]
