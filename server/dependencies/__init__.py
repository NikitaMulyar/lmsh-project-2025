import os
import asyncio

from server.dependencies.vos_data import (save_vos_teams_data_by_year,
                                          save_vos_results_data_by_year)


if not os.path.exists('data/'):
    os.mkdir('data/')

if not os.path.exists('data/vos/'):
    os.mkdir('data/vos/')


async def save_vos_data(year_start=2021, year_end=2025):
    tasks = []
    for year in range(year_start, year_end + 1):
        tasks.append(save_vos_teams_data_by_year(year, return_l2sh_only=False))
        tasks.append(save_vos_results_data_by_year(year, return_l2sh_only=False))
    await asyncio.gather(*tasks)


async def fill_database():
    pass


async def prepare_data():
    await save_vos_data()
    await fill_database()


asyncio.run(prepare_data())
