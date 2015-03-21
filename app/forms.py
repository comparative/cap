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
    principal = StringField('principal', validators=[DataRequired()])
    location = StringField('location', validators=[DataRequired()])
    image = FileField('image')
    heading = StringField('heading', validators=[DataRequired()])
    about = StringField('content', validators=[DataRequired()],widget=TextArea())

class UserForm(Form):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
   
    