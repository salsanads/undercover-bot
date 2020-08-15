import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from undercover.models import init_db


@pytest.fixture(scope="package", autouse=True)
def engine():
    db_file_name = "test-undercover.db"
    engine = create_engine(
        "sqlite:///{db_file_name}".format(db_file_name=db_file_name)
    )
    yield engine
    engine.dispose()
    os.remove(db_file_name)


@pytest.fixture(scope="package", autouse=True)
def setup(engine):
    init_db(engine)


@pytest.fixture(scope="package")
def session_factory(engine):
    session_factory = scoped_session(sessionmaker(bind=engine))
    return session_factory


@pytest.fixture
def session(session_factory):
    return session_factory()
