from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    return render_template('index.html', title='Home', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # Connect to database
    db = sqlite3.connect('path/to/database')
    c = db.cursor()

    # Execute sql statement and grab all records where the "usuario" and
    # "senha" are the same as "user" and "password"
    c.execute('SELECT * FROM sabb WHERE usuario = ? AND senha = ?', (user, password))
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)