from sqlalchemy import create_engine

from .game_state import GameState, Status
from .models import init_db


def main(db_url, env="dev"):
    echo = env != "prod"
    engine = create_engine(db_url, echo=echo)
    init_db(engine)
