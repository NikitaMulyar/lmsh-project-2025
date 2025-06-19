from sqlalchemy import func, case, or_

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


def get_vos_finals_stats(year: int) -> list[int, int, int, int]:
    with get_session() as session:
        part = func.count(case((Record.status.in_(["Участник", "Призер", "Победитель"]), 1)))
        diploms = func.count(case((Record.status.in_(["Призер", "Победитель"]), 1)))
        pobed = func.count(case((Record.status == "Победитель", 1)))
        priz = func.count(case((Record.status == "Призер", 1)))

        query = session.query(
            part, diploms, pobed, priz
        ).join(User).join(Event).filter(
            Event.year == year,
            Event.code == 'ЗЭ ВСОШ'
        ).group_by(Event.year)

        records = query.all()
        return list(records[0])


def get_filtered_subjects_vos_finals(year: int, statuses: list[str],
                                     numbers: list[int], subjects: list[str]) \
        -> list[list[str, int, int, int, int]]:
    with get_session() as session:
        graduate_years = [year + 11 - number for number in numbers]

        part = func.count(case((Record.status.in_(["Участник", "Призер", "Победитель"]), 1)))
        diploms = func.count(case((Record.status.in_(["Призер", "Победитель"]), 1)))
        pobed = func.count(case((Record.status == "Победитель", 1)))
        priz = func.count(case((Record.status == "Призер", 1)))

        # Предикаты для фильтрации по агрегатам
        having_clauses = []
        if "Участник" in statuses:
            having_clauses.append(diploms == 0)
        if "Призер" in statuses:
            having_clauses.append(priz > 0)
        if "Победитель" in statuses:
            having_clauses.append(pobed > 0)

        query = session.query(
            Event.subject,
            part, diploms, pobed, priz
        ).join(User).join(Event).filter(
            Event.year == year,
            Event.code == 'ЗЭ ВСОШ'
        )

        if len(subjects) > 0:
            query = query.where(Event.subject.in_(subjects))

        if len(graduate_years) > 0:
            query = query.where(User.graduate_year.in_(graduate_years))

        query = query.group_by(
            Event.id, Event.subject
        )

        if having_clauses:
            query = query.having(or_(*having_clauses))

        query = query.order_by(Event.subject)
        records = [[el for el in row] for row in query.all()]
        return records
