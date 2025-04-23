from flask_wtf import FlaskForm
from sqlalchemy import orm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    title = StringField('Job title', validators=[DataRequired()])
    content = TextAreaField("team lider id")
    experience = TextAreaField("work size")
    colab = TextAreaField("Collaborators")
    is_private = BooleanField("finish?")
    submit = SubmitField('submit')
    categories = orm.relationship("Category",
                                  secondary="association",
                                  backref="work")