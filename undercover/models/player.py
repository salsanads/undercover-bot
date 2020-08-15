from sqlalchemy import Boolean, Column, ForeignKeyConstraint, String

from undercover.payloads import Role

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

    @classmethod
    @add_session(expire_on_commit=False)
    def get(cls, user_id, session):
        return session.query(cls).filter_by(user_id=user_id).first()

    @classmethod
    @add_session(expire_on_commit=False)
    def kill(cls, user_id, session):
        player = session.query(cls).filter_by(user_id=user_id).first()
        player.alive = False
        if player.role == Role.MR_WHITE.name:
            player.guessing = True
        return player

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

    @classmethod
    @add_session
    def update_guessing(cls, user_id, guessing_status, session):
        session.query(cls).filter_by(user_id=user_id).update(
            {"guessing": guessing_status}
        )
