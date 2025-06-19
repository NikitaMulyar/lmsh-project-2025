from server.models.event import Event

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


def get_vos_finals_subjects_list(year: int) -> list[str]:
    with get_session() as session:
        query = session.query(
            Event.subject
        ).filter(
            Event.year == year,
            Event.code == 'ЗЭ ВСОШ'
        ).order_by(
            Event.subject
        )

        records = [i[0] for i in query.all()]
        return records
