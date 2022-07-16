from sqlalchemy import BigInteger, Column, Integer

from together_bot.models import Base


class DnfGradeChannel(Base):
    __tablename__ = "dnf_grade_channel"

    id = Column(Integer, primary_key=True)
    discord_id = Column(BigInteger, unique=True)


# 편의를 위해 만든 shortcut function임.
# 모든 DB 접근에 대해 session을 함수로 감싸지 않아도 됨.
def save(session, discord_id: int) -> DnfGradeChannel:
    channel = DnfGradeChannel(discord_id=discord_id)
    session.add(channel)
    return channel


def find_by_discord_id(session, discord_id: int) -> DnfGradeChannel:
    return session.query(DnfGradeChannel).filter_by(discord_id=discord_id).one_or_none()


def find_all(session) -> list[DnfGradeChannel]:
    return session.query(DnfGradeChannel).all()
