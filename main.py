from flask import Flask, render_template, redirect, request, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import json

from data import db_session
from forms.add_product import AddProductForm
from forms.login_form import LoginForm
from data.users import User
from data.pizza import Pizza
from data.order import Order, Association
from forms.register import RegisterForm
from forms.edit_user import EditUser
from forms.order_form import Order_Form
from forms.product_edit import ProductEdit
from datetime import datetime, timedelta


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Wrong login or password", form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route("/")
def index():
    if 'basket' not in session:
        session['basket'] = json.dumps({})
    db_sess = db_session.create_session()
    pizza = db_sess.query(Pizza).all()
    if 'basket' in session:
        basket = json.loads(session['basket'])
    else:
        basket = {}
    return render_template("index.html", pizzas=pizza,
                           title='Вкусная пицца',
                           basket=basket)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register', form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register', form=form,
                                   message="This user already exists")
        user = User(
            name=form.name.data,
            email=form.email.data,
            telephone=form.telephone.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/edituser', methods=['GET', 'POST'])
@login_required
def edituser():
    edit_form = EditUser()
    db_sess = db_session.create_session()
    if edit_form.validate_on_submit():
        user = db_sess.query(User).get(current_user.id)
        user.name = edit_form.name.data
        user.email = edit_form.email.data
        user.address = edit_form.address.data
        user.telephone = edit_form.telephone.data
        if edit_form.password.data:
            user.set_password(edit_form.password.data)
        db_sess.commit()
        return redirect('/')

    user = db_sess.query(User).get(current_user.id)
    edit_form.name.data = user.name
    edit_form.email.data = user.email
    edit_form.telephone.data = user.telephone
    edit_form.address.data = user.address

    return render_template('edituser.html', form=edit_form, title='Редактировать профиль')


@app.route('/list-user')
@login_required
def list_user():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return render_template('list_user.html', users=users)


@app.route('/manager-<id>')  # Переключаем роль пользователя
@login_required
def switch_role(id):
    if id != '1':
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(id)
        if user.role:
            user.role = None
        else:
            user.role = 'manager'
        db_sess.commit()
        return redirect('/list-user')
    return redirect('/list-user')


@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    add_form = AddProductForm()
    if add_form.validate_on_submit():
        db_sess = db_session.create_session()
        if add_form.image.data:
            img = request.files[add_form.image.name].read()
            img_name = datetime.now().strftime('%d%m%y%S%M%H')
            format_file = add_form.image.data.filename.split('.')[-1]
            with open(f'static/img/{img_name}.{format_file}', 'wb') as f:
                f.write(img)
        pizza = Pizza(
            title=add_form.title.data,
            description=add_form.description.data,
            weight=add_form.weight.data,
            cost=add_form.cost.data,
            image=f'img/{img_name}.{format_file}'
        )
        db_sess.add(pizza)
        db_sess.commit()
        return redirect('/')
    return render_template('addjob.html', title='Adding a job', form=add_form)


@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    form = ProductEdit()
    db_sess = db_session.create_session()
    pizza = db_sess.query(Pizza).get(id)
    if form.validate_on_submit():
        pizza.title = form.title.data
        pizza.description = form.description.data
        pizza.weight = form.weight.data
        pizza.cost = form.cost.data
        if form.image.data:
            img = request.files[form.image.name].read()
            img_name = datetime.now().strftime('%d%m%y%S%M%H')
            format_file = form.image.data.filename.split('.')[-1]
            with open(f'static/img/{img_name}.{format_file}', 'wb') as f:
                f.write(img)
            pizza.image = f'img/{img_name}.{format_file}'
        db_sess.commit()
        return redirect('/')
    form.title.data = pizza.title
    form.description.data = pizza.description
    form.weight.data = pizza.weight
    form.cost.data = pizza.cost
    return render_template('product_edit.html', title='Редактировать пиццу', form=form)


@app.route('/product_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def product_delete(id):
    db_sess = db_session.create_session()
    pizza = db_sess.query(Pizza).get(id)
    db_sess.delete(pizza)
    db_sess.commit()
    return redirect('/')


@app.route('/add_basket/<int:id>')
def add_basket(id):
    if 'basket' in session:
        basket = json.loads(session['basket'])
        basket[id] = 1
        session['basket'] = json.dumps(basket)
    else:
        session['basket'] = json.dumps({id: 1})
    return redirect('/')


@app.route('/del_basket/<int:id>')
def del_basket(id):
    basket = json.loads(session['basket'])
    basket.pop(str(id))
    session['basket'] = json.dumps(basket)
    return redirect('/')


@app.route('/basket')
def basket():
    if 'basket' in session:
        basket = json.loads(session['basket'])
        id_basket = list(map(int, basket.keys()))
        db_sess = db_session.create_session()
        pizzas = db_sess.query(Pizza).filter(Pizza.id.in_(id_basket))
        li = []
        for i in pizzas:
            i.count = basket[str(i.id)]
            li.append(i)
        summa = sum(map(lambda x: x.count * x.cost, li))
        order_button = True
        if not basket:
            order_button = False
        return render_template('basket.html', pizzas=pizzas, sum=summa, order_button=order_button)


@app.route('/prepend/<id>')
def prepend(id):
    basket = json.loads(session['basket'])
    basket[id] -= 1
    if basket[id] < 1:
        basket[id] = 1
    session['basket'] = json.dumps(basket)
    return redirect('/basket')


@app.route('/append/<id>')
def append(id):
    basket = json.loads(session['basket'])
    basket[id] += 1
    session['basket'] = json.dumps(basket)
    return redirect('/basket')


@app.route('/del/<id>')
def basket_delet(id):
    basket = json.loads(session['basket'])
    del basket[id]
    session['basket'] = json.dumps(basket)
    return redirect('/basket')


@app.route('/order', methods=['GET', 'POST'])
def order():
    order_form = Order_Form(time_delivery=datetime.now() + timedelta(hours=1))
    if current_user.is_authenticated:
        order_form.user_name.data = current_user.name
        order_form.address.data = current_user.address
        order_form.telephone.data = current_user.telephone
    basket = json.loads(session['basket'])
    if order_form.validate_on_submit():
        db_sess = db_session.create_session()
        order = Order(
            user_name=order_form.user_name.data,
            telephone=order_form.telephone.data,
            address=order_form.address.data,
            time_delivery=order_form.time_delivery.data)
        for pizza in basket:
            a = Association(count=basket[pizza])
            a.pizza = db_sess.query(Pizza).get(int(pizza))
            order.pizzas.append(a)
        session['basket'] = json.dumps({})
        db_sess.add(order)
        db_sess.commit()
        return render_template('order_ok.html', title='Заказ принят')
    return render_template('order.html', title='Оформление заказа', form=order_form)


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    # date = datetime.strptime(date, '%Y-%m-%d H:M:f')
    format='%d.%m.%y, %H:%M'
    return date.strftime(format)


@app.route('/orders')
@login_required
def orders():
    db_sess = db_session.create_session()
    orders = db_sess.query(Order).all()
    for order in orders:
        summ = 0
        for pizza in order.pizzas:
            summ += pizza.pizza.cost * pizza.count
        order.cost = summ
    return render_template('orders.html', orders=orders, title='Заказы')


@app.route('/delorder/<id>')
@login_required
def del_order(id):
    db_sess = db_session.create_session()
    order = db_sess.query(Order).get(int(id))
    db_sess.delete(order)
    db_sess.commit()
    return redirect('/orders')


def main():
    db_session.global_init("db/pizza.sqlite")

    app.run()


if __name__ == '__main__':
    main()
