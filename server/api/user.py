from flask import Blueprint, jsonify

from server.services.user_crud import get_user_by_id


user_api = Blueprint('user_api', __name__, url_prefix='/api/user')


@user_api.route('/<id>', methods=['GET'])
def user_info(id: str):
    user = get_user_by_id(id)

    if user is not None:
        d = {}
        for record in user.records:
            code = f'{record.event.code} {record.event.year}'
            if code not in d:
                d[code] = [[record.event.year, record.event.rsosh_level], []]
            d[code][1].append([record.event.subject, record.status, record.points])

        data = []
        for title, info in d.items():
            data.append([title, info[1], info[0]])
        data.sort(key=lambda elem: (elem[2][0], -elem[2][1]), reverse=True)

        for i in range(len(data)):
            del data[i][-1]
            data[i][-1].sort(key=lambda elem: (elem[1], elem[0]))

        return jsonify(data), 200
    else:
        return jsonify({'message': 'Пользователя не существует'}), 404
