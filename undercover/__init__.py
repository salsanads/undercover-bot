from sqlalchemy import create_engine

from .models import init_db
from .payloads import GameState, Role, Status


def main(database_url, env="dev"):
    echo = env != "prod"
    engine = create_engine(database_url, echo=echo)
    init_db(engine)
