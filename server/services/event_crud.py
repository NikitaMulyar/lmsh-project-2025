from server.models.event import Event

from server.backend.database import get_session


def create_event(title: str, subject: str | None, rsosh_level: int | None,
                 year: int, extra: str | None,
                 olymp_code: str | None, olymp: str | None,
                 stage_code: str | None, stage: str | None,
                 english_olymp_code: str | None, english_stage_code: str | None) -> Event:
    """
    Создание события и добавление в базу данных
    :param title: Название олимпиады/события. Нет строгих требований (нельзя писать в конце год, он дописывается где нужно сам). Можно писать что угодно
    :param subject: Предмет
    :param rsosh_level: Для олимпиад РСОШ используется для сортировки, для остальных - для разграничения типов и сортировки
    :param year: Год олимпиады
    :param extra: Любая доп. информация
    :param olymp_code: Код олимпиады. Например: ЕГЭ, ОГЭ, ВсОШ, МОШ, PROD
    :param olymp: Краткое название олимпиады (без предмета) (используется для группировки). Например: ЕГЭ, ЗЭ ВсОШ, МЭ ВсОШ, МОШ, PROD
    :param stage_code: Код этапа. Например: ОЭ (отборочный), ЗЭ (заключительный)
    :param stage: Полное название этапа. Например: Заключительный, Отборочный
    :param english_olymp_code: Код олимпиады на английском. Например: prod, vos, mosh
    :param english_stage_code: Код этапа на английском. Например: invite, school, municip, region, finals, qualify
    :return: модель SQLAlchemy класса ``Event``
    """
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
    """
    Возвращает отсортированный по алфавиту список предметов этапа ВсОШ
    :param year: год ВсОШ. От 2021 до 2025
    :param stage: этап ВсОШ. Один из ``['finals', 'region', 'municip', 'school', 'invite']``
    :return:
    """
    with get_session() as session:
        query = session.query(
            Event.subject
        ).filter(
            Event.year == year,
            Event.english_stage_code == stage,
            Event.english_olymp_code == 'vos'
        ).order_by(
            Event.subject
        )

        records = [i[0] for i in query.all()]
        return records
