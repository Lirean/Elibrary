from flask.ext.wtf import Form
from wtforms import SubmitField, HiddenField
from wtforms import ValidationError

class AddBookForm(Form):
    submit = SubmitField('Add to my library')

class RemoveBookForm(Form):
	submit = SubmitField('Remove from my library')