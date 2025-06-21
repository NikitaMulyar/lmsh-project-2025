import asyncio

from flask import Flask

from server.api.user import user_api
from server.api.vos_data import vos_data_api
from server.backend.database import create_db
from server.dependencies import prepare_data
from server.routes import main
from server.routes.vos_data import vos_data


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'lmsh_2025_uraaaa'

app.register_blueprint(vos_data_api)
app.register_blueprint(user_api)

app.register_blueprint(main)
app.register_blueprint(vos_data)


if __name__ == '__main__':
    # create_db()
    # asyncio.run(prepare_data())
    app.run()
