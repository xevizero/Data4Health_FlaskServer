from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

metadata = db.Model.metadata


class EmergencyServicesAPI(db.Model):
    __tablename__ = 'EmergencyServicesAPI'

    EmergencyServiceId = db.Column(db.Integer, primary_key=True)
    AreaCode = db.Column(db.String, nullable=False)
    EmergencyServiceSupportsWebAPI = db.Column(db.Boolean, nullable=False)
    EmergencyServiceAPIUrl = db.Column(db.String)
    EmergencyServicePhoneNumber = db.Column(db.String)


class EmergencyEvents(db.Model):
    __tablename__ = 'EmergencyStats'

    eventId = db.Column(db.Integer, primary_key=True)
    eventTime = db.Column(db.Integer, primary_key=True)
    eventDesc = db.Column(db.String)


class EmergencyRequestsCallCenter(db.Model):
    __tablename__ = 'EmergencyRequestsCallCenter'

    eventId = db.Column(db.Integer, primary_key=True)
    eventTime = db.Column(db.Integer, nullable=False)
    eventDesc = db.Column(db.String)
    eventUserId = db.Column(db.Integer)
    eventLat = db.Column(db.Float)
    eventLong = db.Column(db.Float)
    eventPhoneNumber = db.Column(db.String)


class User(UserMixin, db.Model):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    passwordHash = db.Column(db.String(128), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    userPhoneNumber = db.Column(db.String)
    sex = db.Column(db.String, nullable=False)
    token = db.Column(db.String)

    #settings = db.relationship('UserSetting', backref='User', lazy='dynamic')


    def __repr__(self):
        return '<User {}>'.format(self.name)

    def set_password(self, password):
        self.passwordHash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwordHash, password)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user


class BloodPressure(db.Model):
    __tablename__ = 'BloodPressure'

    bloodPressureUserId = db.Column(db.Integer, primary_key=True)
    bloodPressureLowValue = db.Column(db.Integer, nullable=False)
    bloodPressureHighValue = db.Column(db.Integer, nullable=False)
    bloodPressureTimestamp = db.Column(db.DateTime, nullable=False)


class Caretaker(db.Model):
    __tablename__ = 'Caretaker'

    caretakerId = db.Column(db.Integer, primary_key=True)
    observedUserId = db.Column(db.Integer, nullable=False, primary_key=True)
    subscription = db.Column(db.Boolean, nullable=False)
    # 0 rifiutata
    # 1 accettata
    # 2 in corso
    requestStatusCode = db.Column(db.Integer, nullable=False)


class DailyStep(db.Model):
    __tablename__ = 'DailyStep'

    dailyStepsId = db.Column(db.Integer, primary_key=True)
    stepsValue = db.Column(db.Integer, nullable=False)
    stepsDate = db.Column(db.Date, nullable=False, primary_key=True)

    def __repr__(self):
        return '<StepData {}>'.format(self.stepsValue)


class HeartRate(db.Model):
    __tablename__ = 'HeartRate'

    heartRateUserId = db.Column(db.Integer, primary_key=True)
    heartRateValue = db.Column(db.Integer, nullable=False)
    heartRateTimestamp = db.Column(db.DateTime, nullable=False, primary_key=True)


class UserSetting(db.Model):
    __tablename__ = 'UserSetting'

    userId = db.Column(db.Integer, primary_key=True)
    defaultLocationLat = db.Column(db.Float, nullable=False)
    defaultLocationLong = db.Column(db.Float, nullable=False)
    automatedSOSOn = db.Column(db.Boolean, nullable=False)
    developerAccount = db.Column(db.Boolean, nullable=False)
    anonymousDataSharingON = db.Column(db.Boolean, nullable=False)


class UsersLocation(db.Model):
    __tablename__ = 'UsersLocation'

    usersLocationId = db.Column(db.Integer, primary_key=True)
    userLat = db.Column(db.Float, nullable=False)
    userLong = db.Column(db.Float, nullable=False)
    locationUpdateTimestamp = db.Column(db.DateTime, nullable=False)


class Weight(db.Model):
    __tablename__ = 'Weight'

    userIdWeight = db.Column(db.Integer, primary_key=True)
    weightValue = db.Column(db.Float, nullable=False)
    weightTimestamp = db.Column(db.DateTime, nullable=False)


class Run(db.Model):
    __tablename__ = 'Run'

    runId = db.Column(db.Integer, primary_key=True)
    eventName = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    startTime = db.Column(db.DateTime, nullable=False)
    locationLat = db.Column(db.Float, nullable=False)
    locationLong = db.Column(db.Float, nullable=False)
    public = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    organizerId = db.Column(db.ForeignKey('User.id'), nullable=False)

    user = db.relationship('User')
    users = db.relationship('User', secondary='RunViewer')


class RunParticipant(db.Model):
    __tablename__ = 'RunParticipant'

    participantsRunId = db.Column(db.ForeignKey('Run.runId'), primary_key=True, nullable=False)
    participantsUserId = db.Column(db.ForeignKey('User.id'), primary_key=True, nullable=False)
    dataVisibility = db.Column(db.Boolean, nullable=False)

    run = db.relationship('Run')
    user = db.relationship('User')


t_RunViewers = db.Table(
    'RunViewer', metadata,
    db.Column('ViewersRunId', db.ForeignKey('Run.runId'), primary_key=True, nullable=False),
    db.Column('ViewersUserId', db.ForeignKey('User.id'), primary_key=True, nullable=False)
)


class RunWaypoint(db.Model):
    __tablename__ = 'RunWaypoint'

    pathRunId = db.Column(db.ForeignKey('Run.runId'), primary_key=True, nullable=False)
    waypointIndex = db.Column(db.Integer, primary_key=True, nullable=False)
    pathLat = db.Column(db.Float, nullable=False)
    pathLong = db.Column(db.Float, nullable=False)
    optionalName = db.Column(db.String)

    run = db.relationship('Run')


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
