import asyncio

import httpx
import bs4
import json
import re

from rich.console import Console
from rich.panel import Panel


async def save_vos_teams_data_by_year(year: int):
    """
    Сохраняет данные о команде Сборной Москвы на финале ВсОШ за заданный год в папку 'data/vos/finals/'.
    :param year: год финала ВсОШ
    :return:
    """
    console = Console()  # для красивого вывода статусов обработки в консоль

    parsed_data = []
    async with httpx.AsyncClient() as client:
        attempts = 3
        while attempts > 0:
            try:
                result = await client.get(f'https://vos.olimpiada.ru/team/year/{year}/staff')
                console.print(
                    Panel.fit(
                        f"[bold green]Успешно[/bold green]\n"
                        f"[green]Участники - ЗЭ ВсОШ {year} год[/green]",
                        title="[green]Статус[/green]",
                        border_style="green"
                    )
                )
                break
            except Exception:
                console.print(
                    Panel.fit(
                        f"[bold yellow]Ошибка[/bold yellow]\n"
                        f"[yellow]Участники - ЗЭ ВсОШ {year} год\n"
                        f"Повторная попытка...[/yellow]",
                        title="[yellow]Статус[/yellow]",
                        border_style="yellow"
                    )
                )
                await asyncio.sleep(0.2)
                attempts -= 1
        if attempts == 0:
            console.print(
                Panel.fit(
                    f"[bold red]Не удалось получить данные[/bold red]\n"
                    f"[red]Участники - ЗЭ ВсОШ {year} год[/red]",
                    title="[red]Статус[/red]",
                    border_style="red"
                )
            )
            file = open(f'data/vos/finals/teams_{year}.json', mode='w')
            json.dump([], file, ensure_ascii=False, indent=4)
            file.close()
            return

        soup = bs4.BeautifulSoup(result.text
                                 .replace('&nbsp;', ' '),
                                 features='lxml')

        # Все блоки с предметами (отмечены <p><strong><span>)

        for p in soup.find_all("p"):
            strong = p.find("strong")
            if not strong:
                continue

            span = strong.find("span")
            if not span:
                continue

            title = ".".join(span.text.strip('\n \t').split('.')[1:]).strip('\n \t')  # Название предмета
            if title == 'ru':  # Случайно попадается почта
                continue

            data = {
                'title': title,
                'team': {}
            }
            cur_tag = p.find_next_sibling()  # Перемещение к следующему тегу
            while cur_tag and cur_tag.name != 'hr':  # Двигаемся до конца страницы, пока можем
                class_ = cur_tag.text.split()[0]  # Класс

                cur_tag = cur_tag.find_next_sibling()
                for student in cur_tag.find_all('li'):
                    fio, school = student.text.split(',', maxsplit=1)
                    fio = fio.strip('\n \t')
                    school = school.strip('\n \t')
                    if not data['team'].get(class_):
                        data['team'][class_] = []
                    data['team'][class_].append([fio, school])

                cur_tag = cur_tag.find_next_sibling()
            parsed_data.append(data)

    file = open(f'data/vos/finals/teams_{year}.json', mode='w')
    json.dump(parsed_data, file, ensure_ascii=False, indent=4)
    file.close()


async def save_vos_results_data_by_year(year: int):
    """
    Сохраняет данные о результатах Сборной Москвы на финале ВсОШ за заданный год в папку 'data/vos/finals/'.
    :param year: год финала ВсОШ
    :return:
    """

    console = Console()  # для красивого вывода статусов обработки в консоль

    parsed_data = []
    async with httpx.AsyncClient() as client:
        attempts = 3
        while attempts > 0:
            try:
                result = await client.get(f'https://vos.olimpiada.ru/team/year/{year}/results')
                console.print(
                    Panel.fit(
                        f"[bold green]Успешно[/bold green]\n"
                        f"[green]ПиПы - ЗЭ ВсОШ {year} год[/green]",
                        title="[green]Статус[/green]",
                        border_style="green"
                    )
                )
                break
            except Exception:
                console.print(
                    Panel.fit(
                        f"[bold yellow]Ошибка[/bold yellow]\n"
                        f"[yellow]ПиПы - ЗЭ ВсОШ {year} год\n"
                        f"Повторная попытка...[/yellow]",
                        title="[yellow]Статус[/yellow]",
                        border_style="yellow"
                    )
                )
                await asyncio.sleep(0.2)
                attempts -= 1
        if attempts == 0:
            console.print(
                Panel.fit(
                    f"[bold red]Не удалось получить данные[/bold red]\n"
                    f"[red]ПиПы - ЗЭ ВсОШ {year} год[/red]",
                    title="[red]Статус[/red]",
                    border_style="red"
                )
            )
            file = open(f'data/vos/finals/results_{year}.json', mode='w')
            json.dump([], file, ensure_ascii=False, indent=4)
            file.close()
            return

        soup = bs4.BeautifulSoup(result.text
                                 .replace('&nbsp;', ' '),
                                 features='lxml')

        # Все блоки с предметами (отмечены <p><strong><span>)

        for p in soup.find_all("p"):
            strong = p.find("strong")
            if not strong:
                continue

            span = strong.find("span")
            if not span:
                continue

            title = ".".join(span.text.strip('\n \t').split('.')[1:]).strip('\n \t')  # Название предмета
            if title == 'ru':  # Случайно попадается почта
                continue

            data = {
                'title': title,
                'pobed': {},
                'priz': {}
            }
            cur_status = None  # Храним текущий статус, поскольку он будет меняться
            cur_tag = p.find_next_sibling()
            while cur_tag and cur_tag.name != 'hr':  # Двигаемся до конца страницы, пока можем
                if 'победител' in cur_tag.text.lower():
                    cur_status = 'pobed'  # Запоминаем текущий статус, поскольку после него идет список людей с ним
                    cur_tag = cur_tag.find_next_sibling()
                    continue
                elif 'призер' in cur_tag.text.lower().replace('ё', 'е'):
                    cur_status = 'priz'
                    cur_tag = cur_tag.find_next_sibling()
                    continue

                class_ = cur_tag.text.split()[0]

                cur_tag = cur_tag.find_next_sibling()
                for student in cur_tag.find_all('li'):
                    fio, school = student.text.split(',', maxsplit=1)  # На всякий случай делаем только 1 сплит
                    fio = fio.strip('\n \t')

                    unique_class = list(re.finditer(r'\s\((\d\d?) класс\)', fio))  # Некоторые участники
                    # выступают за класс старше, поэтому в скобках у них написан их настоящий класс. Запоминаем
                    if len(unique_class) == 1:
                        idx_to_cut = unique_class[0].span()[0]
                        unique_class = unique_class[0].group(1)
                    else:
                        unique_class = class_
                        idx_to_cut = len(fio)
                    fio = fio[:idx_to_cut]

                    school = school.strip('\n \t')
                    if not data[cur_status].get(unique_class):
                        data[cur_status][unique_class] = []
                    data[cur_status][unique_class].append([fio, school])

                cur_tag = cur_tag.find_next_sibling()
            parsed_data.append(data)

    file = open(f'data/vos/finals/results_{year}.json', mode='w')
    json.dump(parsed_data, file, ensure_ascii=False, indent=4)
    file.close()
