from flask_wtf import FlaskForm
from sqlalchemy import orm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    title = StringField('product title', validators=[DataRequired()])
    price = TextAreaField("price product")
    category = TextAreaField("category product")
    description = TextAreaField("description")
    discount = TextAreaField("discount")
    quantity = TextAreaField("quantity")
    is_popular = BooleanField("is_popular?")
    submit = SubmitField('submit')
    categories = orm.relationship("Category",
                                  secondary="association",
                                  backref="products")
