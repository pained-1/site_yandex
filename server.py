import os
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, abort, send_file, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired
from data import db_session
from data.product import Product
from data.users import User
from data.cart import Cart
import sqlite3
from flask_paginate import Pagination, get_page_parameter
import io
import imghdr
from sklearn.datasets import make_blobs
from flask_optional_routes import OptionalRoutes
from forms.user import RegisterForm
from forms.product import ProductForm

app = Flask(__name__, static_folder='static')
optional = OptionalRoutes(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db = SQLAlchemy()
db.init_app(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)


def calculate_discount(price, discount):
    if discount and discount > 0:
        return price * (1 - discount / 100)
    return price


@app.template_filter('price_discount')
def price_discount_filter(price, discount):
    return calculate_discount(price, discount)


@app.route("/")
def home():
    db_sess = db_session.create_session()
    work = db_sess.query(Product)
    db_sess.close()
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
    db_sess.close()
    return send_file(
        image_io,
        mimetype=mimetype,
        as_attachment=False,
        download_name=f'work_{work_id}.{image_type}' if image_type else 'work_image'
    )


@app.route('/product_card/<name>')
def product_card(name):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.title == name).first()
    user = db_sess.query(User)
    db_sess.close()

    if not product:
        abort(404)  # Вернёт 404 если товар не найден
    db_sess.close()
    return render_template('detail.html', product=product, user=current_user)


@optional.routes('/shop/<category_slug>?/')
def shop(category_slug=None):
    page = request.args.get('page', type=int, default=1)
    per_page = 12
    db_sess = db_session.create_session()
    categories = db_sess.query(Product.category).all()
    categories_list = [name[0] for name in categories]
    all_categories = set()
    for i in categories_list:
        all_categories.add(i)
    if category_slug:
        products_query = db_sess.query(Product).filter(Product.category == category_slug)
    else:
        products_query = db_sess.query(Product)
    # pages = db_sess.query(Product).paginate(page=page, per_page=1)
    db_sess.close()
    return render_template('list.html', category=category_slug, categories=all_categories, products=products_query)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            age=form.age.data,
            surname=form.surname.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        db_sess.close()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    ret = db_sess.query(User).get(user_id)
    db_sess.close()
    return ret


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            db_sess.close()
            return redirect("/")
        db_sess.close()
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@app.route("/add_to_cart/<int:item_id>")
def add_to_cart(item_id):
    db_sess = db_session.create_session()
    try:
        product = db_sess.query(Product).get(item_id)
        item_to_add = db_sess.query(Product).get(item_id)
        item_exists = db_sess.query(Cart).filter(Cart.product_link == item_id,
                                                 Cart.customer_link == current_user.id).first()
        # for item in item_exists:
        #     print(item.id)
        if item_exists:
            item_exists.quantity += 1
            db_sess.commit()
        else:
            new_cart_item = Cart()
            new_cart_item.quantity = 1
            new_cart_item.product_link = item_to_add.id
            new_cart_item.customer_link = current_user.id
            db_sess.add(new_cart_item)
            db_sess.commit()
        flash(f'Товар "{product.title}" добавлен в корзину', 'success')
        return redirect(url_for('product_card', name=product.title))
    except Exception as e:
        db_sess.rollback()
        flash('Ошибка при добавлении в корзину', 'error')
        return redirect(url_for('/'))

    finally:
        db_sess.close()


@app.route("/cart")
@login_required
def cart():
    db_sess = db_session.create_session()
    cart = db_sess.query(Cart).filter(Cart.customer_link == current_user.id).all()
    amount = 0
    for item in cart:
        amount += price_discount_filter(item.product.price, item.product.discount) * item.quantity
    db_sess.close()
    return render_template('cart.html', cart=cart, amount=amount, total=amount)


@app.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    action = request.form.get('action')
    db_sess = db_session.create_session()

    try:
        cart_item = db_sess.query(Cart).filter_by(
            id=item_id,
            customer_link=current_user.id
        ).first()

        if cart_item:
            if action == 'increase':
                cart_item.quantity += 1
            elif action == 'decrease' and cart_item.quantity > 1:
                cart_item.quantity -= 1

            db_sess.commit()
            db_sess.close()
    except Exception as e:
        db_sess.rollback()
        flash('Ошибка обновления', 'error')
    finally:
        db_sess.close()

    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    db_sess = db_session.create_session()
    cart_item = db_sess.query(Cart).filter_by(id=item_id, customer_link=current_user.id).first()

    if cart_item:
        db_sess.delete(cart_item)
        db_sess.commit()
        flash('Товар удален из корзины', 'error')

    db_sess.close()
    return redirect(url_for('cart'))


@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(id=current_user.id).first()
    db_sess.close()
    if not user.admin:
        flash('Вы не Админ, товар не будет добавлен', 'error')
        return redirect('/')
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        produc = Product()
        produc.title = form.title.data
        if db_sess.query(Product).filter(Product.title == form.title.data).first():
            return render_template('produc.html', title='Добавление товара',
                                   form=form,
                                   message="Такое название уже есть")
        produc.price = form.price.data
        produc.is_popular = form.is_popular.data
        produc.quantity = form.quantity.data
        produc.description = form.description.data
        produc.category = form.category.data
        produc.user_id = current_user.id
        f = request.files['file']
        produc.image = f.read()
        db_sess.add(produc)
        db_sess.commit()

        return redirect('/')

    return render_template('produc.html', title='Добавление товара',
                           form=form)


@app.route('/admin')
def admin():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(id=current_user.id).first()
    db_sess.close()
    print(user.admin)
    if not user.admin:
        flash('Вы не Админ', 'error')
        return redirect('/')
    return render_template('admin.html')


@app.route('/delete_product/<int:item_id>')
@login_required
def delete_product(item_id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == item_id).first()
    user = db_sess.query(User).filter_by(id=current_user.id).first()
    if product and user.admin:
        db_sess.delete(product)
        db_sess.commit()
    else:
        abort(404)
    db_sess.close()
    return redirect('/shop')


@app.route('/product_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = ProductForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(id=current_user.id).first()
    db_sess.close()
    if not user.admin:
        flash('Вы не Админ, вы не можете редактировать товар', 'error')
        return redirect('/')
    if request.method == "GET":
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == id).first()
        if product:
            form.title.data = product.title
            form.price.data = product.price
            form.category.data = product.category
            form.discount.data = product.discount
            form.description.data = product.description
            form.quantity.data = product.quantity
            form.is_popular.data = product.is_popular

        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        produc = db_sess.query(Product).filter(Product.id == id).first()
        if produc:
            produc.title = form.title.data
            produc.price = form.price.data
            produc.discount = form.discount.data
            produc.category = form.category.data
            produc.description = form.description.data
            produc.quantity = form.quantity.data
            produc.is_popular = form.is_popular.data
            f = request.files['file']
            if f:
                produc.image = f.read()
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('produc.html',
                           title='Редактирование товара',
                           form=form
                           )


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    db_session.global_init('db/blogs.db')
    app.run(host='0.0.0.0', debug=True, port=port, threaded=True)
