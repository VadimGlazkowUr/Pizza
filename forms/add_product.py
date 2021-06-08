from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, FileField
from wtforms.validators import DataRequired


class AddProductForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = StringField('Состав', validators=[DataRequired()])
    weight = IntegerField('Вес г.', validators=[DataRequired()])
    cost = IntegerField('Стоимость', validators=[DataRequired()])
    image = FileField('Фото')

    submit = SubmitField('Добавить')
