from contextlib import contextmanager
from functools import partial, wraps

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()
Base = declarative_base()


def init_db(engine):
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)


@contextmanager
def create_session():
    session = Session()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def add_session(func=None, expire_on_commit=True):
    if func is None:
        return partial(add_session, expire_on_commit=expire_on_commit)

    @wraps(func)
    def wrapper(*args, **kwargs):
        with create_session() as session:
            if not expire_on_commit:
                session.expire_on_commit = False
            return func(*args, session, **kwargs)

    return wrapper
