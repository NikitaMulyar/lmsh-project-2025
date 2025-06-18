import asyncio

from flask import Flask

from server.backend.database import create_db
from server.dependencies import prepare_data

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    create_db()
    asyncio.run(prepare_data())
    app.run()
