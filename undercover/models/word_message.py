from sqlalchemy import BigInteger, Column

from .database import Base, add_session


class WordMessage(Base):
    __tablename__ = "word_message"

    message_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, primary_key=True)
    room_id = Column(BigInteger, nullable=False)

    def __init__(self, message_id, user_id, room_id):
        self.message_id = message_id
        self.user_id = user_id
        self.room_id = room_id

    @classmethod
    @add_session
    def insert_all(cls, word_messages, session):
        session.add_all(word_messages)

    @classmethod
    @add_session(expire_on_commit=False)
    def get_all(cls, room_id, session):
        return session.query(cls).filter_by(room_id=room_id).all()

    @classmethod
    @add_session
    def delete_all(cls, room_id, session):
        session.query(cls).filter_by(room_id=room_id).delete()
