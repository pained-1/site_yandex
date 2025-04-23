import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template

from data import db_session
from data.work import Work

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db = SQLAlchemy()
db.init_app(app)

@app.route("/")
def index():
    return render_template('base.html')

@app.route("/iblan")
def iblan():
    db_sess = db_session.create_session()
    work = db_sess.query(Work)
    return render_template('index.html', work=work)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    db_session.global_init('db/blogs.db')
    app.run(host='0.0.0.0', port=port)