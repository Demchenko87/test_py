from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, validators, SelectField


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///base.db"
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'mysecret'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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

class AddTables(FlaskForm):
    number_t = StringField('number_t')
    quantity_chairs = StringField('quantity_chairs')
    with_tab = StringField('with_tab')
    height_tab = StringField('height_tab')
    margin_top = StringField('margin_top')
    margin_left = StringField('margin_left')
    rotate = StringField('rotate')
    so = SelectField('so', choices=[('square', 'Квадрат'), ('oval', 'Овал')])


@app.route('/')
def index():
    tables = Tables.query.all()
    return render_template('index.html', tables=tables)

@app.route('/add-table', methods=['GET', 'POST'])
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

@app.route('/edit_table', methods=['GET', 'POST'])
def edit_table():
    table = Tables.query.first()
    if request.method == 'POST':
        table.number_t = request.form['number_t']
        table.quantity_chairs = request.form['quantity_chairs']
        table.with_tab = request.form['with_tab']
        table.height_tab = request.form['height_tab']
        table.margin_top = request.form['margin_top']
        table.margin_left = request.form['margin_left']
        table.rotate = request.form['rotate']
        table.so = request.form['so']
        db.session.commit()
        return redirect(request.referrer)
    return render_template('edit-table.html', admin=True, table=table)

@app.route('/table/<int:id>', methods=['GET'])
def delete_table(id):
    group = Tables.query.filter_by(id=id).first()
    db.session.delete(group)
    db.session.commit()
    return redirect(request.referrer)

if __name__ == '__main__':
    app.run()
