import os
import asyncio
import json

from server.services.user_crud import create_user, get_user_by_fio
from server.services.event_crud import create_event
from server.services.record_crud import create_record

from server.dependencies.vos_data import (save_vos_teams_data_by_year,
                                          save_vos_results_data_by_year)

from rich.console import Console
from rich.panel import Panel


if not os.path.exists('data/'):
    os.mkdir('data/')

if not os.path.exists('data/vos/'):
    os.mkdir('data/vos/')

if not os.path.exists('data/vos/finals/'):
    os.mkdir('data/vos/finals/')


async def save_vos_finals_data(year_start: int, year_end: int):
    """
    Сохраняет данные о команде и результатах Сборной Москвы на финале ВсОШ за заданные года.
    :param year_start: начальный год
    :param year_end: последний год
    :return:
    """
    tasks = []
    for year in range(year_start, year_end + 1):
        tasks.append(save_vos_teams_data_by_year(year))
        tasks.append(save_vos_results_data_by_year(year))
    await asyncio.gather(*tasks)


async def fill_database_vos_finals_data(year_start: int, year_end: int):
    """
    Использует данные из папки `data/vos/finals/` для занесения лицеистов и их результатов в базу данных
    :param year_start: начальный год
    :param year_end: последний год
    :return:
    """

    console = Console()  # для красивого вывода статусов обработки в консоль
    events_rsosh_levels = json.load(open('static/json/events_rsosh_levels.json', mode='rb'))
    # соответствие rsosh_level для типа мероприятия

    statuses = {}
    # Словарь с каскадными ключами:
    # год (int) -> предмет (str) -> ФИО (str)
    # Значение - 'pobed' или 'priz'
    for year in range(year_start, year_end + 1):
        statuses[year] = {}
        results = json.load(open(f'data/vos/finals/results_{year}.json', mode='rb'))
        for subject in results:
            statuses[year][subject['title']] = {}
            for number in subject['pobed']:
                for student in subject['pobed'][number]:
                    statuses[year][subject['title']][student[0]] = 'pobed'
            for number in subject['priz']:
                for student in subject['priz'][number]:
                    statuses[year][subject['title']][student[0]] = 'priz'

    for year in range(year_start, year_end + 1):
        teams = json.load(open(f'data/vos/finals/teams_{year}.json', mode='rb'))
        for subject in teams:
            event = create_event(f'ЗЭ ВсОШ по {subject['title']}',
                                 subject['title'], events_rsosh_levels['ЗЭ ВсОШ'],
                                 year, None,
                                 'ВсОШ', 'ЗЭ ВсОШ',
                                 'ЗЭ', 'Заключительный',
                                 'vos', 'finals')
            # Создание события, чтобы использовать его id для создания записей
            for number in subject['team']:
                for student in subject['team'][number]:
                    # Рассматриваем только второшкольников
                    if 'лицей' in student[1].lower() \
                            and 'вторая школа' in student[1].lower():
                        user = get_user_by_fio(student[0])
                        if user is None:
                            user = create_user(student[0],
                                               year + 11 - int(number), None)
                        # Лицеист мог стать ПиПом в разных предметах, поэтому важно не дублировать его.
                        # После этого вместо кучи ифов пытаемся достать статус участия. Если нет - то он был участником.
                        try:
                            won = statuses[year][subject['title']][student[0]]
                        except Exception:
                            won = None
                        if won is None:
                            won = 'Участник'
                        elif won == 'pobed':
                            won = 'Победитель'
                        elif won == 'priz':
                            won = 'Призер'
                        create_record(user.id, event.id, won, None, None)
        console.print(
            Panel.fit(
                f"[bold green]Успешное добавление в БД[/bold green]\n"
                f"[green]Участники и ПиПы Л2Ш - ЗЭ ВсОШ {year} год[/green]",
                title="[green]Статус[/green]",
                border_style="green"
            )
        )


async def prepare_data(year_start=2021, year_end=2025):
    """
    Вызывает функции ``save_vos_finals_data`` и ``fill_database_vos_finals_data``
    :param year_start: начальный год
    :param year_end: последний год
    :return:
    """
    await save_vos_finals_data(year_start, year_end)
    await fill_database_vos_finals_data(year_start, year_end)
