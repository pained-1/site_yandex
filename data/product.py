import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Product(SqlAlchemyBase,SerializerMixin):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    discount = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    is_popular = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    image = sqlalchemy.Column(sqlalchemy.BLOB, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    # news = orm.relationship("News", back_populates='user')
    user = orm.relationship('User')
    categories = orm.relationship("Category",
                                  secondary="association",
                                  backref="work")
