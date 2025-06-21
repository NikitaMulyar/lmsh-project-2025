from flask import Blueprint, jsonify

from server.services.user_crud import get_user_stats, get_user_records


# Блюпринт для эндпоинтов, связанных с данными юзера (API)
user_api = Blueprint('user_api', __name__, url_prefix='/api/user')


@user_api.route('/<id>', methods=['GET'])
def user_info(id: str):
    """
    Эндпоинт принимает id (в формате UUID) юзера и возвращает информацию о нем: статистику в виде списка:

    id (str),
    ФИО (str),
    год выпуска (int),
    профиль (str),
    суммарный балл за ЕГЭ (int),
    ср. балл ОГЭ (float),
    кол-во побед (int),
    кол-во призерств (int),
    кол-во участий, % успешных выступлений (отношение дипломов к участиям) (int)

    и записи об участии/призерстве/победах в олимпиадах, ЕГЭ, ОГЭ и пр. мероприятиях в виде словаря с
    ключами ``vos, rsosh, ege, oge, other`` и значениями вида:

    ---

    :param id: id юзера в формате UUID
    :return: Словарь с ключами ``stats`` и ``records``
    """
    result = {
        'stats': get_user_stats(id),
        'records': get_user_records(id)
    }

    return jsonify(result), 200
