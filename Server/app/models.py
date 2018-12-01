from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

metadata = db.Model.metadata


class EmergencyServicesAPI(db.Model):
    __tablename__ = 'EmergencyServicesAPI'

    EmergencyServiceId = db.Column(db.Integer, primary_key=True)
    AreaCode = db.Column(db.String, nullable=False)
    EmergencyServiceSupportsWebAPI = db.Column(db.Boolean, nullable=False)
    EmergencyServiceAPIUrl = db.Column(db.String)
    EmergencyServicePhoneNumber = db.Column(db.String)


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

    #settings = db.relationship('UserSetting', backref='User', lazy='dynamic')


    def __repr__(self):
        return '<User {}>'.format(self.name)

    def set_password(self, password):
        self.passwordHash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwordHash, password)


class BloodPressure(User):
    __tablename__ = 'BloodPressure'

    bloodPressureUserId = db.Column(db.ForeignKey('User.id'), primary_key=True)
    bloodPressureLowValue = db.Column(db.Integer, nullable=False)
    bloodPressureHighValue = db.Column(db.Integer, nullable=False)
    bloodPressureTimestamp = db.Column(db.DateTime, nullable=False)


class Caretaker(User):
    __tablename__ = 'Caretaker'

    caretakerId = db.Column(db.ForeignKey('User.id'), primary_key=True)
    observedUserId = db.Column(db.Integer, nullable=False)
    subscription = db.Column(db.Boolean, nullable=False)
    requestStatusCode = db.Column(db.Integer, nullable=False)


class DailyStep(User):
    __tablename__ = 'DailyStep'

    dailyStepsId = db.Column(db.ForeignKey('User.id'), primary_key=True)
    stepsValue = db.Column(db.Integer, nullable=False)
    stepsDate = db.Column(db.Date, nullable=False)


class HeartRate(User):
    __tablename__ = 'HeartRate'

    heartRateUserId = db.Column(db.ForeignKey('User.id'), primary_key=True)
    heartRateValue = db.Column(db.Integer, nullable=False)
    heartRateTimestamp = db.Column(db.DateTime, nullable=False)


class UserSetting(db.Model):
    __tablename__ = 'UserSetting'

    userId = db.Column(db.Integer,
                       #db.ForeignKey('User.id'),
                       primary_key=True)
    defaultLocationLat = db.Column(db.Float, nullable=False)
    defaultLocationLong = db.Column(db.Float, nullable=False)
    automatedSOSOn = db.Column(db.Boolean, nullable=False)
    developerAccount = db.Column(db.Boolean, nullable=False)
    anonymousDataSharingON = db.Column(db.Boolean, nullable=False)


class UsersLocation(User):
    __tablename__ = 'UsersLocation'

    usersLocationId = db.Column(db.ForeignKey('User.id'), primary_key=True)
    userLat = db.Column(db.Float, nullable=False)
    userLong = db.Column(db.Float, nullable=False)
    locationUpdateTimestamp = db.Column(db.DateTime, nullable=False)


class Weight(User):
    __tablename__ = 'Weight'

    userIdWeight = db.Column(db.ForeignKey('User.id'), primary_key=True)
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
