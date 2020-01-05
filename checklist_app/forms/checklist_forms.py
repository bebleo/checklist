from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Regexp


class CreateListForm(FlaskForm):
    list_title = StringField(
        "list_title", 
        validators=[InputRequired("Title for the list required.")]
    )
    list_description = TextAreaField("list_description")


class EditListForm(CreateListForm):
    pass