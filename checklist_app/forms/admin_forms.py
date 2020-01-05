from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import InputRequired, Email, EqualTo


class AddUserForm(FlaskForm):
    username = StringField(
        "username",
        default="",
        validators=[Email("Email must be a valid address.")]
    )
    given_name = StringField("given_name", default="")
    family_name = StringField("family_name", default="")
    password = PasswordField(
        "password",
        validators=[
            InputRequired("Password cannot be blank."),
            EqualTo("confirm", message="Password and confirmation must match.")
        ]
    )
    confirm = PasswordField("confirm")
    is_admin = BooleanField("is_admin")
