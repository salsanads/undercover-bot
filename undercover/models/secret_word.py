from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import func

from .database import Base, add_session


class SecretWord(Base):
    __tablename__ = "secret_words"

    id = Column(Integer, autoincrement=True, primary_key=True)
    # temporary workaround due to unsupported ARRAY in SQLite
    __related_words = Column("related_words", String, nullable=False)
    related_words = []

    def __init__(self, related_words):
        self.related_words = related_words
        self.__related_words = str(related_words)

    @classmethod
    @add_session
    def get_random(cls, session):
        secret_word = SecretWord([])
        while len(secret_word.related_words) < 2:
            secret_word = session.query(cls).order_by(func.random()).first()
            secret_word.related_words = eval(secret_word.__related_words)
        return secret_word
