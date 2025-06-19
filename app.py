import asyncio

from flask import Flask

from server.api.user import user_api
from server.api.vos_data import vos_data_api
from server.backend.database import create_db
from server.dependencies import prepare_data


app = Flask(__name__)
app.register_blueprint(vos_data_api)
app.register_blueprint(user_api)


if __name__ == '__main__':
    # create_db()
    # asyncio.run(prepare_data())
    app.run()
