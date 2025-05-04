from flask import Flask, make_response, jsonify
from data import db_session
from data.users import User
from data.product import Product
from data import db_session, news_api

from flask_restful import reqparse, abort, Api, Resource

from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()