from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email
import phonenumbers

from saveYourGroceries.data.user import User 

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo('password')])
    number = StringField("Cell Number", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    # recaptcha = RecaptchaField()
    submit = SubmitField("Create Account")

    def validate_username(self, username):
        user = User.find_user(username=username.data)
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_number(self, number):
        try:
            input_number = phonenumbers.parse(number.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except:
            raise ValidationError('Invalid phone number.')
        user = User.find_user(number=number.data)
        if user:
            raise ValidationError('Please use a different number')
