import json
import os

from flask import Blueprint, render_template

from server.forms.vos_filters import FilterVos

import requests


vos_data = Blueprint('vos_data', __name__, url_prefix='/vos')


@vos_data.route('/<stage>/<int:year>', methods=['GET', 'POST'])
def vos_table(stage: str, year: int):
    subjects = requests.get(
        f'http://{os.getenv('HOST')}:{os.getenv('PORT')}/api/vos/subjects/{stage}/{year}'
    ).json()
    for i in range(len(subjects)):
        subjects[i] = [subjects[i], subjects[i]]

    year_stats = requests.get(
        f'http://{os.getenv('HOST')}:{os.getenv('PORT')}/api/vos/stats/{stage}/{year}'
    ).json()

    stage_ru = json.load(open('static/json/vos/stages.json', mode='rb'))[stage]

    form = FilterVos()
    form.subjects.choices = subjects
    if form.index.data is None:
        form.index.data = 'fio'

    students = []

    if form.validate_on_submit():
        students = requests.get(
            f'http://{os.getenv('HOST')}:{os.getenv('PORT')}/api/vos/{stage}/{year}?index={form.index.data}',
            json={'statuses': form.statuses.data,
                  'numbers': form.numbers.data,
                  'subjects': form.subjects.data
                  }
        ).json()

        return render_template('vos.html', form=form,
                               title=f'Заключительный этап ВсОШ',
                               table_index=form.index.data,
                               year_stats=year_stats, YEAR=year, STAGE=stage_ru,
                               students=students)

    return render_template('vos.html', form=form,
                           title=f'Заключительный этап ВсОШ',
                           table_index=form.index.data,
                           year_stats=year_stats, YEAR=year, STAGE=stage_ru,
                           students=students)
