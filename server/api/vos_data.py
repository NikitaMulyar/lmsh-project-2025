from flask import Blueprint, request, jsonify

from server.services.event_crud import get_vos_subjects_list
from server.services.record_crud import (get_vos_stats,
                                         get_filtered_subjects_vos)
from server.services.user_crud import get_filtered_users_vos


# Блюпринт для эндпоинтов, связанных с данными ВсОШ (API)
vos_data_api = Blueprint('vos_data_api', __name__, url_prefix='/api/vos')


@vos_data_api.route('/<stage>/<int:year>', methods=['GET'])
def vos_info(stage: str, year: int):
    """
    Эндпоинт принимает path-параметры stage (этап) и year (год проведения этапа), query-параметр index -
    ключ группировки, и body-параметры для фильтрации данных: statuses (статусы участия в этапе), numbers (классы) и
    subjects (предметы).

    index может принимать одно из значений ``['fio', 'subject']``. ``fio`` - группировка по участникам, ``subject``
    - группировка по предметам.

    statuses - список, который может быть либо пустым, либо содержать значения
    ``['Участник', 'Призер', 'Победитель']`` (каждое из них либо есть, либо нет)

    numbers - список, который может быть либо пустым, либо содержать значения
    ``[6, 7, 8, 9, 10, 11]`` (каждое из них либо есть, либо нет)

    subjects - список, который может быть либо пустым, либо содержать названия предметов (важно: каждое
    значение должно быть уникальным)

    В случае невалидных данных возвращается код BAD_REQUEST (400) и словарь JSON с
    причиной ответа.

    1. Группировка по ``fio``:

    Возвращается список. Элемент списка - список вида

    id (str),
    ФИО (str),
    год выпуска (int),
    кол-во участий (int),
    кол-во дипломов (int),
    кол-во побед (int),
    <отсортированный в алфавитном порядке список редметов со статусом 'Победитель'> (list[str]),
    кол-во призерств (int),
    <отсортированный в алфавитном порядке список предметов со статусом 'Призер'> (list[str])

    2. Группировка по ``subject``:

    Возвращается список. Элемент списка - список вида

    предмет (str),
    кол-во участников (int),
    кол-во дипломов (int),
    кол-во победителей (int),
    кол-во призеров (int)

    :param stage: этап ВсОШ. Один из ``['finals', 'region', 'municip', 'school', 'invite']``
    :param year: год. В диапазоне от 2021 до 2025
    :return: Список списков
    """
    if stage not in ['finals', 'region', 'municip', 'school', 'invite']:
        return jsonify({'message': 'Неверный этап ВсОШ'}), 400

    if request.args.get('index') is None or request.args['index'] not in ['fio', 'subject']:
        return jsonify({'message': 'Индексом может быть ФИО или предмет'}), 400

    try:
        data = request.get_json()
    except Exception:
        data = {}

    if request.args['index'] == 'fio':
        res = get_filtered_users_vos(year, stage,
                                     data.get('statuses', []),
                                     data.get('numbers', []),
                                     data.get('subjects', []))
    else:
        res = get_filtered_subjects_vos(year, stage,
                                        data.get('statuses', []),
                                        data.get('numbers', []),
                                        data.get('subjects', []))
    return jsonify(res), 200


@vos_data_api.route('/stats/<stage>/<int:year>', methods=['GET'])
def vos_stats_by_year(stage: str, year: int):
    """
    Эндпоинт принимает path-параметры stage (этап) и year (год проведения этапа).

    Возвращается список из 4 чисел (int):

    кол-во участников, кол-во дипломов, кол-во победителей, кол-во призеров

    :param stage: этап ВсОШ. Один из ``['finals', 'region', 'municip', 'school', 'invite']``
    :param year: год. В диапазоне от 2021 до 2025
    :return: Список из 4 чисел типа int
    """
    if stage not in ['finals', 'region', 'municip', 'school', 'invite']:
        return jsonify({'message': 'Неверный этап ВсОШ'}), 400

    return jsonify(get_vos_stats(year, stage)), 200


@vos_data_api.route('/subjects/<stage>/<int:year>', methods=['GET'])
def vos_subjects_by_year(stage: str, year: int):
    """
    Эндпоинт принимает path-параметры stage (этап) и year (год проведения этапа).

    :param stage: этап ВсОШ. Один из ``['finals', 'region', 'municip', 'school', 'invite']``
    :param year: год. В диапазоне от 2021 до 2025
    :return: Отсортированный по алфавиту список предметов этапа ВсОШ
    """
    if stage not in ['finals', 'region', 'municip', 'school', 'invite']:
        return jsonify({'message': 'Неверный этап ВсОШ'}), 400

    return jsonify(get_vos_subjects_list(year, stage)), 200
