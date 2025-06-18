from sqlalchemy.orm import joinedload

from server.models.event import Event
from server.models.user import User
from server.models.record import Record

from server.backend.database import get_session


def create_event(title: str, subject: str | None, code: str | None,
                 rsosh_level: int | None, year: int, extra: str | None,
                 stage: str | None) -> Event:
    with get_session() as session:
        event = Event(title=title, subject=subject, code=code,
                      rsosh_level=rsosh_level, year=year, extra=extra,
                      stage=stage)
        session.add(event)
        session.commit()
        return event
