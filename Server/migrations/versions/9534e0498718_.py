"""empty message

Revision ID: 9534e0498718
Revises: 
Create Date: 2018-12-04 17:31:25.867853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9534e0498718'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Caretaker',
    sa.Column('caretakerId', sa.Integer(), nullable=False),
    sa.Column('observedUserId', sa.Integer(), nullable=False),
    sa.Column('subscription', sa.Boolean(), nullable=False),
    sa.Column('requestStatusCode', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('caretakerId', 'observedUserId')
    )
    op.create_table('DailyStep',
    sa.Column('dailyStepsId', sa.Integer(), nullable=False),
    sa.Column('stepsValue', sa.Integer(), nullable=False),
    sa.Column('stepsDate', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('dailyStepsId', 'stepsDate')
    )
    op.create_table('EmergencyServicesAPI',
    sa.Column('EmergencyServiceId', sa.Integer(), nullable=False),
    sa.Column('AreaCode', sa.String(), nullable=False),
    sa.Column('EmergencyServiceSupportsWebAPI', sa.Boolean(), nullable=False),
    sa.Column('EmergencyServiceAPIUrl', sa.String(), nullable=True),
    sa.Column('EmergencyServicePhoneNumber', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('EmergencyServiceId')
    )
    op.create_table('HeartRate',
    sa.Column('heartRateUserId', sa.Integer(), nullable=False),
    sa.Column('heartRateValue', sa.Integer(), nullable=False),
    sa.Column('heartRateTimestamp', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('heartRateUserId', 'heartRateTimestamp')
    )
    op.create_table('User',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('surname', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('passwordHash', sa.String(length=128), nullable=False),
    sa.Column('birthday', sa.Date(), nullable=False),
    sa.Column('userPhoneNumber', sa.String(), nullable=True),
    sa.Column('sex', sa.String(), nullable=False),
    sa.Column('token', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('UserSetting',
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.Column('defaultLocationLat', sa.Float(), nullable=False),
    sa.Column('defaultLocationLong', sa.Float(), nullable=False),
    sa.Column('automatedSOSOn', sa.Boolean(), nullable=False),
    sa.Column('developerAccount', sa.Boolean(), nullable=False),
    sa.Column('anonymousDataSharingON', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('userId')
    )
    op.create_table('BloodPressure',
    sa.Column('bloodPressureUserId', sa.Integer(), nullable=False),
    sa.Column('bloodPressureLowValue', sa.Integer(), nullable=False),
    sa.Column('bloodPressureHighValue', sa.Integer(), nullable=False),
    sa.Column('bloodPressureTimestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['bloodPressureUserId'], ['User.id'], ),
    sa.PrimaryKeyConstraint('bloodPressureUserId')
    )
    op.create_table('EmergencyStats',
    sa.Column('eventId', sa.Integer(), nullable=False),
    sa.Column('eventTime', sa.Integer(), nullable=False),
    sa.Column('eventDesc', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['eventId'], ['User.id'], ),
    sa.PrimaryKeyConstraint('eventId')
    )
    op.create_table('Run',
    sa.Column('runId', sa.Integer(), nullable=False),
    sa.Column('eventName', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('startTime', sa.DateTime(), nullable=False),
    sa.Column('locationLat', sa.Float(), nullable=False),
    sa.Column('locationLong', sa.Float(), nullable=False),
    sa.Column('public', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('organizerId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['organizerId'], ['User.id'], ),
    sa.PrimaryKeyConstraint('runId')
    )
    op.create_table('UsersLocation',
    sa.Column('usersLocationId', sa.Integer(), nullable=False),
    sa.Column('userLat', sa.Float(), nullable=False),
    sa.Column('userLong', sa.Float(), nullable=False),
    sa.Column('locationUpdateTimestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['usersLocationId'], ['User.id'], ),
    sa.PrimaryKeyConstraint('usersLocationId')
    )
    op.create_table('Weight',
    sa.Column('userIdWeight', sa.Integer(), nullable=False),
    sa.Column('weightValue', sa.Float(), nullable=False),
    sa.Column('weightTimestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['userIdWeight'], ['User.id'], ),
    sa.PrimaryKeyConstraint('userIdWeight')
    )
    op.create_table('RunParticipant',
    sa.Column('participantsRunId', sa.Integer(), nullable=False),
    sa.Column('participantsUserId', sa.Integer(), nullable=False),
    sa.Column('dataVisibility', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['participantsRunId'], ['Run.runId'], ),
    sa.ForeignKeyConstraint(['participantsUserId'], ['User.id'], ),
    sa.PrimaryKeyConstraint('participantsRunId', 'participantsUserId')
    )
    op.create_table('RunViewer',
    sa.Column('ViewersRunId', sa.Integer(), nullable=False),
    sa.Column('ViewersUserId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['ViewersRunId'], ['Run.runId'], ),
    sa.ForeignKeyConstraint(['ViewersUserId'], ['User.id'], ),
    sa.PrimaryKeyConstraint('ViewersRunId', 'ViewersUserId')
    )
    op.create_table('RunWaypoint',
    sa.Column('pathRunId', sa.Integer(), nullable=False),
    sa.Column('waypointIndex', sa.Integer(), nullable=False),
    sa.Column('pathLat', sa.Float(), nullable=False),
    sa.Column('pathLong', sa.Float(), nullable=False),
    sa.Column('optionalName', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['pathRunId'], ['Run.runId'], ),
    sa.PrimaryKeyConstraint('pathRunId', 'waypointIndex')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('RunWaypoint')
    op.drop_table('RunViewer')
    op.drop_table('RunParticipant')
    op.drop_table('Weight')
    op.drop_table('UsersLocation')
    op.drop_table('Run')
    op.drop_table('EmergencyStats')
    op.drop_table('BloodPressure')
    op.drop_table('UserSetting')
    op.drop_table('User')
    op.drop_table('HeartRate')
    op.drop_table('EmergencyServicesAPI')
    op.drop_table('DailyStep')
    op.drop_table('Caretaker')
    # ### end Alembic commands ###