from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, FileField, FloatField
from wtforms.validators import DataRequired


class ProductEdit(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = StringField('Состав', validators=[DataRequired()])
    weight = IntegerField('Вес г.', validators=[DataRequired()])
    cost = FloatField('Стоимость', validators=[DataRequired()])
    image = FileField('Фото')

    submit = SubmitField('Сохранить')
