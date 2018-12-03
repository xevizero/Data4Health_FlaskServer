from flask import render_template, flash, redirect, url_for, request, send_from_directory
from app import app, db, ALLOWED_EXTENSIONS
from app.forms import LoginForm, RegistrationForm, GeneralQueryForm
from app.models import User, UserSetting, DailyStep, HeartRate
from flask_login import logout_user, login_required, current_user, login_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from sqlalchemy.sql import func
from datetime import date, timedelta
import json, datetime, os, time


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        print(user.token)
        print(user.token.decode('ascii'))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        print(user.email + ' just logged in!')
        token = user.generate_auth_token()
        user.token = token
        db.session.commit()
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    print(current_user.__repr__() + ' just logged out!')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, surname=form.surname.data, email=form.email.data,
                    userPhoneNumber=form.phonenumber.data, sex=form.sex.data, birthday=form.birthday.data)
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
    colours = ['Red', 'Blue', 'Black', 'Orange']
    if form.validate_on_submit():
        stringsql = form.query.data
        print(stringsql)
        result = db.engine.execute(stringsql)
        result2 = db.engine.execute(stringsql)
        names=[]
        for row in result:
            names.append(row)
        jresponse = json.dumps([(dict(row.items())) for row in result2])
    return render_template('sqlquery.html', title='My Develop', form=form , tab=names, jtext=jresponse, colours=colours)


@app.route('/android', methods=['GET', 'POST'])
def android():
    input_json = request.get_json(force=True)
    print(input_json)
    jresponse = json.dumps(input_json)
    #result = db.engine.execute("SELECT * FROM Users WHERE Name=" +"'" + ciao+"'")
    #print(result)
    #jresponse = json.dumps([(dict(row.items())) for row in result])
    #print(jresponse)
    return 'Tutto ok'


@app.route('/android/register', methods=['GET', 'POST'])
def android_register():
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    userPhoneNumber = request.form['userPhoneNumber']
    birthday_str = request.form['birthday']
    birthday = datetime.datetime.strptime(birthday_str, "%Y-%m-%d").date()
    password = request.form['password']
    sex = request.form['sex']
    present = User.query.filter_by(email=email).first()
    defaultLocationLat = float(0.0)
    defaultLocationLong = float(0.0)
    automatedSOSOn = bool(request.form['automatedSOSOn'])
    developerAccount = bool(request.form['developerAccount'])
    anonymousDataSharingON = bool(request.form['anonymousDataSharingON'])
    if present:
        response = {'Response': 'Error', 'Message': 'Already used email.', 'Code': '100'}
        jresponse = json.dumps(response)
        print(jresponse)
        return jresponse
    if 'file' not in request.files:
        response = {'Response': 'Error', 'Message': 'File not present in upload.', 'Code': '101'}
        jresponse = json.dumps(response)
        print(jresponse)
        return jresponse
    file = request.files['file']
    if file.filename == '':
        response = {'Response': 'Error', 'Message': 'No file name.', 'Code': '102'}
        jresponse = json.dumps(response)
        print(jresponse)
        return jresponse
    if file and allowed_file(file.filename):
        filename = email + '.png'
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print("The file has been saved.")
    user = User(name=name, surname=surname, email=email,
                userPhoneNumber=userPhoneNumber, birthday=birthday, sex=sex)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    userSetting = UserSetting(userId=user.get_id(), defaultLocationLat=defaultLocationLat,
                              defaultLocationLong=defaultLocationLong, automatedSOSOn=automatedSOSOn,
                              developerAccount=developerAccount, anonymousDataSharingON=anonymousDataSharingON)
    db.session.add(userSetting)
    db.session.commit()
    response = {'Response': 'Success', 'Message': 'The User has been correctly registered.', 'Code': '200'}
    jresponse = json.dumps(response)
    print(jresponse)
    return jresponse


@app.route('/android/login', methods=['GET', 'POST'])
def android_login():
    input_json = request.get_json(force=True)
    email = input_json['email']
    password = input_json['password']
    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        response = {'Response': 'Error', 'Message': 'Incorrect Username or Password.', 'Code': '103'}
        print(response)
        jresponse = json.dumps(response)
        return jresponse
    login_user(user)
    token = user.generate_auth_token()
    user.token = token.decode('ascii')

    #FAKE HEALTH DATA!
    #dailySteps = DailyStep(dailyStepsId=user.get_id(), stepsValue=50, stepsDate=datetime.datetime.now())
    heartRate = HeartRate(heartRateUserId=user.get_id(), heartRateValue=80, heartRateTimestamp=datetime.datetime.now())
    dailySteps = DailyStep.query.filter_by(dailyStepsId=user.get_id(), stepsDate=datetime.date.today()).first()
    dailySteps.stepsValue = dailySteps.stepsValue + 20
    db.session.add(heartRate)
    db.session.commit()
    response = {'Response': 'Success', 'Message': 'The User has been correctly logged in.', 'Code': '201',
                'Token': token.decode('ascii')}
    print(response)
    jresponse = json.dumps(response)
    return jresponse


@app.route('/android/homepage', methods=['GET', 'POST'])
def android_homepage():
    input_json = request.get_json(force=True)
    token = input_json['Token']
    user = User.query.filter_by(token=token).first()
    if user is None:
        response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        jresponse = json.dumps(response)
        return jresponse

    return 'Tutto ok.'


@app.route('/android/profile', methods=['GET', 'POST'])
def android_profile():
    input_json = request.get_json(force=True)
    token = input_json['Token']
    print(token)
    user = User.verify_auth_token(token)
    if user is None:
        response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        jresponse = json.dumps(response)
        return jresponse
    midnight = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    now = datetime.datetime.now()
    pastPoint = now - datetime.timedelta(seconds=15)
    #todaySteps = DailyStep.query.filter(DailyStep.dailyStepsId == user.get_id(), DailyStep.stepsDate > midnight)\
    #    .with_entities(func.avg(DailyStep.stepsValue).label('average')).first()
    todaySteps = DailyStep.query.filter_by(dailyStepsId=user.get_id(), stepsDate=datetime.date.today()).first()
    heartbeat = db.session.query(func.avg(HeartRate.heartRateValue))\
        .filter(HeartRate.heartRateUserId==user.get_id(),
                HeartRate.heartRateTimestamp>midnight, HeartRate.heartRateTimestamp<pastPoint).scalar()
    print(heartbeat)
    response = {}
    data = {}
    response['Response'] = 'Success'
    response['Message'] = "Here's the user info."
    response['Code'] = '202'
    data['Name'] = user.name
    data['Surname'] = user.surname
    data['Birthday'] = user.birthday.strftime('%Y-%m-%d')
    data['Sex'] = user.sex
    data['Steps'] = todaySteps.stepsValue
    data['Heartbeat'] = int(heartbeat)
    response["Data"] = data
    jresponse = json.dumps(response)
    print(jresponse)
    return jresponse


@app.route('/android/uploads',  methods=['GET', 'POST'])
def uploaded_file():
    token = request.form['Token']
    filename = request.form['Filename']
    print(token)
    user = User.verify_auth_token(token)
    if user is None:
        #response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        #jresponse = json.dumps(response)
        return 404
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)







#deprecated but useful defs
@app.route('/uploads', methods=['GET', 'POST'])
def uploads():
    if 'file' not in request.files:
        response = {'Response': 'Error', 'Message': 'File not present in upload.'}
        jresponse = json.dumps(response)
        print(jresponse)
        return jresponse
    file = request.files['file']
    if file.filename == '':
        response = {'Response': 'Error', 'Message': 'No file name.'}
        jresponse = json.dumps(response)
        print(jresponse)
        return jresponse
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        response = {'Response': 'Success', 'Message': 'The file has been saved.'}
        jresponse = json.dumps(response)
        print(jresponse)
        return jresponse
    response = {'Response': 'Error', 'Message': 'End of uploads(), server problem.'}
    jresponse = json.dumps(response)
    print(jresponse)
    return jresponse


