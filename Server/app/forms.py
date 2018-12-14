from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Optional
from app.models import User

years = []
for year in range(100):
    stri = '{}'.format(year+1900)
    years.append(tuple([stri, stri]))

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    birthday = DateField('Birthday', validators=[DataRequired()])
    phonenumber = StringField('Phone number', validators=[DataRequired()])
    sex = StringField('Sex', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    developer_option = BooleanField('Developer Account')
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class GeneralQueryForm(FlaskForm):
    age_from = SelectField('Age From', choices=years, validators=[Optional()])
    age_to = SelectField('Age To', choices=years, validators=[Optional()])
    weight_from = IntegerField('Weight From', validators=[Optional()])
    weight_to = IntegerField('Weight To', validators=[Optional()])
    sex = SelectField('Sex', choices=[('Male','Male'), ('Female','Female'), ('Other','Other')], validators=[Optional()])
    argument = SelectField('Option', choices=[('HeartRate', 'Heart Rate'), ('BloodPressure','Blood Pressure'), ('DailyStep','Daily Step')], validators=[DataRequired()])
    submit = SubmitField('Send')

