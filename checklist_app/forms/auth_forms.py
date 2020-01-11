from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import BooleanField, PasswordField, StringField, ValidationError

from checklist_app.models.user import get_user

from .shared_validators import (confirm_req, password_conf, password_req,
                                username_combo, username_email)


class LoginForm(FlaskForm):
    username = StringField("username", validators=[username_email])
    password = PasswordField("password", validators=[password_req])
    remember = BooleanField("remember")

    error_msg = "Login incorrect, please try again."
    _user = None

    def validate_username(self, field):
        self._user = get_user(field.data)
        if self._user is None:
            raise ValidationError(self.error_msg)

    def validate_password(self, field):
        if self._user:
            if not check_password_hash(self._user['password'], field.data):
                raise ValidationError(self.error_msg)


class RegistrationForm(FlaskForm):
    username = StringField("username", validators=username_combo)
    given_name = StringField('given_name')
    family_name = StringField("family_name")
    password = PasswordField("password",
                             validators=[password_req, password_conf])
    confirm = PasswordField("confirm", validators=[confirm_req])


class SendPasswordChangeForm(FlaskForm):
    username = StringField("username", validators=username_combo)


class UpdatePasswordForm(FlaskForm):
    username = StringField("username", validators=username_combo)
    password = PasswordField("password",
                             validators=[password_conf, password_req])
    confirm = PasswordField("confirm", validators=[confirm_req])
