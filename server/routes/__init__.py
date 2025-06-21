from flask import Blueprint, render_template


main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
def main_page():
    return render_template('main.html')


@main.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html")


@main.errorhandler(400)
def bad_request(e):
    return render_template("errors/400.html")
