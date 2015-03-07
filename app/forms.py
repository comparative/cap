from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])

class NewsForm(Form):
    title = StringField('title', validators=[DataRequired()])
    content = StringField('content', validators=[DataRequired()],widget=TextArea())