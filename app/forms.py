from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea

class LoginForm(Form):
    email = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

class NewsForm(Form):
    title = StringField('title', validators=[DataRequired()])
    image = FileField('image')
    content = StringField('content', validators=[DataRequired()],widget=TextArea())
    
class CountryForm(Form):
    name = StringField('name', validators=[DataRequired()])
    heading = StringField('heading', validators=[DataRequired()])
    about = StringField('content', validators=[DataRequired()],widget=TextArea())