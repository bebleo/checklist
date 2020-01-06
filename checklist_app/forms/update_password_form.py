from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, EqualTo, InputRequired

class UpdatePasswordForm(FlaskForm):
    username = StringField(
        "username",
        validators=[
            InputRequired("Username cannot be empty."),
            Email("Username must be a valid email address.")
        ]
    )
    password = PasswordField(
        "password",
        validators=[
            InputRequired("Password cannot be blank."),
            EqualTo("confirm", message="Password and confirmation must match.")
        ]
    )
    confirm = PasswordField("confirm")