from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from checklist_app.models.user import get_user
from werkzeug.security import check_password_hash

class LoginForm(FlaskForm):
    username = StringField("username", validators=[Email("Email must be a valid address.")])
    password = PasswordField("password", validators=[DataRequired("Password cannot be blank.")])
    remember = BooleanField("remember")

    _user = None

    def validate_username(self, field):
        self._user = get_user(field.data)
        if self._user is None:
            raise ValidationError("Login incorrect, please try again.")

    def validate_password(self, field):
        if self._user:
            if not check_password_hash(self._user['password'], field.data):
                raise ValidationError("Login incorrect, please try again.")

