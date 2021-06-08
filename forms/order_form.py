from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, DateTimeField
from wtforms.validators import DataRequired


class Order_Form(FlaskForm):
    user_name = StringField('Ваше имя', validators=[DataRequired()])
    telephone = StringField('Номер телефона', validators=[DataRequired()])
    address = StringField('Адрес доставки', validators=[DataRequired()])
    time_delivery = DateTimeField('Время доставки')
    submit = SubmitField('Заказать')
