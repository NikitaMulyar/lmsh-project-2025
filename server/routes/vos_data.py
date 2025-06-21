from flask import Blueprint, render_template, request, redirect

from server.forms.vos_filters import FilterVosFinals

import requests


vos_data = Blueprint('vos_data', __name__, url_prefix='/vos')


@vos_data.route('/finals/<int:year>', methods=['GET', 'POST'])
def vos_finals_table(year: int):
    subjects = requests.get(
        f'http://127.0.0.1:5000/api/vos/subjects/finals/{year}'
    ).json()
    for i in range(len(subjects)):
        subjects[i] = [subjects[i], subjects[i]]

    year_stats = requests.get(
        f'http://127.0.0.1:5000/api/vos/stats/finals/{year}'
    ).json()

    form = FilterVosFinals()
    form.subjects.choices = subjects
    if form.index.data is None:
        form.index.data = 'fio'

    students = []

    if form.validate_on_submit():
        students = requests.get(
            f'http://127.0.0.1:5000/api/vos/finals/{year}?index={form.index.data}',
            json={'statuses': form.statuses.data,
                  'numbers': form.numbers.data,
                  'subjects': form.subjects.data
                  }
        ).json()

        return render_template('vos/finals.html', form=form,
                               title=f'Заключительный этап ВсОШ',
                               table_index=form.index.data,
                               year_stats=year_stats, year=year, students=students)

    return render_template('vos/finals.html', form=form,
                           title=f'Заключительный этап ВсОШ',
                           table_index=form.index.data,
                           year_stats=year_stats, year=year, students=students)
