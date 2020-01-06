from flask_wtf import FlaskForm
from wtforms import (BooleanField, PasswordField, SelectMultipleField,
                     StringField)
from wtforms.validators import Email, EqualTo, InputRequired
from wtforms.widgets import ListWidget, CheckboxInput

from checklist_app.models.user import AccountStatus


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class BaseUserForm(FlaskForm):
    username = StringField(
        "username",
        default="",
        validators=[
            InputRequired("Username must not be blank."),
            Email("Email must be a valid address.")
        ]
    )
    given_name = StringField("given_name", default="")
    family_name = StringField("family_name", default="")
    is_admin = BooleanField("is_admin")


class AddUserForm(BaseUserForm):
    password = PasswordField(
        "password",
        validators=[
            InputRequired("Password cannot be blank."),
            EqualTo("confirm", message="Password and confirmation must match.")
        ]
    )
    confirm = PasswordField("confirm")


class EditUserForm(BaseUserForm):
    account_flag = MultiCheckboxField(
        label="Account Flags",
        _name="account_flag",
        coerce=int,
        choices = [
            (AccountStatus.DEACTIVATED.value,"Account disabled"),
            (AccountStatus.PASSWORD_RESET_REQUIRED.value,"User must change password on next login"),
            (AccountStatus.VERIFICATION_REQUIRED.value,"Account verification required")
        ]
    )

        