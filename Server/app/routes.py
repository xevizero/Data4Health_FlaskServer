from flask import render_template, flash, redirect, url_for, request, send_from_directory, jsonify
from app import app, db, ALLOWED_EXTENSIONS, UPLOAD_FOLDER, PROJECT_HOME
from app.forms import LoginForm, RegistrationForm, GeneralQueryForm
from app.models import User, UserSetting, DailyStep, HeartRate, Caretaker, EmergencyServicesAPI,\
    EmergencyRequestsCallCenter, EmergencyEvents, Weight, BloodPressure
from flask_login import logout_user, login_required, current_user, login_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from sqlalchemy.sql import func
from sqlalchemy import or_, and_
from datetime import date, timedelta
from shutil import copy2
import json, datetime, os, time


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/index')
@login_required
def index():
    usersettings = UserSetting.query.filter_by(userId=current_user.id).first()
    if usersettings is None:
        developer = False
    else:
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
        userSetting = UserSetting(userId=user.get_id(), defaultLocationLat=0,
                                  defaultLocationLong=0, automatedSOSOn=1,
                                  developerAccount=1, anonymousDataSharingON=1)
        db.session.add(userSetting)
        db.session.commit()
        copy2('{}/user.png'.format(PROJECT_HOME), UPLOAD_FOLDER)
        os.rename('{}user.png'.format(UPLOAD_FOLDER), UPLOAD_FOLDER + '{}.png'.format(user.email))
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/data4help/api', methods=['GET', 'POST'])
def data4helpapi():
    jres = None
    legalIDs = UserSetting.query.with_entities(UserSetting.userId).filter_by(anonymousDataSharingON=1).all()
    legalIntIDs = [id[0] for id in legalIDs]
    argument = request.args.get('Argument')
    sex = request.args.get('Sex')
    age_from = request.args.get('AgeFrom')
    age_to = request.args.get('AgeTo')
    weight_from = request.args.get('WeightFrom')
    weight_to = request.args.get('WeightTo')
    sexIntIDs = []
    ageFromIntIDs = []
    ageToIntIDs = []
    weightFromIntIDs = []
    weightToIntIDs = []
    if sex is not None:
        sexIDs = User.query.with_entities(User.id).filter(User.sex!=sex).all()
        sexIntIDs = [id[0] for id in sexIDs]
        for id in sexIntIDs:
            if id in legalIntIDs:
                legalIntIDs.remove(id)
    if age_from is not None:
        age_from_complete = age_from + "-01-01"
        ageFromIDs = User.query.with_entities(User.id).filter(User.birthday>age_from_complete).all()
        ageFromIntIDs = [id[0] for id in ageFromIDs]
        for id in ageFromIntIDs:
            if id in legalIntIDs:
                legalIntIDs.remove(id)
    if age_to is not None:
        age_to_complete = age_to + "-01-01"
        ageToIDs = User.query.with_entities(User.id).filter(User.birthday<age_to_complete).all()
        ageToIntIDs = [id[0] for id in ageToIDs]
        for id in ageToIntIDs:
            if id in legalIntIDs:
                legalIntIDs.remove(id)
    if weight_from is not None:
        weightFromIDs = Weight.query.with_entities(Weight.userIdWeight)\
            .filter(Weight.weightValue>weight_from).all()
        weightFromIntIDs = [id[0] for id in weightFromIDs]
        for id in weightFromIntIDs:
            if id in legalIntIDs:
                legalIntIDs.remove(id)
    if weight_to is not None:
        weightToIDs = Weight.query.with_entities(Weight.userIdWeight)\
            .filter(Weight.weightValue<weight_to).all()
        weightToIntIDs = [id[0] for id in weightToIDs]
        for id in weightToIntIDs:
            if id in legalIntIDs:
                legalIntIDs.remove(id)
    if argument == 'BloodPressure':
        #result = BloodPressure.query.with_entities(BloodPressure.bloodPressureUserId,
        #                                           BloodPressure.bloodPressureLowValue,
        #                                           BloodPressure.bloodPressureHighValue,
        #                                           BloodPressure.bloodPressureTimestamp).filter(BloodPressure.bloodPressureUserId.in_(legalIntIDs)).all()
        stringsql = "SELECT * FROM BloodPressure WHERE BloodPressure.bloodPressureUserId in " \
                    "(" + ''.join(str(legalIntIDs)[1:-1]) + ")"
    elif argument == "HeartRate":
        stringsql = "SELECT * FROM HeartRate WHERE HeartRate.heartRateUserId in " \
                    "(" + ''.join(str(legalIntIDs)[1:-1]) + ")"
    else:
        stringsql = "SELECT * FROM DailyStep WHERE DailyStep.dailyStepsId in " \
                    "(" + ''.join(str(legalIntIDs)[1:-1]) + ")"
    res = db.engine.execute(stringsql)
    jres = json.dumps([(dict(row.items())) for row in res])
    print(jres)
    #stringsql = form.query.data
    #print(stringsql)
    #result = db.engine.execute(stringsql)
    #result2 = db.engine.execute(stringsql)
    #jresponse = json.dumps([(dict(row.items())) for row in result2])
    return jres

@app.route('/sqlquery', methods=['GET', 'POST'])
@login_required
def sqlquery():
    jres = None
    form = GeneralQueryForm()
    legalIDs = UserSetting.query.with_entities(UserSetting.userId).filter_by(anonymousDataSharingON=1).all()
    legalIntIDs = [id[0] for id in legalIDs]
    print(legalIntIDs)
    if form.validate_on_submit():
        argument = form.argument.data
        sex = form.sex.data
        age_from = form.age_from.data
        age_to = form.age_to.data
        weight_from = form.weight_from.data
        weight_to = form.weight_to.data
        sexIntIDs = []
        ageFromIntIDs = []
        ageToIntIDs = []
        weightFromIntIDs = []
        weightToIntIDs = []
        if sex != "None":
            sexIDs = User.query.with_entities(User.id).filter_by(sex!=sex).all()
            sexIntIDs = [id[0] for id in sexIDs]
            for id in sexIntIDs:
                if id in legalIntIDs:
                    legalIntIDs.remove(id)
        if age_from != "None":
            age_from_complete = age_from + "-01-01"
            ageFromIDs = User.query.with_entities(User.id).filter(User.birthday>age_from_complete).all()
            ageFromIntIDs = [id[0] for id in ageFromIDs]
            for id in ageFromIntIDs:
                if id in legalIntIDs:
                    legalIntIDs.remove(id)
        if age_to != "None":
            age_to_complete = age_to + "-01-01"
            ageToIDs = User.query.with_entities(User.id).filter(User.birthday<age_to_complete).all()
            ageToIntIDs = [id[0] for id in ageToIDs]
            for id in ageToIntIDs:
                if id in legalIntIDs:
                    legalIntIDs.remove(id)
        if weight_from is not None:
            weightFromIDs = Weight.query.with_entities(Weight.userIdWeight)\
                .filter(Weight.weightValue>weight_from).all()
            weightFromIntIDs = [id[0] for id in weightFromIDs]
            for id in weightFromIntIDs:
                if id in legalIntIDs:
                    legalIntIDs.remove(id)
        if weight_to is not None:
            weightToIDs = Weight.query.with_entities(Weight.userIdWeight)\
                .filter(Weight.weightValue<weight_to).all()
            weightToIntIDs = [id[0] for id in weightToIDs]
            for id in weightToIntIDs:
                if id in legalIntIDs:
                    legalIntIDs.remove(id)
        if argument == 'BloodPressure':
            #result = BloodPressure.query.with_entities(BloodPressure.bloodPressureUserId,
            #                                           BloodPressure.bloodPressureLowValue,
            #                                           BloodPressure.bloodPressureHighValue,
            #                                           BloodPressure.bloodPressureTimestamp).filter(BloodPressure.bloodPressureUserId.in_(legalIntIDs)).all()
            stringsql = "SELECT * FROM BloodPressure WHERE BloodPressure.bloodPressureUserId in " \
                        "(" + ''.join(str(legalIntIDs)[1:-1]) + ")"
        elif argument == "HeartRate":
            stringsql = "SELECT * FROM HeartRate WHERE HeartRate.heartRateUserId in " \
                        "(" + ''.join(str(legalIntIDs)[1:-1]) + ")"
        else:
            stringsql = "SELECT * FROM DailyStep WHERE DailyStep.dailyStepsId in " \
                        "(" + ''.join(str(legalIntIDs)[1:-1]) + ")"
        res = db.engine.execute(stringsql)
        jres = json.dumps([(dict(row.items())) for row in res])
        print(jres)
        #stringsql = form.query.data
        #print(stringsql)
        #result = db.engine.execute(stringsql)
        #result2 = db.engine.execute(stringsql)
        #jresponse = json.dumps([(dict(row.items())) for row in result2])
    return render_template('sqlquery.html', title='My Develop', form=form, jtext=jres)


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
    userSettings = UserSetting.query.filter_by(userId=user.get_id()).first()
    if userSettings is None:
        response = {'Response': 'Error', 'Message': 'No settings found for this user.', 'Code': '110'}
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
    response['AutomatedSOSOn'] = userSettings.automatedSOSOn
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
    emergencystats = EmergencyEvents.query.filter_by(eventId=user.get_id()).order_by(EmergencyEvents.eventTime.desc()).first()
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

    if emergencystats is None:
        data['EmergencyTime'] = 0
        data['EmergencyType'] = 'None'
    else:
        data['EmergencyTime'] = emergencystats.eventTime
        data['EmergencyType'] = emergencystats.eventDesc
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
    emergencystats = EmergencyEvents.query.filter_by(eventId=ext_user.get_id()).order_by(EmergencyEvents.eventTime.desc()).first()
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
        data['EmergencyTime'] = 0
        data['EmergencyType'] = 'None'
    else:
        if caretaking.requestStatusCode is (0 or 2):
            data['Subscription'] = False
            data['StatusCode'] = caretaking.requestStatusCode
            data['Steps'] = 0
            data['Heartbeat'] = "No measurements"
            data['EmergencyTime'] = 0
            data['EmergencyType'] = 'None'
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
            if emergencystats is None:
                data['EmergencyTime'] = 0
                data['EmergencyType'] = 'None'
            else:
                data['EmergencyTime'] = emergencystats.eventTime
                data['EmergencyType'] = emergencystats.eventDesc
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
    requests = Caretaker.query.filter_by(observedUserId=user.get_id(), requestStatusCode=2).all()
    observedusers = Caretaker.query.filter_by(caretakerId=user.get_id(), subscription=1, requestStatusCode=1).all()
    midnight = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    response = {}
    data = {}
    reqs =[]
    alerts = []
    for req in requests:
        qr = User.query.filter_by(id=req.caretakerId).first()
        elem = {}
        elem['Email'] = qr.email
        elem['Surname'] = qr.surname
        elem['Name'] = qr.name
        reqs.append(elem)
    for observeduser in observedusers:
        qr = User.query.filter_by(id=observeduser.observedUserId).first()
        emergencystats = EmergencyEvents.query.filter_by(eventId=observeduser.observedUserId).order_by(EmergencyEvents.eventTime.desc()).filter(EmergencyEvents.eventTime >= midnight).first()
        elem = {}
        elem['Email'] = qr.email
        elem['Surname'] = qr.surname
        elem['Name'] = qr.name
        if emergencystats is not None:
            elem['EmergencyTime'] = emergencystats.eventTime
            elem['EmergencyType'] = emergencystats.eventDesc
            alerts.append(elem)
    data['Requests'] = reqs
    data['Alerts'] = alerts
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
    caretake = Caretaker.query.filter_by(caretakerId=ext_user.get_id(), observedUserId=user.get_id()).first()
    caretake.requestStatusCode = answer
    db.session.commit()

    response = {'Response': 'Success', 'Code': '209', 'Message': "Answer submitted."}
    jresponse = json.dumps(response)
    return jresponse


@app.route('/android/sync_health_data', methods=['GET', 'POST'])
def sync_health_data():
    input_json = request.get_json(force=True)
    token = input_json['Token']
    print(token)
    user = User.verify_auth_token(token)
    if user is None:
        response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        jresponse = json.dumps(response)
        return jresponse
    steps = input_json['Steps']
    heartrate = input_json['Heartrate']

    heartRate = HeartRate(heartRateUserId=user.get_id(), heartRateValue=heartrate,
                          heartRateTimestamp=datetime.datetime.now())
    dailySteps = DailyStep.query.filter_by(dailyStepsId=user.get_id(), stepsDate=datetime.date.today()).first()
    if dailySteps is None:
        newDailySteps = DailyStep(dailyStepsId=user.get_id(), stepsValue=steps, stepsDate=datetime.date.today())
        db.session.add(newDailySteps)
    else:
        dailySteps.stepsValue = steps
    db.session.add(heartRate)
    db.session.commit()

    response = {'Response': 'Success', 'Code': '210', 'Message': "Data submitted."}
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
        caretake = Caretaker.query.filter_by(caretakerId=ext_user.get_id(), observedUserId=user.get_id()).first()
        caretake.requestStatusCode = 0
        db.session.commit()
    response = {'Response': 'Success', 'Code': '209', 'Message': "Cleared users' notifications.", 'Number': number}
    jresponse = json.dumps(response)
    return jresponse


@app.route('/android/manage_automatedsos', methods=['GET', 'POST'])
def manage_automatedsos():
    input_json = request.get_json(force=True)
    token = input_json['Token']
    print(token)
    setting = input_json['AutomatedSOS']
    user = User.verify_auth_token(token)
    if user is None:
        response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        jresponse = json.dumps(response)
        return jresponse
    userSettings = UserSetting.query.filter_by(userId=user.get_id()).first()
    if userSettings is None:
        response = {'Response': 'Error', 'Message': 'No settings found for this user.', 'Code': '110'}
        jresponse = json.dumps(response)
        return jresponse

    userSettings.automatedSOSOn = setting
    db.session.commit()

    response = {'Response': 'Success', 'Code': '210', 'Message': "Data submitted."}
    jresponse = json.dumps(response)
    return jresponse


@app.route('/android/emergency_automatedsos', methods=['GET', 'POST'])
def emergency_automatedsos():
    input_json = request.get_json(force=True)
    token = input_json['Token']
    print(token)
    type = input_json['Type']
    accurate = input_json['Accurate']
    latitude = input_json['Latitude']
    longitude = input_json['Longitude']
    user = User.verify_auth_token(token)
    if user is None:
        response = {'Response': 'Error', 'Message': 'The token does not correspond to a User.', 'Code': '104'}
        jresponse = json.dumps(response)
        return jresponse

    if not accurate:
        userSettings = UserSetting.query.filter_by(userId=user.get_id()).first()
        if userSettings is None:
            response = {'Response': 'Error', 'Message': 'No settings found for this user.', 'Code': '110'}
            jresponse = json.dumps(response)
            return jresponse
        latitude = userSettings.defaultLocationLat
        longitude = userSettings.defaultLocationLong

    service = choose_service_from_location(latitude, longitude)
    if service is None:
        response = {'Response': 'Error', 'Message': 'No emergency service available for this area.', 'Code': '130'}
        jresponse = json.dumps(response)
        return jresponse

    emergencyrequest = EmergencyRequestsCallCenter(eventTime=datetime.datetime.now(), eventDesc=type,
                                                   eventUserId=user.get_id(), eventLat=latitude,
                                                   eventLong=longitude,
                                                   eventPhoneNumber=service.EmergencyServicePhoneNumber)

    emergencystat = EmergencyEvents(eventId=user.get_id(),eventTime=datetime.datetime.now(),eventDesc=type)

    db.session.add(emergencyrequest)
    db.session.add(emergencystat)
    db.session.commit()
    response = {'Response': 'Success', 'Code': '220', 'Message': "Data submitted."}
    jresponse = json.dumps(response)
    return jresponse


# This function fakes the calculation of the real service to call
def choose_service_from_location(latitude, longitude):
    service = EmergencyServicesAPI.query.first()
    return service


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


@app.route('/customer_service/requests')
def getRequests():
    requests = EmergencyRequestsCallCenter.query.all()
    return requests


@app.route('/customer_service/call_center_panel')
def call_center_panel():

    return render_template("call_center.html", title='Personnel panel', requests=getRequests())
