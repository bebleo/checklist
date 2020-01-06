from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import Email, EqualTo, InputRequired


class RegistrationForm(FlaskForm):
    username = StringField("username", 
        validators=[InputRequired("Username cannot be empty."), 
                    Email("Username must be a valid email")])
    given_name = StringField('given_name')
    family_name = StringField("family_name")
    password = PasswordField("password", 
        validators=[InputRequired("Password cannot be empty."), 
                    EqualTo("confirm", message="Password and confirmation must match.")])
    confirm = PasswordField("confirm", 
        validators={InputRequired("Password cannot be empty.")})
