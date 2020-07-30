from functools import wraps

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Session = scoped_session(sessionmaker())
Base = declarative_base()


def init_db(engine):
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)


def add_session(func):
    @wraps(func)
    def inner(*args, **kwargs):
        session = Session()
        return func(*args, session, **kwargs)

    return inner
