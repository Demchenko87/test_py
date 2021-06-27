from datetime import datetime
from flask import Flask, render_template, url_for, session,jsonify, request, redirect
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore, Security, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
import email_validator
import smtplib, ssl
from flask_mail import Mail, Message


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///base.db"
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'mysecret'
app.config['SECURITY_PASSWORD_SALT'] = 'salt'
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_POST'] = 465
# app.config['MAIL_ASCII_ATTACHMENTS'] = T
app.config['MAIL_USERNAME'] = '' # Email
app.config['MAIL_PASSWORD'] = '' # Password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

roles_users = db.Table('roles_users', db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
                       )
class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


class Tables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_t = db.Column(db.Integer)
    quantity_chairs = db.Column(db.Integer)
    with_tab = db.Column(db.String(100), nullable=True)
    height_tab = db.Column(db.String(100), nullable=True)
    margin_top = db.Column(db.Integer)
    margin_left = db.Column(db.Integer)
    rotate = db.Column(db.Integer)
    so = db.Column(db.String(50), nullable=True)
    order = db.relationship('Order_Tables', backref='table', lazy=True)
    datechek = db.Column(db.String(100), nullable=True)

class AddTables(FlaskForm):
    number_t = StringField('number_t')
    quantity_chairs = StringField('quantity_chairs')
    date = StringField('date')
    with_tab = StringField('with_tab')
    height_tab = StringField('height_tab')
    margin_top = StringField('margin_top')
    margin_left = StringField('margin_left')
    rotate = StringField('rotate')
    so = SelectField('so', choices=[('square', 'Квадрат'), ('oval', 'Овал')])

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    address = db.Column(db.String(100))
    email = db.Column(db.String(50))
    date = db.Column(db.String(50))
    tables = db.Column(db.String(50))
    items = db.relationship('Order_Tables', backref='order', lazy=True)

class Order_Tables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id'))
    quantity = db.Column(db.Integer)

class Checkout(FlaskForm):
    name = StringField('First Name')
    address = StringField('Address')
    email = StringField('Email')
    date = StringField('Date')
    items = db.relationship('Order_Tables', backref='order', lazy=True)
    tables = StringField('Tables')
    table_numbers = TextAreaField('Table_numbers')

def handle_cart():
    tables = []
    for item in session['cart']:
        table = Tables.query.filter_by(id=item['id']).first()
        tables.append({'id': table.id,
                       'number_t': table.number_t,
                       'quantity_chairs':  table.quantity_chairs,
                       'with_tab': table.with_tab,
                       'height_tab': table.height_tab,
                       'margin_top': table.margin_top,
                       'rotate': table.rotate,
                       'so': table.so,
                       })
    return tables

@app.route('/', methods=['POST', 'GET'])
def index():
    tables = Tables.query.all()
    push_date = datetime.today().strftime('%Y-%m-%d')
    datechek = push_date
    orders = Order.query.all()

    # if request.method == 'POST':
    #     push_date = request.form['date']
    #     return jsonify({'date': push_date})
    if request.method == 'POST':
        push_date = request.form['date']

        for i in tables:
            i.datechek = push_date
            db.session.commit()

    count_cart = check_count()
    orders_table = Order.query.all()
    return render_template('index.html',orders=orders, tables=tables, push_date=push_date, count_cart=count_cart, orders_table=orders_table)

@app.route('/admin')
@login_required
def admin():
    return redirect('/')

@app.route('/search', methods=['GET', 'POST'])
def search():
    search = request.args.get('search')
    if search:
        orders_table = Order.query.filter(Order.date.contains(search))
    else:
        orders_table = Order.query.all()
    return render_template('search.html', orders_table=orders_table, search=search)


@app.route('/add-table', methods=['GET', 'POST'])
@login_required
def add_table():
    form = AddTables()
    if form.validate_on_submit():
        table = Tables(number_t=form.number_t.data,
                      quantity_chairs=form.quantity_chairs.data,
                      with_tab=form.with_tab.data,
                      height_tab=form.height_tab.data,
                      margin_top=form.margin_top.data,
                      margin_left=form.margin_left.data,
                      rotate=form.rotate.data,
                       so=form.so.data)
        db.session.add(table)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add-table.html', form=form)

@app.route('/edit_table/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_table(id):
    table = Tables.query.get(id)
    if request.method == 'POST':
        table.number_t = request.form['number_t']
        table.quantity_chairs = request.form['quantity_chairs']
        table.date = request.form['date']
        table.with_tab = request.form['with_tab']
        table.height_tab = request.form['height_tab']
        table.margin_top = request.form['margin_top']
        table.margin_left = request.form['margin_left']
        table.rotate = request.form['rotate']
        table.so = request.form['so']
        db.session.commit()
        return redirect(request.referrer)
    return render_template('edit-table.html', table=table)

@app.route('/table/<int:id>', methods=['GET'])
@login_required
def delete_table(id):
    group = Tables.query.filter_by(id=id).first()
    db.session.delete(group)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/quick-add-json', methods=['POST'])
def quick_add():
    id = request.form['id_tov']
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append({'id': id, 'quantity': 1})
    session.modified = True
    count = 0
    for i in session['cart']:
        count += 1
    return jsonify({'id': id, 'count': count})

@app.route('/quick-delete-json', methods=['POST'])
def quick_delete():
    id = request.form['id_tov']
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].remove({'id': id, 'quantity': 1})
    session.modified = True
    count = 0
    for i in session['cart']:
        count += 1
    return jsonify({'id': id, 'count': count})

@app.route('/cart')
def cart():
    count_cart = check_count()
    tables = handle_cart()
    return render_template('cart.html', tables=tables, count_cart=count_cart)

def check_count():
    count_cart = 0
    if 'cart' in session:
        for item in session['cart']:
            quantity = int(item['quantity'])
            count_cart += quantity
    else:
        count_cart = 0
    return count_cart


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    tables = handle_cart()
    form = Checkout()
    count_cart = check_count()
    if form.validate_on_submit():
        order = Order()
        form.populate_obj(order)
        for table in tables:
            order_item = Order_Tables(quantity=1, table_id=table['id'])
            order.items.append(order_item)
            table = Tables.query.filter_by(id=table['id'])
        db.session.add(order)
        db.session.commit()
        session['cart'] = []
        session.modified = True

        email = request.form['email']
        name = request.form['name']
        date = request.form['date']
        table_numbers = request.form['table_numbers']

        orders_message = str("Регистрация стола на имя: " + name + ' ' + "Дата: " + date + ' | ' + table_numbers)
        message = Message(date, sender="conderroman@gmail.com", recipients=[email])
        message.body = orders_message
        mail.send(message)


        return redirect(url_for('index'))
    return render_template('checkout.html', form=form, count_cart=count_cart, tables=tables)



@app.route('/orders')
@login_required
def orders():
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)

@app.route('/orders/<order_id>', methods=['GET', 'POST'])
@login_required
def order(order_id):
    order = Order.query.filter_by(id=int(order_id)).first()
    return render_template('order-view.html', order=order)

@app.route('/orders/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def del_order(id):
    order = Order.query.filter_by(id=id).first()
    db.session.delete(order)
    db.session.commit()

    return redirect(url_for('orders'))


if __name__ == '__main__':
    app.run()
