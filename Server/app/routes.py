from flask import render_template, flash, redirect, url_for, request
from app import app, db,UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from app.forms import LoginForm, RegistrationForm, GeneralQueryForm
from app.models import User, UserSetting
from flask_login import logout_user, login_required, current_user, login_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import json, datetime, os

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

@app.route('/android/register')
def android_register():
    name = request.args.get('name')
    surname = request.args.get('surname')
    email = request.args.get('email')
    userPhoneNumber = request.args.get('userPhoneNumber')
    birthday_str = request.args.get('birthday')
    birthday = datetime.datetime.strptime(birthday_str, "%Y-%m-%d").date()
    password = request.args.get('password')
    sex = request.args.get('sex')
    present = User.query.filter_by(email=email).first()
    defaultLocationLat = float(0.0)
    defaultLocationLong = float(0.0)
    automatedSOSOn = bool(request.args.get('automatedSOSOn'))
    developerAccount = bool(request.args.get('developerAccount'))
    anonymousDataSharingON = bool(request.args.get('anonymousDataSharingON'))
    if present:
        response = {'Response': 'Error', 'Message': 'Already used email.'}
        jresponse = json.dumps(response)
        print(jresponse)
        return jresponse
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
    response = {'Response': 'Success', 'Message': 'The User has been correctly registered.'}
    jresponse = json.dumps(response)
    print(jresponse)
    return jresponse

@app.route('/uploads', methods=['GET', 'POST'])
def uploads():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return 'Tutto ok'