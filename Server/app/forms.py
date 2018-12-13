from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField,SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


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
      query = StringField('City', validators=[DataRequired()])
      sex = SelectField('Sex', choices=[('M','Male'), ('F','Female'), ('O','Other')],validators=[DataRequired()])
      option = SelectField('Option', choices=[('B','Blood preassure'), ('D','Daily step')],validators=[DataRequired()])
      submit = SubmitField('Send')

