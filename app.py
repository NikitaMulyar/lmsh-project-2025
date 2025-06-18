from flask import Flask

from server.backend.database import get_session


app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    session = get_session()
    session.close()
    app.run()
