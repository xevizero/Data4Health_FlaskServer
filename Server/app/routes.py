from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, GeneralQueryForm
from app.models import User, UserSetting
from flask_login import logout_user, login_required, current_user, login_user
from werkzeug.urls import url_parse
import json

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html", title='Home Page')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, surname=form.surname.data, email=form.email.data,
                    userPhoneNumber=form.phonenumber.data, birthday=form.birthday.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/sqlquery', methods=['GET', 'POST'])
@login_required
def sqlquery():
    names = 'aspetta la tua risposta'
    jresponse = None
    form = GeneralQueryForm()
    if form.validate_on_submit():
        stringsql = form.query.data
        print(stringsql)
        result = db.engine.execute(stringsql)
        result2 = db.engine.execute(stringsql)
        names=[]
        for row in result:
            names.append(row)
        print(names)
        jresponse = json.dumps([(dict(row.items())) for row in result2])
        print(jresponse)
    return render_template('sqlquery.html', title='My Develop', form=form , tab=names, jtext=jresponse)



@app.route('/android')
def android():
      ciao = request.args.get('username')
      result = db.engine.execute("SELECT * FROM Users WHERE Name=" +"'" + ciao+"'")
      print(result)
      jresponse = json.dumps([(dict(row.items())) for row in result])
      print(jresponse)
      return jresponse

@app.route('/android/register')
def android_register():
    name = request.args.get('username')
    surname = request.args.get('surname')
    email = request.args.get('email')
    userPhoneNumber = request.args.get('userPhoneNumber')
    birthday = request.args.get('birthday')
    password = request.args.get('password')
    sex = request.args.get('sex')
    automatedSOSOn = request.args.get('automatedSOSn')
    developerAccount = request.args.get('developerAccount')
    anonymousDataSharingON = request.args.get('anonymousDataSharingON')
    present = User.query.filter_by(email=email).first()
    if present:
        response = {'Response': 'Error', 'Message': 'Already used email.'}
        jresponse = json.dumps(response)
        print(jresponse)
        return jresponse
    user = User(name=name, surname=surname, email=email,
                userPhoneNumber=userPhoneNumber, birthday=birthday, sex=sex)
    user.set_password(password)
    id = user.get_id()
    defaultLocationLat = 0.0
    defaultLocationLong = 0.0
    userSetting = UserSetting(userId=id, defaultLocationLat=defaultLocationLat,
                              defaultLocationLong=defaultLocationLong, automatedSOSOn=automatedSOSOn,
                              developerAccount=developerAccount, anonymousDataSharingON=anonymousDataSharingON)
    db.session.add(user)
    db.session.add(userSetting)
    db.session.commit()
    response = {'Response': 'Success', 'Message': 'The User has been correctly registered.'}
    jresponse = json.dumps(response)
    print(jresponse)
    return jresponse