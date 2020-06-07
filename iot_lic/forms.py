# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, RadioField, SelectField, \
    SelectMultipleField, IntegerField
from wtforms.validators import DataRequired
from wtforms.widgets import ListWidget, CheckboxInput


class IndexForm(FlaskForm):
    device_name = StringField('Device name', validators=[DataRequired()])
    ip = StringField('IP address', validators=[DataRequired()])
    port = StringField('Port', validators=[DataRequired()])
    submit = SubmitField('Add')


class ComForm(FlaskForm):
    device_name = StringField('Device name', validators=[DataRequired()])
    command = StringField('Command', validators=[DataRequired()])
    submit = SubmitField('Add')