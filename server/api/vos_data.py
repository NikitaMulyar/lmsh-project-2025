from flask import Blueprint, request, jsonify

from server.services.event_crud import get_vos_subjects_list
from server.services.record_crud import (get_vos_stats,
                                         get_filtered_subjects_vos)
from server.services.user_crud import get_filtered_users_vos


vos_data_api = Blueprint('vos_data_api', __name__, url_prefix='/api/vos')


@vos_data_api.route('/<stage>/<int:year>', methods=['GET'])
def vos_info(stage: str, year: int):
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
    if stage not in ['finals', 'region', 'municip', 'school', 'invite']:
        return jsonify({'message': 'Неверный этап ВсОШ'}), 400

    return jsonify(get_vos_stats(year, stage)), 200


@vos_data_api.route('/subjects/<stage>/<int:year>', methods=['GET'])
def vos_subjects_by_year(stage: str, year: int):
    if stage not in ['finals', 'region', 'municip', 'school', 'invite']:
        return jsonify({'message': 'Неверный этап ВсОШ'}), 400

    return jsonify(get_vos_subjects_list(year, stage)), 200
