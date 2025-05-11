import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Cart(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'carts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    customer_link = sqlalchemy.Column(sqlalchemy.Integer,
                                      sqlalchemy.ForeignKey("users.id"), nullable=False)
    product_link = sqlalchemy.Column(sqlalchemy.Integer,
                                     sqlalchemy.ForeignKey("products.id"), nullable=False)
    # news = orm.relationship("News", back_populates='user')
    user = orm.relationship('User')
    product = orm.relationship('Product')
