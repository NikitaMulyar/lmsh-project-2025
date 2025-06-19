from flask import Blueprint, request, jsonify

from server.services.user_crud import get_filtered_users_vos_finals
from server.services.record_crud import (get_vos_finals_stats,
                                         get_filtered_subjects_vos_finals)


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
            res = {
                'stats': get_vos_finals_stats(year),
                'index': request.args['index'],
                'data': get_filtered_users_vos_finals(year,
                                                      data.get('statuses', []),
                                                      data.get('numbers', []),
                                                      data.get('subjects', []))
            }
        else:
            res = {
                'stats': get_vos_finals_stats(year),
                'index': request.args['index'],
                'data': get_filtered_subjects_vos_finals(year,
                                                         data.get('statuses', []),
                                                         data.get('numbers', []),
                                                         data.get('subjects', []))
            }
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'message': 'Некорректный запрос',
                        'details': e.__str__()}), 400
