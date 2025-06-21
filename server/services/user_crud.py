from sqlalchemy.orm import joinedload
from sqlalchemy import func, case, or_, cast, String

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
            .options(joinedload(User.records).joinedload(Record.event)).first()
        return user


def get_user_by_id(id: str) -> User | None:
    with get_session() as session:
        user = session.query(User).where(User.id == id)\
            .options(joinedload(User.records).joinedload(Record.event)).first()
        return user


def get_filtered_users_vos_finals(year: int, statuses: list[str],
                                  numbers: list[int], subjects: list[str]) \
        -> list[list[str, str, int, int, int, int, str, int, str]]:
    # id, ФИО, Год выпуска, Участие, Дипломы, Победитель, <список предметов побед.>, Призер, <список предметов приз.>
    with get_session() as session:
        graduate_years = [year + 11 - number for number in numbers]

        part = func.count(case((Record.status.in_(["Участник", "Призер", "Победитель"]), 1)))
        diploms = func.count(case((Record.status.in_(["Призер", "Победитель"]), 1)))
        pobed = func.count(case((Record.status == "Победитель", 1)))
        priz = func.count(case((Record.status == "Призер", 1)))

        condition_pobed_subjects = case(
            (Record.status == "Победитель", Event.subject),  # склеиваем только Победитель
            else_=None  # NULL значения будут пропущены group_concat
        )
        condition_priz_subjects = case(
            (Record.status == "Призер", Event.subject),  # склеиваем только Победитель
            else_=None  # NULL значения будут пропущены group_concat
        )

        # Предикаты для фильтрации по агрегатам
        having_clauses = []
        if "Участник" in statuses:
            having_clauses.append(diploms == 0)
        if "Призер" in statuses:
            having_clauses.append(priz > 0)
        if "Победитель" in statuses:
            having_clauses.append(pobed > 0)

        number = 11 - (User.graduate_year - year)
        fio_with_number = func.concat(
            User.fio,
            " (",
            cast(number, String),
            ")"
        ).label("fio_with_number")

        query = session.query(
            User.id,
            fio_with_number,
            User.graduate_year,
            part, diploms,
            pobed, func.group_concat(condition_pobed_subjects, '$$'),
            priz, func.group_concat(condition_priz_subjects, '$$')
        ).join(User).join(Event).filter(
            Event.year == year,
            Event.code == 'ЗЭ ВСОШ'
        )

        if len(subjects) > 0:
            query = query.where(Event.subject.in_(subjects))

        if len(graduate_years) > 0:
            query = query.where(User.graduate_year.in_(graduate_years))

        query = query.group_by(
            User.id, fio_with_number, User.graduate_year
        )

        if having_clauses:
            query = query.having(or_(*having_clauses))

        query = query.order_by(User.fio)
        records = [[el for el in row] for row in query.all()]
        for i in range(len(records)):
            records[i] = \
            records[i][:-3] + \
            ([sorted(records[i][-3].split('$$'))] if records[i][-3] else [[]]) + \
            [records[i][-2]] + \
            ([sorted(records[i][-1].split('$$'))] if records[i][-1] else [[]])

        return records
