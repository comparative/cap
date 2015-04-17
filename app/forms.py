from flask.ext.uploads import IMAGES
from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileAllowed
from wtforms import StringField, BooleanField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.widgets import TextArea
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from models import Country

def countries_factory():
    return Country.query.all()

class LoginForm(Form):
    email = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

class PageForm(Form):
    title = StringField('title', validators=[DataRequired()])
    body = StringField('body', validators=[DataRequired()],widget=TextArea())
    
class FileForm(Form):
    name = StringField('name', validators=[DataRequired()])
    file = FileField('file')

class NewsForm(Form):
    title = StringField('title', validators=[DataRequired()])
    image = FileField('image',validators=[FileAllowed(IMAGES, 'Please choose an image file.')])
    content = StringField('content', validators=[DataRequired()],widget=TextArea())
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)

class ResearchForm(Form):
    title = StringField('title', validators=[DataRequired()])
    file = FileField('file',validators=[FileAllowed(['pdf'], 'Papers must be formatted as .pdf')])
    image = FileField('image')
    body = StringField('content', validators=[Length(min=0, max=9000)],widget=TextArea()) 
    featured = BooleanField('featured', default=False)
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)
    
class StaffForm(Form):
    name = StringField('name', validators=[DataRequired()])
    title = StringField('title')
    institution = StringField('institution')
    sort_order = IntegerField('sort_order', [NumberRange(min=0, max=10)])
    image = FileField('image',validators=[FileAllowed(IMAGES, 'Please choose an image file.')])
    body = StringField('content', validators=[DataRequired()],widget=TextArea()) 
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True) 

class CountryForm(Form):
    name = StringField('name', validators=[DataRequired()])
    short_name = StringField('name', validators=[DataRequired()])
    principal = StringField('principal')
    location = StringField('location')
    image = FileField('image',validators=[FileAllowed(IMAGES, 'Please choose an image file.')])
    heading = StringField('heading', validators=[DataRequired()])
    about = StringField('content', validators=[DataRequired()],widget=TextArea())
    embed_url = principal = StringField('embed_url')
    
class UserForm(Form):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    country = QuerySelectField(query_factory=countries_factory,allow_blank=True)
    
class SlideForm(Form):
    heading = StringField('heading', validators=[DataRequired()])
    subheading = StringField('subheading', validators=[DataRequired()])
    link = StringField('link', validators=[DataRequired()])
    image = FileField('image',validators=[FileAllowed(IMAGES, 'Please choose an image file.')])
    active = BooleanField('active', default=False)
   
    