from sqlalchemy.orm import joinedload

from server.models.event import Event
from server.models.user import User
from server.models.record import Record

from server.backend.database import get_session


def create_user(fio: str, graduate_year: int, profile: str | None) -> User:
    with get_session() as session:
        user = User(fio=fio, graduate_year=graduate_year, profile=profile)
        session.add(user)
        session.commit()
        return user


def get_user_by_fio(fio: str) -> User | None:
    with get_session() as session:
        user = session.query(User).where(User.fio == fio)\
            .options(joinedload(User.records)).first()
        return user


def get_filtered_users_vos_finals():
    pass
