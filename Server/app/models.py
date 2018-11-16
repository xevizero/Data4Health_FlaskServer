from app import db


from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Table, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class EmergencyServicesAPI(Base):
    __tablename__ = 'EmergencyServicesAPIs'

    EmergencyServiceId = Column(Integer, primary_key=True)
    AreaCode = Column(String, nullable=False)
    EmergencyServiceSupportsWebAPI = Column(Boolean, nullable=False)
    EmergencyServiceAPIUrl = Column(String)
    EmergencyServicePhoneNumber = Column(String)


class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    Name = Column(String, nullable=False)
    Surname = Column(String, nullable=False)
    Email = Column(String, nullable=False)
    Birthday = Column(Date, nullable=False)
    UserPhoneNumber = Column(String)


class BloodPressure(User):
    __tablename__ = 'BloodPressure'

    BloodPressureUserId = Column(ForeignKey('Users.id'), primary_key=True)
    BloodPressureLowValue = Column(Integer, nullable=False)
    BloodPressureHighValue = Column(Integer, nullable=False)
    BloodPressureTimestamp = Column(DateTime, nullable=False)


class Caretaker(User):
    __tablename__ = 'Caretakers'

    CaretakerId = Column(ForeignKey('Users.id'), primary_key=True)
    ObservedUserId = Column(Integer, nullable=False)
    Subscription = Column(Boolean, nullable=False)


class DailyStep(User):
    __tablename__ = 'DailySteps'

    DailyStepsId = Column(ForeignKey('Users.id'), primary_key=True)
    StepsValue = Column(Integer, nullable=False)
    StepsDate = Column(Date, nullable=False)


class HeartRate(User):
    __tablename__ = 'HeartRate'

    HeartRateUserId = Column(ForeignKey('Users.id'), primary_key=True)
    HeartRateValue = Column(Integer, nullable=False)
    HeartRateTimestamp = Column(DateTime, nullable=False)


class UserSetting(User):
    __tablename__ = 'UserSettings'

    UserId = Column(ForeignKey('Users.id'), primary_key=True)
    DefaultLocationLat = Column(Float, nullable=False)
    DefaultLocationLong = Column(Float, nullable=False)
    AutomatedSOSOn = Column(Boolean, nullable=False)
    DeveloperAccount = Column(Boolean, nullable=False)
    AnonymousDataSharingON = Column(Boolean, nullable=False)


class UsersLocation(User):
    __tablename__ = 'UsersLocation'

    UsersLocationId = Column(ForeignKey('Users.id'), primary_key=True)
    UserLat = Column(Float, nullable=False)
    UserLong = Column(Float, nullable=False)
    LocationUpdateTimestamp = Column(DateTime, nullable=False)


class Weight(User):
    __tablename__ = 'Weight'

    UserIdWeight = Column(ForeignKey('Users.id'), primary_key=True)
    WeightValue = Column(Float, nullable=False)
    WeightTimestamp = Column(DateTime, nullable=False)


class Run(Base):
    __tablename__ = 'Run'

    RunId = Column(Integer, primary_key=True)
    EventName = Column(String, nullable=False)
    Description = Column(String, nullable=False)
    StartTime = Column(DateTime, nullable=False)
    LocationLat = Column(Float, nullable=False)
    LocationLong = Column(Float, nullable=False)
    Public = Column(Boolean, nullable=False, server_default=text("false"))
    OrganizerId = Column(ForeignKey('Users.id'), nullable=False)

    User = relationship('User')
    Users = relationship('User', secondary='RunViewers')


class RunParticipant(Base):
    __tablename__ = 'RunParticipants'

    ParticipantsRunId = Column(ForeignKey('Run.RunId'), primary_key=True, nullable=False)
    ParticipantsUserId = Column(ForeignKey('Users.id'), primary_key=True, nullable=False)
    DataVisibility = Column(Boolean, nullable=False)

    Run = relationship('Run')
    User = relationship('User')


t_RunViewers = Table(
    'RunViewers', metadata,
    Column('ViewersRunId', ForeignKey('Run.RunId'), primary_key=True, nullable=False),
    Column('ViewersUserId', ForeignKey('Users.id'), primary_key=True, nullable=False)
)


class RunWaypoint(Base):
    __tablename__ = 'RunWaypoints'

    PathRunId = Column(ForeignKey('Run.RunId'), primary_key=True, nullable=False)
    WaypointIndex = Column(Integer, primary_key=True, nullable=False)
    PathLat = Column(Float, nullable=False)
    PathLong = Column(Float, nullable=False)
    OptionalName = Column(String)

    Run = relationship('Run')
