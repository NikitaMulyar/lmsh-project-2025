import asyncio

import httpx
import bs4
import json
import re

from rich.console import Console
from rich.panel import Panel


async def save_vos_teams_data_by_year(year: int, return_l2sh_only=True) \
        -> list[dict[str, str | dict[str, list[str]]]] | None:
    console = Console()

    parsed_data = []
    async with httpx.AsyncClient() as client:
        attempts = 3
        while attempts > 0:
            try:
                result = await client.get(f'https://vos.olimpiada.ru/team/year/{year}/staff')
                console.print(
                    Panel.fit(
                        f"[bold green]Успешно[/bold green]\n"
                        f"[green]Участники - {year} год[/green]",
                        title="[green]Статус[/green]",
                        border_style="green"
                    )
                )
                break
            except Exception:
                console.print(
                    Panel.fit(
                        f"[bold yellow]Ошибка[/bold yellow]\n"
                        f"[yellow]Участники - {year} год\n"
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
                    f"[red]Участники - {year} год[/red]",
                    title="[red]Статус[/red]",
                    border_style="red"
                )
            )
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

            title = span.text.strip('\n \t').split('.')[1].strip('\n \t')
            if title == 'ru':
                continue

            data = {
                'title': title,
                'team': {}
            }
            cur_tag = p.find_next_sibling()
            while cur_tag and cur_tag.name != 'hr':
                class_ = cur_tag.text.split()[0]

                cur_tag = cur_tag.find_next_sibling()
                for student in cur_tag.find_all('li'):
                    fio, school = student.text.split(',', maxsplit=1)
                    fio = fio.strip('\n \t')
                    school = school.strip('\n \t')
                    if not return_l2sh_only:
                        if not data['team'].get(class_):
                            data['team'][class_] = []

                        data['team'][class_].append([fio, school])
                    elif return_l2sh_only and 'лицей' in school.lower() \
                            and 'вторая школа' in school.lower():
                        if not data['team'].get(class_):
                            data['team'][class_] = []

                        data['team'][class_].append([fio, school])
                cur_tag = cur_tag.find_next_sibling()
            parsed_data.append(data)

    if not return_l2sh_only:
        file = open(f'data/vos/teams_{year}.json', mode='w')
        json.dump(parsed_data, file, ensure_ascii=False, indent=4)
        file.close()

    return parsed_data


async def save_vos_results_data_by_year(year: int, return_l2sh_only=True) \
        -> list[dict[str, str | dict[str, list[str]]]] | None:
    console = Console()

    parsed_data = []
    async with httpx.AsyncClient() as client:
        attempts = 3
        while attempts > 0:
            try:
                result = await client.get(f'https://vos.olimpiada.ru/team/year/{year}/results')
                console.print(
                    Panel.fit(
                        f"[bold green]Успешно[/bold green]\n"
                        f"[green]ПиПы - {year} год[/green]",
                        title="[green]Статус[/green]",
                        border_style="green"
                    )
                )
                break
            except Exception:
                console.print(
                    Panel.fit(
                        f"[bold yellow]Ошибка[/bold yellow]\n"
                        f"[yellow]ПиПы - {year} год\n"
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
                    f"[red]ПиПы - {year} год[/red]",
                    title="[red]Статус[/red]",
                    border_style="red"
                )
            )
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

            title = span.text.strip('\n \t').split('.')[1].strip('\n \t')
            if title == 'ru':
                continue

            data = {
                'title': title,
                'pobed': {},
                'priz': {}
            }
            cur_status = None
            cur_tag = p.find_next_sibling()
            while cur_tag and cur_tag.name != 'hr':
                if 'победител' in cur_tag.text.lower():
                    cur_status = 'pobed'
                    cur_tag = cur_tag.find_next_sibling()
                    continue
                elif 'призер' in cur_tag.text.lower().replace('ё', 'е'):
                    cur_status = 'priz'
                    cur_tag = cur_tag.find_next_sibling()
                    continue

                class_ = cur_tag.text.split()[0]

                cur_tag = cur_tag.find_next_sibling()
                for student in cur_tag.find_all('li'):
                    fio, school = student.text.split(',', maxsplit=1)
                    fio = fio.strip('\n \t')

                    unique_class = list(re.finditer(r'\s\((\d\d?) класс\)', fio))
                    if len(unique_class) == 1:
                        idx_to_cut = unique_class[0].span()[0]
                        unique_class = unique_class[0].group(1)
                    else:
                        unique_class = class_
                        idx_to_cut = len(fio)
                    fio = fio[:idx_to_cut]

                    school = school.strip('\n \t')
                    if not return_l2sh_only:
                        if not data[cur_status].get(unique_class):
                            data[cur_status][unique_class] = []

                        data[cur_status][unique_class].append([fio, school])
                    elif return_l2sh_only and 'лицей' in school.lower() \
                            and 'вторая школа' in school.lower():
                        if not data[cur_status].get(unique_class):
                            data[cur_status][unique_class] = []

                        data[cur_status][unique_class].append([fio, school])
                cur_tag = cur_tag.find_next_sibling()
            parsed_data.append(data)

    if not return_l2sh_only:
        file = open(f'data/vos/results_{year}.json', mode='w')
        json.dump(parsed_data, file, ensure_ascii=False, indent=4)
        file.close()

    return parsed_data
