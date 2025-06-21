import os

from flask import Blueprint, render_template

import requests


user_data = Blueprint('user_data', __name__, url_prefix='/user')


@user_data.route('/<id>', methods=['GET'])
def user_profile(id: str):
    res = requests.get(
        f'http://{os.getenv('HOST')}:{os.getenv('PORT')}/api/user/{id}'
    ).json()

    return render_template('profile.html', user_data=res['records'],
                           user_stats=res['stats'])
