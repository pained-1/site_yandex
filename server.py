import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from data import db_session
from data.product import Product
import sqlite3

from flask_paginate import Pagination, get_page_parameter
from flask import abort, send_file
import io
import imghdr
from flask_optional_routes import OptionalRoutes
app = Flask(__name__, static_folder='static')
optional = OptionalRoutes(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db = SQLAlchemy()
db.init_app(app)
bootstrap = Bootstrap(app)
def calculate_discount(price, discount):
    if discount and discount > 0:
        return price * (1 - discount/100)
    return price
@app.template_filter('price_discount')
def price_discount_filter(price, discount):
    return calculate_discount(price, discount)
@app.route("/")
def index():
    return render_template('base.html')

@app.route("/iblan")
def iblan():
    db_sess = db_session.create_session()
    work = db_sess.query(Product)
    return render_template('index.html', products=work)


@app.route('/work_image/<int:work_id>')
def get_work_image(work_id):
    db_sess = db_session.create_session()
    work = db_sess.query(Product).get(work_id)

    if not work or not work.image:
        # Можно вернуть изображение-заглушку
        return send_file('static/img/noimage.jpg', mimetype='image/png')

    # Определяем тип изображения
    image_type = imghdr.what(None, h=work.image)
    mimetype = f'image/{image_type}' if image_type else 'image/jpeg'

    # Создаем файлоподобный объект из BLOB-данных
    image_io = io.BytesIO(work.image)

    return send_file(
        image_io,
        mimetype=mimetype,
        as_attachment=False,
        download_name=f'work_{work_id}.{image_type}' if image_type else 'work_image'
    )
@app.route('/test-css')
def test_css():
    return '''
    <link rel="stylesheet" href="/static/css/base.css">
    <body style="padding: 50px;">
        Если фон красный - CSS работает. Иначе проверьте:<br>
        1. Файл static/css/base.css существует<br>
        2. URL <a href="/static/css/base.css">/static/css/base.css</a> открывает CSS-код
    </body>
    '''

@app.route('/product_card/<name>')
def product_card(name):
    db_sess = db_session.create_session()
    work = db_sess.query(Product)
    # names = db_sess.query(Product).filter(Product.title == name).all()
    names = ""
    for titl in work:
        if titl.title == name:
            names = titl
    return render_template('detail.html', product=names)

@optional.routes('/shop/<category_slug>?/')
def shop(category_slug=None):
    # page = request.args.get('page', type=int, default=1)
    # per_page = 12
    db_sess = db_session.create_session()
    categories = db_sess.query(Product.category).all()
    categories_list = [name[0] for name in categories]
    all_categories = set()
    for i in categories_list:
        all_categories.add(i)
    if category_slug:
        products_query = db_sess.query(Product).filter(Product.category==category_slug)
    else:
        products_query = db_sess.query(Product)
    # pages = db_sess.query(Product).paginate(page=page, per_page=1)
    return render_template('list.html', category=category_slug, categories=all_categories,products=products_query)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    db_session.global_init('db/blogs.db')
    app.run(host='0.0.0.0', port=port)