import random
from datetime import datetime

from sqlalchemy import create_engine

from .models import init_db
from .payloads import GameState, Role, Status


def main(db_url, env="dev"):
    echo = env != "prod"
    engine = create_engine(db_url, echo=echo)
    init_db(engine)

    random.seed(datetime.now())
