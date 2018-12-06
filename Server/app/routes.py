from flask import render_template, flash, redirect, url_for, request, send_from_directory
from app import app, db, ALLOWED_EXTENSIONS
from app.forms import LoginForm, RegistrationForm, GeneralQueryForm
from app.models import User, UserSetting, DailyStep, HeartRate, Caretaker
from flask_login import logout_user, login_required, current_user, login_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from sqlalchemy.sql import func
from sqlalchemy import or_, and_
from datetime import date, timedelta
import json, datetime, os, time


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/index')
@login_required
def index():
    usersettings = UserSetting.query.filter_by(userId=current_user.id).first()
    developer = usersettings.developerAccount

    return render_template("index.html", title='Home Page', developer=developer, name=current_user.name)


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
        token = user.generate_auth_token()
        user.token = token.decode('ascii')
        db.session.commit()
        login_user(user, remember=form.remember_me.data)
        print(user.email + ' just logged in!')
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
    token = user.generate_auth_token()
    user.token = token.decode('ascii')
    db.session.commit()
    login_user(user)
    #FAKE HEALTH DATA!
    #dailySteps = DailyStep(dailyStepsId=user.get_id(), stepsValue=50, stepsDate=datetime.datetime.now())
    #heartRate = HeartRate(heartRateUserId=user.get_id(), heartRateValue=80, heartRateTimestamp=datetime.datetime.now())
    #dailySteps = DailyStep.query.filter_by(dailyStepsId=user.get_id(), stepsDate=datetime.date.today()).first()
    #dailySteps.stepsValue = dailySteps.stepsValue + 20
    #db.session.add(heartRate)
    #db.session.commit()
    response = {'Response': 'Success', 'Message': 'The User has been correctly logged in.', 'Code': '201',
                'Token': token.decode('ascii')}
    print(response)
    jresponse = json.dumps(response)
    return jresponse


@app.route('/android/homepage', methods=['GET', 'POST'])
def android_homepage():
    input_json = request.get_json(force=True)
    token = input_json['Token']
    user = User.verify_auth_token(token)
    if user is None:
        response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        jresponse = json.dumps(response)
        return jresponse
    friends = Caretaker.query.filter_by(caretakerId=user.get_id(), requestStatusCode=1).all()
    data = []
    for friend in friends:
        qr = User.query.filter_by(id=friend.observedUserId).first()
        elem = {}
        elem['Email'] = qr.email
        data.append(elem)
    response = {}
    response['Response'] = 'Success'
    response['Message'] = "Here're the users' mails."
    response['Name'] = user.name
    response['Surname'] = user.surname
    response['Data'] = data
    response['Code'] = '206'
    jresponse = json.dumps(response)
    print(jresponse)
    return jresponse


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
    if todaySteps is None:
        data['Steps'] = 0
    else:
        data['Steps'] = todaySteps.stepsValue
    if heartbeat is None:
        data['Heartbeat'] = "No measurements"
    else:
        data['Heartbeat'] = int(heartbeat)
    response["Data"] = data
    jresponse = json.dumps(response)
    print(jresponse)
    return jresponse


@app.route('/android/external_profile', methods=['GET', 'POST'])
def android_external_profile():
    input_json = request.get_json(force=True)
    token = input_json['Token']
    print(token)
    user = User.verify_auth_token(token)
    if user is None:
        response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        jresponse = json.dumps(response)
        return jresponse
    ext_email = input_json['Email']
    ext_user = User.query.filter_by(email=ext_email).first()
    if ext_user is None:
        response = {'Response': 'Error', 'Message': 'The searched User does not exist.', 'Code': '105'}
        jresponse = json.dumps(response)
        return jresponse
    midnight = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    now = datetime.datetime.now()
    pastPoint = now - datetime.timedelta(seconds=15)
    caretaking = Caretaker.query.filter_by(caretakerId=user.get_id(), observedUserId=ext_user.get_id()).first()
    todaySteps = DailyStep.query.filter_by(dailyStepsId=ext_user.get_id(), stepsDate=datetime.date.today()).first()
    heartbeat = db.session.query(func.avg(HeartRate.heartRateValue))\
        .filter(HeartRate.heartRateUserId==ext_user.get_id(),
                HeartRate.heartRateTimestamp>midnight, HeartRate.heartRateTimestamp<pastPoint).scalar()
    response = {}
    data = {}
    response['Response'] = 'Success'
    response['Message'] = "Here's the user info."
    response['Code'] = '203'
    data['Name'] = ext_user.name
    data['Surname'] = ext_user.surname
    data['Birthday'] = ext_user.birthday.strftime('%Y-%m-%d')
    data['Sex'] = ext_user.sex
    if caretaking is None:
        data['Subscription'] = False
        data['StatusCode'] = 0
        data['Steps'] = 0
        data['Heartbeat'] = "No measurements"
    else:
        if caretaking.requestStatusCode is (0 or 2):
            data['Subscription'] = False
            data['StatusCode'] = caretaking.requestStatusCode
            data['Steps'] = 0
            data['Heartbeat'] = "No measurements"
        else:
            data['Subscription'] = caretaking.subscription
            data['StatusCode'] = caretaking.requestStatusCode
            if todaySteps is None:
                data['Steps'] = 0
            else:
                data['Steps'] = todaySteps.stepsValue
            if heartbeat is None:
                data['Heartbeat'] = "No measurements"
            else:
                data['Heartbeat'] = int(heartbeat)
    response["Data"] = data
    jresponse = json.dumps(response)
    print(jresponse)
    return jresponse


@app.route('/android/uploads',  methods=['GET', 'POST'])
def uploaded_file():
    token = request.args.get('Token')
    filename = request.args.get('Filename')
    print(token)
    user = User.verify_auth_token(token)
    if user is None:
        #response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        #jresponse = json.dumps(response)
        return 404
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/android/research', methods=['GET', 'POST'])
def android_research():
    input_json = request.get_json(force=True)
    token = input_json['Token']
    print(token)
    user = User.verify_auth_token(token)
    if user is None:
        response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        jresponse = json.dumps(response)
        return jresponse
    text = input_json['Text']
    result = User.query.filter(and_(or_(User.name.contains(text), User.surname.contains(text))),
                               (User.id != user.get_id())).all()
    response = {}
    response['Response'] = 'Success'
    response['Message'] = "Here's the result."
    data = []
    for elem in result:
        user = {}
        user['Name'] = elem.name
        user['Surname'] = elem.surname
        user['Email'] = elem.email
        data.append(user)
    response['Data'] = data
    response['Code'] = '208'
    jresponse = json.dumps(response)
    print(jresponse)
    return jresponse


@app.route('/android/remove_friend_request', methods=['GET', 'POST'])
def remove_friend_request():
    input_json = request.get_json(force=True)
    token = input_json['Token']
    user = User.verify_auth_token(token)
    if user is None:
        response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        jresponse = json.dumps(response)
        return jresponse
    ext_email = input_json['Email']
    ext_user = User.query.filter_by(email=ext_email).first()
    if ext_user is None:
        response = {'Response': 'Error', 'Message': 'The searched User does not exist.', 'Code': '105'}
        jresponse = json.dumps(response)
        return jresponse
    caretaking = Caretaker.query.filter_by(caretakerId=user.get_id(), observedUserId=ext_user.get_id()).first()
    if caretaking is None:
        response = {'Response': 'Error', 'Message': 'This user already isn''t in your friends list.', 'Code': '109'}
        jresponse = json.dumps(response)
        return jresponse
    else:
        if caretaking.requestStatusCode == 1 or caretaking.requestStatusCode == 2:
            caretaking.subscription = 0
            caretaking.requestStatusCode = 0
            db.session.commit()
        else:
            response = {'Response': 'Error', 'Message': 'This user already isn''t in your friends list', 'Code': '109'}
            jresponse = json.dumps(response)
            return jresponse
    response = {'Response': 'Success', 'Message': 'Friend removed', 'Code': '204'}
    jresponse = json.dumps(response)
    print(jresponse)
    return jresponse


@app.route('/android/friend_request', methods=['GET', 'POST'])
def friend_request():
    input_json = request.get_json(force=True)
    token = input_json['Token']
    user = User.verify_auth_token(token)
    if user is None:
        response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        jresponse = json.dumps(response)
        return jresponse
    ext_email = input_json['Email']
    ext_user = User.query.filter_by(email=ext_email).first()
    if ext_user is None:
        response = {'Response': 'Error', 'Message': 'The searched User does not exist.', 'Code': '105'}
        jresponse = json.dumps(response)
        return jresponse
    caretaking = Caretaker.query.filter_by(caretakerId=user.get_id(), observedUserId=ext_user.get_id()).first()
    if caretaking is None:
        caretaking = Caretaker(caretakerId=user.get_id(), observedUserId=ext_user.get_id(),
                               subscription=0, requestStatusCode=2)
        db.session.add(caretaking)
        db.session.commit()
    else:
        if caretaking.requestStatusCode == 0:
            caretaking.subscription = 0
            caretaking.requestStatusCode = 2
            db.session.commit()
        else:
            response = {'Response': 'Error', 'Message': 'Request already sent', 'Code': '106'}
            jresponse = json.dumps(response)
            return jresponse
    response = {'Response': 'Success', 'Message': 'Friend request sent', 'Code': '204'}
    jresponse = json.dumps(response)
    print(jresponse)
    return jresponse


@app.route('/android/subscription_request', methods=['GET', 'POST'])
def subscription_request():
    input_json = request.get_json(force=True)
    token = input_json['Token']
    user = User.verify_auth_token(token)
    if user is None:
        response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        jresponse = json.dumps(response)
        return jresponse
    ext_email = input_json['Email']
    subscription_query = input_json['Query']
    ext_user = User.query.filter_by(email=ext_email).first()
    if ext_user is None:
        response = {'Response': 'Error', 'Message': 'The searched User does not exist.', 'Code': '105'}
        jresponse = json.dumps(response)
        return jresponse
    caretaking = Caretaker.query.filter_by(caretakerId=user.get_id(), observedUserId=ext_user.get_id()).first()
    if caretaking is None:
        response = {'Response': 'Error', 'Message': 'This person is not in your friends list.', 'Code': '107'}
        jresponse = json.dumps(response)
        return jresponse
    else:
        if caretaking.requestStatusCode == 1:
            caretaking.subscription = subscription_query
            db.session.commit()
        else:
            response = {'Response': 'Error', 'Message': 'This person is not in your friends list.', 'Code': '107'}
            jresponse = json.dumps(response)
            return jresponse
    response = {'Response': 'Success', 'Message': 'Subscription modified', 'Code': '205', 'Data': subscription_query}
    jresponse = json.dumps(response)
    print(jresponse)
    return jresponse


@app.route('/android/notifications', methods=['GET', 'POST'])
def android_notifications():
    input_json = request.get_json(force=True)
    token = input_json['Token']
    user = User.verify_auth_token(token)
    if user is None:
        response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        jresponse = json.dumps(response)
        return jresponse
    requests = Caretaker.query.filter_by(caretakerId=user.get_id(), requestStatusCode=2).all()
    response = {}
    data = {}
    reqs =[]
    for req in requests:
        qr = User.query.filter_by(id=req.observedUserId).first()
        elem = {}
        elem['Email'] = qr.email
        elem['Surname'] = qr.surname
        elem['Name'] = qr.name
        reqs.append(elem)
    data['Requests'] = reqs
    response['Data'] = data
    response['Response'] = 'Success'
    response['Code'] = '207'
    jresponse = json.dumps(response)
    print(jresponse)
    return jresponse


@app.route('/android/notifications_request_answer', methods=['GET', 'POST'])
def notifications_request_answer():
    input_json = request.get_json(force=True)
    token = input_json['Token']
    print(token)
    user = User.verify_auth_token(token)
    if user is None:
        response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        jresponse = json.dumps(response)
        return jresponse
    email = input_json['Email']
    answer = input_json['Answer']
    ext_user = User.query.filter_by(email=email).first()
    caretake = Caretaker.query.filter_by(caretakerId=user.get_id(), observedUserId=ext_user.get_id()).first()
    caretake.requestStatusCode = answer
    db.session.commit()

    response = {'Response': 'Success', 'Code': '209', 'Message': "Answer submitted."}
    jresponse = json.dumps(response)
    return jresponse


@app.route('/android/notifications_clear_all', methods=['GET', 'POST'])
def android_clear_all():
    input_json = request.get_json(force=True)
    token = input_json['Token']
    print(token)
    user = User.verify_auth_token(token)
    if user is None:
        response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        jresponse = json.dumps(response)
        return jresponse
    emails = input_json['Email']
    print(emails)
    number = 0
    for email in emails:
        number = number + 1
        ext_user = User.query.filter_by(email=email).first()
        caretake = Caretaker.query.filter_by(caretakerId=user.get_id(), observedUserId=ext_user.get_id()).first()
        caretake.requestStatusCode = 0
        db.session.commit()
    response = {'Response': 'Success', 'Code': '209', 'Message': "Cleared users' notifications.", 'Number': number}
    jresponse = json.dumps(response)
    return jresponse


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


