from flask.ext.uploads import IMAGES
from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileAllowed
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from models import Country

def countries_factory():
    return Country.query.all()

class LoginForm(Form):
    email = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

class NewsForm(Form):
    title = StringField('title', validators=[DataRequired()])
    image = FileField('image',validators=[FileAllowed(IMAGES, 'Please choose an image file.')])
    content = StringField('content', validators=[DataRequired()],widget=TextArea())
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)

class ResearchForm(Form):
    title = StringField('title', validators=[DataRequired()])
    paper = FileField('paper',validators=[FileAllowed(['pdf'], 'Papers must be formatted as .pdf')])
    body = StringField('content', validators=[DataRequired()],widget=TextArea()) 
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)
    
class StaffForm(Form):
    name = StringField('name', validators=[DataRequired()])
    title = StringField('title')
    institution = StringField('institution')
    image = FileField('image',validators=[FileAllowed(IMAGES, 'Please choose an image file.')])
    body = StringField('content', validators=[DataRequired()],widget=TextArea()) 
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)   

class CountryForm(Form):
    name = StringField('name', validators=[DataRequired()])
    principal = StringField('principal')
    location = StringField('location')
    image = FileField('image',validators=[FileAllowed(IMAGES, 'Please choose an image file.')])
    heading = StringField('heading', validators=[DataRequired()])
    about = StringField('content', validators=[DataRequired()],widget=TextArea())
    
class UserForm(Form):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)
   
    