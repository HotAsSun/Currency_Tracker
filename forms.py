from flask_wtf import FlaskForm
from flask_login import current_user , login_manager
from wtforms import StringField , PasswordField , BooleanField , SubmitField
from wtforms.validators import DataRequired , Length , Email , EqualTo , ValidationError
from models import Users



class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(),Length(min=4,max=20)])
    email = StringField('email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('password',
                             validators=[DataRequired(), Length(min=4,max=63  ) ])
    confirm_password = PasswordField('confirm password',
                             validators=[DataRequired(), Length(min=4,max=63),EqualTo('password')])
    submit = SubmitField('sign up')


    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

   
    
class LoginForm(FlaskForm):
    email = StringField('email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('password',
                             validators=[DataRequired(), Length(min=4,max=63  ) ])
    remember = BooleanField('remember me ')

    submit = SubmitField('log in')