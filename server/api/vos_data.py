from flask import Blueprint, request, jsonify

from server.services.event_crud import get_vos_finals_subjects_list
from server.services.record_crud import (get_vos_finals_stats,
                                         get_filtered_subjects_vos_finals)
from server.services.user_crud import get_filtered_users_vos_finals

vos_data_api = Blueprint('vos_data_api', __name__, url_prefix='/api/vos')


@vos_data_api.route('/finals/<int:year>', methods=['GET'])
def vos_finals_info(year: int):
    if request.args.get('index') is None or request.args['index'] not in ['fio', 'subject']:
        return jsonify({'message': 'Индексом может быть ФИО или предмет'}), 400

    try:
        data = request.get_json()
    except Exception:
        data = {}

    try:
        if request.args['index'] == 'fio':
            res = get_filtered_users_vos_finals(year,
                                                data.get('statuses', []),
                                                data.get('numbers', []),
                                                data.get('subjects', []))
        else:
            res = get_filtered_subjects_vos_finals(year,
                                                   data.get('statuses', []),
                                                   data.get('numbers', []),
                                                   data.get('subjects', []))
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'message': 'Некорректный запрос',
                        'details': e.__str__()}), 400


@vos_data_api.route('/stats/finals/<int:year>', methods=['GET'])
def vos_finals_stats_by_year(year: int):
    return jsonify(get_vos_finals_stats(year)), 200


@vos_data_api.route('/subjects/finals/<int:year>', methods=['GET'])
def vos_finals_subjects_by_year(year: int):
    return jsonify(get_vos_finals_subjects_list(year)), 200
