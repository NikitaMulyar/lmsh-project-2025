from sqlalchemy.orm import joinedload

from server.models.event import Event
from server.models.user import User
from server.models.record import Record

from server.backend.database import get_session


def create_record(user_id: str, event_id: str, status: str | None,
                  points: int | None, extra: str | None) -> Record:
    with get_session() as session:
        record = Record(user_id=user_id, event_id=event_id, status=status,
                        points=points, extra=extra)
        session.add(record)
        session.commit()
        return record
