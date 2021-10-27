from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, IntegerField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError

class DeleteForm(FlaskForm):
    id = IntegerField('ID')
    username = StringField('Username')
    squadron_id = IntegerField('Squadron ID')
    type = StringField('Job Type')
    submit = SubmitField('Submit')
