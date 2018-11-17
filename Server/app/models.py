from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

metadata = db.Model.metadata


class EmergencyServicesAPI(db.Model):
    __tablename__ = 'EmergencyServicesAPIs'

    EmergencyServiceId = db.Column(db.Integer, primary_key=True)
    AreaCode = db.Column(db.String, nullable=False)
    EmergencyServiceSupportsWebAPI = db.Column(db.Boolean, nullable=False)
    EmergencyServiceAPIUrl = db.Column(db.String)
    EmergencyServicePhoneNumber = db.Column(db.String)


class User(UserMixin, db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String, nullable=False)
    Surname = db.Column(db.String, nullable=False)
    Email = db.Column(db.String, nullable=False)
    Password_Hash = db.Column(db.String(128), nullable=False)
    Birthday = db.Column(db.Date, nullable=False)
    UserPhoneNumber = db.Column(db.String)

    def __repr__(self):
        return '<User {}>'.format(self.Name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class BloodPressure(User):
    __tablename__ = 'BloodPressure'

    BloodPressureUserId = db.Column(db.ForeignKey('Users.id'), primary_key=True)
    BloodPressureLowValue = db.Column(db.Integer, nullable=False)
    BloodPressureHighValue = db.Column(db.Integer, nullable=False)
    BloodPressureTimestamp = db.Column(db.DateTime, nullable=False)


class Caretaker(User):
    __tablename__ = 'Caretakers'

    CaretakerId = db.Column(db.ForeignKey('Users.id'), primary_key=True)
    ObservedUserId = db.Column(db.Integer, nullable=False)
    Subscription = db.Column(db.Boolean, nullable=False)


class DailyStep(User):
    __tablename__ = 'DailySteps'

    DailyStepsId = db.Column(db.ForeignKey('Users.id'), primary_key=True)
    StepsValue = db.Column(db.Integer, nullable=False)
    StepsDate = db.Column(db.Date, nullable=False)


class HeartRate(User):
    __tablename__ = 'HeartRate'

    HeartRateUserId = db.Column(db.ForeignKey('Users.id'), primary_key=True)
    HeartRateValue = db.Column(db.Integer, nullable=False)
    HeartRateTimestamp = db.Column(db.DateTime, nullable=False)


class UserSetting(User):
    __tablename__ = 'UserSettings'

    UserId = db.Column(db.ForeignKey('Users.id'), primary_key=True)
    DefaultLocationLat = db.Column(db.Float, nullable=False)
    DefaultLocationLong = db.Column(db.Float, nullable=False)
    AutomatedSOSOn = db.Column(db.Boolean, nullable=False)
    DeveloperAccount = db.Column(db.Boolean, nullable=False)
    AnonymousDataSharingON = db.Column(db.Boolean, nullable=False)


class UsersLocation(User):
    __tablename__ = 'UsersLocation'

    UsersLocationId = db.Column(db.ForeignKey('Users.id'), primary_key=True)
    UserLat = db.Column(db.Float, nullable=False)
    UserLong = db.Column(db.Float, nullable=False)
    LocationUpdateTimestamp = db.Column(db.DateTime, nullable=False)


class Weight(User):
    __tablename__ = 'Weight'

    UserIdWeight = db.Column(db.ForeignKey('Users.id'), primary_key=True)
    WeightValue = db.Column(db.Float, nullable=False)
    WeightTimestamp = db.Column(db.DateTime, nullable=False)


class Run(db.Model):
    __tablename__ = 'Run'

    RunId = db.Column(db.Integer, primary_key=True)
    EventName = db.Column(db.String, nullable=False)
    Description = db.Column(db.String, nullable=False)
    StartTime = db.Column(db.DateTime, nullable=False)
    LocationLat = db.Column(db.Float, nullable=False)
    LocationLong = db.Column(db.Float, nullable=False)
    Public = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    OrganizerId = db.Column(db.ForeignKey('Users.id'), nullable=False)

    User = db.relationship('User')
    Users = db.relationship('User', secondary='RunViewers')


class RunParticipant(db.Model):
    __tablename__ = 'RunParticipants'

    ParticipantsRunId = db.Column(db.ForeignKey('Run.RunId'), primary_key=True, nullable=False)
    ParticipantsUserId = db.Column(db.ForeignKey('Users.id'), primary_key=True, nullable=False)
    DataVisibility = db.Column(db.Boolean, nullable=False)

    Run = db.relationship('Run')
    User = db.relationship('User')


t_RunViewers = db.Table(
    'RunViewers', metadata,
    db.Column('ViewersRunId', db.ForeignKey('Run.RunId'), primary_key=True, nullable=False),
    db.Column('ViewersUserId', db.ForeignKey('Users.id'), primary_key=True, nullable=False)
)


class RunWaypoint(db.Model):
    __tablename__ = 'RunWaypoints'

    PathRunId = db.Column(db.ForeignKey('Run.RunId'), primary_key=True, nullable=False)
    WaypointIndex = db.Column(db.Integer, primary_key=True, nullable=False)
    PathLat = db.Column(db.Float, nullable=False)
    PathLong = db.Column(db.Float, nullable=False)
    OptionalName = db.Column(db.String)

    Run = db.relationship('Run')


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
