from sqlalchemy.orm import joinedload
from sqlalchemy import func, case, or_, cast, String, Integer

from server.models.event import Event
from server.models.user import User
from server.models.record import Record

from server.backend.database import get_session

from sqlalchemy.sql.functions import coalesce


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


def get_filtered_users_vos(year: int, stage: str, statuses: list[str],
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
            Event.english_stage_code == stage,
            Event.english_olymp_code == 'vos'
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


def get_user_stats(id: str) -> list[str, str, int, str | None, int, int, int, int, int, float]:
    with get_session() as session:
        # id, ФИО, Год выпуска, профиль, балл ЕГЭ, ср. балл ОГЭ, кол-во побед, кол-во призерств, кол-во участий,
        # % успешных выступлений
        part = func.count(case((Record.status.in_(["Участник", "Призер", "Победитель"]), 1)))
        diploms = func.count(case((Record.status.in_(["Призер", "Победитель"]), 1)))
        pobed = func.count(case((Record.status == "Победитель", 1)))
        priz = func.count(case((Record.status == "Призер", 1)))

        query = session.query(
            User.id,
            User.fio,
            User.graduate_year,
            User.profile,
            coalesce(func.sum(case((Event.english_olymp_code == 'ege', Record.points))), 0),  # Балл ЕГЭ
            coalesce(func.avg(case((Event.english_olymp_code == 'oge', Record.points))), 0),  # Ср. балл ОГЭ
            pobed, priz, part,
            cast(func.round(diploms / part * 100), Integer)  # % Успешных выступлений
        ).join(User).join(Event).where(
            User.id == id
        ).group_by(
            User.id, User.fio, User.graduate_year
        )

        records = query.all()

        return list(records[0]) if len(records) == 1 else ['', '', 0, None, 0, 0, 0, 0, 0, 0.0]


def get_user_records(id: str) -> dict[str, list]:
    user = get_user_by_id(id)
    if user is None:
        return {
            'vos': [],
            'rsosh': [],
            'ege': [],
            'oge': [],
            'other': []
        }

    bins = {
        'vos': {},
        'rsosh': {},
        'ege': {},
        'oge': {},
        'other': {}
    }
    # Разнесем все записи по "корзинкам". Ключом будет список из 2 элементов: заголовка и ключа сортировки для
    # списка
    for record in user.records:
        # ВсОШ
        if -100 <= record.event.rsosh_level <= -96:
            key = (f'{record.event.olymp} {record.event.year}',
                   (-record.event.year, record.event.rsosh_level))
            if not bins['vos'].get(key):
                bins['vos'][key] = []

            bins['vos'][key].append([record.event.subject, record.status, record.points])
        # РСОШ
        elif 1 <= record.event.rsosh_level <= 3:
            key = (f'{record.event.olymp} {record.event.year}',
                   (-record.event.year, record.event.rsosh_level, record.event.olymp))
            if not bins['rsosh'].get(key):
                bins['rsosh'][key] = []

            bins['rsosh'][key].append([record.event.subject, record.status, record.points])
        # ЕГЭ
        elif record.event.rsosh_level == -90:
            key = (f'{record.event.olymp} {record.event.year}',
                   (-record.event.year, record.event.olymp))
            if not bins['ege'].get(key):
                bins['ege'][key] = []

            bins['ege'][key].append([record.event.subject, record.status, record.points])
        # ОГЭ
        elif record.event.rsosh_level == -89:
            key = (f'{record.event.olymp} {record.event.year}',
                   (-record.event.year, record.event.olymp))
            if not bins['oge'].get(key):
                bins['oge'][key] = []

            bins['oge'][key].append([record.event.subject, record.status, record.points])
        # Прочее
        else:
            key = (f'{record.event.title} {record.event.year}',
                   (-record.event.year, record.event.title))
            if not bins['other'].get(key):
                bins['other'][key] = []

            bins['other'][key].append([record.event.subject, record.status, record.points])

    bins2 = {
        'vos': [],
        'rsosh': [],
        'ege': [],
        'oge': [],
        'other': []
    }
    # Подготовим данные для передачи на бэкенд. Отсортируем по ключу
    for event_type in bins:
        for key, value in bins[event_type].items():
            bins2[event_type].append([key, sorted(value, key=lambda el: el[0])])
        bins2[event_type].sort(key=lambda el: el[0][1])

    return bins2
