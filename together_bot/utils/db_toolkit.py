import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

from together_bot.models import Base

load_dotenv()

Session = sessionmaker()


def setup():
    DATABASE_URL = os.getenv("DATABASE_URL")
    # Heroku의 URL을 SQLAlchemy에서 사용하기 위해 수정함.(PR #74)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)
