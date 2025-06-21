from sqlalchemy import func, case, or_

from server.models.event import Event
from server.models.user import User
from server.models.record import Record

from server.backend.database import get_session


def create_record(user_id: str, event_id: str, status: str | None,
                  points: int | None, extra: str | None) -> Record:
    """
    Создание записи и добавление в базу данных
    :param user_id:
    :param event_id:
    :param status:
    :param points:
    :param extra:
    :return: модель SQLAlchemy класса ``Record``
    """
    with get_session() as session:
        record = Record(user_id=user_id, event_id=event_id, status=status,
                        points=points, extra=extra)
        session.add(record)
        session.commit()
        return record


def get_vos_stats(year: int, stage: str) -> list[int, int, int, int]:
    """
    Возвращает статистику ВсОШ по заданному этапу и году

    Возвращается список из 4 чисел (int):

    кол-во участников, кол-во дипломов, кол-во победителей, кол-во призеров

    :param year: год ВсОШ. От 2021 до 2025
    :param stage: этап ВсОШ. Один из ``['finals', 'region', 'municip', 'school', 'invite']``
    :return: Список из 4 чисел типа int
    """
    with get_session() as session:
        part = func.count(case((Record.status.in_(["Участник", "Призер", "Победитель"]), 1)))
        diploms = func.count(case((Record.status.in_(["Призер", "Победитель"]), 1)))
        pobed = func.count(case((Record.status == "Победитель", 1)))
        priz = func.count(case((Record.status == "Призер", 1)))

        query = session.query(
            part, diploms, pobed, priz
        ).join(User).join(Event).filter(
            Event.year == year,
            Event.english_stage_code == stage,
            Event.english_olymp_code == 'vos'
        ).group_by(Event.year)

        records = query.all()
        return list(records[0]) if len(records) == 1 else [0, 0, 0, 0]


def get_filtered_subjects_vos(year: int, stage: str, statuses: list[str],
                              numbers: list[int], subjects: list[str]) \
        -> list[list[str, int, int, int, int]]:
    """
    Подсчитывается статистика ВсОШ.

    Возвращается список. Элемент списка - список вида

    предмет (str),
    кол-во участников (int),
    кол-во дипломов (int),
    кол-во победителей (int),
    кол-во призеров (int)

    :param year: год ВсОШ. От 2021 до 2025
    :param stage: этап ВсОШ. Один из ``['finals', 'region', 'municip', 'school', 'invite']``
    :param statuses: список, который может быть либо пустым, либо содержать значения ``['Участник', 'Призер', 'Победитель']`` (каждое из них либо есть, либо нет)
    :param numbers: список, который может быть либо пустым, либо содержать значения ``[6, 7, 8, 9, 10, 11]`` (каждое из них либо есть, либо нет)
    :param subjects: список, который может быть либо пустым, либо содержать названия предметов (важно: каждое значение должно быть уникальным)
    :return: Список списков
    """
    with get_session() as session:
        graduate_years = [year + 11 - number for number in numbers]

        # Выражения для подсчета количества участников, дипломов, победителей и призеров по предмету
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
            Event.english_stage_code == stage,
            Event.english_olymp_code == 'vos'
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
