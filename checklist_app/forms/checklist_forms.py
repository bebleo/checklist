from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired


class CreateListForm(FlaskForm):
    list_title = StringField(
        "list_title",
        validators=[InputRequired("Title for the list required.")],
        default=""
    )
    list_description = TextAreaField("list_description", default="")


class EditListForm(CreateListForm):
    pass


class AddItemForm(FlaskForm):
    item_text = StringField(
        "item_text",
        validators=[InputRequired("Text for item required.")],
        default=""
    )
