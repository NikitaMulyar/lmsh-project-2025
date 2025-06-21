from server.models.event import Event

from server.backend.database import get_session


def create_event(title: str, subject: str | None, rsosh_level: int | None,
                 year: int, extra: str | None,
                 olymp_code: str | None, olymp: str | None,
                 stage_code: str | None, stage: str | None,
                 english_olymp_code: str | None, english_stage_code: str | None) -> Event:
    with get_session() as session:
        event = Event(title=title, subject=subject, rsosh_level=rsosh_level,
                      year=year, extra=extra,
                      olymp_code=olymp_code, olymp=olymp,
                      stage_code=stage_code, stage=stage,
                      english_olymp_code=english_olymp_code, english_stage_code=english_stage_code)
        session.add(event)
        session.commit()
        return event


def get_vos_subjects_list(year: int, stage: str) -> list[str]:
    with get_session() as session:
        query = session.query(
            Event.subject
        ).filter(
            Event.year == year,
            Event.english_stage_code == stage,
            Event.olymp == 'ЗЭ ВсОШ'
        ).order_by(
            Event.subject
        )

        records = [i[0] for i in query.all()]
        return records
