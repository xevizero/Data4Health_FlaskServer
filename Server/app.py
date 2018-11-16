from flask import Flask
from config import Config
from app import app


app = Flask(__name__)
app.config.from_object(Config)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
