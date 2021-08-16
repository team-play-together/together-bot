import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import sessionmaker

import together_bot.models.fword_user as fword_user


# 각 테스트마다 인메모리 DB를 재시작함.
@pytest.fixture(autouse=True)
def Session():
    engine = create_engine("sqlite:///:memory:")
    fword_user.setup(engine)
    Session = sessionmaker(engine)
    return Session


def test_save(Session):
    discord_id = 123456
    with Session() as session:
        fword_user.save(session, discord_id)
        result = fword_user.find_by_discord_id(session, discord_id)
        assert result.discord_id == discord_id


def test_save_duplicated_discord_id(Session):
    discord_id = 123456
    with pytest.raises(
        IntegrityError,
        match="UNIQUE constraint failed: fword_user.discord_id",
    ):
        with Session() as session:
            fword_user.save(session, discord_id)
            fword_user.save(session, discord_id)
            session.commit()


def test_id_autoincrement(Session):
    with Session() as session:
        fword_user.save(session, 123)
        fword_user.save(session, 456)
        fword_user.save(session, 789)
        user_list = fword_user.find_all(session)
        for i, user in enumerate(user_list, start=1):
            assert i == user.id


def test_delete(Session):
    discord_id = 123
    with Session() as session:
        # !fword watch off 명령어에서 discord_id를 쿼리 후 삭제하는 걸 테스트하기 위해 save()의 반환값을 쓰지않음.
        fword_user.save(session, discord_id)
        session.commit()
        user = fword_user.find_by_discord_id(session, discord_id)
        session.delete(user)
        session.commit()
        assert fword_user.find_by_discord_id(session, discord_id) is None
