import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

import together_bot.models.fword_user

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

Session = sessionmaker()


def setup():
    engine = create_engine(DATABASE_URL)
    together_bot.models.fword_user.setup(engine)
    Session.configure(bind=engine)
