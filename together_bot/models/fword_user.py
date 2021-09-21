from sqlalchemy import BigInteger, Column, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def setup(engine):
    Base.metadata.create_all(engine)


class FwordUser(Base):
    __tablename__ = "fword_user"

    id = Column(Integer, primary_key=True)
    discord_id = Column(BigInteger, unique=True)


# 편의를 위해 만든 shortcut function임.
# 모든 DB 접근에 대해 session을 함수로 감싸지 않아도 됨.
def save(session, discord_id: int) -> FwordUser:
    fword_user = FwordUser(discord_id=discord_id)
    session.add(fword_user)
    return fword_user


def find_by_discord_id(session, discord_id: int) -> FwordUser:
    return session.query(FwordUser).filter_by(discord_id=discord_id).one_or_none()


def find_all(session) -> list[FwordUser]:
    return session.query(FwordUser).all()
