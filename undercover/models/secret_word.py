from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import func

from .database import Base, add_session


class SecretWord(Base):
    __tablename__ = "secret_words"

    id = Column(Integer, autoincrement=True, primary_key=True)
    word_1 = Column(String, nullable=False)
    word_2 = Column(String, nullable=False)

    def __init__(self, word_1, word_2):
        self.word_1 = word_1
        self.word_2 = word_2

    @classmethod
    @add_session
    def get_random(cls, session):
        return session.query(cls).order_by(func.random()).first()
