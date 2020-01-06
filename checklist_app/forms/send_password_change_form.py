from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Email, DataRequired

class SendPasswordChangeForm(FlaskForm):
    username = StringField(
        "username", 
        validators = [
            DataRequired("Email cannot be empty."), 
            Email("Email must be a valid email address.")
        ]
    )