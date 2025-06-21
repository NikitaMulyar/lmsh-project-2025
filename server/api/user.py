from flask import Blueprint, jsonify

from server.services.user_crud import get_user_stats, get_user_records


user_api = Blueprint('user_api', __name__, url_prefix='/api/user')


@user_api.route('/<id>', methods=['GET'])
def user_info(id: str):
    result = {
        'stats': get_user_stats(id),
        'records': get_user_records(id)
    }

    return jsonify(result), 200
