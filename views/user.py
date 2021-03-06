from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from peewee import DoesNotExist
from core.models import User, Order, OrderList, Bread
from core.forms import LoginForm, RegistrationForm

app = Blueprint('user', __name__)
bcrypt = Bcrypt()

@app.route('/register/', methods=['GET', 'POST'])
def register():
    form=RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user=User.create(
            first_name=form.first_name.data.title(),
            last_name=form.last_name.data.title(),
            username=form.username.data,
            password=bcrypt.generate_password_hash(form.password.data)
        )
        session['username']=user.username
        session['first_name']=user.first_name
        session['last_name']=user.last_name
        return redirect(url_for('index'))
    return render_template('user/register.html', form=form)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form=LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            user=User.get(User.username == form.username.data)
            
            if not bcrypt.check_password_hash(user.password, form.password.data):
                form.password.errors.append('Incorrect Password.')
            else:
                session['username']=user.username
                session['first_name']=user.first_name
                session['last_name']=user.last_name
                return redirect(url_for('index'))
        except DoesNotExist:
            form.username.errors.append('User does not exists.')

    return render_template('user/login.html', form=form)

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    session.pop('first_name', None)
    session.pop('last_name', None)
    session.pop('basket', None)
    return redirect(url_for('index'))

@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('user.login'))
    try:
        item=[row for row in OrderList
            .select(OrderList, Bread.name.alias('bread_name'))
            .join(Bread)
            .switch(OrderList)
            .join(Order)
            .where(Order.user==session['username'])
            .dicts()]
        order=[row for row in Order
            .select()
            .where(Order.user==session['username'])
            .order_by(Order.date.desc())
            .limit(6)
            .dicts()]
    except DoesNotExist:
        order=None
        item=None
    return render_template('user/profile.html', order=order, item=item)
